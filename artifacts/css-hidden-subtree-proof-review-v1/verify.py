import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise SystemExit('requires -I -S without optimization')
sys.dont_write_bytecode = True
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import subprocess

ROOT = Path(__file__).resolve().parent

def need(ok, why):
    if not ok:
        raise SystemExit('REJECT: ' + why)

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def roster(root):
    files, dirs = set(), set()
    def walk(path):
        for entry in os.scandir(path):
            p = Path(entry.path)
            mode = p.lstat().st_mode
            rel = p.relative_to(root).as_posix()
            if stat.S_ISREG(mode):
                files.add(rel)
            elif stat.S_ISDIR(mode):
                dirs.add(rel)
                walk(p)
            else:
                need(False, 'nonregular:' + rel)
    walk(root)
    return files, dirs

def authenticate(root, pin):
    actual, dirs = roster(root)
    need(sha(root / 'FILES.json') == pin, 'manifest pin')
    files = json.loads((root / 'FILES.json').read_text())['files']
    need(all(not Path(n).is_absolute() and '..' not in Path(n).parts for n in files), 'paths')
    need(actual == set(files) | {'FILES.json', 'FREEZE.json'}, 'file roster')
    expected_dirs = {str(p) for n in files for p in Path(n).parents if str(p) != '.'}
    need(dirs == expected_dirs, 'directory roster')
    for n, h in files.items():
        need(sha(root / n) == h, 'hash:' + n)
    need(json.loads((root/'FREEZE.json').read_text()) == {'FILES_sha256':pin,'payload_count':len(files)}, 'freeze')
    return files

parser = argparse.ArgumentParser()
parser.add_argument('--manifest-sha', required=True)
args = parser.parse_args()
files = authenticate(ROOT, args.manifest_sha)
inner = 'e93989395671b1edb1b9586d77a9898596c526ef4a8b1f0a18df12ccbaf25452'
need(len(authenticate(ROOT/'capsule',inner))==22,'inner count')
r=subprocess.run([sys.executable,'-I','-S',str(ROOT/'capsule/replay.py'),'--manifest-sha',inner,'--verify-only'],capture_output=True,text=True)
need(r.returncode==0 and not r.stderr,'nested source verification')
summary=json.loads((ROOT/'replay/SUMMARY.json').read_text())
need(summary['outcome']=='PASS_SCOPED_SUBTREE_PROJECTION','replay status')
need(summary['new_audits']==36 and summary['imported_audits']==30 and summary['bindings']==15,'counts')
names=[]
for module in ('Hidden','Subtree'):
    names += [module+'.'+n for n in re.findall(r'^theorem (\w+)',(ROOT/f'capsule/lean/{module}.lean').read_text(),re.M)]
need(len(names)==66,'audit count')
need(re.findall(r"^'([\w.]+)'",(ROOT/'replay/lean-audits.stdout').read_text(),re.M)==names,'exact audit roster')
expected=(ROOT/'replay/lean-rows.stdout').read_text().splitlines()
need(len(expected)==6144,'rows')
mutants={'omit_mark':1920,'root_bit_only':512,'has_dirty_children_prunes':416,'principal_lists_only':384,'ignore_table_barrier':128,'ignore_dirty_barrier':960,'force_clean_query':3072}
for variant in ['none',*mutants]:
    for optimization in ('O0','O2'):
        name=variant+'-'+optimization
        actual=(ROOT/f'replay/run-{name}.stdout').read_text().splitlines()
        need(len(actual)==6144 and all(len(x.split(','))==38 and int(x.split(',')[0])==i for i,x in enumerate(actual)),'native row grammar')
        need(not (ROOT/f'replay/run-{name}.stderr').read_text(),'native stderr')
        need(sum(a!=b for a,b in zip(actual,expected))==mutants.get(variant,0),'native discrepancy count')
checks=re.findall(r'^theorem (\w+)',(ROOT/'Independent.lean').read_text(),re.M)
audit=(ROOT/'independent-output/Independent.stdout').read_text()
need(len(checks)==9 and re.findall(r"^'Independent.([\w]+)'",audit,re.M)==checks,'independent roster')
need(all(x.endswith('depends on axioms: [propext, Quot.sound]') for x in audit.splitlines()),'independent axioms')
need(not (ROOT/'independent-output/Independent.stderr').read_text(),'independent stderr')
commands=json.loads((ROOT/'independent-output/COMMANDS.json').read_text())
need(len(commands)==3 and all(c['returncode']==0 for c in commands),'independent exits')
guards=json.loads((ROOT/'GUARDS.json').read_text())
need(len(guards)==9 and all(g['returncode']!=0 and not g['output_created'] for g in guards[:-1]) and guards[-1]['returncode']==0,'guards')
need(not any(n.endswith(('.olean','.pyc')) for n in files),'generated outputs')
print(json.dumps({'outcome':'PASS_SCOPED_INDEPENDENT_REVIEW','payloads':len(files),'audits':66,'independent_checks':9,'rows_per_mode':6144,'guards':8}))
