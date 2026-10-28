import copy
import hashlib
import importlib.util
import json
import os
from collections import Counter
from pathlib import Path
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CAPSULE = ROOT / 'artifacts/css-linear-second-position-final-wpt-v2'
RUNTIME = ROOT / 'artifacts/css-linear-second-position-promotion-runtime-v1/candidate-wpt'
CAPSULE_SHA = '75bf310adaeb9aa68c2f8e8a38a59b9e33205ac9a98236c640c369700e1e14e6'
read = lambda p: json.loads(p.read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


r = load('linear_final_review_runner', CAPSULE / 'run.py')
b = load('linear_final_review_bindings', CAPSULE / 'bindings.py')
r.authenticate(CAPSULE, CAPSULE_SHA)
fixed, policy, epoch = read(CAPSULE / 'POLICY.json'), read(RUNTIME / 'POLICY.json'), read(RUNTIME / 'EPOCH.json')
bound = b.bind_policy(ROOT, CAPSULE, fixed, epoch, sha(RUNTIME / 'EPOCH.json'), 'candidate-1', r)
assert bound == policy
original = b.validate_original(ROOT, CAPSULE, policy, r)
result, saved = read(RUNTIME / 'RESULT.json'), read(RUNTIME / 'ASSESSMENT.json')
assert result == {'comparison_gate_passed': True, 'execution_error': None, 'exit': 0,
    'native_fix_acceptance': False, 'observation_gate_passed': True, 'observation_only': False,
    'phase': 'candidate-1', 'phase_gate_passed': True, 'preservation_error': None}
events = [json.loads(line) for line in (RUNTIME / 'raw.jsonl').read_text().splitlines()]
assessor = load('linear_final_review_assessor', CAPSULE / 'assess.py')
checks = load('linear_final_review_checks', ROOT / policy['helpers']['checks'])
metadata = read(RUNTIME / 'APPLICATION-METADATA.json')
assessment = assessor.assess(events, result['exit'], policy, checks, original=original, run_binding=metadata)
b.validate_final_assessment(ROOT, CAPSULE, policy, assessment, r)
publication = r.augment_assessment(assessment, phase='candidate-1', capsule_sha=CAPSULE_SHA,
    epoch_sha=sha(RUNTIME / 'EPOCH.json'), policy=policy, capsule_directory=str(CAPSULE.relative_to(ROOT)),
    experiment_sha=sha(CAPSULE / 'EXPERIMENT.json'), execution_preserved=True)
assert json.loads(json.dumps(publication)) == saved
rows = [e for e in events if e.get('action') == 'test_status']
ends = [e for e in events if e.get('action') == 'test_end']
starts = [e for e in events if e.get('action') == 'test_start']
rosters = {group: {(url, name) for url, names in policy[group].items() for name in names}
           for group in ('target_subtests', 'calibration_subtests', 'regression_subtests')}
assert [len(rosters[k]) for k in rosters] == [6, 2, 40]
assert len(rows) == 48 and Counter((e['test'], e['subtest']) for e in rows) == Counter(set.union(*rosters.values()))
assert len(starts) == len(ends) == 4
assert Counter(e['test'] for e in starts) == Counter(policy['tests'].keys()) == Counter(e['test'] for e in ends)
assert Counter(e['status'] for e in rows) == {'PASS': 36, 'FAIL': 12}
assert all(e['status'] == 'OK' for e in ends)
assert all(e['status'] == 'PASS' for e in rows if (e['test'], e['subtest']) in rosters['target_subtests'] | rosters['calibration_subtests'])
assert assessment['complete'] and assessment['errors'] == [] and assessment['infrastructure_faults'] == [] and assessment['crashes'] == []
prior = read(ROOT / policy['paired_runtime'] / 'candidate-wpt/ASSESSMENT.json')
signature = lambda e: tuple((k, k in e, json.dumps(e.get(k), sort_keys=True)) for k in ('status', 'message', 'expected', 'known_intermittent'))
oldrows = {(e['test'], e['subtest']): e for e in prior['rows']}
assert all(signature(e) == signature(oldrows[(e['test'], e['subtest'])]) for e in rows
           if (e['test'], e['subtest']) in rosters['regression_subtests'] | rosters['calibration_subtests'])
assert read(RUNTIME / 'PRE.json') == read(RUNTIME / 'POST.json')
assert metadata == read(RUNTIME / 'APPLICATION-METADATA-POST.json') == read(ROOT / policy['build_directory'] / 'APPLICATION-METADATA.json')
cleanup = read(RUNTIME / 'CLEANUP.json')
assert cleanup['owned_group_absent'] and cleanup['temporary_root_removed']
process = read(RUNTIME / 'PROCESS.json')
assert process['pid'] == process['pgid'] and process['pid'] > 0
command = read(RUNTIME / 'COMMAND.json')
assert command['wrapper_manifest_sha256'] == CAPSULE_SHA and command['epoch_sha256'] == policy['epoch_sha256']
assert command['phase'] == 'candidate-1' and '--headless' in command['command'] and '--processes=1' in command['command']
assert {v.removeprefix('--include=') for v in command['command'] if v.startswith('--include=')} == set(policy['tests'])
assert read(RUNTIME / 'ROOT-TERMINAL.json') == {'session': 75689, 'chunk': '4023ee', 'exit': 0}
assert read(RUNTIME / 'COMPARISON.json') == {'comparison_gate_passed': True, 'errors': [], 'native_fix_acceptance': False}
for name, digest in {**policy['build_evidence'], **policy['rename_evidence']}.items():
    assert sha(ROOT / name) == digest, name
owner = ROOT / policy['owner_runtime']
archive_sha = '49dd20af0babd48191342aad99ebaf2c46af7f1149389b52b8bdfe8b9952561e'
r.authenticate(owner, archive_sha)
archive = read(owner / 'FILES.json')
archive_files, archive_links = b.old_bindings_inventory(owner, r)
assert len(archive) == 67
assert archive_files == dict(archive, **{'FILES.json': archive_sha})
assert archive_links == read(owner / 'SYMLINKS.json') == {'candidate-wpt/tests/tools': str(ROOT / 'testing/web-platform/tests/tools')}
built = read(ROOT / policy['build_epoch'])
assert sha(ROOT / policy['build_epoch']) == policy['build_epoch_sha256']
ownership = read(owner / 'OWNERSHIP.json')
old = 'testing/web-platform/tests' + policy['target_rename']['old']
new = 'testing/web-platform/tests' + policy['target_rename']['new']
baseline = read(CAPSULE / 'PROMOTION-BASELINE-EPOCH.json')
b.project_promotion(built, baseline, dict(policy, installed_tests={old: policy['target_rename']['sha256']}), ownership, r)
renamed = copy.deepcopy(built)
for field in ('pins', 'installed_identities'):
    renamed[field][new] = renamed[field].pop(old)
renamed['raw_index_observation']['current'] = epoch['raw_index_observation']['current']
assert renamed == epoch
rename = ROOT / policy['rename_runtime']
assert read(rename / 'PRE-CURRENT-EPOCH.json') == built and read(rename / 'EPOCH.json') == epoch
relocated = {b.SOURCE: ownership[b.SOURCE], new: dict(ownership[old], path=new)}
assert read(rename / 'OWNERSHIP.json') == {new: relocated[new]}
b.project_promotion(epoch, baseline, policy, relocated, r)
rename_result = read(rename / 'RESULT.json')
assert all(rename_result[k] is True for k in ('renamed', 'body_and_inode_preserved', 'native_and_binaries_unchanged', 'preservation_verified'))
assert rename_result['epoch_sha256'] == policy['epoch_sha256'] and not rename_result['accepted']
build, inner = read(ROOT / policy['build_result']), read(ROOT / policy['inner_build_result'])
assert build['command_success'] and build['preservation_verified'] and build['browser_build_performed']
assert build['error'] is None and not build['owned_processes'] and not build['publication_errors'] and not build['accepted']
assert inner['exit'] == 0 and inner['error'] is None and inner['stop_reason'] is None
assert inner['owned_group_absent'] and not inner['cleanup_errors']
installed = read(owner / 'INSTALLED-EPOCH.json')
normalized = copy.deepcopy(built)
for name in policy['rebuilt_binaries']:
    normalized['pins'][name] = installed['pins'][name]
normalized['raw_index_observation']['current'] = installed['raw_index_observation']['current']
normalized['linear_guard_transition'] = installed['linear_guard_transition']
assert normalized == installed
assert read(RUNTIME / 'NORMAL-BINARIES.json') == policy['phase_binaries']
assert all(epoch['pins'][name] == digest for name, digest in policy['phase_binaries'].items())
for name, item in read(CAPSULE / 'SOURCE-PINS.json').items():
    relative = Path(name.removeprefix('testing/web-platform/'))
    destination = (RUNTIME / ('tests' if relative.parts[0] == 'tests' else 'metadata')).joinpath(*relative.parts[1:])
    if item['exists']:
        assert sha(destination) == item['sha256'], name
    else:
        assert not destination.exists(), name
files, links = {}, {}
for directory, dirs, names in os.walk(RUNTIME, followlinks=False):
    for name in dirs[:] + names:
        p = Path(directory) / name
        relative = str(p.relative_to(RUNTIME))
        if p.is_symlink():
            links[relative] = os.readlink(p)
            if name in dirs:
                dirs.remove(name)
        elif p.is_file() and relative not in {'README.md', 'SYMLINKS.json', 'FILES.json'}:
            files[str(p.relative_to(ROOT))] = sha(p)
assert links == {'tests/tools': str(ROOT / 'testing/web-platform/tests/tools')}
pins = {**files, **policy['build_evidence'], **policy['rename_evidence'], str(CAPSULE.relative_to(ROOT)) + '/FILES.json': CAPSULE_SHA}
pins[str(owner.relative_to(ROOT)) + '/FILES.json'] = archive_sha
if (HERE / 'EVIDENCE.json').exists():
    assert read(HERE / 'EVIDENCE.json') == pins
review = {'status': 'PASS', 'full_raw_and_publication_replay': True, 'final_subtests': 48,
    'final_pass': 36, 'final_existing_fail': 12, 'target_pass': 6, 'calibration_pass': 2,
    'regression_signatures_preserved': 40, 'paired_candidate_end_signatures_preserved': 4,
    'target_path_only_signature_mapping': 7, 'original_baseline_subtests': 42,
    'original_target_subtests': 0, 'original_target_crashes': 1, 'six_fail_repairs_claimed': False,
    'saved_preservation_metadata_cleanup_verified': True, 'installed_build_and_rename_joined': True,
    'outer_build_terminal_receipt_available': False, 'final_wrapper_exit': 0,
    'native_acceptance_by_this_review': False, 'evidence_supports_root_acceptance': True,
    'live_census_or_current_control_check': False, 'browser_reexecuted': False}
for name, value in [('REVIEW.json', review), ('EVIDENCE.json', pins)]:
    p = HERE / name
    if p.exists():
        assert read(p) == value
    else:
        p.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')
print(json.dumps(review, indent=2))
