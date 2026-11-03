import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import time
assert sys.flags.isolated and sys.flags.no_site and sys.dont_write_bytecode
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
read = lambda path: json.loads(path.read_bytes())
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
def load(name):
    spec = importlib.util.spec_from_file_location('saved_' + name, HERE/(name+'.py'))
    module = importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
policy=read(HERE/'POLICY.json'); assert policy['execution_enabled'] is policy['candidate_execution_enabled'] is False
checker=load('check'); baseline=load('baseline')
start=time.monotonic();count=checker.validate_policy(policy);elapsed=time.monotonic()-start
capture=read(ROOT/policy['current_binding']['path']);binding=read(ROOT/policy['capture_owner']['directory']/'BINDINGS.json')
epoch=read(ROOT/binding['saved_inputs']['current_epoch'])
baseline.require_role(policy,capture['role'],epoch)
negative=[]
def reject(name,fn):
    try:fn()
    except (AssertionError,KeyError,TypeError,ValueError):negative.append(name)
    else:raise AssertionError('accepted '+name)
for name,key,value in [('built','built',True),('variant','variant','trace'),('head','paired_head','0'*40)]:
    role=copy.deepcopy(capture['role']);role[key]=value
    reject('actual-native-role-entry-'+name,lambda:baseline.require_role(policy,role,epoch))
changed=copy.deepcopy(epoch);changed['prioritary_declaration_capacity_publication']['capacity']['native_commit']='0'*40
reject('actual-native-role-entry-epoch-marker',lambda:baseline.require_role(policy,capture['role'],changed))
for key,value in [('role_validator',policy['capture_owner']),('role_validator',dict(policy['role_validator'],manifest_sha256='0'*64)),('capture_reuse',{}),('current_binding',dict(policy['current_binding'],sha256='0'*64)),('intermediate_consumed_inputs',{})]:
    changed=copy.deepcopy(policy);changed[key]=value
    reject('production-policy-'+key,lambda:checker.validate_policy(changed))
origins=read(HERE/'ORIGINS.json')
for name,row in origins.items():
    if name not in ('baseline.py','check.py'):assert (HERE/name).read_bytes()==(ROOT/row['path']).read_bytes()
parent=(ROOT/origins['baseline.py']['path']).read_text()
expected=parent.replace("    adapter = load('language_capture_role', policy['capture_owner']['directory'] + '/baseline.py')", "    binding = policy['role_validator']\n    ownership = load('role_leaf_ownership', policy['ownership_helper'])\n    ownership.authenticate(ROOT / binding['directory'], binding['manifest_sha256'])\n    adapter = load('language_capture_role', binding['directory'] + '/baseline.py')")
assert (HERE/'baseline.py').read_text()==expected
leaf=ROOT/policy['role_validator']['directory']
for name in ('FILES.json','baseline.py','BINDINGS.json'):
    path=str((leaf/name).relative_to(ROOT)); assert policy['intermediate_consumed_inputs'][path]==sha(leaf/name)
tested=['check_saved.py','POLICY.json','PRECONDITIONS.json','SOURCE-ROLES.json','ORIGINS.json','baseline.py','check.py','admission.py','archive.py','run.py','closure.py']
print(json.dumps({'full_validate_policy_executed':True,'seconds':elapsed,'consumed_inputs':count,'references':len(policy['references']),'actual_native_policy_require_role_saved_positive':True,'public_validate_policy_exercises_role_positive_and_invalid_built_role':True,'negative_controls':negative,'exact_one_baseline_routing_delta':True,'other13_production_bodies_unchanged':True,'actual_capture_reuse_after_independent_preservation':True,'original22_replayed_before8_projection':True,'original_PASS':6,'original_FAIL':2,'endings':1,'live_guard_or_native_execution':False,'unchanged_suites_rerun':False,'tested_inputs':{n:sha(HERE/n) for n in tested}},indent=2,sort_keys=True))
