from pathlib import Path
import hashlib
import json
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
source = ROOT/'relocated'
external = {'FREEZE.json':'49809a90476bf07dc1780c4942136fd27a862cf0147e31a11ba2671d7bd52e12','MANIFEST.json':'5f00da8cda2a48e4e9e0e34cfaa68f75ca97f9bc64890465283cd7ba6d253e20','check.py':'8958afc0475c9ee10c0758ed587946ebea053e288dca0883a2c032920a59e5c2'}
for name,pin in external.items():assert digest(source/name)==pin
m=read(source/'MANIFEST.json');assert len(m)==463
assert {str(f.relative_to(source)) for f in source.rglob('*') if f.is_file()}==set(m)|{'MANIFEST.json','FREEZE.json'}
for name,pin in m.items():assert digest(source/name)==pin
for name,pin in read(ROOT/'RETAINED-RECEIPTS.json').items():assert digest(ROOT/name)==pin
r=ROOT/'receipts'
replay=read(r/'REPLAY.json');assert replay['status']=='PASS' and replay['authenticated_inputs']==463 and replay['source_definitions']==72
assert all(c['exit']==0 for c in replay['commands'])
assert digest(r/'SOURCE-BINDINGS.json')==digest(source/'SOURCE-BINDINGS.json')
inv=read(source/'LEAN-INVENTORY.json');names=read(source/'AUDIT-NAMES.json')
proof=read(r/'proof/CHECK.json');assert proof==replay['proof']
assert (proof['modules'],proof['new_modules'],proof['audits'],proof['new_audits'])==(57,11,448,77)
import re
rows=re.findall(r"^'([^']+)' (?:depends on axioms: \[([^]]*)\]|does not depend on any axioms)$",(r/'proof/Audit.log').read_text(),re.M)
assert [n for n,_ in rows]==names and len(names)==448
assert set(a.strip() for _,g in rows for a in g.split(',') if a.strip())=={'propext','Quot.sound','Classical.choice'}
assert len(inv['new_names'])==77 and sum(n.startswith('WrapperWitnesses.') for n in inv['new_names'])==17
lean_mutants=read(source/'LEAN-MUTATIONS.json')
for m in lean_mutants:
    witness=[c for c in proof['commands'] if c['log']=='mutation-'+m['id']+'-witness.log']
    rejected=[c for c in proof['commands'] if c['log']=='mutation-'+m['id']+'-rejected.log']
    assert len(witness)==len(rejected)==1 and witness[0]['exit']==0 and rejected[0]['exit']!=0
    text=(r/'proof'/rejected[0]['log']).read_text()
    assert 'error:' in text and not any(x in text for x in ['unknown identifier','unexpected token','unknown namespace','unknown constant'])
    assert m['witness'] in (r/'proof'/('mutation-'+m['id'])/'Witness.lean').read_text()
native=read(r/'native/CHECK.json');assert native==replay['native']
assert native['cases']==10 and native['operation_snapshots']==69
cases=read(source/'CASES.json');keys=[]
for i,c in enumerate(cases):
    keys.append([str(i),'0','init'])
    keys.extend([str(i),str(j+1),op] for j,op in enumerate(c['ops']))
expected=(r/'native/model.txt').read_text().splitlines()
def grammar(lines):
    assert len(lines)==len(keys)==69
    for line,key in zip(lines,keys):
        fields=line.split('|');assert len(fields)==11 and fields[:3]==key

grammar(expected)
for mode in ['debug','release']:
    assert (r/'native'/mode/'raw.txt').read_text().splitlines()==expected
    assert all(c['exit']==0 for c in read(r/'native'/mode/'COMMANDS.json'))
counts={'drop-fresh-function-effect':11,'replay-function-effect':6,'reset-disables-tracking':2,'wrong-cache-key':51,'skip-omits-pending':8,'next-clears-cache-after-skip':8,'skip-drops-comment-writes':18}
details=read(ROOT/'MUTATION-REVIEW.json')
for m in read(source/'MUTATIONS.json'):
    q=r/'native'/('mutant-'+m['id']);actual=(q/'raw.txt').read_text().splitlines();grammar(actual)
    commands=read(q/'COMMANDS.json');assert all(c['exit']==0 for c in commands)
    assert Path(commands[-1]['command'][0]).name=='probe'
    diffs=[{'index':i,'model':x,'native_mutant':y} for i,(x,y) in enumerate(zip(expected,actual)) if x!=y]
    assert len(diffs)==counts[m['id']]
    record=next(d for d in details if d['id']==m['id']);assert record['differences']==diffs
assert native['rejected_trace_corruptions']==['drop-first','duplicate-first','unknown-operation','extra-field','swap-first-two','observer-none-empty']
guards=read(ROOT/'GUARDS.json')
assert [g['name'] for g in guards]==['changed-lean','extra-file','extra-directory','symlink-file','duplicate-manifest','path-escape','without-isolation','existing-output']
assert all(g['exit']!=0 and 'AssertionError' in g['stderr'] and g['no_generated_output'] for g in guards)
assert sum(x['logical_bytes'] for x in read(ROOT/'CLEANUP.json'))==83155550
assert authenticate()==count
print(json.dumps({'status':'PASS','verdict':'ACCEPT_SCOPED_WRAPPER_COMPONENT','inputs':count,'producer_inputs':463,'modules':57,'audits':448,'new_audits':77,'source_bindings':72,'native_snapshots_per_mode':69,'native_mutants':7,'Lean_mutants':3,'integrity_challenges':8,'generated_bytes_removed':83155550}))
