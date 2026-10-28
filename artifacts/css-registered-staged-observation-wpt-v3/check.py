import ast
import importlib.util
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
def load(name):
    spec=importlib.util.spec_from_file_location(name,HERE/(name+'.py'));module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
helper=load('run');old=ROOT/'artifacts/css-registered-staged-observation-wpt-v2'
for name in ['run.py','bindings.py','SOURCE-SUCCESSION.json']:
    assert (HERE/name).read_bytes()==(old/name).read_bytes(),name
policy=helper.read(HERE/'POLICY.json');prior=helper.read(old/'POLICY.json')
allowed={'execution_enabled','tests','target_subtests','live_oracle_sources','cardinality_description'}
assert {k:v for k,v in policy.items() if k not in allowed}=={k:v for k,v in prior.items() if k not in allowed}
oldpins=helper.read(old/'SOURCE-PINS.json');pins=helper.read(HERE/'SOURCE-PINS.json')
for name,item in pins.items():
    if name in oldpins:assert item==oldpins[name]
    if item['exists']:assert helper.sha(HERE/item['capture'])==helper.sha(ROOT/item['origin'])==item['sha256']
for name,pin in helper.read(HERE/'REFERENCES.json').items():assert helper.sha(ROOT/name)==pin,name
for path in HERE.glob('*.py'):ast.parse(path.read_text())
epoch=helper.read(ROOT/'artifacts/css-registered-number-native-runtime-v1/CURRENT-EPOCH.json')
phase=load('bindings').validate_phase(ROOT,HERE,policy,epoch,helper)
(HERE/'CHECK.json').write_text(json.dumps({'phase_binding':phase,'same_lifecycle_and_build_bindings':True,'fixture_only_policy_delta':True,'shared_resource_pins_unchanged':True,'fixture_hashes_verified':True,'python_syntax':True,'browser_executed':False,'live_source_index_epoch_mutated':False},indent=2,sort_keys=True)+'\n')
print(json.dumps({'phase_binding':True,'same_lifecycle':True,'fixture_only_delta':True}))
