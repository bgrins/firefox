import ast
import copy
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
read = lambda path: json.loads(path.read_text())
policy = read(HERE / 'POLICY.json')
epoch = read(HERE / 'INITIAL-EPOCH.json')
role = read(HERE / 'INITIAL-ROLE.json')
source = ast.parse((HERE / 'install.py').read_text())
function = next(node for node in source.body if isinstance(node, ast.FunctionDef) and node.name == 'check_evidence')
namespace = {'ROOT':ROOT, 'read':read, 'sha':lambda path:hashlib.sha256(path.read_bytes()).hexdigest(), 'os':SimpleNamespace(getpid=lambda:1),
             'subprocess':SimpleNamespace(run=lambda *a,**k:SimpleNamespace(stdout='FAKE CENSUS')),
             'load':lambda *a:SimpleNamespace(process_census_clear=lambda text,pid:None)}
exec(compile(ast.Module(body=[function], type_ignores=[]), str(HERE / 'install.py'), 'exec'), namespace)
helper = SimpleNamespace(group_absent=lambda *a:None, quiescent=lambda *a:None)
namespace['check_evidence'](helper, role, policy, epoch)
rejected = []
def reject(name, mutate, change_policy=None):
    def altered(path):
        value = read(path)
        mutate(path, value)
        return value
    namespace['read'] = altered
    changed = copy.deepcopy(policy)
    if change_policy:
        change_policy(changed)
    try:
        namespace['check_evidence'](helper, role, changed, epoch)
    except (AssertionError, KeyError):
        rejected.append(name)
    else:
        raise AssertionError('corruption accepted: '+name)
first = ROOT / policy['required_runs'][0]
second = ROOT / policy['required_runs'][1]
def field(path, name, value):
    return lambda p,d:d.__setitem__(name,value) if p==path else None
reject('incomplete second', field(second/'ASSESSMENT.json','complete',False))
reject('unpreserved second', field(second/'ASSESSMENT.json','execution_preserved',False))
reject('infrastructure error', field(second/'RESULT.json','execution_error','injected'))
reject('missing cleanup', field(second/'CLEANUP.json','owned_group_absent',False))
reject('wrong epoch', field(second/'ASSESSMENT.json','epoch_sha256','0'*64))
reject('wrong source', field(second/'ASSESSMENT.json','native_sources',{'unknown':'0'*64}))
reject('container failure', lambda p,d:d['rows'][0].__setitem__('status','FAIL') if p==first/'ASSESSMENT.json' else None)
reject('duplicate container identity', lambda p,d:d['rows'][0].__setitem__('subtest',d['rows'][1]['subtest']) if p==first/'ASSESSMENT.json' else None)
reject('duplicate run', lambda p,d:None, lambda p:p.__setitem__('required_runs',[p['required_runs'][0]]*2))
reject('pending reduction', lambda p,d:None, lambda p:p.__setitem__('minimal_lh_observation_pending',True))
print(json.dumps({'complete':True,'actual_saved_semantic_positive':True,'negative_count':len(rejected),
                  'rejected':rejected,'process_and_group_calls_mocked':True,
                  'live_query_or_install_executed':False},indent=2))
