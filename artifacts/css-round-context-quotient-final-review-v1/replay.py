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
CAPSULE = ROOT / 'artifacts/css-round-context-quotient-final-wpt-v3'
RUNTIME = ROOT / 'artifacts/css-round-context-quotient-promotion-runtime-1/candidate-wpt'
read = lambda p: json.loads(p.read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


publisher = load('saved_publisher', CAPSULE / 'run.py')
publisher.authenticate(CAPSULE, 'a91caf66cf1b9310f657e603f6c79ce690c0ec253425d358a10815934c8c3714')
for name, pin in read(HERE / 'REFERENCES.json').items():
    assert sha(ROOT / name) == pin, name
policy = read(RUNTIME / 'POLICY.json')
epoch = read(RUNTIME / 'EPOCH.json')
assert sha(RUNTIME / 'EPOCH.json') == policy['epoch_sha256'] == '3bdf00886a778b3d68b0fe119c1b3205f08686053cf7be406049cdb0bad7ebbe'
bindings = load('saved_bindings', CAPSULE / 'bindings.py')
assessor = load('saved_assessor', CAPSULE / 'assess.py')
helper = SimpleNamespace(**vars(publisher))
original = bindings.validate_original(ROOT, CAPSULE, policy, helper)
baseline = read(CAPSULE / 'PROMOTION-BASELINE-EPOCH.json')
owner = ROOT / policy['owner_runtime']
ownership = read(owner / 'OWNERSHIP.json')
bindings.project_promotion(epoch, baseline, policy, ownership, helper)
for name, pin in policy['build_evidence'].items():
    assert sha(ROOT / name) == pin, name
build = ROOT / policy['build_directory']
assert (build / 'EPOCH.json').read_bytes() == (RUNTIME / 'EPOCH.json').read_bytes()
br = read(build / 'RESULT.json')
assert br['command_success'] and br['preservation_verified'] and br['browser_build_performed']
assert br['error'] is None and br['owned_processes'] == {} and br['publication_errors'] == []
inner = read(build / 'build-RESULT.json')
assert inner['exit'] == 0 and inner['owned_group_absent'] and not inner['cleanup_errors']
assert inner['error'] is None and inner['stop_reason'] is None
installed = read(owner / 'INSTALLED-EPOCH.json')
normalized = json.loads(json.dumps(epoch))
for name in policy['rebuilt_binaries']:
    normalized['pins'][name] = installed['pins'][name]
normalized['raw_index_observation']['current'] = installed['raw_index_observation']['current']
normalized['round_context_quotient_transition'] = installed['round_context_quotient_transition']
assert normalized == installed
fixture = 'css/css-values/round-context-quotient-precision.html'
source = ROOT / 'artifacts/css-round-context-quotient-repair-v4/candidate/testing/web-platform/tests' / fixture
assert (RUNTIME / 'tests' / fixture).read_bytes() == source.read_bytes()
checks = load('saved_checks', ROOT / policy['helpers']['checks'])
events = [json.loads(line) for line in (RUNTIME / 'raw.jsonl').read_text().splitlines()]
result = read(RUNTIME / 'RESULT.json')
assert result['observation_gate_passed'] and result['comparison_gate_passed']
assert result['execution_error'] is None and result['preservation_error'] is None
assert result['exit'] == 1
metadata = read(RUNTIME / 'APPLICATION-METADATA.json')
assert metadata == read(RUNTIME / 'APPLICATION-METADATA-POST.json') == read(build / 'APPLICATION-METADATA.json')
assert metadata['revision'] == epoch['semantic_index']['head'] == policy['frozen_head']
assert metadata['sha256'] == read(RUNTIME / 'INPUT-PINS.json')[policy['application_ini']]
assert read(RUNTIME / 'PRE.json') == read(RUNTIME / 'POST.json')
cleanup = read(RUNTIME / 'CLEANUP.json')
assert cleanup['owned_group_absent'] and cleanup['temporary_root_removed']
replay = assessor.assess(events, result['exit'], policy, checks, original=original, run_binding=metadata)
replay = publisher.augment_assessment(replay, phase='candidate-1', capsule_sha=sha(CAPSULE / 'FILES.json'),
    epoch_sha=sha(RUNTIME / 'EPOCH.json'), policy=policy,
    capsule_directory=str(CAPSULE.relative_to(ROOT)), experiment_sha=sha(CAPSULE / 'EXPERIMENT.json'), execution_preserved=True)
replay = json.loads(json.dumps(replay))
assert replay == read(RUNTIME / 'ASSESSMENT.json')
bindings.validate_final_assessment(ROOT, CAPSULE, policy, replay, helper)
assert replay['complete'] and not replay['errors'] and not replay['infrastructure_faults']
assert len(replay['rows']) == 737 and len(replay['ends']) == 12
assert all(row['status'] == 'OK' for row in replay['ends'])
targets = [row for row in replay['rows'] if row['test'] in policy['target_subtests']]
assert len(targets) == 25 and all(row['status'] == 'PASS' for row in targets)
assert Counter(row['status'] for row in replay['rows']) == {'PASS': 727, 'FAIL': 10}
assert replay['regression_signature'] == original['regression_signature']
for name, pin in read(RUNTIME / 'OWNED-INPUT-PINS.json').items():
    assert sha(RUNTIME / name) == pin
print(json.dumps({'full_raw_publication_replay': True, 'rows': 737, 'pass': 727, 'existing_fail': 10,
    'target_pass': 25, 'paired_target_repairs': 13, 'regression_signatures_unchanged': 712,
    'ends_unchanged': 12, 'all_remaining_final_signatures_equal_paired_candidate': True, 'exact_named_PASS_row_omitted': True,
    'saved_build_source_metadata_and_preservation_verified': True,
    'live_guards_or_browser_executed': False, 'native_acceptance': False}, indent=2))
