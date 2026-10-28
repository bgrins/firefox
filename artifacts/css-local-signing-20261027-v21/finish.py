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
PREVIOUS = ROOT / 'artifacts/css-local-signing-20261027-v20'
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
assert previous['head'] == '2a85779b573a0e2ccbfb1c5012bbb81ef1478294'
assert sha(RUNTIME / 'CURRENT-EPOCH.json') == previous['current_epoch_sha256']
inputs = read(HERE / 'INPUTS.json')
assert previous['head'] == inputs['frozen_head']
assert sha(RUNTIME / 'CURRENT-EPOCH.json') == inputs['runtime_epoch_sha256']
assert sha(RUNTIME / 'ROLE.json') == inputs['role_sha256']
assert sha(RUNTIME / 'OWNED.json') == inputs['owned_sha256']
for directory, pin in inputs['packages'].items():
    package = ROOT / directory
    assert sha(package / 'FILES.json') == pin
    for name, item in read(package / 'FILES.json').items():
        assert sha(package / name) == (item['sha256'] if isinstance(item, dict) else item)
transition = ROOT / 'artifacts/css-registered-zoom-standalone-transition-v1'
assert read(transition / 'POLICY.json')['execution_enabled'] is False
assert read(transition / 'POLICY.json')['head'] == previous['head']
assert epoch['registered_number_transition'] == read(PREVIOUS / 'CURRENT-EPOCH.json')['registered_number_transition']
assert epoch['registered_number_transition']['compiled'] is True
assert epoch['registered_number_transition']['accepted'] is False
assert read(HERE / 'INITIAL-EPOCH.json')['semantic_index']['head'] == previous['head']
roles = read(ROOT / 'artifacts/css-registered-zoom-normalization-proposal-v3/SOURCE-ROLES.json')
assert len(roles) == 7
for name, role in roles.items():
    assert sha(ROOT / role['base']) == role['base_sha256']
parent = previous['head']
receipts = {}
for name in ['research']:
    receipt = read(HERE / (name + '-receipt.json'))
    assert receipt['parent'] == parent and receipt['signature_verified']
    assert all(path.startswith('artifacts/') for path in receipt['files'])
    parent = receipt['commit']
    receipts[name] = receipt
assert parent == epoch['semantic_index']['head'] == git('rev-parse', 'HEAD').decode().strip()
native = previous['dirty_native_source_pins']
assert len(native) == 9 and set(epoch['modified_native_paths']) == set(native)
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
research = ledger['latest_registered_number_research']
research.setdefault('writing_mode_followup', {})['bitflags_iteration_proof'] = {
    'artifact': 'artifacts/css-writing-mode-bitflags-order-model-v1',
    'kernel_checked_declarations': 5, 'nine_bit_masks_checked': 512,
    'decisive_ordering_mutant_rejected': True, 'canonical_coverage_increment': 0,
    'native_refinement_proved': False,
}
research.setdefault('zoom_followup_checkpoint', {})['standalone_transition_preparation'] = {
    'artifact': 'artifacts/css-registered-zoom-standalone-transition-v1',
    'status': 'DISABLED_UNEXECUTED_PREPARATION',
    'execution_enabled': False, 'original_native_paths': 0, 'candidate_native_paths': 7,
    'prior_frozen_head': previous['head'], 'binding_successor_required': True,
    'prewrite_review_fixes_pending': True,
}
research['runner_head_rebind_required'] = True
ledger['latest_verified_working_epoch']['runner_head_rebind_required'] = True
(ROOT / ledger_names[0]).write_text(json.dumps(ledger, indent=2, ensure_ascii=False) + '\n')
title, rest = (ROOT / ledger_names[1]).read_text().split('\n\n', 1)
paragraph = (
    'Signing checkpoint: five kernel-checked bitflag iteration declarations cover all 512 '
    'nine-bit masks and reject the ordering mutant. This conditional model adds no canonical '
    'CSS coverage or native refinement claim. The standalone zoom transition is preserved '
    'as disabled, unexecuted preparation with known prewrite review fixes pending. Its '
    'frozen HEAD and epoch become historical after signing and require a reviewed successor. '
    'The current compiled nine-file candidate and all prior browser evidence are unchanged. '
    'Next complete the transition safeguards and paired validation of the seven-file zoom '
    'change without the admission repair. No native fix is accepted; the count remains 137.'
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
         'The nine live native edits remain dirty and preserved in previously signed artifacts. '
         'All 50 parked prototype bodies and the 140-entry recovery inventory were checked. '
         'The nested Lean repository and browser binaries are preserved. No push or CI submission occurred.']
(HERE / 'CHECKPOINT.md').write_text('\n'.join(rows) + '\n')
files = [HERE / name for name in ['commit.py', 'finish.py', 'INITIAL-EPOCH.json',
         'BEFORE.json', 'PRE-CHECKPOINT-EPOCH.json', 'PREVIOUS-FINAL-CHECK.json',
         'ROADMAP-UPDATE.json', 'CHECKPOINT.md', 'INPUTS.json']]
files += list((HERE / 'ledger-preimages').iterdir())
for name in receipts:
    files += [HERE / (name + suffix) for suffix in
              ['-selection.json', '-receipt.json', '-signature.log']]
files += [ROOT / name for name in ledger_names]
pins = {str(path.relative_to(ROOT)): sha(path) for path in files}
save(HERE / 'checkpoint-selection.json', {
    'id': 'checkpoint',
    'message': 'No bug - Checkpoint bitflag proof and disabled standalone zoom preparation. r?#firefox-style-system-reviewers',
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
    'normalization_experimental_unaccepted': True, 'standalone_transition_executed': False,
    'runner_head_rebind_required': True,
})
print((HERE / 'FINAL-CHECK.json').read_text(), flush=True)
