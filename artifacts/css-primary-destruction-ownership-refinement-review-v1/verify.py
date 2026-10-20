import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise SystemExit("Require python3 -I -S without optimization")
sys.dont_write_bytecode = True
import hashlib
import json
from pathlib import Path
import stat

ROOT = Path(__file__).resolve().parent

def pairs(items):
    out = {}
    for key, value in items:
        assert key not in out
        out[key] = value
    return out

def read(path):
    return json.loads(path.read_text(), object_pairs_hook=pairs)

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

if len(sys.argv) != 3 or sys.argv[1] != "--files-sha256":
    raise SystemExit("Usage: python3 -I -S verify.py --files-sha256 REVIEW_PIN")
assert sha(ROOT / "FILES.json") == sys.argv[2]
manifest = read(ROOT / "FILES.json")
directories = {"."}
for name, expected in manifest.items():
    path = Path(name)
    assert not path.is_absolute() and path.as_posix() == name and ".." not in path.parts
    assert stat.S_ISREG((ROOT / path).lstat().st_mode) and sha(ROOT / path) == expected, name
    directories.update(str(p) for p in path.parents)
actual = set()
for path in ROOT.rglob("*"):
    name = path.relative_to(ROOT).as_posix()
    mode = path.lstat().st_mode
    if stat.S_ISREG(mode):
        actual.add(name)
    else:
        assert stat.S_ISDIR(mode) and name in directories
assert actual == set(manifest) | {"FILES.json", "FREEZE.json"}
freeze = read(ROOT / "FREEZE.json")
assert freeze["files_sha256"] == sys.argv[2] and freeze["payload_count"] == len(manifest)
assert sha(ROOT/'source/FILES.json')=='c9d46c3317fb6756068607237405939930da2f23d2096acec6b5091a30aaace9'
assert sha(ROOT/'source/FREEZE.json')=='9ee21358cabfa3f7ec9a6a58b41ab917ef57a21c91f262874138997246448e96'
for name,expected in read(ROOT/'source/FILES.json').items():
    assert sha(ROOT/'source'/name)==expected
result=read(ROOT/'replay/RESULT.json')
assert result['result']=='PASS' and result['audits']==74 and result['modules']==8
assert result['semantic_falseclaim_controls']==5 and result['source_bindings']==21 and result['storage_declarations']==10
import re
names=[x['name'] for x in read(ROOT/'source/AUDIT-NAMES.json')]
audit=(ROOT/'replay/Audit.stdout').read_text()
assert re.findall(r"'([^']+)' (?:depends on axioms|does not depend on any axioms)",audit)==names
for group in re.findall(r'depends on axioms:\s*\[([^]]*)\]',audit):
    assert set(re.findall(r'[A-Za-z][A-Za-z0-9_.]*',group)) <= {'propext','Quot.sound','Classical.choice'}
for name in read(ROOT/'source/FALSECLAIMS.json'):
    text=(ROOT/'replay'/(name+'.stdout')).read_text()
    assert 'decide' in text and 'false' in text
ch=read(ROOT/'CHALLENGES-RESULT.json')
assert ch['exit']==0 and not ch['stderr']
expected=['capacity_is_an_external_choice','same_heap_fails_under_zero_capacity','full_world_allows_dangling_raw_reference','world_does_not_establish_primary_coherence','foreign_descriptor_is_outside_the_world','different_roles_already_exclude_alias','freed_then_reused_address_has_no_generation_tag']
assert re.findall(r"'OwnershipReview.([^']+)' depends on axioms:",ch['stdout'])==expected
for group in re.findall(r'depends on axioms:\s*\[([^]]*)\]',ch['stdout']):
    assert set(re.findall(r'[A-Za-z][A-Za-z0-9_.]*',group)) <= {'propext','Quot.sound'}
assert ch['stdout']==(ROOT/'CHALLENGES.log').read_text()
assert sha(ROOT/'producer-receipts/FILES.json')=='00ca4ec6f852e9ffe0b1bda3030c760cabe83659fb48bba1f81a8ed983938e2f'
r=read(ROOT/'producer-receipts/RESULT.json')
assert r['canonical']==r['relocated']==result and r['pre_output_guard_rejections']==11
assert read(ROOT/'CLEANUP.json')['all_compiler_sessions_terminal']
assert read(ROOT/'VERDICT.json')['status']=='ACCEPT_SCOPED_OWNERSHIP_REFINEMENT'
print(json.dumps({'review_inputs':len(manifest),'producer_audits':74,'independent_challenges':7,'verdict':'ACCEPT_SCOPED_OWNERSHIP_REFINEMENT','full_native_closure':False}))
