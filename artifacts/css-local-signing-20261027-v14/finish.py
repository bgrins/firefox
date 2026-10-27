import copy
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

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
before = s.a.verify_current(s.h, ROOT, ENV, epoch)
receipts = {name: read(HERE / (name + '-receipt.json')) for name in
            ['numeric-implementation', 'numeric-tests', 'shorthand-formatting']}
assert all(v['signature_verified'] for v in receipts.values())
assert read(RUNTIME / 'head-original-build-2/RESULT.json')['owned_processes'] == {}
assert read(RUNTIME / 'head-original-build-2/build-RESULT.json')['stop_reason'] == 'TERMINATION_REQUESTED'
restoration = read(RUNTIME / 'RESTORATION-PLAN.json')
for name, pin in restoration['paths'].items():
    assert sha(ROOT / name) == pin['head_original']
    assert hashlib.sha256(git('show', 'HEAD:' + name)).hexdigest() == pin['head_original']
    assert sha(RUNTIME / 'prototype-original' / name) == pin['prototype_original']
snapshot = ROOT / 'artifacts/css-unfinished-work-checkpoint-20261027-v8'
source_pins = read(snapshot / 'SOURCE-PINS.json')
for name, pin in source_pins.items():
    source = RUNTIME / 'prototype-original' / name if name in restoration['paths'] else ROOT / name
    assert sha(source) == pin, name

ledger_name = 'artifacts/stylo-bloom-tools/CURRENT-COMMITS.json'
plan_name = 'artifacts/stylo-bloom-tools/PLAN-OF-RECORD.md'
preimages = HERE / 'ledger-preimages'
preimages.mkdir()
old_pins = {}
for name in [ledger_name, plan_name]:
    old_pins[name] = sha(ROOT / name)
    assert any(epoch[key].get(name) == old_pins[name] for key in
               ['pins', 'staged_working', 'committed_research_working_payloads'])
    (preimages / Path(name).name).write_bytes((ROOT / name).read_bytes())
ledger = read(ROOT / ledger_name)
assert ledger['committed_native_fixes'] == 137
save(HERE / 'PREVIOUS-LATEST-RESEARCH.json', {
    key: ledger[key] for key in ['latest_research_signing', 'latest_verified_working_epoch',
                                 'latest_registered_number_research']})
ledger['latest_research_signing'] = {
    'status': 'SIGNED_VERIFIED_LOCAL',
    'commits': {name: value['commit'] for name, value in receipts.items()},
    'directory': str(HERE.relative_to(ROOT)),
}
ledger['latest_verified_working_epoch'] = {
    'path': 'artifacts/css-registered-number-native-runtime-v1/CURRENT-EPOCH.json',
    'status': 'Committed native sources installed for baseline comparison; build stopped cleanly for signing and must resume',
    'prototype_overlay_installed': False,
    'restoration_plan': 'artifacts/css-registered-number-native-runtime-v1/RESTORATION-PLAN.json',
    'baseline_build_complete': False,
}
ledger['latest_registered_number_research'].update({
    'status': 'IMPLEMENTATION_AND_TEST_PROPOSALS_SIGNED_NATIVE_VALIDATION_PENDING',
    'implementation_commit': receipts['numeric-implementation']['commit'],
    'tests_commit': receipts['numeric-tests']['commit'],
    'head_proposal': 'artifacts/css-registered-number-preparation-head-proposal-v1',
    'prototype_proposal': 'artifacts/css-registered-number-preparation-proposal-v1',
    'browser_capsule': 'artifacts/css-registered-number-wpt-capsule-v2',
    'browser_targets_prepared': 58,
    'browser_regression_assertions_prepared': 446,
    'browser_reftests_prepared': 6,
    'browser_comparison_executed': False,
    'pending_gtest_overlay': 'artifacts/css-registered-number-pending-gtest-overlay-v1',
    'pending_gtest_total_prepared': 22,
    'pending_gtest_overlay_executed': False,
    'accepted_fix_increment': 0,
})
(ROOT / ledger_name).write_text(json.dumps(ledger, indent=2, ensure_ascii=False) + '\n')
plan = (ROOT / plan_name).read_text()
title, old_first, rest = plan.split('\n\n', 2)
paragraph = (
    'Next: finish the committed-source baseline build, run the registered-number '
    '58-target browser comparison with 446 regression assertions and six reftests, '
    'then build and test the proposed native repair. Implementation proposals and '
    'the expanded comparison tools are signed; native acceptance is still pending. '
    'The first baseline build hit stale generated-header declarations; the retry '
    'passed Rust compilation and was stopped cleanly during C++ compilation to sign '
    'the work. Resume incrementally. The 50 tracked native prototype bodies remain '
    'preserved in css-registered-number-native-runtime-v1/prototype-original and '
    'the signed unfinished-work checkpoint v8. After the standalone comparison, '
    'restore those prototypes and validate the pending-demand overlay (22 prepared '
    'GTests, including two new tests). The isolated Lean model remains at 20 '
    'audited declarations, 14 kernel examples and seven negative controls; no '
    'canonical coverage or native-refinement credit is added. Numeric self-font '
    'cycle policy remains unresolved. Continue the Bloom milestones and production '
    'pending-provider work after these gates.'
)
(ROOT / plan_name).write_text(title + '\n\n' + paragraph + '\n\n' + rest)
current = copy.deepcopy(epoch)
for name in [ledger_name, plan_name]:
    for key in ['pins', 'staged_working', 'committed_research_working_payloads']:
        if name in current[key]:
            current[key][name] = sha(ROOT / name)
state = s.h.index_state(ROOT, ENV)
current['semantic_index'] = s.h.semantic_index(state)
current['raw_index_observation']['current'] = state['raw_index']
s.a.verify_current(s.h, ROOT, ENV, current)
epoch_path.write_text(json.dumps(current, indent=2, sort_keys=True) + '\n')
save(HERE / 'ROADMAP-UPDATE.json', {
    'before': old_pins,
    'after': {name: sha(ROOT / name) for name in old_pins},
    'accepted_fixes': 137,
    'recovery_source_pins_verified': len(source_pins),
    'tracked_native_prototype_bodies_preserved': len(restoration['paths']),
    'native_head_blobs_unchanged_by_research_commits': True,
})
save(HERE / 'PRE-CHECKPOINT-EPOCH.json', current)
save(HERE / 'OWNED-SNAPSHOT.json', read(RUNTIME / 'OWNED.json'))
save(HERE / 'ROLE-SNAPSHOT.json', read(RUNTIME / 'ROLE.json'))

lines = ['# Registered-number research signing checkpoint', '',
         '| Commit | Work |', '| --- | --- |']
for name, label in [('numeric-implementation', 'Captured native admission and dependency proposals; independent review'),
                    ('numeric-tests', '58-target browser comparison and pending-demand test overlay'),
                    ('shorthand-formatting', 'Five Python formatting changes; identical ASTs')]:
    lines.append('| ' + receipts[name]['commit'] + ' | ' + label + ' |')
lines += ['',
    'Accepted fixes remain 137 (138 tracked records, held fix 120 excluded). These commits do not accept a new native fix. The new browser and GTest cases have not run. Static artifact checks and independent reviews passed.', '',
    'All 140 source pins in the signed unfinished-work checkpoint v8 match either their live bodies or the preserved prototype bodies. The current tracked native tree is committed HEAD for a standalone baseline comparison; 50 prototype files are intentionally parked, and their untracked companions remain in place. Restore the prototype only after the standalone comparison. No prototype body was discarded.', '',
    'The first baseline build failed on stale generated declarations. The retry passed Rust compilation and was stopped cleanly during C++ compilation for this signing session. Both process groups are gone; preservation checks passed. Neither attempt is a completed native validation.', '',
    'Resume from artifacts/css-registered-number-native-runtime-v1/CURRENT-EPOCH.json after final signing synchronization. Use WPT capsule v2; v1 is historical and unexecuted. Restart build.py with a fresh label, head-original-build-3. All intermediate build outputs are retained for incremental reuse. The checkpoint records immutable runtime material; CURRENT-EPOCH.json, OWNED.json and ROLE.json remain mutable continuation files.', '',
    'The previous prototype integration and unfinished WPTs remain recoverable through the signed v8 snapshot. The nested CSS Lean repository is unchanged. No push, Try submission or Phabricator action was taken.',
]
(HERE / 'CHECKPOINT.md').write_text('\n'.join(lines) + '\n')

runtime_pins = {}
for path in sorted(RUNTIME.rglob('*')):
    if path.is_file() and path.relative_to(RUNTIME).as_posix() not in {
        'CURRENT-EPOCH.json', 'OWNED.json', 'ROLE.json'}:
        assert not path.is_symlink()
        runtime_pins[str(path.relative_to(RUNTIME))] = sha(path)
save(HERE / 'RUNTIME-CHECKPOINT-FILES.json', runtime_pins)
pins = {str((RUNTIME / name).relative_to(ROOT)): pin for name, pin in runtime_pins.items()}
for path in sorted(HERE.rglob('*')):
    if path.is_file() and path.name != 'CURRENT-EPOCH.json' and path.name != 'finish-driver.log':
        pins[str(path.relative_to(ROOT))] = sha(path)
for name in [ledger_name, plan_name]:
    pins[name] = sha(ROOT / name)
save(HERE / 'checkpoint-selection.json', {
    'id': 'checkpoint',
    'message': 'No bug - Checkpoint registered number proposals and baseline build state. r?#firefox-style-system-reviewers',
    'files': sorted(pins),
    'source_pins': pins,
})
with (HERE / 'checkpoint-driver.log').open('x') as stream:
    subprocess.run([sys.executable, '-I', '-S', '-B', str(HERE / 'commit.py'),
                    str(HERE / 'checkpoint-selection.json')], cwd=ROOT, env=ENV,
                   stdout=stream, stderr=subprocess.STDOUT, check=True)
final = read(HERE / 'checkpoint-receipt.json')
assert final['signature_verified']
assert not git('diff', '--name-only')
assert not git('diff', '--cached', '--name-only')
assert git('-C', 'artifacts/css-spec-lean', 'rev-parse', 'HEAD').decode().strip() == '162b20fb7c53a0ab89b20875a965baee98fb66bb'
for name, pin in pins.items():
    assert hashlib.sha256(git('show', 'HEAD:' + name)).hexdigest() == pin, name
current = read(epoch_path)
s.a.verify_current(s.h, ROOT, ENV, current)
(RUNTIME / 'CURRENT-EPOCH.json').write_bytes(epoch_path.read_bytes())
save(HERE / 'FINAL-CHECK.json', {
    'head': final['commit'],
    'commits': {name: value['commit'] for name, value in receipts.items()} | {'checkpoint': final['commit']},
    'signatures_verified': True,
    'tracked_tree_clean': True,
    'staging_empty': True,
    'unfinished_prototypes_preserved': True,
    'accepted_fixes': 137,
    'canonical_coverage_increment': 0,
    'current_epoch_sha256': sha(epoch_path),
    'runtime_epoch_synchronized': True,
    'baseline_build_complete': False,
})
print((HERE / 'FINAL-CHECK.json').read_text(), flush=True)
