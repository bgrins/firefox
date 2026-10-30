from pathlib import Path
import difflib
import hashlib
import json
import shutil
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
V5 = ROOT/'artifacts/css-registered-selected-color-dependency-proposal-v5'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
FORMAT = Path('/Users/bgrins/.rustup/toolchains/1.97.1-aarch64-apple-darwin/bin/rustfmt')
assert sha(FORMAT) == 'ab19d01d0a7a3a901c62b6b013a98452d38084b5d7f446ccb20c5e83c10db99f'
for path,pin in json.loads((HERE/'REFERENCES.json').read_text()).items():
    assert sha(ROOT/path)==pin['sha256']
    assert (ROOT/path).stat().st_size==pin['bytes']
for name,pin in json.loads((V5/'FILES.json').read_text()).items():
    assert sha(V5/name)==pin['sha256']
roles=json.loads((HERE/'SOURCE-ROLES.json').read_text())
patch=[];delta=[]
for name,row in roles.items():
    base,candidate,previous=HERE/'base'/name,HERE/'candidate'/name,V5/'candidate'/name
    assert sha(base)==sha(ROOT/row['source'])==row['base_sha256']
    assert sha(candidate)==row['candidate_sha256'] and sha(previous)==row['v5_candidate_sha256']
    if not name.endswith('cascade.rs'): assert candidate.read_bytes()==previous.read_bytes()
    formatted=subprocess.run([str(FORMAT),'--check','--config-path',str(HERE/'rustfmt.toml'),str(candidate)],capture_output=True,text=True)
    assert formatted.returncode==0 and not formatted.stderr,(formatted.stdout,formatted.stderr)
    patch.extend(difflib.unified_diff(base.read_text().splitlines(True),candidate.read_text().splitlines(True),fromfile='a/'+name,tofile='b/'+name))
    delta.extend(difflib.unified_diff(previous.read_text().splitlines(True),candidate.read_text().splitlines(True),fromfile='a/'+name,tofile='b/'+name))
assert ''.join(patch)==(HERE/'native.patch').read_text()
assert ''.join(delta)==(HERE/'V5-DELTA.patch').read_text()
name='servo/components/style/properties/cascade.rs'
base=(HERE/'base'/name).read_text();candidate=(HERE/'candidate'/name).read_text()
def admission(source):
    start=source.index('fn find_non_custom_references(')
    return source[start:source.index('/// Resolves the custom properties',start)]
extra='    if registration_needs_image_dependencies(registration) {\n        result |= ReferenceFlags::COLOR_SCHEME;\n    }\n'
assert admission(candidate).count(extra)==1
assert admission(candidate).replace(extra,'')==admission(base)
assert candidate.count('refine_image_dependencies = registration_needs_image_dependencies(registration);')==1
assert candidate.index('refine_image_dependencies = registration_needs_image_dependencies(registration);') < candidate.index('let mut prepared_custom = None;')
assert 'if let VarType::Custom(ref name) = var\n                && refine_image_dependencies\n            {\n                let may_compute_color =' in candidate
assert 'if registered\n                && refine_image_dependencies\n                && cyclic' in candidate
with tempfile.TemporaryDirectory(prefix='css-image-only-patch-') as temporary:
    scratch=Path(temporary);shutil.copytree(HERE/'base',scratch/'tree')
    for reverse in [False,True]:
        args=['patch']+(['-R'] if reverse else [])+['-p1','-i',str(HERE/'native.patch')]
        result=subprocess.run(args,cwd=scratch/'tree',capture_output=True,text=True)
        assert result.returncode==0,(result.stdout,result.stderr)
        for name in roles:assert (scratch/'tree'/name).read_bytes()==(HERE/('base' if reverse else 'candidate')/name).read_bytes()
assert not scratch.exists()
receipt={'source_pairs':3,'changed_from_v5':1,'provider_and_classifier_exact_v5':True,'base_admission_preserved_except_image_gate':True,'whole_preparation_and_late_default_gated':True,'patch_forward_reverse':True,'rustfmt_files':3,'formatter_sha256':sha(FORMAT),'scratch':str(scratch),'scratch_removed':True,'native_compile':False,'browser_executed':False,'classifier_tests_rerun':False}
(HERE/'STATIC-CHECK.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
print(json.dumps(receipt))
