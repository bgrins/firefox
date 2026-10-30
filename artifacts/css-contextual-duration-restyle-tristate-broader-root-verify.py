import argparse
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
ROOT = Path(__file__).resolve().parents[1]
HERE = ROOT / 'artifacts/css-contextual-duration-restyle-tristate-broader-v1'
PAIR = ROOT / 'artifacts/css-contextual-duration-restyle-tristate-broader-runtime-1'
RUNTIME = ROOT / 'artifacts/css-registered-number-native-runtime-v1'
read = lambda path: json.loads(path.read_bytes())
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def save(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write('\n')


parser = argparse.ArgumentParser()
parser.add_argument('--session', type=int, required=True)
parser.add_argument('--terminal', required=True)
parser.add_argument('--exit', type=int, required=True, dest='exit_code')
args = parser.parse_args()
assert args.session > 0 and args.terminal and all(c in '0123456789abcdef' for c in args.terminal)
assert args.exit_code == 0, 'Success-only verifier; failed-owner restoration requires a separate review'

policy = read(HERE / 'POLICY.json')
owner = load('root_trace_owner', policy['ownership_helper'])
owner.authenticate(HERE, '58c6fe38b9be06eb7ea27e76dcbca029a742c784d5142f8bc6f5a34b69b3939f')
state = load('root_trace_state', policy['state_helper'])
bundle = load('root_trace_bundle', policy['bundle_helper'])
env = dict(os.environ, GIT_OPTIONAL_LOCKS='0', PYTHONDONTWRITEBYTECODE='1')
assert not any(os.environ.get(k) for k in ('GIT_DIR', 'GIT_WORK_TREE', 'GIT_INDEX_FILE', 'GIT_OBJECT_DIRECTORY', 'GIT_ALTERNATE_OBJECT_DIRECTORIES'))
assert {name: sha(RUNTIME / name) for name in policy['controls']} == policy['controls']
assert not (RUNTIME / 'SOURCE-TRANSITION.lock').exists()
result = read(PAIR / 'CANDIDATE-RESULT.json')
assert result['success'] and result['restoration_verified'] and result['error'] is None
assert result['runtime_controls_unchanged'] and result['empty_staging_preserved']
assert result['publication_errors'] == [] and not result['native_fix_acceptance']
assert read(PAIR / 'RESTORATION.json')['errors'] == []
assert read(PAIR / 'RESTORATION.json')['owned_processes'] == {}
backup = read(PAIR / 'BACKUP-CLEANUP.json')
assert backup['removed'] and backup['verified_original_restoration'] and not backup['retained_after_failure']
assert not (PAIR / 'backups').exists()
build = read(PAIR / 'candidate-build/build-RESULT.json')
assert build['exit'] == 0 and build['owned_group_absent'] and build['cleanup_errors'] == []
assert build['error'] is None and build['stop_reason'] is None
roles = read(HERE / 'SOURCE-ROLES.json')
compiled = read(PAIR / 'candidate-build/RESULT.json')
assert compiled['command_success'] and compiled['preservation_verified'] and compiled['error'] is None
assert compiled['native_sources'] == {name: record['candidate_sha256'] for name, record in roles.items()}
assert set(compiled['binaries']) == set(policy['rebuilt_binaries'])
command = read(PAIR / 'candidate-build/COMMAND.json')
assert command['source_sha256'] == compiled['native_sources'] and command['owner_manifest'] == sha(HERE / 'FILES.json')
assert command['command'] == ['/Users/bgrins/venvs/firefox/bin/python', './mach', 'build', 'binaries', '-j2']
assert compiled['snapshot'] == read(PAIR / 'PHASES-PRE.json') == read(PAIR / 'PHASES-POST.json')
for receipt in ('build-PROCESS.json','WAKE-PROCESS.json'):
    owner.group_absent(read(PAIR / 'candidate-build' / receipt)['pgid'])
assessor = load('root_broader_assessor', str((HERE / 'assess.py').relative_to(ROOT)))
checks = load('root_broader_checks', policy['wpt']['checks_helper'])
comparison = load('root_broader_comparison', str((HERE / 'comparison.py').relative_to(ROOT)))
for capsule_key,binding_key in (('baseline_capsule','baseline_binding'),('inactive_capsule','inactive_binding'),('reduced_capsule','reduced_binding')):
    capsule,binding = policy[capsule_key],policy[binding_key]
    owner.authenticate(ROOT / capsule['directory'],capsule['sha256'])
    owner.authenticate(ROOT / binding['directory'],binding['manifest_sha256'])
    directory = ROOT / binding['directory']
    assert read(directory / binding['terminal_path']) == binding['terminal'] and binding['terminal']['exit'] == 0
    assert sha(directory / 'RESULT.json') == binding['result_sha256']
comparison.replay_all(ROOT,policy)
load('root_broader_prior_target',str((HERE / 'target.py').relative_to(ROOT))).verify(ROOT,policy,HERE)
phase_results, summaries, application = {}, {}, None
for kind,rows,ends in (('normative',49,10),('reftest',0,1),('inactive',1,1),('reduced',2,1)):
    phase = PAIR / (kind + '-wpt')
    current = dict(policy,phase_kind=kind,wpt=policy['phases'][kind])
    assert current['wpt'] == comparison.expected_wpt(ROOT,current)
    owner.group_absent(read(phase / 'PROCESS.json')['pgid'])
    outcome = read(phase / 'RESULT.json')
    assert outcome['success'] and outcome['exit'] == 0 and outcome['preservation_verified'] and outcome['execution_error'] is None
    assert outcome['comparison_gate_passed'] and outcome['native_fix_acceptance'] is False
    cleanup = read(phase / 'CLEANUP.json')
    assert cleanup['owned_group_absent'] and cleanup['temporary_root_removed']
    settings = read(phase / 'ASSESSMENT-POLICY.json')
    assert settings == comparison.phase_policy(current['wpt'])
    events = [json.loads(line) for line in (phase / 'raw.jsonl').read_text().splitlines()]
    metadata = read(phase / 'APPLICATION-METADATA.json')
    original = comparison.replay_original(ROOT,current,assessor,checks)
    assessment = assessor.assess(events,outcome['exit'],settings,checks,original=original,run_binding=metadata)
    assert json.loads(json.dumps(assessment)) == read(phase / 'ASSESSMENT.json')
    assert assessment['complete'] and assessment['errors'] == []
    assert assessment['comparison_gate_passed'] and assessment['comparison_errors'] == []
    assert len(assessment['rows']) == rows and all(row['status'] == 'PASS' for row in assessment['rows'])
    assert len(assessment['ends']) == ends and all(end['status'] == ('PASS' if kind == 'reftest' else 'OK') for end in assessment['ends'])
    assert read(phase / 'PRE.json') == read(phase / 'POST.json') == compiled['snapshot']
    assert metadata == read(phase / 'APPLICATION-METADATA-POST.json')
    assert metadata['revision'] == metadata['build_revision'] == metadata['harness_revision'] == policy['head']
    assert metadata['source_role'] == 'candidate'
    if application is None:
        application = metadata
    assert application == metadata
    assert compiled['binaries'] == read(phase / 'BINARY-PINS.json')
    phase_results[kind] = {key:sha(phase / filename) for key,filename in [('assessment_sha256','ASSESSMENT.json'),('raw_sha256','raw.jsonl'),('result_sha256','RESULT.json')]}
    summaries[kind] = {'callbacks_passed':rows,'endings':ends,'ending_status':'PASS' if kind == 'reftest' else 'OK','raw_replay_verified':True,'comparison_passed':True}
restyles = load('root_broader_restyles',str((HERE / 'restyles.py').relative_to(ROOT)))
projector = load('root_broader_restyle_projection',policy['restyle_projection']['path'])
phase = PAIR / 'restyles'
owner.group_absent(read(phase / 'PROCESS.json')['pgid'])
outcome = read(phase / 'RESULT.json')
assert outcome['exit'] == 0 and outcome['execution_error'] is None and outcome['preservation_verified'] and outcome['owned_group_absent']
assert outcome['comparison_passed'] and outcome['comparison_error'] is None and outcome['native_acceptance'] is False
assert read(phase / 'CLEANUP.json')['owned_group_absent']
events = [json.loads(line) for line in (phase / 'raw.jsonl').read_text().splitlines()]
assessment = restyles.assess(events,outcome['exit'],checks)
assert assessment == read(phase / 'ASSESSMENT.json')
original = restyles.original(ROOT,policy)
assert projector.compare(original,assessment)
assert read(phase / 'PRE.json') == read(phase / 'POST.json') == compiled['snapshot']
assert read(phase / 'APPLICATION-METADATA.json') == read(phase / 'APPLICATION-METADATA-POST.json') == {k:v for k,v in application.items() if k not in ('build_revision','harness_revision','source_role')}
source_command = read(ROOT / policy['restyle_baseline']['directory'] / 'COMMAND.json')['command']
assert [c for c in read(phase / 'COMMAND.json')['command'] if not c.startswith('--log-raw=')] == [c for c in source_command if not c.startswith('--log-raw=')]
phase_results['restyles'] = {key:sha(phase / filename) for key,filename in [('assessment_sha256','ASSESSMENT.json'),('raw_sha256','raw.jsonl'),('result_sha256','RESULT.json')]}
assert result['candidate_phase'] == phase_results
summaries['restyles'] = {'assertions':170,'passed':162,'expected_failures':8,'ending_status':'PASS','raw_replay_verified':True,'comparison_passed':True,'projection_sha256':sha(ROOT / policy['restyle_projection']['path'])}
roles = read(HERE / 'SOURCE-ROLES.json')
for name, role in roles.items():
    record = read(PAIR / 'RESTORATION.json')['sources'][name]
    owner.claim(ROOT, name, role['base_sha256'], record['identity'])
for name, record in policy['accepted_current_payloads'].items():
    owner.claim(ROOT, name, record['sha256'], record['identity'])
for name, pin in policy['source_context_pins'].items():
    assert sha(ROOT / name) == pin
assert bundle.semantic(bundle.scan(ROOT / policy['bundle_path'])) == bundle.semantic(read(PAIR / 'APP-PRE.json'))
assert bundle.semantic({name: bundle.entry(ROOT / name) for name in policy['extra_backup_paths']}) == bundle.semantic(read(PAIR / 'EXTRA-PRE.json'))
for name, path in [('root', ROOT), ('nested', ROOT / 'artifacts/css-spec-lean')]:
    assert hashlib.sha256(state.h.git(path, env, 'ls-files', '-v', '-z')).hexdigest() == policy['prepared_flag_hashes'][name]
old_bytes = (RUNTIME / 'CURRENT-EPOCH.json').read_bytes()
old = json.loads(old_bytes)
observation = read(PAIR / 'RAW-INDEX-OBSERVATION.json')
assert observation['semantic_index_unchanged'] and not observation['canonical_updated']
assert observation['before'] == old['raw_index_observation']['current']
updated = copy.deepcopy(old)
updated['raw_index_observation']['current'] = observation['after']
snapshot = state.a.verify_current(state.h, ROOT, env, updated)
assert snapshot == read(PAIR / 'POST.json')
expected = copy.deepcopy(read(ROOT / policy['baseline_binding']['directory'] / 'POST.json'))
expected['index']['raw_index'] = observation['after']
assert snapshot == expected
app_entry = ROOT / policy['wpt']['application_ini']
terminal = {
    'session_id': args.session, 'terminal_chunk': args.terminal, 'exit': args.exit_code,
    'owner_sha256': sha(HERE / 'FILES.json'), 'result_sha256': sha(PAIR / 'CANDIDATE-RESULT.json'),
    'build_success': True, 'phases': summaries, 'normative_callbacks_passed': 50,
    'reduced_callbacks_passed': 2, 'raw_replay_verified': True,
    'state_and_application_restoration_independently_verified': True,
    'raw_index_observation': observation, 'restored_application_entry': bundle.entry(app_entry),
    'restored_application_target': bundle.entry(app_entry.resolve()),
    'backup_removed_bytes': backup['owned_backup_bytes'], 'native_acceptance': False,
    'self_feedback_numeric_or_convergence_oracle': False,
}
save(PAIR / 'ROOT-TERMINAL.json', terminal)
symlinks = {str(p.relative_to(PAIR)): os.readlink(p) for p in PAIR.rglob('*') if p.is_symlink()}
save(PAIR / 'SYMLINKS.json', symlinks)
manifest = {str(p.relative_to(PAIR)): sha(p) for p in PAIR.rglob('*') if p.is_file() and not p.is_symlink()}
assert 'FILES.json' not in manifest
save(PAIR / 'FILES.json', manifest)
if observation['before'] != observation['after']:
    unchanged = copy.deepcopy(updated)
    unchanged['raw_index_observation']['current'] = observation['before']
    assert unchanged == old
    claim = owner.claim(ROOT, str((RUNTIME / 'CURRENT-EPOCH.json').relative_to(ROOT)), policy['controls']['CURRENT-EPOCH.json'])
    try:
        owner.write_owned(ROOT, claim, owner.encoded(updated))
        assert state.a.verify_current(state.h, ROOT, env, updated) == snapshot
        assert all(sha(RUNTIME / name) == policy['controls'][name] for name in ('OWNED.json', 'ROLE.json'))
    except BaseException:
        owner.write_owned(ROOT, claim, old_bytes)
        raise
refresh = {'before_epoch': policy['controls']['CURRENT-EPOCH.json'], 'after_epoch': sha(RUNTIME / 'CURRENT-EPOCH.json'), 'only_changed_field': 'raw_index_observation.current', 'observation': observation, 'runtime_manifest_sha256': sha(PAIR / 'FILES.json'), 'full_restored_state_verified': True, 'accepted_fix_increment': 0}
save(ROOT / 'artifacts/css-contextual-duration-restyle-tristate-broader-root-refresh.json', refresh)
print(json.dumps({'terminal': terminal, 'refresh': refresh}, indent=2), flush=True)
