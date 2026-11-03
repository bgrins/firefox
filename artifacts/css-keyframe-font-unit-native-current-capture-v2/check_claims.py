import ast
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import sys
import tempfile
from types import SimpleNamespace

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PARENT = ROOT / 'artifacts/css-keyframe-font-unit-native-current-capture-v1'
CANDIDATE = ROOT / 'artifacts/css-keyframe-font-unit-candidate-browser-v2'
read = lambda p: json.loads(p.read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
spec = importlib.util.spec_from_file_location('capture_claims', HERE/'baseline.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
prior = read(PARENT/'BINDINGS.json')
assert {k:v for k,v in prior.items() if k != 'references'} == {k:v for k,v in module.binding.items() if k != 'references'}
assert read(PARENT/'CHECK.json')['exit'] == 0
assert read(PARENT/'CHECK.json')['result']['negative_checks'] == 11
assert (HERE/'capture_current.py').read_bytes() == (PARENT/'capture_current.py').read_bytes()
assert (HERE/'check.py').read_bytes() == (PARENT/'check.py').read_bytes()
old_line = "        assert name not in epoch['pins'] and name not in epoch['installed_identities']"
new_lines = "        assert name not in epoch['installed_identities']\n        assert name not in epoch['pins'] or epoch['pins'][name] == record['base_sha256']"
assert (HERE/'baseline.py').read_text() == (PARENT/'baseline.py').read_text().replace(old_line,new_lines)
native_parent = ROOT/'artifacts/css-keyframe-font-unit-candidate-browser-v1/baseline.py'
assert (CANDIDATE/'baseline.py').read_text() == native_parent.read_text().replace('    '+old_line,'    '+new_lines.replace('\n','\n    '))
source = (CANDIDATE/'baseline.py').read_text()
observe = next(node for node in ast.parse(source).body if isinstance(node,ast.FunctionDef) and node.name=='observe')
loop = next(node for node in observe.body if isinstance(node,ast.For) and ast.unparse(node.target)=='(name, record)' and ast.unparse(node.iter)=='roles.items()')
loop_source = ast.get_source_segment(source,loop)
code = compile(loop_source, str(CANDIDATE/'baseline.py')+'::observe-source-loop','exec')
roles = read(CANDIDATE/'SOURCE-ROLES.json')
assert set(roles) == set(module.binding['additional_sources'])
bodies = {name:(ROOT/row['base_capture']).read_bytes() for name,row in roles.items()}
claims = {name:{'path':name,'owned_sha256':row['base_sha256'],'identity':[101,index+1]} for index,(name,row) in enumerate(roles.items())}
head = module.binding['capacity_commit']
checks = []

def exercise(kind, mode, target):
    epoch = {'pins':{name:row['base_sha256'] for name,row in roles.items()},'installed_identities':{}}
    additional = copy.deepcopy(claims)
    calls = []
    if mode == 'absent-pin': epoch['pins'] = {}
    if mode == 'wrong-pin': epoch['pins'][target] = '0'*64
    if mode == 'existing-identity': epoch['installed_identities'][target] = [101,1]
    if mode == 'wrong-claim': additional[target]['owned_sha256'] = '0'*64
    def git(root,env,operation,object_name):
        assert root == ROOT and env == {} and operation == 'show'
        revision,name = object_name.split(':',1)
        assert revision == head and name in roles
        return b'wrong HEAD' if mode=='wrong-head' and name==target else bodies[name]
    def claim(root,name,pin,*identity):
        assert root == ROOT and pin == roles[name]['base_sha256']
        if mode=='changed-inode' and name==target: raise AssertionError('inode changed')
        if kind=='native': assert identity == (claims[name]['identity'],)
        else: assert identity == ()
        calls.append(name)
        return copy.deepcopy(claims[name])
    state = SimpleNamespace(h=SimpleNamespace(git=git))
    ownership = SimpleNamespace(claim=claim)
    before = copy.deepcopy(epoch)
    try:
        if kind=='capture':
            result = module.claim_additional_sources(ownership,state,{},epoch,head)
        else:
            namespace = dict(ROOT=ROOT,epoch=epoch,roles=roles,additional=additional,sources={},ownership=ownership,state=state,env={},checkpoint={'head':head},hashlib=hashlib)
            exec(code,namespace)
            result = namespace['sources']
    except AssertionError:
        assert mode not in ('pinned','absent-pin')
        if mode in ('wrong-pin','existing-identity'): assert target not in calls
        result = None
    else:
        assert mode in ('pinned','absent-pin')
        assert result == claims and calls == list(roles)
    assert epoch == before
    checks.append({'route':kind,'mode':mode,'target':target,'accepted':result is not None})

for kind in ('capture','native'):
    for mode in ('pinned','absent-pin'):
        exercise(kind,mode,next(iter(roles)))
    for name in roles:
        for mode in ('wrong-pin','existing-identity','wrong-head','changed-inode'):
            exercise(kind,mode,name)
        if kind=='native': exercise(kind,'wrong-claim',name)
owner_path = ROOT/'artifacts/css-registered-number-source-transition-v4/transition.py'
spec = importlib.util.spec_from_file_location('actual_ownership',owner_path)
owner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(owner)
scratch = Path(tempfile.mkdtemp(prefix='keyframe-pinned-source-claims-',dir='/private/tmp'))
physical = []
try:
    for target in roles:
        case = scratch/Path(target).stem
        for name,body in bodies.items():
            path = case/name
            path.parent.mkdir(parents=True,exist_ok=True)
            path.write_bytes(body)
        captured = {name:owner.claim(case,name,row['base_sha256']) for name,row in roles.items()}
        epoch = {'pins':{name:row['base_sha256'] for name,row in roles.items()},'installed_identities':{}}
        before = copy.deepcopy(epoch)
        def git(root,env,operation,object_name):
            assert root == case and env == {} and operation == 'show'
            revision,name = object_name.split(':',1)
            assert revision == head
            return bodies[name]
        namespace = dict(ROOT=case,epoch=epoch,roles=roles,additional=captured,sources={},ownership=owner,state=SimpleNamespace(h=SimpleNamespace(git=git)),env={},checkpoint={'head':head},hashlib=hashlib)
        exec(code,namespace)
        assert namespace['sources'] == captured and epoch == before
        path = case/target
        path.rename(path.with_suffix('.saved'))
        path.write_bytes(bodies[target])
        assert [path.stat().st_dev,path.stat().st_ino] != captured[target]['identity']
        try: exec(code,dict(namespace,sources={}))
        except RuntimeError as exc: assert str(exc) == 'owned identity: '+target
        else: raise AssertionError('Same-byte replacement admitted')
        assert epoch == before
        physical.append({'source':target,'exact_pin_claimed':True,'same_byte_replacement_rejected':True})
finally:
    shutil.rmtree(scratch)
assert not scratch.exists()
print(json.dumps({'success':True,'checks':checks,'positives':4,'negatives':18,'actual_capture_function':True,'actual_native_observe_source_loop':True,'protocol_ownership_and_git_are_doubles':True,'actual_ownership_physical_controls':physical,'scratch':str(scratch),'scratch_removed':True,'epoch_unchanged':True,'live_operations':False,'prior_bridge_checks_reused':11,'source_sha256':sha(HERE/'baseline.py'),'native_source_sha256':sha(CANDIDATE/'baseline.py')},sort_keys=True))
