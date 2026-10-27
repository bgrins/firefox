import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
SNAPSHOT = ROOT / 'artifacts/css-unfinished-work-checkpoint-20261027-v1'
ENV = dict(os.environ, GIT_OPTIONAL_LOCKS='0')
GIT = ['git', '--no-optional-locks', '-c', 'core.fsmonitor=false']


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write('\n')


def git(*args, env=ENV):
    return subprocess.check_output(GIT + list(args), cwd=ROOT, env=env)


h = load('preserve', 'artifacts/css-keyframe-commit-styles-implicit-clean-comparison-v1/compare.py')
a = load('epoch', 'artifacts/css-keyframe-operation-descriptor-post-signing-proposal-v2/epoch.py')
epoch = json.loads((HERE / 'CURRENT-EPOCH.json').read_text())
before = a.verify_current(h, ROOT, ENV, epoch)
save(HERE / 'CHECKPOINT-BEFORE.json', before)
base = json.loads((SNAPSHOT / 'BASE.json').read_text())
pins = json.loads((SNAPSHOT / 'SOURCE-PINS.json').read_text())
patch = SNAPSHOT / 'unfinished.patch'
assert sha(patch) == base['patch_sha256']
for name, expected in pins.items():
    assert sha(ROOT / name) == expected, name
with tempfile.TemporaryDirectory(prefix='css-snapshot-index-', dir='/private/tmp') as scratch:
    isolated = dict(ENV, GIT_INDEX_FILE=str(Path(scratch) / 'index'))
    git('read-tree', base['commit'], env=isolated)
    git('apply', '--cached', '--check', str(patch), env=isolated)
    git('apply', '--cached', str(patch), env=isolated)
    assert set(git('diff', '--cached', '--name-only', base['commit'], env=isolated).decode().splitlines()) == set(pins)
    for name, expected in pins.items():
        assert hashlib.sha256(git('show', ':' + name, env=isolated)).hexdigest() == expected, name
    git('apply', '--cached', '--reverse', str(patch), env=isolated)
    assert git('write-tree', env=isolated).strip() == git('rev-parse', base['commit'] + '^{tree}').strip()
save(SNAPSHOT / 'CHECK.json', {'status': 'EXACT_PATCH_ROUNDTRIP_PASS', 'paths': len(pins), 'source_bodies_unchanged': True, 'temporary_index_removed': True, 'build_or_browser_validation': False})
save(SNAPSHOT / 'FILES.json', {p.name: sha(p) for p in sorted(SNAPSHOT.iterdir()) if p.is_file()})
library = json.loads((HERE / 'LIBRARY-RESULT.json').read_text())
research = json.loads((HERE / 'RESEARCH-RESULTS.json').read_text())
lib_commit = library['commit']
animation_commit, steps_commit = [entry['commit'] for entry in research]
assert all(entry['signature_verified'] for entry in [library, *research])
report = f'''# Signed local checkpoints, 2026-10-27

| Repository | Commit | Contents |
|---|---|---|
| CSS library | `{lib_commit}` | 64 source files; all 2,153 verification source fingerprints still match the passing report. |
| Firefox | `{animation_commit}` | Animation ownership proposals, regression evidence, failed attempts and remaining obligations. |
| Firefox | `{steps_commit}` | Steps admission baseline, specification trace, reviewed repair proposal and standalone Lean companion. |

Signatures and exact committed file bodies were verified. The CSS library working changes and prior staging are now committed; only its unrelated `.DS_Store` remains untracked. The recorded integrated proof result is 11,830 audits, 12,424 executable cases and 170 expected-false cases. This signing session checked every recorded source fingerprint; it did not repeat compilation or browser execution.

The [unfinished-work snapshot](../css-unfinished-work-checkpoint-20261027-v1/README.md) preserves all 132 remaining project working files as an exact, reversible patch. This includes 57 modified tracked files and 75 new project files. It excludes unrelated untracked directories and build outputs. The patch was applied to its recorded base in an isolated index, every resulting body was checked, and reversal restored the exact base tree. Native working files remain in place for continued development.

There are still 131 accepted browser fixes, all committed individually. These checkpoints add no accepted bug. Compact borrowing still needs actual compilation and native tests after two Cargo setup failures. The steps proposal still needs lint, compilation and fresh baseline/candidate/restoration browser comparisons. Its separate Lean model has 10 audits, 11 examples and three false controls; it is not yet integrated into the canonical totals and proves no native refinement.

Nothing was pushed or submitted. The source and binary preservation checks are recorded with the signing receipts. Historical epochs retain their original HEAD/index bindings; continued work must use `FINAL-EPOCH.json` from this signing runtime.
'''
assert base['tracked_paths'] == 57 and base['untracked_project_paths'] == 75
(HERE / 'CHECKPOINT.md').write_text(report)
plan_path = ROOT / 'artifacts/stylo-bloom-tools/PLAN-OF-RECORD.md'
ledger_path = ROOT / 'artifacts/stylo-bloom-tools/BUGFIX-COMMITS.md'
old_plan = plan_path.read_text()
old_ledger = ledger_path.read_text()
save(HERE / 'DOCUMENT-PREIMAGES.json', {str(p.relative_to(ROOT)): sha(p) for p in [plan_path, ledger_path]})
marker = '## Latest verified work\n\n'
assert marker in old_plan
new_plan = old_plan.replace(marker, marker + f'- Latest signed checkpoints: CSS library `{lib_commit[:12]}` in its own repository; animation research `{animation_commit[:12]}` and steps research `{steps_commit[:12]}` on the Firefox branch. The [signing record](../css-local-signing-20261027-v1/CHECKPOINT.md) includes an exact recovery snapshot of 132 unfinished working files. Accepted bug counts are unchanged.\n', 1)
old_step2 = next(line for line in new_plan.splitlines() if line.startswith('2. **Complete current-provider'))
new_step2 = '2. **Complete current-provider animation resolution.** The compact-owner build failed the existing 32-byte declaration-block size assertion. A reviewed one-word borrowed representation is applied, but two isolated test attempts stopped during Cargo setup before compilation. Run those unit/doctests, rebuild the host and run all 17 selected GTests before refreshing the 166-outcome browser comparison. Then connect retained endpoint recipes to winning providers and repair the four calibrated failures. Ownership, animated cycles, recipe errors and complete memory reporting remain open. [Borrow review](../css-keyframe-compact-source-borrow-review-v2/REPORT.md).'
new_plan = new_plan.replace(old_step2, new_step2)
old_step3 = next(line for line in new_plan.splitlines() if line.startswith('3. **Resolve the contextual'))
new_step3 = '3. **Validate isolated calculated `steps()` admission.** The context-free `jump-none` baseline has 16 targeted admission failures and two passing literal controls. The specification trace resolves the calculated NaN case to count two; the reviewed proposal preserves literal and unresolved-context rejection. Run lint and fresh original/candidate/restored comparisons over its 77-case roster. The standalone Lean companion passes 10 audits, 11 examples and three false controls, with no native-refinement claim. Contextual integers and the broader `round()` lead remain separate; held repair 120 stays excluded. [Proposal](../css-steps-jump-none-repair-v2/README.md), [model](../css-steps-origin-clamping-model-v1/REPORT.md).'
new_plan = new_plan.replace(old_step3, new_step3)
plan_path.write_text(new_plan)
old_intro = old_ledger.split('\n\n')[1]
new_intro = f'Latest checkpoint: CSS library `{lib_commit[:12]}` is signed in its own repository; animation research `{animation_commit[:12]}` and steps research `{steps_commit[:12]}` are signed on this branch. An exact recovery patch preserves the unfinished native/proof-tool work. All 131 accepted fixes remain committed, with repair 120 held and excluded; these checkpoints add no accepted bug. See the [signing record](../css-local-signing-20261027-v1/CHECKPOINT.md) and current [plan of record](PLAN-OF-RECORD.md).'
ledger_path.write_text(old_ledger.replace(old_intro, new_intro, 1))
for document in [plan_path, HERE / 'CHECKPOINT.md', SNAPSHOT / 'README.md']:
    for target in re.findall(r'\]\(([^)]+)\)', document.read_text()):
        if '://' not in target and not target.startswith('#'):
            assert (document.parent / target.split('#')[0]).exists(), (document, target)
selected = [
    'commit-library.py', 'commit-research.py', 'seal-checkpoint.py',
    'LIBRARY-RESULT.json', 'LIBRARY-PINS.json', 'LIBRARY-VERIFICATION.json',
    'library-signature.log', 'RESEARCH-RESULTS.json', 'CHECKPOINT.md',
    'animation-research-receipt.json', 'animation-research-signature.log',
    'steps-research-receipt.json', 'steps-research-signature.log',
]
files = {str((HERE / name).relative_to(ROOT)): sha(HERE / name) for name in selected}
files.update({str(path.relative_to(ROOT)): sha(path) for path in SNAPSHOT.iterdir() if path.is_file()})
files.update({str(path.relative_to(ROOT)): sha(path) for path in [plan_path, ledger_path]})
item = {'id': 'recovery-checkpoint', 'expected_head': before['index']['head'], 'message': 'No bug - Preserve unfinished CSS work and update signed checkpoints.', 'files': sorted(files), 'source_pins': files}
save(HERE / 'recovery-checkpoint-item.json', item)
with (HERE / 'recovery-checkpoint-driver.log').open('w') as stream:
    result = subprocess.run(['python3', '-I', '-S', '-B', str(HERE / 'commit-item.py'), str(HERE / 'recovery-checkpoint-item.json')], cwd=ROOT, env=ENV, stdout=stream, stderr=subprocess.STDOUT)
assert result.returncode == 0, 'See driver log; preserve staging on failure'
commit = git('rev-parse', 'HEAD').decode().strip()
for name, expected in files.items():
    assert hashlib.sha256(git('show', commit + ':' + name)).hexdigest() == expected
with (HERE / 'recovery-checkpoint-signature.log').open('w') as stream:
    subprocess.run(GIT + ['-c', 'gpg.ssh.allowedSignersFile=' + str(HERE / 'allowed-signers'), 'verify-commit', commit], cwd=ROOT, env=ENV, stdout=stream, stderr=subprocess.STDOUT, check=True)
current = copy.deepcopy(epoch)
state = h.index_state(ROOT, ENV)
assert state['working_diff'] == before['index']['working_diff']
assert state['cached_diff'] == before['index']['cached_diff']
assert h.index_state(ROOT / 'artifacts/css-spec-lean', ENV) == before['nested_index']
current['semantic_index'] = h.semantic_index(state)
current['raw_index_observation']['current'] = state['raw_index']
for name, expected in files.items():
    if name in current['pins']:
        current['pins'][name] = h.fingerprint(ROOT, name)
    current['committed_research_working_payloads'][name] = expected
current['counts']['committed_research_payloads'] = len(current['committed_research_working_payloads'])
after = a.verify_current(h, ROOT, ENV, current)
save(HERE / 'FINAL-AFTER.json', after)
save(HERE / 'FINAL-EPOCH.json', current)
save(HERE / 'FINAL-RESULT.json', {'status': 'SIGNED_CHECKPOINTS_AND_RECOVERY_VERIFIED', 'commit': commit, 'signature_verified': True, 'root_index_empty': True, 'nested_index_empty': True, 'native_and_binary_bodies_preserved': True, 'recovery_patch_paths': len(pins), 'new_accepted_bugs': 0})
print('Signed recovery checkpoint:', commit, flush=True)
