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
PREVIOUS = ROOT / 'artifacts/css-local-signing-20261027-v17'
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
assert previous['head'] == '770a90f709c0994efae1b8df3d2e3ebff400474b'
assert sha(RUNTIME / 'CURRENT-EPOCH.json') == previous['current_epoch_sha256']
parent = previous['head']
receipts = {}
for name in ['calibration-design', 'zoom-runner', 'zoom-scope']:
    receipt = read(HERE / (name + '-receipt.json'))
    assert receipt['parent'] == parent and receipt['signature_verified']
    assert all(path.startswith('artifacts/') for path in receipt['files'])
    parent = receipt['commit']
    receipts[name] = receipt
assert parent == epoch['semantic_index']['head'] == git('rev-parse', 'HEAD').decode().strip()
native = previous['dirty_native_source_pins']
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
        source = RUNTIME / 'prototype-original' / path if path in restoration else ROOT / path
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
ledger['latest_registered_number_research']['zoom_followup_checkpoint'] = {
    'container_calibration_design': 'artifacts/css-registered-container-zoom-calibration-design-v1',
    'wpt_calibration_runner': 'artifacts/css-registered-zoom-wpt-calibration-v1',
    'scope_proposal': 'artifacts/css-registered-zoom-scope-proposal-v1',
    'browser_execution': False,
    'native_compilation': False,
    'runner_independent_review_pending': True,
    'runner_head_rebind_required': True,
    'accepted_fix_increment': 0,
    'canonical_coverage_increment': 0,
}
(ROOT / ledger_names[0]).write_text(json.dumps(ledger, indent=2, ensure_ascii=False) + '\n')
title, rest = (ROOT / ledger_names[1]).read_text().split('\n\n', 1)
paragraph = (
    'Signing checkpoint: the container-unit zoom calibration design, four-page/56-test '
    'zoom calibration runner and two-file scoped-computation prototype are now saved '
    'in separate signed research commits. The runner has manifest/static controls but '
    'has not run in a browser; independent review and an authenticated update of its '
    'historical HEAD/epoch bindings are required before execution. The scope prototype '
    'passed formatting and patch transport checks but has not been installed or compiled. '
    'Next complete calibration and length/container/CSSOM integration, then build and '
    'repeat the admission, scheduling, regression, sign and zoom gates. The existing '
    'two-file admission candidate remains held for its zoom CSSOM regression. No new '
    'fix or formal coverage is accepted; the accepted fix count remains 137.'
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
         'The two live native edits remain dirty and preserved in previously signed artifacts. '
         'All 50 parked prototype bodies and the 140-entry recovery inventory were checked. '
         'The nested Lean repository and browser binaries are preserved. No push or CI submission occurred.']
(HERE / 'CHECKPOINT.md').write_text('\n'.join(rows) + '\n')
files = [HERE / name for name in ['commit.py', 'finish.py', 'INITIAL-EPOCH.json',
         'BEFORE.json', 'PRE-CHECKPOINT-EPOCH.json', 'PREVIOUS-FINAL-CHECK.json',
         'ROADMAP-UPDATE.json', 'CHECKPOINT.md']]
files += list((HERE / 'ledger-preimages').iterdir())
for name in receipts:
    files += [HERE / (name + suffix) for suffix in
              ['-selection.json', '-receipt.json', '-signature.log']]
files += [ROOT / name for name in ledger_names]
pins = {str(path.relative_to(ROOT)): sha(path) for path in files}
save(HERE / 'checkpoint-selection.json', {
    'id': 'checkpoint',
    'message': 'No bug - Checkpoint zoom research and preserved unfinished fixes. r?#firefox-style-system-reviewers',
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
    'acceptance_held_for_zoom_regression': True, 'runner_head_rebind_required': True,
})
print((HERE / 'FINAL-CHECK.json').read_text(), flush=True)
