import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise SystemExit('Use nonoptimized python3 -I -S')
sys.dont_write_bytecode = True
import argparse
import hashlib
import json
from pathlib import Path
import re
import stat
import subprocess

ROOT = Path(__file__).resolve().parent
INNER = '39401a7bfe598270b1eb664182a0ff00eb5904bed7608ab68938a86294b5a363'

def require(ok, message):
    if not ok:
        raise RuntimeError(message)

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

parser = argparse.ArgumentParser()
parser.add_argument('--manifest-sha', required=True)
args = parser.parse_args()
require(sha(ROOT/'FILES.json') == args.manifest_sha, 'outer pin')
manifest = json.loads((ROOT/'FILES.json').read_text())
files = manifest['files']
actual = set()
directories = set()
for p in ROOT.rglob('*'):
    mode = p.lstat().st_mode
    require(stat.S_ISREG(mode) or stat.S_ISDIR(mode), 'nonregular payload')
    if stat.S_ISREG(mode): actual.add(str(p.relative_to(ROOT)))
    else: directories.add(str(p.relative_to(ROOT)))
require(actual == set(files) | {'FILES.json','FREEZE.json'}, 'outer roster')
expected_dirs = {str(parent) for name in files for parent in Path(name).parents if str(parent) != '.'}
require(directories == expected_dirs, 'outer directories')
for name,digest in files.items(): require(sha(ROOT/name) == digest, 'payload: '+name)
require(json.loads((ROOT/'FREEZE.json').read_text()) == {'FILES_sha256':args.manifest_sha,'payload_count':len(files)},'outer freeze')
require(sha(ROOT/'capsule/FILES.json') == INNER, 'inner pin')
verified = subprocess.run([sys.executable,'-I','-S',str(ROOT/'capsule/replay.py'),'--manifest-sha',INNER,'--verify-only'],capture_output=True,text=True)
require(verified.returncode == 0, verified.stdout+verified.stderr)
names = [module+'.'+n for module in ('Hidden','Subtree','OOF') for n in re.findall(r'^theorem ([A-Za-z0-9_]+)',(ROOT/'capsule/lean'/f'{module}.lean').read_text(),re.M)]
require(len(names)==89,'theorem count')
variants = ['none','omit_mark','root_only','physical_parent','ignore_anon','clear_hidden_dirty','skip_continuations','query_clean','late_mark']
for directory in ('replay-first','replay-relocated'):
    d=ROOT/directory
    summary=json.loads((d/'SUMMARY.json').read_text())
    require(summary['outcome']=='PASS_SCOPED_OOF_PROJECTION' and summary['manifest_sha256']==INNER,'replay outcome')
    require(summary['new_audits']==23 and summary['imported_audits']==66 and summary['bindings']==25,'replay scope')
    audits=(d/'lean-audits.stdout').read_text()
    require(re.findall(r"^'([A-Za-z0-9_.]+)'",audits,re.M)==names,'audit roster')
    rows=(d/'lean-rows.stdout').read_text().splitlines()
    require(len(rows)==6144,'rows')
    for variant in variants:
        for opt in ('O0','O2'):
            actual_rows=(d/f'run-{variant}-{opt}.stdout').read_text().splitlines()
            require(len(actual_rows)==len(rows),'native rows')
            require((actual_rows==rows)==(variant=='none'),'comparison '+variant)
            require(not (d/f'run-{variant}-{opt}.stderr').read_text(),'UBSan output')
    commands=json.loads((d/'COMMANDS.json').read_text())
    require(all(c['exit'] != 0 if c['name'].startswith('false-') else c['exit']==0 for c in commands),'command exit')
    require(len(summary['falseclaims'])==4 and len(summary['mutants'])==16,'controls')
    require(all(not (d/name).exists() for name in summary['removed_products']),'compiler products remain')
guards=json.loads((ROOT/'GUARDS.json').read_text())
require(len(guards)==15 and all(g['exit']!=0 for g in guards),'guards')
require(json.loads((ROOT/'RELOCATION.json').read_text())['exit']==0,'relocation')
require(not list(ROOT.rglob('*.olean')) and not list(ROOT.rglob('*.pyc')),'cached products')
print(json.dumps({'outcome':'PASS_SCOPED_OOF_COMPANION','payloads':len(files),'audits':89,'bindings':25,'replays':2,'rows_per_optimization':6144,'semantic_mutants_per_replay':16,'falseclaims':4,'guards':15},sort_keys=True))
