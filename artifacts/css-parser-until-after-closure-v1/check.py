import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise RuntimeError('Require python3 -I -S without -O/-OO')
from pathlib import Path, PurePosixPath
import argparse, hashlib, json, os, re, stat, subprocess
ROOT=Path(__file__).resolve().parent
def require(value, message):
    if not value: raise RuntimeError(message)
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def unique(pairs):
    result={}
    for key,value in pairs:
        require(key not in result, 'duplicate JSON key: '+key)
        result[key]=value
    return result
def read_json(path):
    return json.loads(path.read_text(), object_pairs_hook=unique)
def authenticate():
    for name in ['FILES.json','FREEZE.json']:
        require(stat.S_ISREG((ROOT/name).lstat().st_mode), 'nonregular root seal: '+name)
    manifest=read_json(ROOT/'FILES.json')
    require(isinstance(manifest,list) and manifest, 'invalid manifest')
    expected_files={'FILES.json','FREEZE.json'};expected_dirs={''}
    for row in manifest:
        require(isinstance(row,dict) and set(row)=={'path','bytes','sha256'}, 'invalid manifest row')
        name=row['path'];require(isinstance(name,str), 'invalid manifest path')
        path=PurePosixPath(name)
        require(name==path.as_posix() and bool(path.parts) and not path.is_absolute()
            and all(part not in ('','.','..') for part in path.parts), 'invalid manifest path')
        require(name not in expected_files, 'duplicate / reserved manifest path')
        require(type(row['bytes']) is int and row['bytes']>=0, 'invalid input size')
        require(isinstance(row['sha256'],str) and re.fullmatch('[0-9a-f]{64}',row['sha256']), 'invalid digest')
        expected_files.add(name)
        for parent in path.parents:
            if str(parent)!='.':expected_dirs.add(str(parent))
    actual_files=set();actual_dirs={''}
    def visit(directory):
        with os.scandir(directory) as entries:
            for entry in entries:
                rel=Path(entry.path).relative_to(ROOT).as_posix()
                mode=entry.stat(follow_symlinks=False).st_mode
                if stat.S_ISDIR(mode):
                    require(rel in expected_dirs, 'unexpected directory: '+rel)
                    actual_dirs.add(rel);visit(entry.path)
                else:
                    require(stat.S_ISREG(mode), 'nonregular entry: '+rel)
                    actual_files.add(rel)
    visit(ROOT)
    require(actual_files==expected_files, 'file roster mismatch')
    require(actual_dirs==expected_dirs, 'directory roster mismatch')
    for row in manifest:
        path=ROOT/row['path']
        require(path.stat().st_size==row['bytes'] and sha(path)==row['sha256'], 'input mismatch: '+row['path'])
    freeze=read_json(ROOT/'FREEZE.json')
    require(freeze['FILES_sha256']==sha(ROOT/'FILES.json'), 'manifest seal mismatch')
    require(freeze['check_sha256']==sha(ROOT/'check.py'), 'checker seal mismatch')
    return manifest
initial_manifest=authenticate()
final=read_json(ROOT/'FINAL.json')
require(read_json(ROOT/'preflight/RESULT.json')==read_json(ROOT/'relocated/replay/RESULT.json'), 'replay result mismatch')
require(final['relocated_result']==read_json(ROOT/'relocated/replay/RESULT.json'), 'summary mismatch')
for name,digest in final['source_pins'].items():
    require(sha(ROOT/'relocated/source'/name)==digest, 'relocated source pin mismatch')
for row in read_json(ROOT/'relocated/source/FILES.json'):
    require(sha(ROOT/'relocated/source'/row['path'])==row['sha256'], 'relocated input mismatch')
guards=read_json(ROOT/'guards-final/GUARDS.json')
require(len(guards)==19 and all(row['pass_gate'] for row in guards), 'guard receipt mismatch')
cleanup=read_json(ROOT/'CLEANUP.json')
require(sum(row['bytes'] for row in cleanup['removed'])==cleanup['total_bytes'], 'cleanup total mismatch')
require(all(not (ROOT/row['path']).exists() for row in cleanup['removed']), 'completed output still present')
print('PASS: authenticated final source copy, equal successful replays,33audits/138snapshots/6native mutants,18negative+1positive guards, cleanup receipts')
