import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('bindings', HERE / 'bindings.py')
b = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b)
read = lambda p: json.loads(p.read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
def need(v, message):
    if not v:
        raise RuntimeError(message)
h = SimpleNamespace(read=read, sha=sha, need=need)
policy = read(HERE / 'POLICY.json')
rejected = []
with tempfile.TemporaryDirectory(prefix='lh-wpt-binding-', dir='/private/tmp') as tmp:
    root = Path(tmp)
    build = root / policy['owner_runtime'] / 'original-build'
    build.mkdir(parents=True)
    epoch = {'semantic_index': {'head': policy['frozen_head']},
             'reversible_line_height_phase': {'role': 'original', 'build_directory': str(build.relative_to(root)),
                'owner_runtime': policy['owner_runtime'], 'source_package_manifest': policy['source_package_manifest']},
             'pins': dict(policy['source_roles']['original'], **{n: 'a'*64 for n in policy['normal_binaries']})}
    result = {'command_success': True, 'preservation_verified': True, 'source_role': 'original',
              'owned_processes': {}, 'error': None, 'publication_errors': [], 'browser_build_performed': True}
    inner = {'exit': 0, 'error': None, 'stop_reason': None, 'cleanup_errors': [], 'owned_group_absent': True}
    def save(name, value):
        (build / name).write_text(json.dumps(value))
    save('EPOCH.json', epoch);save('RESULT.json', result);save('build-RESULT.json', inner);save('COMMAND.json', {'owned': True})
    q = b.bind_policy(root, HERE, policy, epoch, sha(build / 'EPOCH.json'), 'original-1', h)
    b.validate_phase(root, HERE, q, epoch, h)
    def reject(label, fn):
        try:
            fn()
        except (RuntimeError, KeyError, FileNotFoundError):
            rejected.append(label)
        else:
            raise AssertionError(label)
    for key, value in [('role','candidate'),('owner_runtime','artifacts/foreign'),('build_directory','artifacts/foreign/original-build'),('source_package_manifest','0'*64)]:
        bad = copy.deepcopy(epoch);bad['reversible_line_height_phase'][key] = value
        reject('wrong marker '+key, lambda: b.bind_policy(root,HERE,policy,bad,sha(build/'EPOCH.json'),'original-1',h))
    for field, value in [('command_success', False),('preservation_verified',False),('source_role','candidate'),('owned_processes',{'build':4}),('error','failed'),('browser_build_performed',False),('publication_errors',['failed'])]:
        bad=copy.deepcopy(result);bad[field]=value;save('RESULT.json',bad)
        changed = b.bind_policy(root,HERE,policy,epoch,sha(build/'EPOCH.json'),'original-1',h)
        reject('build '+field,lambda:b.validate_phase(root,HERE,changed,epoch,h))
    save('RESULT.json',result)
    for field,value in [('exit',1),('stop_reason','deadline'),('error','failed'),('cleanup_errors',['failed']),('owned_group_absent',False)]:
        bad=copy.deepcopy(inner);bad[field]=value;save('build-RESULT.json',bad)
        changed=b.bind_policy(root,HERE,policy,epoch,sha(build/'EPOCH.json'),'original-1',h)
        reject('inner '+field,lambda:b.validate_phase(root,HERE,changed,epoch,h))
    save('build-RESULT.json',inner)
    for label, mutate in [('native role',lambda e:e['pins'].update(policy['source_roles']['candidate'])),('HEAD',lambda e:e['semantic_index'].update(head='0'*40))]:
        bad=copy.deepcopy(epoch);mutate(bad);save('EPOCH.json',bad)
        changed=b.bind_policy(root,HERE,policy,bad,sha(build/'EPOCH.json'),'original-1',h)
        reject(label,lambda:b.validate_phase(root,HERE,changed,bad,h))
    save('EPOCH.json',epoch)
    reject('stale evidence',lambda:b.validate_phase(root,HERE,q,epoch,h)) if sha(build/'RESULT.json') != q['build_result_sha256'] else None
receipt={'positive':1,'rejected':rejected,'browser_executed':False,'live_state_queried':False,'scratch_removed':True}
(HERE/'BINDING-CONTROLS.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps({'positive':1,'rejected':len(rejected)}))
