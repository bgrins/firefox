import hashlib
import importlib.util
import json
import sys
from collections import Counter
from pathlib import Path
from types import SimpleNamespace

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CAPSULE = ROOT / 'artifacts/css-round-context-quotient-paired-wpt-runner-v2'
RUNTIME = ROOT / 'artifacts/css-round-context-quotient-reversible-pair-runtime-2'
read = lambda p: json.loads(p.read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


publisher = load('saved_publisher', CAPSULE / 'run.py')
publisher.authenticate(CAPSULE, 'f5f6c022ce93ba615a315c9d91e1c415f2297b4a46b5bc2972461e35f8061a8d')
publisher.authenticate(RUNTIME, '47e84cfcff2076fbab2234801d03cfbb4181d10128848909197c16901581189d')
assert {str(p.relative_to(RUNTIME)): str(p.readlink()) for p in RUNTIME.rglob('*') if p.is_symlink()} == read(RUNTIME / 'SYMLINKS.json')
source_package = ROOT / 'artifacts/css-round-context-quotient-repair-v3'
publisher.authenticate(source_package, 'cd6eaec05aea4ad549b9d2906bb8be6a9bf08cbc1c26fb03ee42791fb0370763')
fixture = 'testing/web-platform/tests/css/css-values/round-context-quotient-precision.html'
assert sha(source_package / 'candidate' / fixture) == '961eb87af1dfdb9da434d1e33c30526ad42b56e15b7121bbd8d7f3144d72555c'
assessor = load('saved_assessor', CAPSULE / 'assess.py')
bindings = load('saved_bindings', CAPSULE / 'bindings.py')
helper = SimpleNamespace(**vars(publisher))
summaries, assessments = {}, {}
for role in ('original', 'candidate'):
    phase = role + '-1'
    directory = RUNTIME / (role + '-wpt')
    assert (directory / 'tests/css/css-values/round-context-quotient-precision.html').read_bytes() == (source_package / 'candidate' / fixture).read_bytes()
    policy = read(directory / 'POLICY.json')
    epoch = read(directory / 'EPOCH.json')
    assert bindings.validate_phase(ROOT, CAPSULE, policy, epoch, helper) == read(directory / 'PHASE-BINDING.json')
    original = bindings.validate_original(ROOT, CAPSULE, policy, helper)
    checks = load('saved_checks_' + role, ROOT / policy['helpers']['checks'])
    events = [json.loads(line) for line in (directory / 'raw.jsonl').read_text().splitlines()]
    result = read(directory / 'RESULT.json')
    metadata = read(directory / 'APPLICATION-METADATA.json')
    assert metadata == read(directory / 'APPLICATION-METADATA-POST.json')
    assert metadata['revision'] == epoch['semantic_index']['head'] == policy['frozen_head']
    assert metadata['sha256'] == read(directory / 'INPUT-PINS.json')[policy['application_ini']]
    assert read(directory / 'PRE.json') == read(directory / 'POST.json')
    cleanup = read(directory / 'CLEANUP.json')
    assert cleanup['owned_group_absent'] and cleanup['temporary_root_removed']
    assert result['observation_gate_passed'] and result['execution_error'] is None and result['preservation_error'] is None
    replay = assessor.assess(events, result['exit'], policy, checks, original=original, run_binding=metadata)
    replay = publisher.augment_assessment(replay, phase=phase, capsule_sha=sha(CAPSULE / 'FILES.json'),
        epoch_sha=sha(directory / 'EPOCH.json'), policy=policy,
        capsule_directory=str(CAPSULE.relative_to(ROOT)), experiment_sha=sha(CAPSULE / 'EXPERIMENT.json'),
        execution_preserved=True)
    replay = json.loads(json.dumps(replay))
    assert replay == read(directory / 'ASSESSMENT.json')
    assert replay['complete'] and not replay['errors'] and not replay['infrastructure_faults']
    assert len(replay['rows']) == 738 and len(replay['ends']) == 12
    assert all(row['status'] == 'OK' for row in replay['ends'])
    targets = [row for row in replay['rows'] if row['test'] in policy['target_subtests']]
    controls = [row for row in replay['rows'] if row['test'] not in policy['target_subtests']]
    assert len(targets) == 26 and len(controls) == 712
    summaries[role] = {'all': dict(Counter(row['status'] for row in replay['rows'])),
        'targets': dict(Counter(row['status'] for row in targets)), 'controls': len(controls), 'ends': len(replay['ends']),
        'wpt_exit': result['exit'], 'build_epoch_sha256': sha(directory / 'EPOCH.json')}
    for name, pin in read(directory / 'OWNED-INPUT-PINS.json').items():
        assert sha(directory / name) == pin
    build = RUNTIME / (role + '-build')
    assert (build / 'EPOCH.json').read_bytes() == (directory / 'EPOCH.json').read_bytes()
    for name in ('build-GROUP-CLEANUP.json', 'wake-GROUP-CLEANUP.json'):
        assert read(build / name)['owned_group_absent']
    both = [row for row in targets if row['subtest'] == 'both infinite']
    assert len(both) == 1 and both[0]['status'] == 'PASS'
    assessments[role] = replay

assert summaries['original']['all'] == {'PASS': 715, 'FAIL': 23}
assert summaries['original']['targets'] == {'PASS': 13, 'FAIL': 13}
assert summaries['candidate']['all'] == {'PASS': 728, 'FAIL': 10}
assert summaries['candidate']['targets'] == {'PASS': 26}
assert assessments['candidate']['comparison_gate_passed']
assert assessments['original']['regression_signature'] == assessments['candidate']['regression_signature']
assert assessments['original']['held_signature'] == assessments['candidate']['held_signature']
result = read(RUNTIME / 'RESULT.json')
assert result['success'] and result['restoration_verified'] and result['runtime_controls_unchanged']
assert result['empty_staging_preserved'] and result['backups_removed_after_verification']
assert result['error'] is None and result['publication_errors'] == []
assert read(RUNTIME / 'ROOT-TERMINAL.json')['exit'] == 0
restoration = read(RUNTIME / 'RESTORATION.json')
assert restoration['errors'] == [] and restoration['owned_processes'] == {}
assert restoration['source_sha256'] == {'servo/components/style/values/generics/calc.rs': '2da120028b05d8741d3985a6415a3cf127fefc9e48cad700455600e7f1d41d28'}
before, after = read(RUNTIME / 'PRE.json'), read(RUNTIME / 'POST.json')
raw = read(RUNTIME / 'RAW-INDEX-OBSERVATION.json')
assert before['index']['raw_index'] == raw['before'] and after['index']['raw_index'] == raw['after']
before['index']['raw_index'] = raw['after']
assert before == after and raw['semantic_index_unchanged'] and raw['cause'] == 'unknown'
assert read(RUNTIME / 'BACKUP-CLEANUP.json')['removed'] and not (RUNTIME / 'backups').exists()
print(json.dumps({'phases': summaries, 'full_raw_publication_replay': True,
    'regression_signatures_unchanged': 712, 'ends_unchanged': 12,
    'target_repairs': 13, 'saved_restoration_verified': True,
    'raw_index_cause': 'unknown', 'native_acceptance': False}, indent=2))
