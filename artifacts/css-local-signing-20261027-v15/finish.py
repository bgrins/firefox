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
            ['proofs', 'proposals', 'baseline', 'tools']}
assert all(value['signature_verified'] for value in receipts.values())
build = read(RUNTIME / 'head-original-build-3/RESULT.json')
assert build['command_success'] and build['preservation_verified']
assert build['owned_processes'] == {} and not build['publication_errors']
restoration = read(RUNTIME / 'RESTORATION-PLAN.json')
for name, pin in restoration['paths'].items():
    assert sha(ROOT / name) == pin['head_original']
    assert hashlib.sha256(git('show', 'HEAD:' + name)).hexdigest() == pin['head_original']
    assert sha(RUNTIME / 'prototype-original' / name) == pin['prototype_original']
v14 = read(ROOT / 'artifacts/css-local-signing-20261027-v14/ROADMAP-UPDATE.json')
source_pins = read(ROOT / 'artifacts/css-unfinished-work-checkpoint-20261027-v8/SOURCE-PINS.json')
for name, pin in source_pins.items():
    if name in v14['before']:
        assert pin == v14['before'][name]
        assert sha(ROOT / name) == v14['after'][name]
    else:
        source = RUNTIME / 'prototype-original' / name if name in restoration['paths'] else ROOT / name
        assert sha(source) == pin, name

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
ledger['latest_research_signing'] = {
    'status': 'SIGNED_VERIFIED_LOCAL',
    'commits': {name: value['commit'] for name, value in receipts.items()},
    'directory': str(HERE.relative_to(ROOT)),
}
ledger['latest_verified_working_epoch'] = {
    'path': 'artifacts/css-registered-number-native-runtime-v1/CURRENT-EPOCH.json',
    'status': 'Committed native sources built and baseline observations complete; generalized admission candidate remains unapplied',
    'prototype_overlay_installed': False,
    'restoration_plan': 'artifacts/css-registered-number-native-runtime-v1/RESTORATION-PLAN.json',
    'baseline_build_complete': True,
}
ledger['latest_registered_number_research'].update({
    'status': 'ORIGINAL_BASELINE_COMPLETE_GENERALIZED_ADMISSION_UNAPPLIED',
    'implementation_commit': receipts['proposals']['commit'],
    'tests_commit': receipts['tools']['commit'],
    'head_proposal': 'artifacts/css-registered-admission-preparation-head-proposal-v1',
    'prototype_proposal': 'artifacts/css-registered-admission-preparation-proposal-v1',
    'baseline_readout': 'artifacts/css-registered-numeric-baseline-readout-v1',
    'original_wpt_targets_pass': 38,
    'original_wpt_targets_fail': 20,
    'original_wpt_regression_assertions_pass': 446,
    'original_wpt_reftests_pass': 6,
    'browser_comparison_executed': False,
    'browser_capsule': None,
    'original_browser_capsule': 'artifacts/css-registered-number-wpt-capsule-v2',
    'browser_targets_prepared': 104,
    'held_scheduling_targets_prepared': 16,
    'candidate_native_validation_executed': False,
    'split_fixture': 'artifacts/css-registered-number-wpt-fixture-v3',
    'split_fixture_requires_new_capsule': True,
    'scheduling_workstream': 'Separate pending repair; not accepted or discarded',
    'accepted_fix_increment': 0,
    'canonical_coverage_increment': 0,
})
(ROOT / ledger_name).write_text(json.dumps(ledger, indent=2, ensure_ascii=False) + '\n')
title, previous, rest = (ROOT / plan_name).read_text().split('\n\n', 2)
paragraph = (
    'Next: bind a new comparison capsule and source-transition tool to the signed '
    'HEAD, eight-path generalized admission proposals, and split A/B fixture. '
    'Run the expanded original fixture on the completed committed-source build, '
    'then apply, compile and compare repair A. The existing original run completed '
    'with 38 target passes, 20 target failures, 446 regression passes and six '
    'reftest passes; this is baseline evidence, not repair validation. Repair A '
    'removes false contextual edges using actual grammar admission and intersection '
    'with the old mask. Direct numeric scheduling remains separate pending repair B; '
    'compare its observed values and statuses for unintended changes. The generalized '
    'candidate remains unapplied. Earlier number-only transition tools bind obsolete '
    'three-path proposals and historical HEADs; version them before further execution. '
    'After the standalone comparison, restore all 50 parked native prototypes and '
    'validate the updated pending-demand integration. Their bodies and unfinished '
    'tests remain preserved in the signed v8 checkpoint. Isolated collector and '
    'projection proofs passed, including independent replays; no native-refinement '
    'or canonical coverage credit is added. The projection cycle theorem assumes '
    'a fixed original graph. Self-font numeric defaulting remains unresolved. '
    'Accepted fixes remain 137. Continue Bloom milestones and pending-provider work '
    'after these gates.'
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
    'prior_authorized_ledger_update': 'artifacts/css-local-signing-20261027-v14/ROADMAP-UPDATE.json',
})
save(HERE / 'PRE-CHECKPOINT-EPOCH.json', current)
save(HERE / 'OWNED-SNAPSHOT.json', read(RUNTIME / 'OWNED.json'))
save(HERE / 'ROLE-SNAPSHOT.json', read(RUNTIME / 'ROLE.json'))
lines = ['# Registered admission research checkpoint', '', '| Commit | Work |', '| --- | --- |']
for name, value in receipts.items():
    lines.append('| ' + value['commit'] + ' | ' + name + ' |')
lines += ['', paragraph, '',
          'The nested CSS Lean repository is unchanged. All new candidate code is captured under artifacts; no native candidate was installed. Build outputs remain local for reuse. The original build and browser evidence bind historical HEAD 55dddb9d59e2; later runners must explicitly rebind the current HEAD while preserving those immutable results. No pushes or CI submissions were made.', '',
          'Untracked prototype companions and WPTs remain in the working tree and are also preserved by the earlier signed unfinished-work checkpoint. This commit records a checkpoint, not an accepted implementation fix.']
(HERE / 'CHECKPOINT.md').write_text('\n'.join(lines) + '\n')
pins = {}
for directory in [RUNTIME / 'head-original-build-3', ROOT / 'artifacts/css-registered-admission-projection-root-replay-v1']:
    for path in sorted(directory.rglob('*')):
        if path.is_file():
            assert not path.is_symlink()
            pins[str(path.relative_to(ROOT))] = sha(path)
for path in sorted(HERE.rglob('*')):
    if path.is_file() and path.name not in {'CURRENT-EPOCH.json', 'finish-driver.log'}:
        pins[str(path.relative_to(ROOT))] = sha(path)
for name in old_pins:
    pins[name] = sha(ROOT / name)
save(HERE / 'checkpoint-selection.json', {
    'id': 'checkpoint',
    'message': 'No bug - Checkpoint registered admission research and completed baseline. r?#firefox-style-system-reviewers',
    'files': sorted(pins), 'source_pins': pins,
})
with (HERE / 'checkpoint-driver.log').open('x') as stream:
    subprocess.run([sys.executable, '-I', '-S', '-B', str(HERE / 'commit.py'),
                    str(HERE / 'checkpoint-selection.json')], cwd=ROOT, env=ENV,
                   stdout=stream, stderr=subprocess.STDOUT, check=True)
final = read(HERE / 'checkpoint-receipt.json')
assert final['signature_verified']
assert not git('diff', '--name-only') and not git('diff', '--cached', '--name-only')
assert git('-C', 'artifacts/css-spec-lean', 'rev-parse', 'HEAD').decode().strip() == '162b20fb7c53a0ab89b20875a965baee98fb66bb'
for name, pin in pins.items():
    assert hashlib.sha256(git('show', 'HEAD:' + name)).hexdigest() == pin, name
current = read(epoch_path)
s.a.verify_current(s.h, ROOT, ENV, current)
(RUNTIME / 'CURRENT-EPOCH.json').write_bytes(epoch_path.read_bytes())
save(HERE / 'FINAL-CHECK.json', {
    'head': final['commit'],
    'commits': {name: value['commit'] for name, value in receipts.items()} | {'checkpoint': final['commit']},
    'signatures_verified': True, 'tracked_tree_clean': True, 'staging_empty': True,
    'unfinished_prototypes_preserved': True, 'accepted_fixes': 137,
    'canonical_coverage_increment': 0, 'current_epoch_sha256': sha(epoch_path),
    'runtime_epoch_synchronized': True, 'baseline_build_complete': True,
    'candidate_applied': False,
})
print((HERE / 'FINAL-CHECK.json').read_text(), flush=True)
