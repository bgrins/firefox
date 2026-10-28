import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
read = lambda p: json.loads(p.read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
policy = read(HERE/'POLICY.json')
assert policy['execution_enabled'] is True
assert len(sys.argv) == 3 and sys.argv[1] == policy['epoch_sha256']
assert not any(os.environ.get(k) for k in ('GIT_DIR','GIT_WORK_TREE','GIT_INDEX_FILE','GIT_OBJECT_DIRECTORY','GIT_ALTERNATE_OBJECT_DIRECTORIES'))
ENV = dict(os.environ, GIT_OPTIONAL_LOCKS='0')
for name,pin in policy['references'].items():
    assert sha(ROOT/name) == pin


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT/path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


state = load('cleanup_state','artifacts/css-registered-number-native-runtime-v1/state.py')
owner = load('cleanup_owner','artifacts/css-registered-number-source-transition-v4/transition.py')
bundle = load('cleanup_bundle','artifacts/css-keyframe-normal-recascade-balanced-reuse-runtime-v1/bundle.py')
projection = load('cleanup_projection','artifacts/css-random-grid-raw-index-refresh-v1/projection.py')
owner.authenticate(HERE,sys.argv[2])
prior = ROOT/policy['prior_runtime']
owner.authenticate(prior,policy['prior_manifest'])
evidence = ROOT/policy['typecheck_runtime']
owner.authenticate(evidence,policy['references'][str((evidence/'FILES.json').relative_to(ROOT))])
runtime = ROOT/'artifacts/css-registered-number-native-runtime-v1'
controls = {n:(runtime/n).read_bytes() for n in ('CURRENT-EPOCH.json','ROLE.json','OWNED.json')}
assert sha(runtime/'CURRENT-EPOCH.json') == policy['epoch_sha256']
assert all((evidence/('PRE-'+n)).read_bytes() == controls[n] for n in ('ROLE.json','OWNED.json'))
canonical = json.loads(controls['CURRENT-EPOCH.json'])
assert canonical['semantic_index']['head'] == policy['head'] and canonical['staged_working'] == {}
epoch = projection.derive(read(evidence/'PRE-CURRENT-EPOCH.json'),read(evidence/'OBSERVATION-EPOCH.json'),read(evidence/'POST-OBSERVATION-EPOCH.json'),read(evidence/'RAW-INDEX-OBSERVATION.json'))
assert canonical == epoch
refresh = ROOT/policy['refresh_runtime']
assert read(refresh/'RESULT.json')['preservation_verified'] and read(refresh/'RESULT.json')['updated']
assert read(refresh/'RESULT.json')['epoch_sha256'] == policy['epoch_sha256']
assert (refresh/'EPOCH.json').read_bytes() == controls['CURRENT-EPOCH.json']
assert read(refresh/'POST.json') == read(evidence/'POST.json')
result = read(evidence/'RESULT.json')
assert result['success'] and result['preservation_verified'] and result['source_restored']
assert result['error'] is None and result['publication_errors'] == [] and result['owned_processes'] == {}
assert result['runtime_controls_unchanged'] and result['empty_staging_preserved']
assert read(evidence/'ROOT-TERMINAL.json')['exit_code'] == 0
assert read(evidence/'RESTORATION.json')['errors'] == []
for name in ('build','wake'):
    assert read(evidence/(name+'-GROUP-CLEANUP.json'))['owned_group_absent']
for name in ('build-PROCESS.json','WAKE-PROCESS.json'):
    owner.group_absent(read(evidence/name)['pgid'])
terminal = read(prior/'ROOT-TERMINAL-VERIFICATION.json')
assert terminal['outcome'] == 'BALANCED_REUSE_TIMINGS_VERIFIED_PRESERVED'
assert terminal['actual_exit'] == 0 and terminal['native_mutation'] is False
assert terminal['timing_processes'] == terminal['profiles_removed'] == 8
completed = read(prior/'RESULT.json')
assert completed['captures'] == completed['completed_captures'] == ['capture-01-A','capture-02-B','capture-03-B','capture-04-A','capture-05-B','capture-06-A','capture-07-A','capture-08-B']
assert completed['comparison_error'] is None and completed['source_transitions'] == []
for name in completed['captures']:
    cleanup = read(prior/name/'CLEANUP.json')
    assert cleanup['owned_group_absent'] and cleanup['profile_removed'] and cleanup['errors'] == []
    run = read(prior/name/'RUN.json')
    assert run['error'] is None and run['protocol_errors'] == []
previous = read(ROOT/'artifacts/css-obsolete-balanced-bundle-cleanup-runtime-1/RESULT.json')
assert previous['removed_labels'] == ['A','B'] and previous['preservation_verified']
assert read(ROOT/'artifacts/css-obsolete-balanced-bundle-cleanup-runtime-1/ROOT-TERMINAL.json')['exit_code'] == 0
assert terminal['final_sha256'] == sha(prior/'FINAL.json')
assert terminal['final_pins_sha256'] == sha(prior/'FINAL-PINS.json')
assert read(prior/'RESULT.json')['recovery_errors'] == []
assert read(prior/'CLEANUP.json')['errors'] == []
assert read(prior/'CLEANUP.json')['retained_derivatives'] == policy['labels'] == ['A','B']
receipts = {n:read(prior/(n+'-BUNDLE.json')) for n in policy['labels']}
for label,receipt in receipts.items():
    prefix = str((prior/(label+'.app')).relative_to(ROOT))
    for field in ('pins','committed_research_working_payloads','installed_identities','untracked_native','staged_working'):
        assert not any(k == prefix or k.startswith(prefix+'/') for k in epoch[field])
    assert not any(k == label+'.app' or k.startswith(label+'.app/') for k in read(prior/'FILES.json'))
    bundle.verify(prior/(label+'.app'),receipt)
    assert all(bundle.info(prior/(label+'.app')/n)['mode'] == mode for n,mode in receipt['directory_modes'].items())
    assert all((prior/(label+'.app')/n).lstat().st_nlink == 1 for n in receipt['files'])
lock = runtime/'SOURCE-TRANSITION.lock'
assert not lock.exists() and not lock.is_symlink()
before = state.a.verify_current(state.h,ROOT,ENV,epoch)
assert before == read(evidence/'POST.json')
flags = {n:state.h.git(p,ENV,'ls-files','-v','-z') for n,p in [('root',ROOT),('nested',ROOT/'artifacts/css-spec-lean')]}
output = ROOT/policy['output']
assert output.parent == ROOT/'artifacts' and not output.exists() and not output.is_symlink()
output.mkdir()
state.save(output/'PRE.json',before)
state.save(output/'BUNDLE-RECEIPTS.json',receipts)
removed = []
attempted_label = None
try:
    for label,receipt in receipts.items():
        destination = prior/(label+'.app')
        assert not prior.is_symlink() and not destination.is_symlink()
        assert all((runtime/n).read_bytes() == body for n,body in controls.items())
        assert not lock.exists() and not lock.is_symlink()
        assert state.a.verify_current(state.h,ROOT,ENV,epoch) == before
        processes = subprocess.check_output(['ps','-axo','pid=,command='],text=True)
        assert not any(str(prior/(n+'.app')) in line for n in receipts for line in processes.splitlines())
        bundle.verify(destination,receipt)
        assert all(bundle.info(destination/n)['mode'] == mode for n,mode in receipt['directory_modes'].items())
        attempted_label = label
        shutil.rmtree(destination)
        assert not destination.exists() and not destination.is_symlink()
        removed.append(label)
        attempted_label = None
        state.save(output/(label+'-REMOVED.json'),{'label':label,'receipt_sha256':sha(prior/(label+'-BUNDLE.json')),'retained_bytes':receipt['retained_bytes']})
    after = state.a.verify_current(state.h,ROOT,ENV,epoch)
    assert after == before
    assert all((runtime/n).read_bytes() == body for n,body in controls.items())
    assert all(state.h.git(p,ENV,'ls-files','-v','-z') == flags[n] for n,p in [('root',ROOT),('nested',ROOT/'artifacts/css-spec-lean')])
    owner.authenticate(prior,policy['prior_manifest'])
    state.save(output/'POST.json',after)
    state.save(output/'RESULT.json',{'removed_labels':removed,'removed_logical_bytes':sum(r['retained_bytes'] for r in receipts.values()),'preservation_verified':True,'canonical_controls_unchanged':True,'historical_evidence_preserved':True,'native_fix_acceptance':False})
except BaseException as error:
    state.save(output/'FAILURE.json',{'removed_labels':removed,'error':repr(error),'partial_cleanup_possible_for':attempted_label,'unattempted_bundles_retained':[n for n in receipts if n not in removed and n != attempted_label]})
    raise
