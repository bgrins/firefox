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
PREVIOUS = ROOT / 'artifacts/css-local-signing-20261027-v18'
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
observer = ROOT / 'artifacts/css-registered-container-zoom-observation-v2'
assert sha(observer / 'FILES.json') == '30e90f2870b1278c10c12710e8c259874d0a418033682c9e2d714d393fff5388'
observer_manifest = read(observer / 'FILES.json')
for name, record in observer_manifest.items():
    assert sha(observer / name) == record['sha256']
assert read(observer / 'POLICY.json')['execution_enabled'] is False
assert inputs['execution_enabled'] is True
assert previous['head'] == inputs['frozen_head'] == '1c7870c6d36d002b1c785ec2a6251ddc4ca2a040'
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
assert all(selected.get(path) == pin for path, pin in inputs['evidence_pins'].items())
assert str((proposal / 'FILES.json').relative_to(ROOT)) in selected
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
    'native_source_paths_preserved_dirty': 9,
    'runner_head_rebind_required': True,
    'accepted_fix_increment': 0,
    'canonical_coverage_increment': 0,
}
(ROOT / ledger_names[0]).write_text(json.dumps(ledger, indent=2, ensure_ascii=False) + '\n')
title, rest = (ROOT / ledger_names[1]).read_text().split('\n\n', 1)
paragraph = (
    'Signing checkpoint: registered-value zoom normalization research, reviewed runners, '
    'and three completed admission-only browser observations are preserved. The 56-test '
    'zoom calibration observed 6 PASS and 50 FAIL; the separate no-zoom logical-unit '
    'writing-mode calibration observed all 16 tests failing. Container observations '
    'motivate the experimental per-source zoom contract without claiming normative '
    'parity. ' + inputs['summary'] + ' '
    'The nine live native candidate edits remain unaccepted. The logical-unit scheduling '
    'lead remains separate from zoom normalization and the pending broader numeric '
    'scheduling work. Next complete broader normalization validation and repair remaining '
    'semantic or runtime issues before any standalone native publication. All frozen '
    'HEAD runners require explicit successor binding after this checkpoint. No new fix '
    'or formal coverage is accepted; the accepted fix count remains 137.'
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
         'The container-observer v2 tool is preserved as a disabled, unexecuted draft. '
         'Its pending runtime binding must be replaced before use.', '',
         'The nine live native edits remain dirty and preserved in signed proposal artifacts. '
         'All 50 parked prototype bodies and the 140-entry recovery inventory were checked. '
         'The nested Lean repository and browser binaries are preserved. No push or CI submission occurred.']
(HERE / 'CHECKPOINT.md').write_text('\n'.join(rows) + '\n')
files = [HERE / name for name in ['commit.py', 'finish.py', 'INITIAL-EPOCH.json',
         'BEFORE.json', 'PRE-CHECKPOINT-EPOCH.json', 'PREVIOUS-FINAL-CHECK.json',
         'ROADMAP-UPDATE.json', 'CHECKPOINT.md', 'CHECKPOINT-INPUTS.json', 'INVENTORY.json', 'PLAN.md',
         'ROOT-TERMINATION-CHECK.json']]
files += list((HERE / 'ledger-preimages').iterdir())
files += [observer / 'FILES.json'] + [observer / name for name in observer_manifest]
for name in receipts:
    files += [HERE / (name + suffix) for suffix in
              ['-selection.json', '-receipt.json', '-signature.log']]
files += [ROOT / name for name in ledger_names]
pins = {str(path.relative_to(ROOT)): sha(path) for path in files}
save(HERE / 'checkpoint-selection.json', {
    'id': 'checkpoint',
    'message': 'No bug - Checkpoint experimental normalization and logical-unit evidence. r?#firefox-style-system-reviewers',
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
