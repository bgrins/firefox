from pathlib import Path
import argparse
import hashlib
import json
import subprocess
import sys

assert sys.flags.isolated and sys.flags.no_site
ROOT = Path(__file__).absolute().parent

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def unique(pairs):
    result = {}
    for key, value in pairs:
        assert key not in result, ('duplicate key', key)
        result[key] = value
    return result

def read(path):
    return json.loads(path.read_text(), object_pairs_hook=unique)

def authenticate():
    assert not ROOT.is_symlink()
    freeze = read(ROOT / 'FREEZE.json')
    assert digest(ROOT / 'MANIFEST.json') == freeze['manifest_sha256']
    assert digest(ROOT / 'check.py') == freeze['checker_sha256']
    manifest = read(ROOT / 'MANIFEST.json')
    expected = set(manifest) | {'MANIFEST.json', 'FREEZE.json'}
    files, dirs = set(), set()
    for path in ROOT.rglob('*'):
        assert not path.is_symlink(), path
        assert path.is_file() or path.is_dir(), path
        (files if path.is_file() else dirs).add(str(path.relative_to(ROOT)))
    assert files == expected, ('roster', files ^ expected)
    assert dirs == {str(p) for name in expected for p in Path(name).parents if str(p) != '.'}
    for name, pin in manifest.items():
        path = Path(name)
        assert not path.is_absolute() and '..' not in path.parts and str(path) == name
        assert (ROOT / path).resolve().is_relative_to(ROOT.resolve())
        assert digest(ROOT / path) == pin, name
    return len(manifest)

count = authenticate()
external = {
 'package': {'FREEZE.json':'0a290a6cbf83b6fa1be729cd13a3aeae23b77a4c6f86718baacbe0655bb83afe','MANIFEST.json':'a158bf5fb0be52bb3d252c69e18160e4d3e623a4650204fcff0279eea04fe75a','check.py':'3d84332b8ccbb71d9271efd0bc4df35af6d8e5a894c5d8027aab2b0b06722ae7'},
 'producer-receipts': {'FREEZE.json':'145262528a3c03693fe5e8e8bb5ac5f58d6a2ffc28af196c2314b44899e419aa','MANIFEST.json':'37672b05ce8425b5097dd6fca965343a5f322170879204dd51285f1fef115ee7'}}
for directory,pins in external.items():
 for name,pin in pins.items():assert digest(ROOT/directory/name)==pin
 for name,pin in read(ROOT/directory/'MANIFEST.json').items():assert digest(ROOT/directory/name)==pin
for name,pin in read(ROOT/'evidence/RECEIPT-SEAL.json').items():assert digest(ROOT/'evidence'/name)==pin
replay=ROOT/'evidence/replay'
receipt=read(replay/'REPLAY.json');assert receipt['status']=='PASS' and receipt['authenticated_inputs']==208 and receipt['source_definitions']==70
proof=read(replay/'proof/CHECK.json');assert proof==receipt['proof']
assert (proof['modules'],proof['new_modules'],proof['audits'],proof['new_audits'])==(46,15,371,108)
import re
names=read(ROOT/'package/AUDIT-NAMES.json')
audits=re.findall(r"^'([^']+)' (?:depends on axioms: \[([^]]*)\]|does not depend on any axioms)$",(replay/'proof/Audit.log').read_text(),re.M)
assert [n for n,_ in audits]==names and len(set(names))==371
assert all({s.strip() for s in ax.split(',') if s.strip()}<={'propext','Quot.sound','Classical.choice'} for _,ax in audits)
failed=[c for c in proof['commands'] if c['exit']!=0]
assert len(failed)==3 and all(c['log'].endswith('-rejected.log') for c in failed)
for m in proof['mutations']:
 assert m['definition_and_counterexample']=='PASS' and m['unchanged_theorems']=='REJECTED'
 commands=[c for c in proof['commands'] if c['log']=='mutation-'+m['id']+'-witness.log'];assert len(commands)==1 and commands[0]['exit']==0
 log=(replay/'proof'/('mutation-'+m['id']+'-rejected.log')).read_text()
 assert 'error:' in log and not any(x in log for x in ['unknown identifier','unexpected token','unknown namespace','unknown constant'])
native=read(replay/'native/CHECK.json');assert native==receipt['native']
assert native['cases']==14 and native['operation_snapshots']==87
expected=(replay/'native/model.txt').read_text().splitlines()
keys=[]
for i,c in enumerate(read(ROOT/'package/CASES.json')):
 keys.append([str(i),'0','init'])
 keys.extend([str(i),str(j+1),op] for j,op in enumerate(c['ops']))
assert len(keys)==len(expected)==87
for row,key in zip(expected,keys):assert len(row.split('|'))==11 and row.split('|')[:3]==key
for mode in ['debug','release']:
 assert (replay/'native'/mode/'raw.txt').read_text().splitlines()==expected
 assert all(c['exit']==0 for c in read(replay/'native'/mode/'COMMANDS.json'))
for m in native['native_mutants']:
 assert m['result']=='different projected observations'
 p=replay/'native'/('mutant-'+m['id'])
 assert all(c['exit']==0 for c in read(p/'COMMANDS.json'))
 rows=(p/'raw.txt').read_text().splitlines();assert len(rows)==87
 assert [i for i,(a,b) in enumerate(zip(rows,expected)) if a!=b]==m['rows'] and m['rows']
assert len(native['rejected_trace_corruptions'])==6
assert len(proof['mutations'])==3 and len(native['native_mutants'])==4
assert read(replay/'SOURCE-BINDINGS.json')==read(ROOT/'package/SOURCE-BINDINGS.json')
assert all(v['equal'] and v['live']==v['frozen'] for v in read(ROOT/'CURRENT-SOURCE.json').values())
assert len(read(ROOT/'evidence/EXTRACTION-CHECK.json'))==2
assert all(r['parser_exact_original_plus_wrapper'] and r['tokenizer_exact_original'] for r in read(ROOT/'evidence/EXTRACTION-CHECK.json'))
guards=read(ROOT/'evidence/guards/CHECK.json');assert len(guards)==8
assert all(r['exit']!=0 and not r['output_created'] and not r['shadow_executed'] for r in guards)
cleanup=read(ROOT/'CLEANUP.json');assert len(cleanup)==2
assert all(r['removed'] and r['bytes']>0 and not (ROOT/Path(r['path']).name).exists() for r in cleanup)
assert authenticate()==count
print(json.dumps({'status':'PASS','verdict':'ACCEPT_SCOPED_PUBLIC_HISTORY_COMPONENT','inputs':count,'audits':371,'native_snapshots_each_mode':87,'semantic_mutants':7,'fresh_integrity_guards':8,'removed_generated_bytes':sum(r['bytes'] for r in cleanup)}))
