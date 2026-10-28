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
PREVIOUS = ROOT / 'artifacts/css-local-signing-20261027-v21'
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
assert previous['head'] == 'd6243f35307b62a4a4f6067367d78c948d3f468c'
inputs = read(HERE / 'INPUTS.json')
assert inputs['ready'] is True
retry_adoption = read(HERE / 'research-retry-adoption.json')
successful_log_name = retry_adoption['successful_retry_log']
assert Path(successful_log_name).name == successful_log_name
assert successful_log_name.startswith('research-retry-') and successful_log_name.endswith('-commit.log')
retry_number = successful_log_name.removeprefix('research-retry-').removesuffix('-commit.log')
assert retry_number.isdigit() and int(retry_number) >= 2
successful_log = HERE / successful_log_name
assert successful_log.is_file() and not successful_log.is_symlink()
assert sha(successful_log) == retry_adoption['successful_retry_log_sha256']
assert sha(HERE / 'research-commit.log') == retry_adoption['first_failed_log_sha256']
assert sha(HERE / 'research-retry-1-commit.log') == retry_adoption['prior_failed_retry_log_sha256']
assert previous['head'] == inputs['frozen_head']
assert sha(RUNTIME / 'CURRENT-EPOCH.json') == inputs['runtime_epoch_sha256']
assert sha(RUNTIME / 'ROLE.json') == inputs['role_sha256']
assert sha(RUNTIME / 'OWNED.json') == inputs['owned_sha256']
for directory, pin in inputs['packages'].items():
    package = ROOT / directory
    assert sha(package / 'FILES.json') == pin
    for name, item in read(package / 'FILES.json').items():
        assert sha(package / name) == (item['sha256'] if isinstance(item, dict) else item)
transition = ROOT / 'artifacts/css-registered-zoom-standalone-transition-v3'
assert read(transition / 'POLICY.json')['execution_enabled'] is True
assert read(transition / 'POLICY.json')['head'] == previous['head']
assert epoch['registered_number_transition'] == {
    'role': 'candidate', 'variant': 'zoom-standalone-v1', 'compiled': True,
    'accepted': False, 'last_phase': 'zoom-standalone-candidate-build-1',
}
for path, pin in inputs['evidence_pins'].items():
    assert sha(ROOT / path) == pin, path
original_dir = ROOT / inputs['original_runtime']
candidate_dir = ROOT / inputs['candidate_runtime']
assessments = {}
for role, directory in [('original', original_dir), ('candidate', candidate_dir)]:
    for filename in ['RESULT.json', 'ASSESSMENT.json', 'CLEANUP.json', 'PRE.json', 'POST.json', 'COMPARISON.json', 'EPOCH.json', 'APPLICATION-METADATA.json', 'APPLICATION-METADATA-POST.json']:
        assert str((directory / filename).relative_to(ROOT)) in inputs['evidence_pins']
    assessment = read(directory / 'ASSESSMENT.json')
    result = read(directory / 'RESULT.json')
    cleanup = read(directory / 'CLEANUP.json')
    assert assessment['complete'] and assessment['execution_preserved']
    assert not assessment['errors'] and not assessment['comparison_errors']
    assert result['execution_error'] is None and result['preservation_error'] is None
    assert result['complete_comparison']
    assert cleanup['owned_group_absent'] and cleanup['temporary_root_removed']
    assert len(assessment['rows']) == 636 and len(assessment['ends']) == 29
    assert sum(row['status'] == 'PASS' for row in assessment['ends']) == 6
    assert read(directory / 'PRE.json') == read(directory / 'POST.json')
    saved_epoch = read(directory / 'EPOCH.json')
    assert sha(directory / 'EPOCH.json') == assessment['epoch_sha256']
    assert assessment['run_binding'] == read(directory / 'APPLICATION-METADATA.json') == read(directory / 'APPLICATION-METADATA-POST.json')
    assert assessment['run_binding']['revision'] == previous['head'] == saved_epoch['semantic_index']['head']
    assert saved_epoch['registered_number_transition']['role'] == role
    assert saved_epoch['registered_number_transition']['variant'] == 'zoom-standalone-v1'
    assert saved_epoch['registered_number_transition']['compiled'] is True
    assessments[role] = assessment
comparison = read(candidate_dir / 'COMPARISON.json')
assert comparison['complete'] and len(comparison['rows']) == 665
assert read(candidate_dir / 'RESULT.json')['comparison_gate_passed'] == comparison['broad_regression_gate_passed']
assert comparison['summary'] == inputs['comparison_summary']
adjudication_dir = ROOT / inputs['port_adjudication']
assert sha(adjudication_dir / 'VERDICT.json') == inputs['port_verdict_sha256']
for path, pin in read(adjudication_dir / 'REFERENCES.json').items():
    assert sha(ROOT / path) == pin, path
assert (adjudication_dir / 'RAW-COMPARISON.json').read_bytes() == (candidate_dir / 'COMPARISON.json').read_bytes()
adjudicated = read(adjudication_dir / 'VERDICT.json')
assert adjudicated['adjudicated_broad_gate_passed'] is True
assert adjudicated['raw_wrapper_gate_remains_false'] is True
assert comparison['broad_regression_gate_passed'] is False
assert adjudicated['native_fix_acceptance'] is False and adjudicated['browser_rerun'] is False
assert adjudicated['subtests'] == comparison['summary']['subtests'] == {
    'broad:unchanged': 566, 'zoom70:repaired': 56, 'zoom70:unchanged': 14,
}
assert adjudicated['all_zoom70_pass'] is True and adjudicated['reftests_passed'] == 6

assert read(HERE / 'INITIAL-EPOCH.json')['semantic_index']['head'] == previous['head']
roles = read(ROOT / 'artifacts/css-registered-zoom-normalization-proposal-v3/SOURCE-ROLES.json')
assert len(roles) == 7
for name, role in roles.items():
    assert sha(ROOT / role['base']) == role['base_sha256']
parent = previous['head']
receipts = {}
for name in ['research', 'validation']:
    receipt = read(HERE / (name + '-receipt.json'))
    assert receipt['parent'] == parent and receipt['signature_verified']
    assert all(path.startswith('artifacts/') for path in receipt['files'])
    parent = receipt['commit']
    receipts[name] = receipt
assert parent == epoch['semantic_index']['head'] == git('rev-parse', 'HEAD').decode().strip()
assert retry_adoption['commit'] == receipts['research']['commit'] and retry_adoption['signature_verified']
native = inputs['dirty_native_source_pins']
assert len(native) == 7 and set(epoch['modified_native_paths']) == set(native)
assert native == {path: role['candidate_sha256'] for path, role in roles.items()}
for role in roles.values():
    assert sha(ROOT / role['candidate']) == role['candidate_sha256']
assert set(git('diff', '--name-only').decode().splitlines()) == set(native)
assert not git('diff', '--cached', '--name-only')
for path, pin in native.items():
    assert sha(ROOT / path) == pin
assert not git('diff', previous['head'], parent, '--', 'servo', 'layout', 'dom', 'testing')
recovered_nine = read(ROOT / 'artifacts/css-registered-zoom-standalone-transition-v1/SOURCE-ROLES.json')
assert len(recovered_nine) == 9
original_sources = {path: item['original_sha256'] for path, item in recovered_nine.items()}
assert assessments['original']['native_sources'] == original_sources
assert assessments['candidate']['native_sources'] == original_sources | native
assert read(original_dir / 'EPOCH.json')['modified_native_paths'] == []
assert read(candidate_dir / 'EPOCH.json')['modified_native_paths'] == sorted(native)
experiment = ROOT / 'artifacts/css-registered-zoom-standalone-wpt-v1/EXPERIMENT.json'
assert assessments['original']['experiment_sha256'] == assessments['candidate']['experiment_sha256'] == sha(experiment)
assert experiment.read_bytes() == (ROOT / 'artifacts/css-registered-zoom-standalone-wpt-v2/EXPERIMENT.json').read_bytes()
for role, capsule in [('original', 'artifacts/css-registered-zoom-standalone-wpt-v1'), ('candidate', 'artifacts/css-registered-zoom-standalone-wpt-v2')]:
    assert assessments[role]['capsule_manifest_sha256'] == inputs['packages'][capsule]
for path, item in recovered_nine.items():
    assert sha(ROOT / item['prototype']) == previous['dirty_native_source_pins'][path] == item['prototype_sha256']
    assert sha(ROOT / path) == native.get(path, item['original_sha256'])
    assert hashlib.sha256(git('show', 'HEAD:' + path)).hexdigest() == item['original_sha256']

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
ledger.setdefault('registered_number_research_history', []).append(copy.deepcopy(ledger['latest_registered_number_research']))
research = ledger['latest_registered_number_research']
if 'latest_standalone_zoom_observation' in research:
    research.setdefault('standalone_zoom_history', []).append(copy.deepcopy(research['latest_standalone_zoom_observation']))
research['latest_standalone_zoom_observation'] = {
    'original': inputs['original_runtime'], 'candidate': inputs['candidate_runtime'],
    'original_native_paths': 0, 'candidate_native_paths': 7, 'same_pages': 29,
    'same_subtests': 636, 'same_reftests': 6,
    'comparison_summary': comparison['summary'],
    'broad_regression_gate_passed': comparison['broad_regression_gate_passed'],
    'broad_rejections': comparison['broad_rejections'],
    'port_adjudication': inputs['port_adjudication'],
    'adjudicated_broad_gate_passed': adjudicated['adjudicated_broad_gate_passed'],
    'raw_wrapper_gate_remains_false': True,
    'adjudication_scope': adjudicated['normalization_scope'],
    'candidate_accepted': False, 'accepted_fix_increment': 0,
    'attribution_limit': comparison['attribution_limit'],
}
research['status'] = 'Standalone zoom source0/source7 paired observation completed with preserved execution; native acceptance and container normative adjudication remain pending. Admission repair is parked and separate.'
research.setdefault('writing_mode_followup', {})['provider_readiness_followup'] = {
    'review': 'artifacts/css-registered-writing-mode-v3-static-review-v1',
    'fixture': 'artifacts/css-registered-writing-mode-provider-readiness-wpt-draft-v1',
    'prepared_tests': 16, 'browser_executed': False,
}
experiment_data = read(experiment)
a_names = {(test, name) for test, names in experiment_data['a_subtests'].items() for name in names}
current_rows = assessments['candidate']['rows']
held_tests = set(experiment_data['held_subtests'])
regression_rows = [row for row in current_rows if row['test'] in experiment_data['broad_tests'] and row['test'] not in held_tests and (row['test'], row['subtest']) not in a_names]
research.update(
    candidate_variant='zoom-standalone-v1', candidate_applied=True,
    admission_overlay_installed=False, candidate_build_complete=True, candidate_accepted=False,
    candidate_build='artifacts/css-registered-number-native-runtime-v1/zoom-standalone-candidate-build-1',
    candidate_observation=inputs['candidate_runtime'], original_observation=inputs['original_runtime'],
    browser_capsule='artifacts/css-registered-zoom-standalone-wpt-v2',
    original_browser_capsule='artifacts/css-registered-zoom-standalone-wpt-v1',
    candidate_wpt_targets_pass=sum(row['status'] == 'PASS' and (row['test'], row['subtest']) in a_names for row in current_rows),
    candidate_wpt_targets_fail=sum(row['status'] == 'FAIL' and (row['test'], row['subtest']) in a_names for row in current_rows),
    candidate_wpt_target_scope='A104 subset of the standalone 636-assertion experiment',
    observed_wpt_repairs=sum(row['category'] == 'repaired' and row['subtest'] is not None for row in comparison['rows']),
    observed_wpt_repairs_scope='All 636 named assertions, source0 versus standalone zoom7',
    candidate_regression_assertions_pass=sum(row['status'] == 'PASS' for row in regression_rows),
    candidate_reftests_pass=6,
    held_scheduling_signatures_unchanged=sum(row['category'] == 'unchanged' and row['subtest'] is not None for row in comparison['rows'] if row['test'] in held_tests),
    held_scheduling_all_signatures_unchanged=all(row['category'] == 'unchanged' for row in comparison['rows'] if row['test'] in held_tests),
    zoom_acceptance_blocker='Native acceptance remains pending; source-container zoom interpretation and bounded controls require adjudication. Historical combined-nine CSSOM failures are not asserted to persist.',
    source_transition='artifacts/css-registered-zoom-standalone-transition-v3',
    accepted_fix_increment=0,
)
if 'latest_normalization_observations' in research:
    research['historical_combined_nine_observations'] = research.pop('latest_normalization_observations')
research['zoom_followup_checkpoint'] = {
    'status': 'STANDALONE_PAIRED_OBSERVATION_UNACCEPTED',
    'proposal': 'artifacts/css-registered-zoom-normalization-proposal-v3',
    'native_source_paths_preserved_dirty': 7,
    'terminal_build_result': 'artifacts/css-registered-number-native-runtime-v1/zoom-standalone-candidate-build-1/RESULT.json',
    'candidate_browser_comparison': copy.deepcopy(research['latest_standalone_zoom_observation']),
    'standalone_transition_preparation': {
        'artifact': 'artifacts/css-registered-zoom-standalone-transition-v1',
        'status': 'HISTORICAL_DISABLED_PREPARATION_SUPERSEDED_BY_EXECUTED_V3',
        'successful_successor': 'artifacts/css-registered-zoom-standalone-transition-v3',
    },
    'container_normative_interpretation': 'Open; source-container zoom interpretation requires explicit adjudication and bounded controls',
    'runner_head_rebind_required': True, 'accepted_fix_increment': 0,
}
research['runner_head_rebind_required'] = True
ledger.setdefault('verified_working_epoch_history', []).append(copy.deepcopy(ledger['latest_verified_working_epoch']))
ledger['latest_verified_working_epoch'].update(
    status=research['status'], candidate_variant='zoom-standalone-v1',
    dirty_native_source_pins=native, runner_head_rebind_required=True,
    candidate_accepted=False, candidate_build_complete=True, candidate_applied=True,
    admission_overlay_installed=False, combined_nine_recovery='artifacts/css-registered-zoom-standalone-transition-v1',
)
(ROOT / ledger_names[0]).write_text(json.dumps(ledger, indent=2, ensure_ascii=False) + '\n')
title, rest = (ROOT / ledger_names[1]).read_text().split('\n\n', 1)
paragraph = (
    'Signing checkpoint: the committed-source original and seven-file standalone zoom candidate '
    'were built and tested with the same 29 WPT pages, 636 subtests and six reftests. '
    'Both executions preserved source, binary, index and metadata state. All 70 focused assertions '
    'pass, with 56 repairs and 14 unchanged passes; all 566 broad assertions are unchanged. The raw '
    'comparison remains false solely for six passed-reference diagnostic URL ports. A separately '
    'authenticated offline replay adjudicates the broad gate true after normalizing only those '
    'manifest-exact ports; raw evidence remains unchanged. The admission repair is not installed; its full '
    'nine-file combined state and all 50 parked prototypes remain preserved. Container coordinate '
    'specification gaps and separate writing-mode/provider readiness investigations remain open. '
    'No native fix is accepted; the count remains 137. Signing makes the fixed runner HEAD historical; '
    'a reviewed successor is required before further runtime execution.'
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
         'The seven standalone zoom native edits remain dirty and preserved in previously signed artifacts. '
         'All 50 parked prototype bodies and the 140-entry recovery inventory were checked. '
         'The nested Lean repository and browser binaries are preserved. No push or CI submission occurred.']
(HERE / 'CHECKPOINT.md').write_text('\n'.join(rows) + '\n')
files = [HERE / name for name in ['commit.py', 'finish.py', 'INITIAL-EPOCH.json',
         'BEFORE.json', 'PRE-CHECKPOINT-EPOCH.json', 'PREVIOUS-FINAL-CHECK.json',
         'ROADMAP-UPDATE.json', 'CHECKPOINT.md', 'INPUTS.json', 'CHECKPOINT-OUTLINE.json', 'VALIDATION-INVENTORY.json', 'REVIEW.json']]
files += [HERE / name for name in ['adopt-research-retry.py', 'resume-research.py',
         'research-retry-adoption.json', 'research-commit.log', 'research-driver.log', 'SIGNING-BLOCKED.json',
         'research-retry-1-commit.log', 'research-staged.patch', 'research-message.txt']]
files.append(successful_log)
files += list((HERE / 'ledger-preimages').iterdir())
for name in receipts:
    files += [HERE / (name + suffix) for suffix in
              ['-selection.json', '-receipt.json', '-signature.log']]
files += [ROOT / name for name in ledger_names]
pins = {str(path.relative_to(ROOT)): sha(path) for path in files}
save(HERE / 'checkpoint-selection.json', {
    'id': 'checkpoint',
    'message': 'No bug - Checkpoint standalone registered-value zoom comparison. r?#firefox-style-system-reviewers',
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
assert sha(RUNTIME / 'ROLE.json') == inputs['role_sha256']
assert sha(RUNTIME / 'OWNED.json') == inputs['owned_sha256']
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
    'normalization_experimental_unaccepted': True, 'standalone_transition_executed': True,
    'runner_head_rebind_required': True,
})
print((HERE / 'FINAL-CHECK.json').read_text(), flush=True)
