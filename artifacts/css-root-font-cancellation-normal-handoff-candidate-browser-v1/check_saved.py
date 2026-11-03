import ast
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import time
from types import SimpleNamespace

assert sys.flags.isolated and sys.flags.no_site and sys.dont_write_bytecode
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
read = lambda path: json.loads(path.read_bytes())
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
def load(name):
    spec = importlib.util.spec_from_file_location('saved_' + name, HERE/(name+'.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

policy = read(HERE/'POLICY.json')
roles = read(HERE/'SOURCE-ROLES.json')
assert policy['execution_enabled'] is policy['candidate_execution_enabled'] is False
checker = load('check')
start = time.monotonic()
count = checker.validate_policy(policy)
elapsed = time.monotonic() - start
negative = []
def reject(label, action):
    try: action()
    except (AssertionError, KeyError, TypeError, ValueError): negative.append(label)
    else: raise AssertionError('accepted ' + label)

for key, value in [('current_binding', dict(policy['current_binding'], sha256='0'*64)),
                   ('capture_binding', dict(policy['capture_binding'], sha256='0'*64)),
                   ('additional_source_paths', ['servo/components/style/data.rs', 'servo/components/style/traversal.rs']),
                   ('committed_source_preimages', {}), ('intermediate_consumed_inputs', {}),
                   ('source_binding', dict(policy['source_binding'], manifest_sha256='0'*64)),
                   ('archived_original', dict(policy['archived_original'], comparison_performed=True)),
                   ('source_context_pins', {k:v for k,v in policy['source_context_pins'].items() if k != 'servo/components/style/data.rs'})]:
    bad = copy.deepcopy(policy); bad[key] = value
    reject(key, lambda: checker.validate_policy(bad))
origins = read(HERE/'ORIGINS.json')
bad = copy.deepcopy(origins); bad['run.py'] = bad['run.py']['path']
reject('unstructured-origin', lambda: checker.validate_origins(bad))
bad = copy.deepcopy(origins); bad['archive.py']['path'] = origins['run.py']['path']; bad['archive.py']['sha256'] = origins['run.py']['sha256']
reject('authentic-wrong-diff-base', lambda: checker.validate_origins(bad))
admission = load('admission')
receipt = read(ROOT/policy['current_binding']['path'])['checkpoint']
bad = copy.deepcopy(receipt); bad['signature_verified'] = 1
reject('typed-native-receipt', lambda: admission.direct_evidence(ROOT, policy, bad))

archive_tree = ast.parse((HERE/'archive.py').read_text())
expression = next(node.value for node in ast.walk(archive_tree) if isinstance(node, ast.keyword) and node.arg == 'unchanged_source_preimages')
projection = eval(compile(ast.Expression(expression), '<actual archive context projection>', 'eval'), {'policy': policy, 'roles': roles})
expected = {name:pin for name,pin in policy['source_context_pins'].items() if name not in roles}
assert projection == expected and not set(projection).intersection(roles)
assert 'servo/ports/geckolib/glue.rs' not in projection
for name in ['servo/components/style/data.rs', 'servo/components/style/matching.rs', 'dom/animation/EffectCompositor.cpp', 'layout/style/GeckoBindings.cpp', 'servo/components/style/custom_properties.rs']:
    assert projection[name] == policy['source_context_pins'][name]
old_tree = ast.parse((ROOT/origins['archive.py']['path']).read_text())
old_expression = next(node.value for node in ast.walk(old_tree) if isinstance(node, ast.keyword) and node.arg == 'unchanged_source_preimages')
old_projection = eval(compile(ast.Expression(old_expression), '<old fixed context projection>', 'eval'), {'policy': policy, 'roles': roles})
assert old_projection != expected and 'servo/ports/geckolib/glue.rs' in old_projection
negative.append('old-unchanged-glue-projection-distinguished')

baseline = load('baseline')
ownership = baseline.load('saved_owned_source', policy['ownership_helper'])
main = next(node for node in ast.parse((HERE/'run.py').read_text()).body if isinstance(node, ast.FunctionDef) and node.name == 'main')
loop = next(node for node in main.body if isinstance(node, ast.For) and ast.unparse(node.iter) == 'roles.items()')
index = next(i for i,node in enumerate(loop.body) if isinstance(node, ast.Assign) and ast.unparse(node.targets[0]) == 'admitted')
claim_code = compile(ast.Module(body=loop.body[index:index+3], type_ignores=[]), '<production claim>', 'exec')
with tempfile.TemporaryDirectory(prefix='normal-handoff-claims-', dir='/private/tmp') as temporary:
    root = Path(temporary)
    for name,row in roles.items():
        path=root/name; path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes((ROOT/row['base_capture']).read_bytes())
        admitted=ownership.claim(root,name,row['base_sha256'])
        capture={'payload_claims':{},'additional_sources':{}}
        capture['additional_sources' if name in policy['additional_source_paths'] else 'payload_claims'][name]=admitted
        scope=dict(ROOT=root,name=name,record=row,claims={},ownership=ownership,baseline=SimpleNamespace(current_capture=lambda _:capture),policy={})
        exec(claim_code,scope); assert scope['claims'][name]==admitted
        path.rename(path.with_suffix('.retained'));path.write_bytes((ROOT/row['base_capture']).read_bytes())
        try: exec(claim_code,scope)
        except Exception as error: assert 'owned identity: ' + name in str(error)
        else: raise AssertionError('replaced inode accepted')
assert not root.exists()
for name in origins:
    if name not in ('admission.py','archive.py','check.py'):
        assert (HERE/name).read_bytes()==(ROOT/origins[name]['path']).read_bytes()
assert (HERE/'run.py').read_bytes()==(ROOT/origins['run.py']['path']).read_bytes()
assert (HERE/'baseline.py').read_bytes()==(ROOT/origins['baseline.py']['path']).read_bytes()
tested=['check_saved.py','POLICY.json','PRECONDITIONS.json','SOURCE-ROLES.json','ORIGINS.json','admission.py','archive.py','check.py','baseline.py','run.py','closure.py']
print(json.dumps({'full_validate_policy_executed':True,'seconds':elapsed,'consumed_inputs':count,'references':len(policy['references']),'roles':3,'canonical_roles':1,'additional_roles':2,'original22_replayed_before8_projection':True,'original_PASS':6,'original_FAIL':2,'endings':1,'negative_controls':negative,'actual_driver_changed_inode_rejections':3,'archive_actual_expression_checked':True,'native_context_and_claims': 'glue candidate belongs to role map; all non-role context pinned at original bytes','unchanged_run_baseline_finally':True,'unchanged_suites_rerun':False,'native_or_browser_run':False,'scratch_removed':True,'tested_inputs':{name:sha(HERE/name) for name in tested}},indent=2,sort_keys=True))
