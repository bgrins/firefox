import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
read = lambda p: json.loads(p.read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
policy = read(HERE / 'POLICY.json')
assert policy['execution_enabled'] is True
assert len(sys.argv) == 3 and sys.argv[1] == policy['epoch_sha256']
assert not any(os.environ.get(k) for k in ('GIT_DIR','GIT_WORK_TREE','GIT_INDEX_FILE','GIT_OBJECT_DIRECTORY','GIT_ALTERNATE_OBJECT_DIRECTORIES'))
ENV = dict(os.environ, GIT_OPTIONAL_LOCKS='0')
for name, pin in policy['references'].items():
    assert sha(ROOT / name) == pin


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


state = load('refresh_state', ROOT / 'artifacts/css-registered-number-native-runtime-v1/state.py')
owner = load('refresh_owner', ROOT / 'artifacts/css-registered-number-source-transition-v4/transition.py')
projection = load('refresh_projection', HERE / 'projection.py')
assert policy['source_roles'] == read(ROOT/'artifacts/css-round-special-knowledge-reversible-pair-v2/POLICY.json')['source_roles']
owner.authenticate(HERE, sys.argv[2])
evidence = ROOT / policy['paired_runtime']
assert set(policy['evidence_pins']) == set(policy['required_evidence'])
assert policy['terminal_confirmed_by_root'] is True


def authenticate_evidence():
    for name, pin in policy['evidence_pins'].items():
        owner.claim(ROOT, str((evidence / name).relative_to(ROOT)), pin)


authenticate_evidence()
runtime = ROOT / 'artifacts/css-registered-number-native-runtime-v1'
controls = {n:(runtime/n).read_bytes() for n in ('CURRENT-EPOCH.json','ROLE.json','OWNED.json')}
assert hashlib.sha256(controls['CURRENT-EPOCH.json']).hexdigest() == policy['epoch_sha256']
assert all((evidence/('PRE-'+n)).read_bytes() == b for n,b in controls.items())
claims = {n:owner.claim(ROOT,str((runtime/n).relative_to(ROOT)),hashlib.sha256(b).hexdigest()) for n,b in controls.items()}
canonical = json.loads(controls['CURRENT-EPOCH.json'])
assert canonical['semantic_index']['head'] == policy['head']
outer = read(evidence/'ROOT-TERMINAL.json')
assert outer['exit'] == 0
assert set(read(evidence/'RESULT.json')['phase_results']) == {'original-1', 'candidate-1'}
result = read(evidence/'RESULT.json')
assert result['success'] is True and result['error'] is None and result['publication_errors'] == []
assert result['backups_removed_after_verification'] is True
assert result['restoration_verified'] and result['runtime_controls_unchanged'] and result['empty_staging_preserved']
assert read(evidence/'RESTORATION.json')['errors'] == []
assert read(evidence/'RESTORATION.json')['owned_processes'] == {}
for phase, label in [('original-1','original-wpt'),('candidate-1','candidate-wpt')]:
    assert result['phase_results'][phase]['wrapper_exit'] == 0
    assessment = read(evidence/label/'ASSESSMENT.json')
    assert result['phase_results'][phase]['assessment_sha256'] == sha(evidence/label/'ASSESSMENT.json')
    assert assessment['complete'] and assessment['execution_preserved'] and assessment['errors'] == []
    wpt_result = read(evidence/label/'RESULT.json')
    assert wpt_result['execution_error'] is None and wpt_result['preservation_error'] is None
    assert wpt_result['observation_gate_passed']
    if phase == 'candidate-1':
        assert wpt_result['comparison_gate_passed'] and assessment['comparison_gate_passed']
    assert read(evidence/(phase+'-WRAPPER-CLEANUP.json'))['restoration_safe']
    cleanup = read(evidence/(label+'/CLEANUP.json'))
    assert cleanup['owned_group_absent'] and cleanup['temporary_root_removed']
    owner.group_absent(read(evidence/(label+'/PROCESS.json'))['pgid'])
for role in ('original','candidate'):
    assert read(evidence/(role+'-build')/'build-RESULT.json')['exit'] == 0
    for name in ('build','wake'):
        assert read(evidence/(role+'-build')/(name+'-GROUP-CLEANUP.json'))['owned_group_absent']
    for name in ('build-PROCESS.json','WAKE-PROCESS.json'):
        owner.group_absent(read(evidence/(role+'-build')/name)['pgid'])
pre = read(evidence/'PRE-OBSERVATION-EPOCH.json')
post = read(evidence/'POST-OBSERVATION-EPOCH.json')
raw = read(evidence/'RAW-INDEX-OBSERVATION.json')
updated = projection.derive(canonical, pre, post, raw, policy['source_roles'])
assert state.a.verify_current(state.h,ROOT,ENV,post) == read(evidence/'POST.json')
before = state.a.verify_current(state.h,ROOT,ENV,updated)
flags = {n:state.h.git(p,ENV,'ls-files','-v','-z') for n,p in [('root',ROOT),('nested',ROOT/'artifacts/css-spec-lean')]}
lock = runtime/'SOURCE-TRANSITION.lock'
assert not lock.exists() and not lock.is_symlink()
output = ROOT/policy['output']
assert output.parent == ROOT/'artifacts' and not output.exists() and not output.is_symlink()
output.mkdir()
(output/'PRE-CURRENT-EPOCH.json').write_bytes(controls['CURRENT-EPOCH.json'])
state.save(output/'PRE.json',before)
if canonical == updated:
    state.save(output/'RESULT.json',{'updated':False,'reason':'Raw index unchanged; no canonical write','preservation_verified':True})
    sys.exit(0)
with lock.open('x') as stream:
    stream.write(json.dumps({'pid':os.getpid(),'operation':'Successful Round infinite-step pair raw index observation refresh'})+'\n')
lock_identity = (lock.stat().st_dev,lock.stat().st_ino)


def check_controls(current_bytes):
    for name, claim in claims.items():
        owner.claim(ROOT,claim['path'],claim['owned_sha256'],claim['identity'])
        assert (runtime/name).read_bytes() == (current_bytes if name == 'CURRENT-EPOCH.json' else controls[name])


body = (json.dumps(updated,indent=2,sort_keys=True)+'\n').encode()
release_lock = False
try:
    authenticate_evidence()
    check_controls(controls['CURRENT-EPOCH.json'])
    assert state.a.verify_current(state.h,ROOT,ENV,updated) == before
    owner.write_owned(ROOT,claims['CURRENT-EPOCH.json'],body)
    check_controls(body)
    assert state.a.verify_current(state.h,ROOT,ENV,updated) == before
    assert all(state.h.git(p,ENV,'ls-files','-v','-z') == flags[n] for n,p in [('root',ROOT),('nested',ROOT/'artifacts/css-spec-lean')])
    state.save(output/'POST.json',before)
    (output/'EPOCH.json').write_bytes(body)
    state.save(output/'RESULT.json',{'updated':True,'only_changed_field':'raw_index_observation.current','before':raw['before'],'after':raw['after'],'cause':'unknown','preservation_verified':True,'epoch_sha256':hashlib.sha256(body).hexdigest(),'native_fix_acceptance':False})
    release_lock = True
except BaseException:
    owner.write_owned(ROOT,claims['CURRENT-EPOCH.json'],controls['CURRENT-EPOCH.json'])
    check_controls(controls['CURRENT-EPOCH.json'])
    assert state.a.verify_current(state.h,ROOT,ENV,updated) == before
    assert all(state.h.git(p,ENV,'ls-files','-v','-z') == flags[n] for n,p in [('root',ROOT),('nested',ROOT/'artifacts/css-spec-lean')])
    state.save(output/'ROLLBACK.json',{'canonical_preimage_restored':True,'actual_state_preserved':True})
    release_lock = True
    raise
finally:
    if release_lock:
        assert (lock.stat().st_dev,lock.stat().st_ino) == lock_identity
        lock.unlink()
