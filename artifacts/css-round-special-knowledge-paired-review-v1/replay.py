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
CAPSULE = ROOT / 'artifacts/css-round-special-knowledge-paired-wpt-runner-v2'
RUNTIME = ROOT / 'artifacts/css-round-special-knowledge-reversible-pair-runtime-2'
read = lambda p: json.loads(p.read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


publisher = load('saved_publisher', CAPSULE / 'run.py')
publisher.authenticate(CAPSULE, 'ce2b22d468ba2afdf0c7bbe8c4bb151dd6c3fadcff7d5f95633d4c146981138e')
publisher.authenticate(RUNTIME, 'dff98818c652bdac581dacf593213afbf710527a56fabd5d1853b5dbd05c3c00')
assert {str(p.relative_to(RUNTIME)): str(p.readlink()) for p in RUNTIME.rglob('*') if p.is_symlink()} == read(RUNTIME / 'SYMLINKS.json')
source_package = ROOT / 'artifacts/css-round-special-knowledge-repair-v4'
publisher.authenticate(source_package, '0f78775af71a65272d80201c6bee798edbacbfc11df79a0ec4454821134f2e68')
fixture = 'testing/web-platform/tests/css/css-values/round-deferred-infinite-step.html'
assert sha(source_package / 'candidate' / fixture) == 'b7e21fb6b4ea7ddb55ec790fa967f3d3e206df630b634c9c11b95303afd31d9e'
assessor = load('saved_assessor', CAPSULE / 'assess.py')
bindings = load('saved_bindings', CAPSULE / 'bindings.py')
helper = SimpleNamespace(**vars(publisher))
summaries, assessments = {}, {}
for role in ('original', 'candidate'):
    phase = role + '-1'
    directory = RUNTIME / (role + '-wpt')
    assert (directory / 'tests/css/css-values/round-deferred-infinite-step.html').read_bytes() == (source_package / 'candidate' / fixture).read_bytes()
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
    assert len(replay['rows']) == 712 and len(replay['ends']) == 10
    assert all(row['status'] == 'OK' for row in replay['ends'])
    targets = [row for row in replay['rows'] if row['test'] in policy['target_subtests']]
    controls = [row for row in replay['rows'] if row['test'] not in policy['target_subtests']]
    assert len(targets) == 23 and len(controls) == 689
    summaries[role] = {'all': dict(Counter(row['status'] for row in replay['rows'])),
        'targets': dict(Counter(row['status'] for row in targets)), 'controls': len(controls), 'ends': len(replay['ends']),
        'wpt_exit': result['exit'], 'build_epoch_sha256': sha(directory / 'EPOCH.json')}
    for name, pin in read(directory / 'OWNED-INPUT-PINS.json').items():
        assert sha(directory / name) == pin
    build = RUNTIME / (role + '-build')
    assert (build / 'EPOCH.json').read_bytes() == (directory / 'EPOCH.json').read_bytes()
    for name in ('build-GROUP-CLEANUP.json', 'wake-GROUP-CLEANUP.json'):
        assert read(build / name)['owned_group_absent']
    assessments[role] = replay

assert summaries['original']['all'] == {'PASS': 683, 'FAIL': 29}
assert summaries['original']['targets'] == {'PASS': 4, 'FAIL': 19}
assert summaries['candidate']['all'] == {'PASS': 702, 'FAIL': 10}
assert summaries['candidate']['targets'] == {'PASS': 23}
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
assert restoration['source_sha256'] == {'servo/components/style/values/generics/calc.rs': 'b9a36918f1291b2c08cfb6d83aca73eb309185d1d2691961d6334b7bc69d1274'}
before, after = read(RUNTIME / 'PRE.json'), read(RUNTIME / 'POST.json')
raw = read(RUNTIME / 'RAW-INDEX-OBSERVATION.json')
assert before['index']['raw_index'] == raw['before'] and after['index']['raw_index'] == raw['after']
before['index']['raw_index'] = raw['after']
assert before == after and raw['semantic_index_unchanged'] and raw['cause'] == 'unknown'
assert read(RUNTIME / 'BACKUP-CLEANUP.json')['removed'] and not (RUNTIME / 'backups').exists()
print(json.dumps({'phases': summaries, 'full_raw_publication_replay': True,
    'regression_signatures_unchanged': 689, 'ends_unchanged': 10,
    'target_repairs': 19, 'saved_restoration_verified': True,
    'raw_index_cause': 'unknown', 'native_acceptance': False}, indent=2))
