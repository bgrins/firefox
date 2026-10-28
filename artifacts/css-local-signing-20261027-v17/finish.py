import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
RUNTIME = ROOT / 'artifacts/css-registered-number-native-runtime-v1'
ENV = dict(os.environ, GIT_OPTIONAL_LOCKS='0')
GIT = ['git', '--no-optional-locks', '-c', 'core.fsmonitor=false']


def read(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write('\n')


def git(*args):
    return subprocess.check_output(GIT + list(args), cwd=ROOT, env=ENV)


spec = importlib.util.spec_from_file_location('number_state', RUNTIME / 'state.py')
s = importlib.util.module_from_spec(spec)
spec.loader.exec_module(s)
epoch_path = HERE / 'CURRENT-EPOCH.json'
epoch = read(epoch_path)
s.a.verify_current(s.h, ROOT, ENV, epoch)
receipts = {name: read(HERE / (name + '-receipt.json')) for name in
            ['validation', 'research']}
assert all(value['signature_verified'] for value in receipts.values())
assert receipts['validation']['parent'] == read(HERE / 'INITIAL-EPOCH.json')['semantic_index']['head']
assert receipts['research']['parent'] == receipts['validation']['commit']
assert epoch['semantic_index']['head'] == receipts['research']['commit'] == git('rev-parse', 'HEAD').decode().strip()
assert sha(RUNTIME / 'head-candidate-build-2/RESULT.json') == '04f8c243f35530bbf60c22ac0b171ba0270ab57e6377ae418302976475dc094a'
build = read(RUNTIME / 'head-candidate-build-2/RESULT.json')
assert build['command_success'] and build['preservation_verified']
assert build['owned_processes'] == {} and not build['publication_errors']
restoration = read(RUNTIME / 'RESTORATION-PLAN.json')
assert len(restoration['paths']) == 50
proposal = ROOT / 'artifacts/css-registered-admission-preparation-head-proposal-v3'
assert sha(proposal / 'FILES.json') == '5947882b4b33f46edad51db0a80b522011a90294bdab9288348fc3f09a4e86d1'
roles = read(proposal / 'COMBINED-SOURCE-ROLES.json')
native_pins = {name: pin['sha256'] for name, pin in roles['candidate'].items()}
assert set(native_pins) == {'servo/components/style/custom_properties.rs',
                            'servo/components/style/properties/cascade.rs'}
for name, pin in native_pins.items():
    assert sha(ROOT / roles['candidate'][name]['capture']) == pin
    assert roles['base'][name]['sha256'] == restoration['paths'][name]['head_original']
assert epoch['registered_number_transition'] == {
    'accepted': False, 'compiled': True, 'last_phase': 'head-candidate-build-2',
    'role': 'candidate', 'variant': 'committed-head'}
assert set(epoch['modified_native_paths']) == set(native_pins)
role_bytes = (RUNTIME / 'ROLE.json').read_bytes()
owned_bytes = (RUNTIME / 'OWNED.json').read_bytes()
role = json.loads(role_bytes)
assert role['role'] == 'candidate' and role['variant'] == 'committed-head' and role['built']
assert role['paired_head'] == 'e2839ec561c1e19de963bd0d56f46f4c067685d0'
assert role['last_build'] == 'head-candidate-build-2'

def verify_native():
    assert set(git('diff', '--name-only').decode().splitlines()) == set(native_pins)
    assert not git('diff', '--cached', '--name-only')
    for name, pin in restoration['paths'].items():
        source = ROOT / name
        parked = RUNTIME / 'prototype-original' / name
        assert source.is_file() and not source.is_symlink()
        assert parked.is_file() and not parked.is_symlink()
        assert sha(source) == native_pins.get(name, pin['head_original']), name
        assert hashlib.sha256(git('show', 'HEAD:' + name)).hexdigest() == pin['head_original'], name
        assert sha(parked) == pin['prototype_original'], name
    assert (RUNTIME / 'ROLE.json').read_bytes() == role_bytes
    assert (RUNTIME / 'OWNED.json').read_bytes() == owned_bytes

verify_native()
v14_dir = ROOT / 'artifacts/css-local-signing-20261027-v14'
v15_dir = ROOT / 'artifacts/css-local-signing-20261027-v15'
v14 = read(v14_dir / 'ROADMAP-UPDATE.json')
v15 = read(v15_dir / 'ROADMAP-UPDATE.json')
v16_dir = ROOT / 'artifacts/css-local-signing-20261027-v16'
v16 = read(v16_dir / 'ROADMAP-UPDATE.json')
source_pins = read(ROOT / 'artifacts/css-unfinished-work-checkpoint-20261027-v8/SOURCE-PINS.json')
ledger_paths = {'artifacts/stylo-bloom-tools/CURRENT-COMMITS.json',
                'artifacts/stylo-bloom-tools/PLAN-OF-RECORD.md'}
assert len(source_pins) == 140
for update in [v14, v15, v16]:
    assert set(update['before']) == set(update['after']) == ledger_paths
assert v14['after'] == v15['before']
assert v15['after'] == v16['before']
for name, pin in source_pins.items():
    if name in ledger_paths:
        assert pin == v14['before'][name]
        assert sha(v14_dir / 'ledger-preimages' / Path(name).name) == pin
        assert sha(v15_dir / 'ledger-preimages' / Path(name).name) == v15['before'][name]
        assert sha(v16_dir / 'ledger-preimages' / Path(name).name) == v16['before'][name]
        assert sha(ROOT / name) == v16['after'][name]
        assert hashlib.sha256(git('show', 'HEAD:' + name)).hexdigest() == v16['after'][name]
    else:
        source = RUNTIME / 'prototype-original' / name if name in restoration['paths'] else ROOT / name
        assert sha(source) == pin, name

evidence_pins = {'artifacts/css-registered-number-wpt-runtime-candidate-2/ASSESSMENT.json': 'b1ce69e398ec8ae9f603747636a62c665818b6643ba2147d4c29567196549b31', 'artifacts/css-registered-number-wpt-runtime-candidate-2/RESULT.json': 'f6552b414ebb305d5ad085ad63bdbffc3e9902bfc0d126cdf85f06423f132d78', 'artifacts/css-registered-admission-sign-runtime-candidate-1/RESULT.json': 'ea0cdb91212ce5c4f365024ed174a9545793ae3e7bb1504dbb0b606ab436ed0f', 'artifacts/css-registered-admission-zoom-runtime-candidate-1/RESULT.json': '4e388b2b62cd83024dd9273252ee68260e0769bd407c8c2db8a4c81bf8bc3eb0'}
for name, pin in evidence_pins.items():
    assert sha(ROOT / name) == pin, name
wpt = read(ROOT / 'artifacts/css-registered-number-wpt-runtime-candidate-2/ASSESSMENT.json')
assert wpt['complete'] and wpt['execution_preserved'] and wpt['comparison_gate_passed']
assert not wpt['errors'] and not wpt['comparison_errors']
sign = read(ROOT / 'artifacts/css-registered-admission-sign-runtime-candidate-1/RESULT.json')
zoom = read(ROOT / 'artifacts/css-registered-admission-zoom-runtime-candidate-1/RESULT.json')
for observed in [sign, zoom]:
    assert observed['complete'] and observed['execution_preserved']
    assert observed['error'] is None and observed['preservation_error'] is None
assert sign['comparison']['unchanged'] and sign['comparison']['changed_cases'] == 0
assert len(sign['summary']['rows']) == 24
assert sum(len(row['snapshots']) for row in sign['summary']['rows']) == 48
assert not zoom['comparison']['unchanged'] and zoom['comparison']['changed_cases'] == 8
assert not os.path.lexists(ROOT / 'testing/web-platform/tests/css/css-properties-values-api/registered-numeric-selected-dependencies.html')

ledger_name = 'artifacts/stylo-bloom-tools/CURRENT-COMMITS.json'
plan_name = 'artifacts/stylo-bloom-tools/PLAN-OF-RECORD.md'
(HERE / 'ledger-preimages').mkdir()
old_pins = {}
for name in [ledger_name, plan_name]:
    old_pins[name] = sha(ROOT / name)
    assert any(epoch[key].get(name) == old_pins[name] for key in
               ['pins', 'staged_working', 'committed_research_working_payloads'])
    (HERE / 'ledger-preimages' / Path(name).name).write_bytes((ROOT / name).read_bytes())
ledger = read(ROOT / ledger_name)
assert ledger['committed_native_fixes'] == 137
ledger.setdefault('research_signing_history', []).append(copy.deepcopy(ledger['latest_research_signing']))
ledger.setdefault('verified_working_epoch_history', []).append(copy.deepcopy(ledger['latest_verified_working_epoch']))
ledger['latest_research_signing'] = {
    'status': 'SIGNED_VERIFIED_LOCAL',
    'commits': {name: value['commit'] for name, value in receipts.items()},
    'directory': str(HERE.relative_to(ROOT)),
}
ledger['latest_verified_working_epoch'] = {
    'path': 'artifacts/css-registered-number-native-runtime-v1/CURRENT-EPOCH.json',
    'status': 'Two-file admission candidate compiled; WPT and sign comparisons passed; held for newly observed zoom CSSOM regression',
    'prototype_overlay_installed': False,
    'restoration_plan': 'artifacts/css-registered-number-native-runtime-v1/RESTORATION-PLAN.json',
    'baseline_build_complete': True,
    'candidate_build_complete': True,
    'candidate_applied': True,
    'candidate_accepted': False,
    'dirty_native_source_pins': native_pins,
    'runner_head_rebind_required': True,
}
ledger['latest_registered_number_research'].update({
    'status': 'HELD_FOR_ZOOM_CSSOM_REGRESSION_AFTER_WPT_AND_SIGN_PASS',
    'implementation_commit': ledger['latest_registered_number_research']['implementation_commit'],
    'validation_commit': receipts['validation']['commit'],
    'zoom_research_commit': receipts['research']['commit'],
    'tests_commit': receipts['validation']['commit'],
    'head_proposal': 'artifacts/css-registered-admission-preparation-head-proposal-v3',
    'prototype_proposal': 'artifacts/css-registered-admission-preparation-proposal-v3',
    'baseline_readout': 'artifacts/css-registered-number-wpt-runtime-original-2',
    'original_wpt_targets_pass': 57,
    'original_wpt_targets_fail': 47,
    'original_wpt_regression_assertions_pass': 446,
    'original_wpt_reftests_pass': 6,
    'browser_comparison_executed': True,
    'browser_capsule': 'artifacts/css-registered-number-wpt-capsule-v5',
    'original_browser_capsule': 'artifacts/css-registered-number-wpt-capsule-v3',
    'browser_targets_prepared': 104,
    'held_scheduling_targets_prepared': 16,
    'candidate_native_validation_executed': True,
    'candidate_native_gtests_executed': False,
    'split_fixture': 'artifacts/css-registered-number-wpt-fixture-v3',
    'split_fixture_requires_new_capsule': False,
    'runner_head_rebind_required': True,
    'historical_frozen_head': 'b7583cb3a5908bc26deaf5bedab242c4c8fd8633',
    'candidate_build_complete': True,
    'candidate_applied': True,
    'candidate_accepted': False,
    'candidate_wpt_targets_pass': 104,
    'observed_wpt_repairs': 47,
    'held_scheduling_signatures_unchanged': 16,
    'candidate_regression_assertions_pass': 446,
    'candidate_reftests_pass': 6,
    'sign_cases_unchanged': 24,
    'sign_snapshots_unchanged': 48,
    'zoom_cases_changed': 8,
    'zoom_acceptance_blocker': 'At zoom2 ready-unused-em/fixed-font CSSOM custom value becomes2.5px instead of5px although layout width is corrected to5px.',
    'candidate_observation': 'artifacts/css-registered-number-wpt-runtime-candidate-2',
    'zoom_observation': 'artifacts/css-registered-admission-zoom-runtime-candidate-1',
    'zoom_review': 'artifacts/css-registered-admission-zoom-candidate-review-v1',
    'structural_model': 'artifacts/css-registered-zoom-structural-model-v1',
    'structural_root_replay': 'artifacts/css-registered-zoom-structural-root-replay-v1',
    'wpt_installation': 'HELD; canonical A WPT remains absent',
    'source_transition': 'artifacts/css-registered-number-source-transition-v4',
    'pending_validation': 'artifacts/css-registered-number-pending-validation-v2',
    'original_held_scheduling_failures': 16,
    'candidate_build': 'artifacts/css-registered-number-native-runtime-v1/head-candidate-build-2',
    'original_observation': 'artifacts/css-registered-number-wpt-runtime-original-2',
    'scheduling_workstream': 'Separate pending repair; not accepted or discarded',
    'accepted_fix_increment': 0,
    'canonical_coverage_increment': 0,
})
(ROOT / ledger_name).write_text(json.dumps(ledger, indent=2, ensure_ascii=False) + '\n')
title, previous, rest = (ROOT / plan_name).read_text().split('\n\n', 2)
paragraph = (
    'Next: repair and validate the registered-value zoom representation boundary before '
    'publishing the admission fix. The installed two-file candidate v3 remains compiled '
    'but unaccepted. Its expanded WPT comparison passed all 104 A assertions, repairing '
    '47 original failures, while preserving all 16 held B signatures, 446 existing '
    'assertions and six reftests. The sign observer preserved all 24 cases/48 snapshots. '
    'The zoom observer changed eight cases and exposed a new fixed-font CSSOM regression: '
    'at zoom 2, the ready-unused-em custom value reads 2.5px rather than 5px even though '
    'the ordinary layout width is corrected to 5px. This blocks installation/publication '
    'and acceptance; the successful WPT comparison alone is insufficient. Audit all '
    'typed-value producers and length-bearing representations, preserve percentages and '
    'non-length fields, and validate a revised native normalization repair with focused '
    'zoom WPTs plus the full A/B/regression and sign gates. The new structural Lean model '
    'and independent replay passed six conditional theorems, six examples and three '
    'negative controls; float behavior, matrix conventions and producer completeness '
    'remain native obligations. The draft zoom tests and disabled A-WPT installer are '
    'research only, with no new browser validation or lint claim. Direct numeric scheduling '
    'remains pending repair B; self-font numeric defaulting remains unresolved. After '
    'the standalone repair passes all gates, commit its minimal native/WPT change with '
    'preceding research, then restore the 50 parked prototypes and validate pending-demand '
    'integration. Existing runners bind historical HEAD b7583cb3a590 and require an '
    'authenticated successor relation before reuse. Accepted fixes remain 137; no native '
    'refinement or canonical coverage credit is added. Continue Bloom milestones after '
    'these gates.'
)
(ROOT / plan_name).write_text(title + '\n\n' + paragraph + '\n\n' + rest)
current = copy.deepcopy(epoch)
for name in old_pins:
    for key in ['pins', 'staged_working', 'committed_research_working_payloads']:
        if name in current[key]:
            current[key][name] = sha(ROOT / name)
state = s.h.index_state(ROOT, ENV)
current['semantic_index'] = s.h.semantic_index(state)
current['raw_index_observation']['current'] = state['raw_index']
s.a.verify_current(s.h, ROOT, ENV, current)
epoch_path.write_text(json.dumps(current, indent=2, sort_keys=True) + '\n')
save(HERE / 'ROADMAP-UPDATE.json', {
    'before': old_pins, 'after': {name: sha(ROOT / name) for name in old_pins},
    'accepted_fixes': 137, 'recovery_source_pins_verified': len(source_pins),
    'tracked_native_prototype_bodies_preserved': len(restoration['paths']),
    'native_head_blobs_unchanged_by_research_commits': True,
    'prior_authorized_ledger_update': 'artifacts/css-local-signing-20261027-v16/ROADMAP-UPDATE.json',
    'dirty_native_source_pins': native_pins,
    'candidate_compiled': True,
    'candidate_comparison_complete': True,
    'runner_head_rebind_required': True,
})
save(HERE / 'PRE-CHECKPOINT-EPOCH.json', current)
save(HERE / 'OWNED-SNAPSHOT.json', read(RUNTIME / 'OWNED.json'))
save(HERE / 'ROLE-SNAPSHOT.json', read(RUNTIME / 'ROLE.json'))
lines = ['# Registered admission research checkpoint', '', '| Commit | Work |', '| --- | --- |']
for name, value in receipts.items():
    lines.append('| ' + value['commit'] + ' | ' + name + ' |')
lines += ['', paragraph, '',
          'The nested CSS Lean repository is unchanged. The exact two candidate native files remain dirty and are also captured under signed artifacts; they are compiled but unaccepted. Build outputs remain local for reuse. The paired browser evidence binds original HEAD e2839ec561c1 and candidate HEAD b7583cb3a590; later runners must explicitly rebind the current HEAD while preserving those immutable results. No pushes or CI submissions were made.', '',
          'Untracked prototype companions and WPTs remain in the working tree and are also preserved by the earlier signed unfinished-work checkpoint. This commit records a checkpoint, not an accepted implementation fix.']
(HERE / 'CHECKPOINT.md').write_text('\n'.join(lines) + '\n')
pins = {}
for path in sorted(HERE.rglob('*')):
    if path.is_file() and path.name not in {'CURRENT-EPOCH.json', 'finish-driver.log', 'checkpoint-driver.log'}:
        pins[str(path.relative_to(ROOT))] = sha(path)
for name in old_pins:
    pins[name] = sha(ROOT / name)
save(HERE / 'checkpoint-selection.json', {
    'id': 'checkpoint',
    'message': 'No bug - Checkpoint admission comparisons held for the zoom regression. r?#firefox-style-system-reviewers',
    'files': sorted(pins), 'source_pins': pins,
})
with (HERE / 'checkpoint-driver.log').open('x') as stream:
    subprocess.run([sys.executable, '-I', '-S', '-B', str(HERE / 'commit.py'),
                    str(HERE / 'checkpoint-selection.json')], cwd=ROOT, env=ENV,
                   stdout=stream, stderr=subprocess.STDOUT, check=True)
final = read(HERE / 'checkpoint-receipt.json')
assert final['signature_verified']
verify_native()
assert git('-C', 'artifacts/css-spec-lean', 'rev-parse', 'HEAD').decode().strip() == '162b20fb7c53a0ab89b20875a965baee98fb66bb'
for name, pin in pins.items():
    assert hashlib.sha256(git('show', 'HEAD:' + name)).hexdigest() == pin, name
current = read(epoch_path)
s.a.verify_current(s.h, ROOT, ENV, current)
(RUNTIME / 'CURRENT-EPOCH.json').write_bytes(epoch_path.read_bytes())
save(HERE / 'FINAL-CHECK.json', {
    'head': final['commit'],
    'commits': {name: value['commit'] for name, value in receipts.items()} | {'checkpoint': final['commit']},
    'signatures_verified': True, 'tracked_tree_clean': False, 'dirty_native_source_pins': native_pins, 'staging_empty': True,
    'unfinished_prototypes_preserved': True, 'accepted_fixes': 137,
    'canonical_coverage_increment': 0, 'current_epoch_sha256': sha(epoch_path),
    'runtime_epoch_synchronized': True, 'baseline_build_complete': True,
    'candidate_applied': True, 'candidate_build_complete': True,
    'candidate_comparison_complete': True, 'candidate_accepted': False,
    'acceptance_held_for_zoom_regression': True,
    'runner_head_rebind_required': True,
})
print((HERE / 'FINAL-CHECK.json').read_text(), flush=True)
