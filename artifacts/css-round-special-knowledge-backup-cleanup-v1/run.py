import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
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
ENV = dict(os.environ, GIT_OPTIONAL_LOCKS='0')
assert not any(os.environ.get(k) for k in ('GIT_DIR','GIT_WORK_TREE','GIT_INDEX_FILE','GIT_OBJECT_DIRECTORY','GIT_ALTERNATE_OBJECT_DIRECTORIES'))
def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
for name, pin in policy['references'].items():
    assert sha(ROOT / name) == pin
state = load('cleanup_state', 'artifacts/css-registered-number-native-runtime-v1/state.py')
owner = load('cleanup_owner', 'artifacts/css-registered-number-source-transition-v4/transition.py')
bundle = load('cleanup_bundle', 'artifacts/css-round-special-knowledge-reversible-pair-v1/bundle.py')
owner.authenticate(HERE, sys.argv[2])
prior = ROOT / policy['prior_runtime']
def authenticate_evidence():
    for name, digest in policy['evidence_pins'].items():
        owner.claim(ROOT, str((prior/name).relative_to(ROOT)), digest)
authenticate_evidence()
assert read(prior/'ROOT-TERMINAL.json')['exit'] == 1
runtime = ROOT / 'artifacts/css-registered-number-native-runtime-v1'
controls = {n: (runtime/n).read_bytes() for n in ('CURRENT-EPOCH.json','ROLE.json','OWNED.json')}
assert sha(runtime/'CURRENT-EPOCH.json') == policy['epoch_sha256']
control_claims = {n:owner.claim(ROOT,str((runtime/n).relative_to(ROOT)),hashlib.sha256(body).hexdigest()) for n,body in controls.items()}
def check_controls():
    for n,item in control_claims.items():
        owner.claim(ROOT,item['path'],item['owned_sha256'],item['identity'])
        assert (runtime/n).read_bytes() == controls[n]
epoch = json.loads(controls['CURRENT-EPOCH.json'])
assert epoch['semantic_index']['head'] == policy['head'] and epoch['staged_working'] == {}
assert not os.path.lexists(runtime/'SOURCE-TRANSITION.lock')
assert all((prior/('PRE-'+n)).read_bytes() == body for n,body in controls.items())
projection = load('cleanup_projection', 'artifacts/css-round-special-knowledge-pair-raw-index-refresh-v1/projection.py')
observed = projection.derive(epoch, read(prior/'PRE-OBSERVATION-EPOCH.json'), read(prior/'POST-OBSERVATION-EPOCH.json'), read(prior/'RAW-INDEX-OBSERVATION.json'), policy['source_roles'])
assert state.a.verify_current(state.h,ROOT,ENV,read(prior/'POST-OBSERVATION-EPOCH.json')) == read(prior/'POST.json')
before = state.a.verify_current(state.h, ROOT, ENV, observed)
flags = {n: state.h.git(path,ENV,'ls-files','-v','-z') for n,path in [('root',ROOT),('nested',ROOT/'artifacts/css-spec-lean')]}
result = read(prior/'RESULT.json')
assert result['restoration_verified'] and result['runtime_controls_unchanged'] and result['empty_staging_preserved']
assert read(prior/'RESTORATION.json')['errors'] == [] and read(prior/'RESTORATION.json')['owned_processes'] == {}
assert result['success'] is False and result['error'] == 'AssertionError()' and result['publication_errors'] == []
assert result['backups_removed_after_verification'] is False
assert set(result['phase_results']) == {'original-1'}
for role in ('original',):
    phase = role+'-1'
    wpt = prior/(role+'-wpt')
    assessment = read(wpt/'ASSESSMENT.json')
    assert assessment['complete'] and assessment['execution_preserved'] and assessment['errors'] == []
    assert result['phase_results'][phase]['assessment_sha256'] == sha(wpt/'ASSESSMENT.json')
    assert result['phase_results'][phase]['wrapper_exit'] == 0
    observation = read(wpt/'RESULT.json')
    assert observation['observation_gate_passed'] and observation['execution_error'] is None and observation['preservation_error'] is None
    assert read(prior/(phase+'-WRAPPER-CLEANUP.json'))['restoration_safe']
    assert read(wpt/'CLEANUP.json')['owned_group_absent'] and read(wpt/'CLEANUP.json')['temporary_root_removed']
    owner.group_absent(read(wpt/'PROCESS.json')['pgid'])
for role in ('original',):
    directory = prior/(role+'-build')
    assert read(directory/'build-RESULT.json')['exit'] == 0
    assert read(directory/'build-GROUP-CLEANUP.json')['owned_group_absent']
    assert read(directory/'wake-GROUP-CLEANUP.json')['owned_group_absent']
    for name in ('build-PROCESS.json','WAKE-PROCESS.json'):
        owner.group_absent(read(directory/name)['pgid'])
candidate = prior/'candidate-build'
assert candidate.is_dir() and not candidate.is_symlink()
assert {p.name for p in candidate.iterdir()} == {'COMMAND.json'}
command = read(candidate/'COMMAND.json')
assert command['owner_manifest'] == policy['owner_manifest'] and command['source_role'] == 'candidate'
assert command['source_sha256'] == policy['candidate_source_sha256']
assert command['command'] == ['/Users/bgrins/venvs/firefox/bin/python','./mach','build','binaries','-j2']
assert not os.path.lexists(prior/'candidate-wpt')
app = ROOT/'objdir-full.noindex/dist/Nightly.app'
assert bundle.semantic(bundle.scan(app)) == bundle.semantic(read(prior/'APP-PRE.json'))
extras = read(prior/'EXTRA-PRE.json')
assert bundle.semantic({n:bundle.entry(ROOT/n) for n in extras}) == bundle.semantic(extras)
source = 'servo/components/style/values/generics/calc.rs'
pre = read(prior/'PRE-OBSERVATION-EPOCH.json')
owner.claim(ROOT,source,pre['pins'][source],pre['installed_identities'][source])
backups = prior/'backups'
saved = read(prior/'BACKUPS.json')
assert bundle.scan(backups) == saved['owned_inventory']
assert all(r['kind'] in ('file','directory') for r in saved['owned_inventory'].values())
output = ROOT/policy['output']
assert output.parent == ROOT/'artifacts' and not output.exists() and not output.is_symlink()
bundle.parents(ROOT,output)
output.mkdir()
state.save(output/'PRE.json',before)
state.save(output/'OWNED-BACKUP-INVENTORY.json',saved)
assert state.a.verify_current(state.h,ROOT,ENV,observed) == before
check_controls()
assert bundle.scan(backups) == saved['owned_inventory']
assert not os.path.lexists(runtime/'SOURCE-TRANSITION.lock')
authenticate_evidence()
assert bundle.semantic(bundle.scan(app)) == bundle.semantic(read(prior/'APP-PRE.json'))
assert bundle.semantic({n:bundle.entry(ROOT/n) for n in extras}) == bundle.semantic(extras)
owner.claim(ROOT,source,pre['pins'][source],pre['installed_identities'][source])
try:
    shutil.rmtree(backups)
    assert not backups.exists() and not backups.is_symlink()
except BaseException as error:
    state.save(output/'FAILURE.json',{'error':repr(error),'partial_cleanup_possible':True,'attempted_directory':str(backups),'no_native_acceptance':True})
    raise
after = state.a.verify_current(state.h,ROOT,ENV,observed)
assert after == before
check_controls()
assert all(state.h.git(path,ENV,'ls-files','-v','-z') == flags[n] for n,path in [('root',ROOT),('nested',ROOT/'artifacts/css-spec-lean')])
assert bundle.semantic(bundle.scan(app)) == bundle.semantic(read(prior/'APP-PRE.json'))
assert bundle.semantic({n:bundle.entry(ROOT/n) for n in extras}) == bundle.semantic(extras)
owner.claim(ROOT,source,pre['pins'][source],pre['installed_identities'][source])
state.save(output/'POST.json',after)
state.save(output/'RESULT.json',{'removed_owned_backups':True,'removed_bytes':saved['bytes'],'backup_inventory_sha256':sha(prior/'BACKUPS.json'),'current_epoch_sha256':policy['epoch_sha256'],'canonical_epoch_published':False,'verified_observation_sha256':sha(prior/'POST-OBSERVATION-EPOCH.json'),'preservation_verified':True,'app_source_native_index_runtime_unchanged':True,'prior_experiment_still_failed':True,'candidate_build_not_launched':True,'no_native_acceptance':True})
print('Removed only authenticated obsolete bundle backups; current app/source/index/runtime preserved')
