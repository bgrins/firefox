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
source = ROOT / 'relocated'
pins = {'FREEZE.json':'99b557bb76ae1baa4e48213946bcce78cd1d2658cf6544ab176c4f2dcf58d67f','MANIFEST.json':'b2f916bdd63b820f64a738f96e1640f8ef827bd9d928f1b0c3dfc42262f95cc8','check.py':'0796595f56e235ec3a49b45a228906806acddccd9af8306daecbf56d7f8d3bc3'}
for name,pin in pins.items(): assert digest(source/name)==pin
manifest = read(source/'MANIFEST.json')
assert len(manifest)==21
for name,pin in manifest.items(): assert digest(source/name)==pin
assert {str(p.relative_to(source)) for p in source.rglob('*') if p.is_file()}==set(manifest)|{'MANIFEST.json','FREEZE.json'}
result = read(ROOT/'receipts/RESULT.json')
names = read(source/'THEOREMS.json')
assert len(names)==17 and result['theorems']==names
assert result['authenticated_inputs']==21 and result['source_bindings']==12
assert result['artifact_patch_apply_reverse']=='PASS' and result['native_compilation']=='NOT_RUN'
import re
rows = re.findall(r"^'([^']+)' (?:depends on axioms: \[([^]]*)\]|does not depend on any axioms)$", (ROOT/'receipts/AXIOMS.txt').read_text(), re.M)
assert [name for name,_ in rows]==names
assert set(x.strip() for _,group in rows for x in group.split(',') if x.strip()) == {'propext','Quot.sound'}
mutants=read(source/'MUTANTS.json')
assert result['semantic_mutants_rejected']==[m['name'] for m in mutants]
commands=read(ROOT/'receipts/COMMANDS.json')
assert len(commands)==20
assert [i for i,r in enumerate(commands) if r['exit']!=0]==[5,9,13,17]
for i,m in enumerate(mutants):
    block=commands[2+4*i:6+4*i]
    assert [r['exit'] for r in block]==[0,0,0,1]
    assert all(Path(r['cwd']).name==m['name'] for r in block)
    assert 'decide' in block[-1]['stdout'] and 'is false' in block[-1]['stdout']
    assert not any(word in block[-1]['stdout'].lower() for word in ['unknown identifier','unexpected token','failed to synthesize'])
    assert m['new'] in (ROOT/'receipts/mutants'/m['name']/'Mutant.lean').read_text()
    assert m['goal'] in (ROOT/'receipts/mutants'/m['name']/'Witness.lean').read_text()
assert all(c['exit']==0 for c in commands[-2:])
guards=read(ROOT/'GUARDS.json')
assert [g['name'] for g in guards]==['changed-lean','extra-file','symlink-source','duplicate-manifest']
assert all(g['exit']!=0 and 'AssertionError' in g['stderr'] and g['output_not_created'] for g in guards)
assert sum(r['logical_bytes'] for r in read(ROOT/'CLEANUP.json'))==2937734
assert authenticate()==count
print(json.dumps({'status':'PASS','verdict':'ACCEPT_CONDITIONAL_SELECTED_BRANCH_COMPONENT','inputs':count,'source_inputs':21,'audits':17,'source_bindings':12,'semantic_mutants':4,'fresh_integrity_challenges':4,'generated_bytes_removed':2937734}))
