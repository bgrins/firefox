from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import difflib

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PREVIOUS = ROOT/'artifacts/css-registered-selected-color-dependency-proposal-v5'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(PREVIOUS/'FILES.json') == 'ddda32a04cd233fa9f8eaccfd225d1c34c5dfda698e9d27083405290c792f1b4'
for name,record in json.loads((PREVIOUS/'FILES.json').read_text()).items():
    assert sha(PREVIOUS/name) == record['sha256']
    assert (PREVIOUS/name).stat().st_size == record['bytes']
roles = json.loads((PREVIOUS/'SOURCE-ROLES.json').read_text())
for name,record in roles.items():
    assert sha(PREVIOUS/'base'/name) == sha(ROOT/record['source']) == record['base_sha256']
    for kind in ('base','candidate'):
        destination = HERE/kind/name
        destination.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(PREVIOUS/kind/name,destination)
shutil.copyfile(PREVIOUS/'rustfmt.toml',HERE/'rustfmt.toml')
name = 'servo/components/style/properties/cascade.rs'
p = HERE/'candidate'/name
source = p.read_text()
base = (HERE/'base'/name).read_text()
start = '/// Only registered (typed) properties emit a non-custom edge, from their own value.'
end = '/// Resolves the custom properties for a single `@keyframes` keyframe'
old_function = base[base.index(start):base.index(end)]
new_function = old_function.replace('    result\n}', '    if registration_needs_image_dependencies(registration) {\n        result |= ReferenceFlags::COLOR_SCHEME;\n    }\n    result\n}')
assert new_function != old_function
predicate = '''fn registration_needs_image_dependencies(registration: &PropertyDescriptors) -> bool {
    use crate::properties_and_values::syntax::{ComponentName, data_type::{DataType, DependentDataTypes}};
    let Some(syntax) = registration.syntax.as_ref() else {
        return false;
    };
    !syntax.dependent_types().intersects(DependentDataTypes::COLOR)
        && syntax.components.iter().any(|component| {
            matches!(component.name(), ComponentName::DataType(DataType::Image))
        })
}

'''
source = source[:source.index(start)] + predicate + new_function + source[source.index(end):]
assert source.count('        let mut registered = false;') == 1
source = source.replace('        let mut registered = false;', '        let mut registered = false;\n        let mut refine_image_dependencies = false;')
assert source.count('                registered = !registration.is_universal();') == 1
source = source.replace('                registered = !registration.is_universal();', '                registered = !registration.is_universal();\n                refine_image_dependencies = registration_needs_image_dependencies(registration);')
anchor = '            if let VarType::Custom(ref name) = var {\n                let may_compute_color ='
assert source.count(anchor) == 1
source = source.replace(anchor,'            if let VarType::Custom(ref name) = var\n                && refine_image_dependencies\n            {\n                let may_compute_color =')
anchor = '            if registered\n                && cyclic'
assert source.count(anchor) == 1
source = source.replace(anchor,'            if registered\n                && refine_image_dependencies\n                && cyclic')
p.write_text(source)
rustfmt = Path('/Users/bgrins/.rustup/toolchains/1.97.1-aarch64-apple-darwin/bin/rustfmt')
assert sha(rustfmt) == 'ab19d01d0a7a3a901c62b6b013a98452d38084b5d7f446ccb20c5e83c10db99f'
subprocess.run([str(rustfmt),'--config-path',str(HERE/'rustfmt.toml'),str(p)],check=True)
patch=[]; delta=[]
for name,record in roles.items():
    before=(HERE/'base'/name).read_text();after=(HERE/'candidate'/name).read_text()
    patch.extend(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile='a/'+name,tofile='b/'+name))
    delta.extend(difflib.unified_diff((PREVIOUS/'candidate'/name).read_text().splitlines(True),after.splitlines(True),fromfile='a/'+name,tofile='b/'+name))
    record['v5_candidate_sha256']=record.pop('candidate_sha256')
    record.pop('v4_candidate_sha256')
    record['candidate_sha256']=sha(HERE/'candidate'/name)
(HERE/'native.patch').write_text(''.join(patch))
(HERE/'V5-DELTA.patch').write_text(''.join(delta))
(HERE/'SOURCE-ROLES.json').write_text(json.dumps(roles,indent=2,sort_keys=True)+'\n')
print(json.dumps({'postimages':3,'changed_vs_v5':['cascade.rs'],'native_source_edited':False}))
