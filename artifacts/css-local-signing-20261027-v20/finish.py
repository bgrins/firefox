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
PREVIOUS = ROOT / 'artifacts/css-local-signing-20261027-v19'
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
epoch = read(HERE / 'CURRENT-EPOCH.json')
s.a.verify_current(s.h, ROOT, ENV, epoch)
previous = read(PREVIOUS / 'FINAL-CHECK.json')
inputs = read(HERE / 'CHECKPOINT-INPUTS.json')
late_research_files = [HERE / 'LATE-RESEARCH.json']
for directory, manifest_pin in read(HERE / 'LATE-RESEARCH.json').items():
    package = ROOT / directory
    assert directory.startswith('artifacts/') and '..' not in Path(directory).parts
    assert sha(package / 'FILES.json') == manifest_pin
    late_research_files.append(package / 'FILES.json')
    for name, record in read(package / 'FILES.json').items():
        assert not Path(name).is_absolute() and '..' not in Path(name).parts
        path = package / name
        assert not path.is_symlink() and sha(path) == record['sha256']
        late_research_files.append(path)
assert inputs['execution_enabled'] is True
assert inputs['research_status'] == 'EXPERIMENTAL_ZOOM_NORMALIZATION_VALIDATION_UNACCEPTED'
assert previous['head'] == inputs['frozen_head'] == '6eb538c23bcf3dde9c7631a1c826cba4de562462'
assert sha(RUNTIME / 'CURRENT-EPOCH.json') == inputs['runtime_epoch_sha256']
assert sha(RUNTIME / 'ROLE.json') == inputs['runtime_role_sha256']
assert sha(RUNTIME / 'OWNED.json') == inputs['runtime_owned_sha256']
initial = read(HERE / 'INITIAL-EPOCH.json')
assert initial['semantic_index']['head'] == previous['head']
assert initial['modified_native_paths'] == epoch['modified_native_paths']
assert len(epoch['modified_native_paths']) == 9
for path, pin in inputs['evidence_pins'].items():
    assert sha(ROOT / path) == pin
build_path = inputs['terminal_build_result']
assert build_path in inputs['evidence_pins']
build = read(ROOT / build_path)
assert not build['owned_processes'] and build['preservation_verified']
assert not build['publication_errors']
assert build['command_success'] is inputs['terminal_build_succeeded']
assert epoch['registered_number_transition']['compiled'] is inputs['terminal_build_succeeded']
assert epoch['registered_number_transition']['variant'] == inputs['candidate_variant']
assert epoch['registered_number_transition']['accepted'] is False
assert epoch['registered_number_transition']['last_phase'] == inputs['terminal_build_label']
assert build_path == 'artifacts/css-registered-number-native-runtime-v1/' + inputs['terminal_build_label'] + '/RESULT.json'
assert inputs['candidate_browser_comparison']['accepted'] is False
comparison_root = 'artifacts/css-registered-zoom-wpt-calibration-runtime-zoom-normalization-1/'
for name in ['RESULT.json', 'ASSESSMENT.json', 'COMPARISON.json', 'CLEANUP.json']:
    assert comparison_root + name in inputs['evidence_pins']
observed = read(ROOT / comparison_root / 'ASSESSMENT.json')
comparison = read(ROOT / comparison_root / 'COMPARISON.json')
cleanup = read(ROOT / comparison_root / 'CLEANUP.json')
assert observed['complete'] and observed['execution_preserved']
assert not observed['errors'] and not observed['infrastructure_faults']
assert not observed['comparison_errors']
assert observed['observed_subtest_count'] == len(observed['rows']) == 56
assert all(row['status'] == 'PASS' for row in observed['rows'])
assert comparison['complete_comparison'] and not comparison['native_fix_acceptance']
assert comparison['counts'] == {
    'repaired': 50, 'unchanged_pass': 6, 'changed_fail': 0,
    'new_failures': 0, 'unchanged_fail': 0,
}
assert cleanup['owned_group_absent'] and cleanup['temporary_root_removed']
assert 'PENDING' not in inputs['summary']
proposal = ROOT / inputs['proposal']
assert inputs['proposal'] == 'artifacts/css-registered-zoom-normalization-proposal-v3'
assert inputs['proposal_manifest_sha256'] == '8aa5594696044026109666bf7a493520fba9fb88e34cfb4aec0c923d319c82ef'
assert inputs['candidate_variant'] == 'zoom-normalization-v3'
assert inputs['terminal_build_label'] == 'zoom-normalization-build-2'
assert sha(proposal / 'FILES.json') == inputs['proposal_manifest_sha256']
for name, pin in read(proposal / 'FILES.json').items():
    assert sha(proposal / name) == pin['sha256']
roles = read(proposal / 'SOURCE-ROLES.json')
assert len(roles) == 7
for path, record in roles.items():
    assert sha(ROOT / record['base']) == record['base_sha256']
    assert sha(ROOT / record['candidate']) == record['candidate_sha256']
    assert hashlib.sha256(git('show', 'HEAD:' + path)).hexdigest() == record['base_sha256']
parent = previous['head']
receipts = {}
for name in ['research', 'validation']:
    receipt = read(HERE / (name + '-receipt.json'))
    assert receipt['parent'] == parent and receipt['signature_verified']
    assert all(path.startswith('artifacts/') for path in receipt['files'])
    parent = receipt['commit']
    receipts[name] = receipt
assert parent == epoch['semantic_index']['head'] == git('rev-parse', 'HEAD').decode().strip()
selected = {}
for name in receipts:
    selection = read(HERE / (name + '-selection.json'))
    assert set(selection['files']) == set(receipts[name]['files'])
    selected.update(selection['source_pins'])
historical = read(PREVIOUS / 'CHECKPOINT-INPUTS.json')['evidence_pins']
historical[str((proposal / 'FILES.json').relative_to(ROOT))] = inputs['proposal_manifest_sha256']
for path, pin in inputs['evidence_pins'].items():
    if selected.get(path) == pin:
        continue
    assert historical.get(path) == pin
    assert hashlib.sha256(git('show', previous['head'] + ':' + path)).hexdigest() == pin
assert hashlib.sha256(git('show', previous['head'] + ':' + str((proposal / 'FILES.json').relative_to(ROOT)))).hexdigest() == inputs['proposal_manifest_sha256']
native = previous['dirty_native_source_pins'] | {path: record['candidate_sha256'] for path, record in roles.items()}
assert len(native) == 9
assert set(git('diff', '--name-only').decode().splitlines()) == set(native)
assert not git('diff', '--cached', '--name-only')
for path, pin in native.items():
    assert sha(ROOT / path) == pin
assert not git('diff', previous['head'], parent, '--', 'servo', 'layout', 'dom', 'testing')
restoration = read(RUNTIME / 'RESTORATION-PLAN.json')['paths']
assert len(restoration) == 50
for path, pins in restoration.items():
    assert sha(RUNTIME / 'prototype-original' / path) == pins['prototype_original']
    assert sha(ROOT / path) == native.get(path, pins['head_original'])
    assert hashlib.sha256(git('show', 'HEAD:' + path)).hexdigest() == pins['head_original']
ledger_names = ['artifacts/stylo-bloom-tools/CURRENT-COMMITS.json',
                'artifacts/stylo-bloom-tools/PLAN-OF-RECORD.md']
recovery = read(ROOT / 'artifacts/css-unfinished-work-checkpoint-20261027-v8/SOURCE-PINS.json')
assert len(recovery) == 140
untracked = git('ls-files', '--others', '--exclude-standard', 'dom/animation',
                'layout/style/test/gtest', 'servo/components/style',
                'testing/web-platform/tests/css').decode().splitlines()
assert all(path in recovery for path in untracked)
assert len(untracked) == previous['untracked_project_files_in_signed_recovery'] == 74
for path, pin in recovery.items():
    if path in ledger_names:
        assert sha(ROOT / path) == read(PREVIOUS / 'ROADMAP-UPDATE.json')['after'][path]
    else:
        source = (RUNTIME / 'prototype-original' / path if path in restoration else
                  ROOT / roles[path]['base'] if path in roles else ROOT / path)
        assert sha(source) == pin, path

def evidence(directory, name):
    path = directory + '/' + name
    assert inputs['evidence_pins'].get(path) == sha(ROOT / path)
    return read(ROOT / path)

assert set(inputs['new_observations']) == {'container', 'broad', 'focused'}
observation_summaries = {}
for kind, item in inputs['new_observations'].items():
    assert item['executed'] is True
    directory = item['directory']
    result = evidence(directory, 'RESULT.json')
    cleanup = evidence(directory, 'CLEANUP.json')
    assert cleanup['owned_group_absent']
    assert not result['native_fix_acceptance']
    assert evidence(directory, 'PRE.json') == evidence(directory, 'POST.json')
    saved_epoch = evidence(directory, 'EPOCH.json')
    assert saved_epoch['semantic_index']['head'] == previous['head']
    assert all(saved_epoch['pins'].get(path) == pin for path, pin in native.items())
    if kind == 'container':
        assert result['complete'] and result['execution_preserved']
        assert cleanup['profile_removed'] and cleanup['server_thread_stopped']
        assert result['native_sources'] == native
        assert result['normative_verdict'] == 'not evaluated'
        observation_summaries[kind] = {
            'directory': directory, 'complete': True, 'execution_preserved': True,
            'changed_cases': result['comparison']['changed_cases'],
            'changed_sequences': result['comparison']['changed_sequences'],
            'normative_verdict': 'INCONCLUSIVE', 'accepted': False,
        }
    else:
        assessment = evidence(directory, 'ASSESSMENT.json')
        assert assessment['complete'] and assessment['execution_preserved']
        assert assessment['native_sources'] == native
        assert cleanup['temporary_root_removed']
        assert not assessment['errors'] and not assessment['infrastructure_faults']
        rows = assessment['rows']
        assert assessment['observed_subtest_count'] == len(rows) == (566 if kind == 'broad' else 14)
        observation_summaries[kind] = {
            'directory': directory, 'complete': True, 'execution_preserved': True,
            'subtests': len(rows), 'pass': sum(row['status'] == 'PASS' for row in rows),
            'fail': sum(row['status'] == 'FAIL' for row in rows), 'accepted': False,
            'comparison_gate_passed': result['comparison_gate_passed'],
        }
        if kind == 'focused':
            assert result['observation_gate_passed'] and not assessment['comparison_errors']
            assert all(row['status'] == 'PASS' for row in rows)
            assert inputs['focused_capsule'] == 'artifacts/css-registered-zoom-extra-wpt-observation-v1'
            capsule = ROOT / inputs['focused_capsule']
            assert sha(capsule / 'FILES.json') == inputs['focused_capsule_manifest_sha256'] == assessment['capsule_manifest_sha256']
            policy = read(capsule / 'POLICY.json')
            assert {test:len(names) for test,names in policy['target_subtests'].items()} == {
                '/css/css-properties-values-api/registered-animation-length-zoom.html': 6,
                '/css/css-properties-values-api/registered-numeric-style-range-zoom.html': 8,
            }
            expected_names = {(test,name) for test,names in policy['target_subtests'].items() for name in names}
            assert {(row['test'],row['subtest']) for row in rows} == expected_names
            observation_summaries[kind].update(animation_pass=6, numeric_style_query_pass=8)
        if kind == 'broad':
            assert result['comparison_gate_passed'] and assessment['comparison_gate_passed']
            assert not assessment['comparison_errors']
            assert observation_summaries[kind]['pass'] == 550 and observation_summaries[kind]['fail'] == 16
            policy = read(ROOT / 'artifacts/css-registered-zoom-broad-wpt-v1/POLICY.json')
            for category, count, status in [('target_subtests',104,'PASS'),('held_subtests',16,'FAIL'),('regression_subtests',446,'PASS')]:
                grouped = [row for row in rows if row['test'] in policy[category]]
                assert len(grouped) == count and all(row['status'] == status for row in grouped)
            refs = [end for end in assessment['ends'] if policy['tests'][end['test']] == 'reftest']
            assert len(refs) == 6 and all(end['status'] == 'PASS' for end in refs)
            observation_summaries[kind].update(target_pass=104, held_unchanged_fail=16, regression_pass=446, reftest_pass=6)

(HERE / 'ledger-preimages').mkdir()
before = {}
for name in ledger_names:
    before[name] = sha(ROOT / name)
    (HERE / 'ledger-preimages' / Path(name).name).write_bytes((ROOT / name).read_bytes())
ledger = read(ROOT / ledger_names[0])
assert ledger['committed_native_fixes'] == 137
ledger.setdefault('research_signing_history', []).append(copy.deepcopy(ledger['latest_research_signing']))
ledger['latest_research_signing'] = {
    'status': 'SIGNED_VERIFIED_LOCAL',
    'commits': {name: value['commit'] for name, value in receipts.items()},
    'directory': str(HERE.relative_to(ROOT)),
}
ledger.setdefault('verified_working_epoch_history', []).append(
    copy.deepcopy(ledger['latest_verified_working_epoch']))
ledger['latest_verified_working_epoch'] = {
    'path': 'artifacts/css-registered-number-native-runtime-v1/CURRENT-EPOCH.json',
    'status': inputs['summary'],
    'prototype_overlay_installed': False,
    'restoration_plan': 'artifacts/css-registered-number-native-runtime-v1/RESTORATION-PLAN.json',
    'candidate_applied': True,
    'candidate_build_complete': inputs['terminal_build_succeeded'],
    'candidate_accepted': False,
    'candidate_variant': inputs['candidate_variant'],
    'proposal': inputs['proposal'],
    'dirty_native_source_pins': native,
    'runner_head_rebind_required': True,
}
ledger.setdefault('registered_number_research_history', []).append(
    copy.deepcopy(ledger['latest_registered_number_research']))
research = ledger['latest_registered_number_research']
research.update({
    'status': inputs['research_status'], 'candidate_accepted': False,
    'normalization_proposal': inputs['proposal'],
    'browser_capsule': 'artifacts/css-registered-zoom-broad-wpt-v1',
    'candidate_build': 'artifacts/css-registered-number-native-runtime-v1/zoom-normalization-build-2',
    'candidate_observation': inputs['new_observations']['broad']['directory'],
    'candidate_wpt_targets_pass': 104, 'observed_wpt_repairs': 47,
    'held_scheduling_signatures_unchanged': 16,
    'candidate_regression_assertions_pass': 446, 'candidate_reftests_pass': 6,
    'historical_frozen_head': previous['head'], 'runner_head_rebind_required': True,
    'zoom_acceptance_blocker': 'The historical 56-test zoom failures are repaired by the experimental candidate; full native acceptance remains withheld. Container coordinate normative trace is INCONCLUSIVE; writing-mode scheduling is separate unaccepted work.',
    'wpt_installation': 'Canonical A WPT remains absent; no native publication or acceptance.',
    'latest_normalization_observations': observation_summaries,
})
research['zoom_quantization_research'] = {
    'model': 'artifacts/css-zoom-quantization-model-v1',
    'independent_replay': 'artifacts/css-zoom-quantization-independent-replay-v1',
    'kernel_checked_named_theorems': 10,
    'rejected_false_controls': 5,
    'assumptions': ['signed rational lengths', 'positive rational zoom',
                    'exact arithmetic', 'truncation toward zero to 60 app units per CSS pixel'],
    'ieee_floating_point_modeled': False,
    'native_refinement_proved': False,
    'container_producer_correspondence_proved': False,
    'canonical_coverage_increment': 0,
}
research['writing_mode_followup'] = {
    'status': 'V3_PREPARED_PENDING_BROWSER_VALIDATION',
    'proposal': 'artifacts/css-registered-logical-unit-writing-mode-repair-proposal-v3',
    'prepared_wpt_tests': 36,
    'proposal_compiled': False,
    'proposal_browser_executed': False,
    'baseline_tests': 16, 'baseline_failures': 16,
    'synthetic_line_height_edge_removed': True,
    'remaining_boundaries': ['genuine writing-mode SCC policy', 'early application through existing line-height scheduling'],
    'candidate_accepted': False,
    'historical_v2_blocker': 'Composite-bit iteration can panic; do not apply v2 as-is.',
    'independent_review': 'artifacts/css-registered-writing-mode-independent-review-v1',
    'independent_review_scope': 'v2 only; v3 independent review remains pending',
    'v3_flag_order_corrected': True,
    'isolated_rust_masks_checked': 512,
    'isolated_rust_probe': 'artifacts/css-registered-logical-unit-writing-mode-repair-proposal-v3/BITFLAGS-PROBE.json',
    'root_isolated_replay': str(HERE.relative_to(ROOT)) + '/ROOT-BITFLAGS-REPLAY.json',
}
for historical_key in ['sign_cases_unchanged', 'sign_snapshots_unchanged', 'zoom_cases_changed']:
    research.pop(historical_key, None)
ledger['latest_registered_number_research']['zoom_followup_checkpoint'] = {
    'status': 'EXPERIMENTAL_UNACCEPTED',
    'proposal': inputs['proposal'],
    'proposal_manifest_sha256': inputs['proposal_manifest_sha256'],
    'admission_only_zoom_calibration': {'tests': 56, 'pass': 6, 'fail': 50},
    'logical_unit_baseline': {'tests': 16, 'pass': 0, 'fail': 16,
                              'status': 'CONFIRMED_LEAD_NO_ACCEPTED_FIX'},
    'container_observation': {'scenarios': 42, 'initial_targets': 94,
                              'mutation_sequences': 3, 'mutation_targets': 30,
                              'normative_parity_claim': False},
    'terminal_build_result': build_path,
    'native_compilation_succeeded': inputs['terminal_build_succeeded'],
    'candidate_browser_comparison': inputs['candidate_browser_comparison'],
    'new_observations': observation_summaries,
    'native_source_paths_preserved_dirty': 9,
    'runner_head_rebind_required': True,
    'accepted_fix_increment': 0,
    'canonical_coverage_increment': 0,
}
(ROOT / ledger_names[0]).write_text(json.dumps(ledger, indent=2, ensure_ascii=False) + '\n')
title, rest = (ROOT / ledger_names[1]).read_text().split('\n\n', 1)
paragraph = (
    'Signing checkpoint: the experimental nine-file normalization candidate retains its successful '
    '56-test zoom comparison and now passes all 104 admission assertions, 446 regression assertions '
    'and six reftests while preserving all 16 held scheduling failures exactly. The container '
    'candidate observation completed, but its measured coordinate predictions are not normative '
    'passes: the fresh published-algorithm trace remains INCONCLUSIVE. ' + inputs['summary'] + ' '
    'The logical writing-mode lead remains separate and unaccepted; its revised proposal removes '
    'the synthetic line-height edge but still needs genuine-cycle and early-application analysis. '
    'All nine native edits, 50 parked prototype bodies and 140 recovery pins remain preserved. '
    'Frozen runners require explicit successor binding after signing. No native fix or canonical '
    'formal coverage is accepted; the accepted fix count remains 137.'
)
(ROOT / ledger_names[1]).write_text(title + '\n\n' + paragraph + '\n\n' + rest)
current = copy.deepcopy(epoch)
for name in ledger_names:
    for key in ['pins', 'staged_working', 'committed_research_working_payloads']:
        if name in current[key]:
            assert current[key][name] == before[name]
            current[key][name] = sha(ROOT / name)
state = s.h.index_state(ROOT, ENV)
current['semantic_index'] = s.h.semantic_index(state)
current['raw_index_observation']['current'] = state['raw_index']
s.a.verify_current(s.h, ROOT, ENV, current)
(HERE / 'CURRENT-EPOCH.json').write_text(json.dumps(current, indent=2, sort_keys=True) + '\n')
save(HERE / 'ROADMAP-UPDATE.json', {
    'before': before, 'after': {name: sha(ROOT / name) for name in ledger_names},
    'prior_authorized_ledger_update': str((PREVIOUS / 'ROADMAP-UPDATE.json').relative_to(ROOT)),
    'accepted_fixes': 137, 'recovery_source_pins_verified': 140,
    'untracked_project_files_in_signed_recovery': len(untracked),
    'tracked_native_prototype_bodies_preserved': 50,
    'dirty_native_source_pins': native,
})
save(HERE / 'PRE-CHECKPOINT-EPOCH.json', current)
save(HERE / 'PREVIOUS-FINAL-CHECK.json', previous)
rows = ['# Local signing checkpoint', '', '| Commit | Work |', '| --- | --- |']
rows += ['| ' + value['commit'] + ' | ' + name + ' |' for name, value in receipts.items()]
rows += ['', paragraph, '',
         'The nine live native edits remain dirty and preserved in signed proposal artifacts. '
         'All 50 parked prototype bodies and the 140-entry recovery inventory were checked. '
         'The nested Lean repository and browser binaries are preserved. No push or CI submission occurred.']
(HERE / 'CHECKPOINT.md').write_text('\n'.join(rows) + '\n')
files = [HERE / name for name in ['commit.py', 'finish.py', 'INITIAL-EPOCH.json',
         'BEFORE.json', 'PRE-CHECKPOINT-EPOCH.json', 'PREVIOUS-FINAL-CHECK.json',
         'ROADMAP-UPDATE.json', 'CHECKPOINT.md', 'CHECKPOINT-INPUTS.json', 'INVENTORY.json', 'PLAN.md',
         'ROOT-BITFLAGS-REPLAY.json', 'ROOT-BITFLAGS-REPLAY.log']]
files += list((HERE / 'ledger-preimages').iterdir())
files += late_research_files
for name in receipts:
    files += [HERE / (name + suffix) for suffix in
              ['-selection.json', '-receipt.json', '-signature.log']]
files += [ROOT / name for name in ledger_names]
pins = {str(path.relative_to(ROOT)): sha(path) for path in files}
save(HERE / 'checkpoint-selection.json', {
    'id': 'checkpoint',
    'message': 'No bug - Checkpoint experimental zoom regression results and open semantics. r?#firefox-style-system-reviewers',
    'files': sorted(pins), 'source_pins': pins,
})
with (HERE / 'checkpoint-driver.log').open('x') as stream:
    subprocess.run([sys.executable, '-I', '-S', '-B', str(HERE / 'commit.py'),
                    str(HERE / 'checkpoint-selection.json')], cwd=ROOT, env=ENV,
                   stdout=stream, stderr=subprocess.STDOUT, check=True)
final = read(HERE / 'checkpoint-receipt.json')
assert final['signature_verified'] and final['parent'] == parent
current = read(HERE / 'CURRENT-EPOCH.json')
s.a.verify_current(s.h, ROOT, ENV, current)
assert not git('diff', '--cached', '--name-only')
assert set(git('diff', '--name-only').decode().splitlines()) == set(native)
for path, pin in native.items():
    assert sha(ROOT / path) == pin
for path, pin in pins.items():
    assert hashlib.sha256(git('show', 'HEAD:' + path)).hexdigest() == pin
assert git('-C', 'artifacts/css-spec-lean', 'rev-parse', 'HEAD').decode().strip() == '162b20fb7c53a0ab89b20875a965baee98fb66bb'
assert sha(RUNTIME / 'ROLE.json') == inputs['runtime_role_sha256']
assert sha(RUNTIME / 'OWNED.json') == inputs['runtime_owned_sha256']
assert sha(RUNTIME / 'CURRENT-EPOCH.json') == inputs['runtime_epoch_sha256']
(RUNTIME / 'CURRENT-EPOCH.json').write_bytes((HERE / 'CURRENT-EPOCH.json').read_bytes())
save(HERE / 'FINAL-CHECK.json', {
    'head': final['commit'],
    'commits': {name: value['commit'] for name, value in receipts.items()} | {'checkpoint': final['commit']},
    'signatures_verified': True, 'staging_empty': True, 'tracked_tree_clean': False,
    'dirty_native_source_pins': native, 'unfinished_prototypes_preserved': True,
    'untracked_project_files_in_signed_recovery': len(untracked),
    'accepted_fixes': 137, 'canonical_coverage_increment': 0,
    'current_epoch_sha256': sha(RUNTIME / 'CURRENT-EPOCH.json'),
    'runtime_epoch_synchronized': True, 'candidate_accepted': False,
    'normalization_experimental_unaccepted': True, 'logical_unit_lead_accepted': False,
    'terminal_build_succeeded': inputs['terminal_build_succeeded'],
    'runner_head_rebind_required': True,
})
print((HERE / 'FINAL-CHECK.json').read_text(), flush=True)
