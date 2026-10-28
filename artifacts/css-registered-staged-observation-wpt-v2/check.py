import ast
import copy
import importlib.util
import json
import os
from pathlib import Path
from types import SimpleNamespace

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
def load(name):
    spec=importlib.util.spec_from_file_location(name,HERE/(name+'.py'))
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
helper=load('run');bindings=load('bindings')
policy=helper.read(HERE/'POLICY.json')
epoch=helper.read(ROOT/'artifacts/css-registered-number-native-runtime-v1/CURRENT-EPOCH.json')
phase=bindings.validate_phase(ROOT,HERE,policy,epoch,helper)
rejected=[]
def reject(name,alter_epoch=None,override_path=None,alter_read=None):
    value=copy.deepcopy(epoch)
    if alter_epoch:alter_epoch(value)
    proxy=SimpleNamespace(read=helper.read,sha=helper.sha,need=helper.need)
    if override_path:
        modified=copy.deepcopy(helper.read(override_path));alter_read(modified)
        proxy.read=lambda path:modified if path==override_path else helper.read(path)
    try:bindings.validate_phase(ROOT,HERE,policy,value,proxy)
    except RuntimeError:rejected.append(name)
    else:raise AssertionError(name)
for name,mutate in [
 ('uncompiled',lambda e:e['registered_number_transition'].update(compiled=False)),
 ('accepted',lambda e:e['registered_number_transition'].update(accepted=True)),
 ('wrong variant',lambda e:e['registered_number_transition'].update(variant='other')),
 ('missing native edit',lambda e:e['modified_native_paths'].pop()),
 ('binary drift',lambda e:e['pins'].update({policy['normal_binaries'][0]:'other'})),
 ('source drift',lambda e:e['pins'].update({next(iter(policy['source_roles']['candidate'])):'other'})),
 ('identity drift',lambda e:e['installed_identities'].update({next(iter(e['installed_identities'])):[0,0]})),
 ('nested drift',lambda e:e['nested_semantic_index'].update(head='other')),
]:reject(name,alter_epoch=mutate)
reject('historical build HEAD rewritten',override_path=ROOT/policy['build_epoch'],alter_read=lambda e:e['semantic_index'].update(head=policy['frozen_head']))
reject('historical source drift',override_path=ROOT/policy['build_epoch'],alter_read=lambda e:e['pins'].update({next(iter(policy['source_roles']['candidate'])):'other'}))
reject('failed historical build',override_path=ROOT/policy['build_result'],alter_read=lambda e:e.update(command_success=False))
reject('wrong signed successor parent',override_path=HERE/'SOURCE-SUCCESSION.json',alter_read=lambda e:e['commits'][0].update(parent='other'))
base=ROOT/'artifacts/css-registered-staged-observation-wpt-v1'
for name in ['SOURCE-PINS.json','SELECTED.json','TARGET-SUBTESTS.json','SUBSET-MANIFEST.json']:
    assert (HERE/name).read_bytes()==(base/name).read_bytes(),name
for item in helper.read(HERE/'SOURCE-PINS.json').values():
    if item['exists']:
        assert helper.sha(HERE/item['capture'])==helper.sha(base/item['capture'])==item['sha256']
for path,pin in helper.read(HERE/'REFERENCES.json').items():assert helper.sha(ROOT/path)==pin,path
for path in HERE.glob('*.py'):ast.parse(path.read_text())
h=helper.load('preservation',ROOT/policy['helpers']['preservation'])
guard=helper.load('ordinary_guard',ROOT/policy['helpers']['epoch'])
preserved=guard.verify_current(h,ROOT,dict(os.environ,GIT_OPTIONAL_LOCKS='0'),epoch)
(HERE/'CHECK.json').write_text(json.dumps({'phase_binding':phase,'negative_binding_controls':rejected,'identical_fixture_and_manifest_inputs':True,'ordinary_preservation_verified':True,'preserved':preserved,'browser_executed':False,'native_or_index_or_epoch_mutated':False},indent=2,sort_keys=True)+'\n')
print(json.dumps({'signed_successors':len(phase['artifact_only_successors']),'negative_binding_controls':len(rejected),'ordinary_preservation_verified':True,'identical_inputs':True}))
