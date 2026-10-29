import copy
import hashlib
import json
import os
import runpy
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
OLD = ROOT / 'artifacts/css-all-work-readout-20261028-v7'
GROUP = 'Animations, timelines and transitions'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text())


def git(*args):
    env = dict(os.environ, GIT_OPTIONAL_LOCKS='0')
    return subprocess.check_output(['git', *args], cwd=ROOT, env=env, text=True).strip()


def main():
    signing = ROOT / sys.argv[1]
    assert signing.resolve() == ROOT / 'artifacts/css-local-signing-20261029-v54'
    assert digest(OLD / 'FILES.json') == 'fbd065766f1a46ead8a4c12dc047d81066960e7be242f6eb55497f199ee15301'
    for name, sha in read(OLD / 'FILES.json').items():
        assert digest(OLD / name) == sha
    inputs = read(signing / 'INPUTS.json')
    assert inputs['execution_enabled'] and inputs['final_validation_ready'] and inputs['publication_enabled']
    shape_path = signing / 'ROOT-NATIVE-SHAPE-AUDIT.json'
    assert digest(shape_path) == '3d8fe5f8205baf11830005351b1fac2a92948bfa2d4e835a33537e57ec401122'
    shape = read(shape_path)
    assert shape['accepted_native_commits'] == 146 and shape['commits_with_artifacts_paths'] == 0
    assert shape['commits_with_wpt'] == 146 and shape['dependency_free_cherry_pick_claim'] is False
    assert isinstance(inputs['fix'], int) and inputs['fix'] > 0
    revalidation = signing / 'final_validation.py'
    assert digest(revalidation) == inputs['references'][str(revalidation.relative_to(ROOT))]
    runpy.run_path(str(revalidation))['verify'](ROOT, inputs)
    new_fix = inputs['fix']
    acceptance_path = ROOT / inputs['acceptance_path']
    assert digest(acceptance_path) == inputs['acceptance_sha256']
    acceptance = read(acceptance_path)
    assert acceptance['status'] == 'READY_FOR_STANDALONE_SIGNED_COMMIT'
    assert acceptance['fix'] == new_fix
    for gate in ('promoted_build_passed', 'promoted_wpt_passed', 'wpt_lint_passed'):
        assert acceptance[gate] is True
    assert acceptance['target_pass'] == 8
    assert acceptance['repaired_target_subtests'] == 8
    assert acceptance['accepted_dependencies'] == []
    assert acceptance['group'] == inputs['accepted_group'] == GROUP
    assert acceptance['regressions_unchanged'] == 90
    assert acceptance['ends_unchanged'] == 16
    assert acceptance['landing_wpt_subtests'] == 29 and acceptance['final_wpt_exit'] == 0
    assert acceptance['supplemental_validation'] == {'pass': 8, 'repaired_targets': 2, 'regressions_unchanged': 6, 'ends_unchanged': 1, 'exit': 0}
    assert acceptance['root_acceptance_approved'] is True
    assert acceptance['evidence_pins'] == inputs['evidence_pins'] and inputs['evidence_pins']
    for name, sha in acceptance['evidence_pins'].items():
        assert digest(ROOT / name) == sha
    receipts = {kind: read(signing / f'{kind}-receipt.json')
                for kind in ('research', 'validation', 'native-fix')}
    for receipt in receipts.values():
        assert receipt['signature_verified'] is True
        assert receipt['working_bodies_and_nested_index_preserved'] is True
        assert git('rev-parse', receipt['commit'] + '^{tree}') == receipt['tree']
        assert git('rev-parse', receipt['commit'] + '^') == receipt['parent']
    assert receipts['research']['parent'] == inputs['initial_head']
    assert receipts['validation']['parent'] == receipts['research']['commit']
    assert receipts['native-fix']['parent'] == receipts['validation']['commit']
    writes = {'dom/base/Element.cpp', 'dom/base/ShadowRoot.cpp', 'dom/base/ShadowRoot.h',
              'testing/web-platform/tests/dom/nodes/moveBefore/shadow-descendant-css-animation-preserve.html',
              'testing/web-platform/tests/dom/nodes/moveBefore/shadow-descendant-custom-element-reactions.html',
              'testing/web-platform/tests/dom/nodes/moveBefore/shadow-descendant-iframe-preserve.html',
              'testing/web-platform/tests/dom/nodes/moveBefore/shadow-move-controls.html'}
    deleted = 'testing/web-platform/meta/dom/nodes/moveBefore/custom-element-move-reactions.html.ini'
    expected = writes | {deleted}
    native = receipts['native-fix']['commit']
    selection = read(signing / 'native-selection.json')
    assert digest(signing / 'native-selection.json') == acceptance['payload_sha256']
    assert set(selection['source_pins']) == writes and set(selection['files']) == expected
    assert set(selection['deleted_preimages']) == {deleted}
    assert set(receipts['native-fix']['files']) == expected
    assert set(git('diff-tree', '--no-commit-id', '--name-only', '-r', native).splitlines()) == expected
    for name, sha in selection['source_pins'].items():
        body = subprocess.check_output(['git', 'show', native + ':' + name], cwd=ROOT,
                                       env=dict(os.environ, GIT_OPTIONAL_LOCKS='0'))
        assert hashlib.sha256(body).hexdigest() == sha
    helper = signing / 'deletion.py'
    assert digest(helper) == inputs['references'][str(helper.relative_to(ROOT))]
    runpy.run_path(str(helper))['verify'](ROOT, inputs, read(signing / 'CURRENT-EPOCH.json'), selection, receipts['native-fix']['parent'], native)
    head = git('rev-parse', 'HEAD')
    assert head == native
    data = read(OLD / 'ACCEPTED-FIXES.json')
    assert data['accepted'] == inputs['previous_accepted_fixes'] == 146 and data['tracked'] == 147
    assert new_fix == data['tracked'] + 1
    new_count = data['accepted'] + 1
    old_group_count = data['group_counts'][GROUP]
    assert len(data['fixes']) == 146 and all(item['fix'] != new_fix for item in data['fixes'])
    old_records = copy.deepcopy(data['fixes'])
    entry = copy.deepcopy(acceptance['ledger_entry'])
    entry.update(fix=new_fix, native_commit=native,
                 research_commit=receipts['research']['commit'],
                 validation_commit=receipts['validation']['commit'],
                 acceptance={'path': inputs['acceptance_path'], 'sha256': inputs['acceptance_sha256']},
                 status='COMMITTED_NATIVE_WPT', signature_verified=True)
    subject = git('show', '-s', '--format=%s', native)
    data['fixes'].append({'group': GROUP, 'ledger_record': entry, 'fix': new_fix,
                         'native_commit': native, 'subject': subject,
                         'evidence_commits': [receipts[k]['commit'] for k in ('research', 'validation')]})
    data.update(head=head, accepted=new_count, tracked=new_fix)
    data['group_counts'][GROUP] += 1
    assert len(data['fixes']) == sum(data['group_counts'].values()) == new_count
    assert data['fixes'][:-1] == old_records
    assert data['held_fix_ids'] == [120]
    checks = read(OLD / 'COMMIT-CHECK.json')['checks']
    for receipt in receipts.values():
        checks[receipt['commit']] = {'subject': git('show', '-s', '--format=%s', receipt['commit'])}
    for commit, item in checks.items():
        git('merge-base', '--is-ancestor', commit, head)
        item['ancestor_of_head'] = True
    text = (OLD / 'README.md').read_text()
    oldhead = read(OLD / 'ACCEPTED-FIXES.json')['head']
    text = text.replace('**146 accepted native fixes', f'**{new_count} accepted native fixes')
    text = text.replace('IDs run through 147', f'IDs run through {new_fix}').replace(oldhead, head)
    text = text.replace('All 146 accepted native commits', f'All {new_count} accepted native commits')
    text = text.replace('324 distinct commits checked', f'{len(checks)} distinct commits checked')
    text = text.replace(f'| {GROUP} | {old_group_count} |', f'| {GROUP} | {old_group_count + 1} |')
    text = text.replace('| **Total** | **146 |', f'| **Total** | **{new_count}** |')
    text = text.replace('28 October 2026', '29 October 2026')
    text = text.replace('Separate fix commits do not imply dependency-free cherry-picks.', 'Separate fix commits do not imply dependency-free cherry-picks. Root separately checked all 146 prior native diff-trees: none contain artifacts paths and all include WPT, including fix4 in the Mozilla WPT tree. The new native receipt verifies the exact standalone eight-path payload.')
    text = text.replace('Counts are local repairs,', f'Append shadow move-context preservation repair {new_fix} to {GROUP}. Counts are local repairs,')
    title = subject.removeprefix('No bug - ').split('. r?')[0].replace('|', '\\|')
    row = f"| {new_fix} | {title} | `{native[:12]}` | " + ', '.join(f"`{receipts[k]['commit'][:12]}`" for k in ('research', 'validation')) + ' |\n\n'
    assert text.count('### Text and fonts\n') == 1
    text = text.replace('\n\n### Text and fonts\n', '\n' + row + '### Text and fonts\n')
    scope = (f'Fix {new_fix} preserves move context through shadow-root traversal, covering CSS animation identity, custom-element move reactions and iframe state. '
             'The standalone payload contains three DOM sources, four WPT pages with 29 callbacks, and deletion of obsolete custom-element expected-FAIL metadata. '
             'Source review and browser witnesses preceded the scoped mathematical companion. The original/candidate primary pair repaired eight failures: 90 PASS / 8 FAIL became 98 PASS, preserving 90 controls and 16 endings. '
             'The historical candidate child exit 1 reflects the unchanged expected-FAIL row passing. The separate iframe original had six PASS and two FAIL with one OK ending. '
             'Final installed validation passed 98 primary callbacks and eight separate iframe callbacks on the same compiled application, with 16 and one OK endings respectively and child exits 0. '
             'These local Gecko runs retain the held provider prototype and configured preferences; no clean-upstream or Servo-only execution is claimed. '
             'The scoped companion supplies abstract support, not native refinement or canonical Lean coverage. The ownership-v2 correction and known bug 1458189 declaring-root observation remain separate future-easing research with no duplicate discovery credit.\n\n')
    text = text.replace('## Research and prototypes — excluded from accepted counts', scope + '## Research and prototypes — excluded from accepted counts')
    text = text.replace('prepared for the v52 checkpoint', 'prepared for the v54 checkpoint')
    text = text.replace('The separate shadow move-context proposal and system-browser observations remain unaccepted research.', 'At that historical checkpoint, the separate shadow move-context proposal remained unaccepted; the later acceptance is recorded below.')
    text = text.replace('Configured native groundwork and models exist; complete lifecycle/dependency publication and targetless API policy remain unfinished.', 'Configured native groundwork and the corrected ownership-v2 model exist; the next nineteen-case comparison remains pending. The separate literal declaring-root observation reproduces known bug 1458189, while contextual syntax readiness remains unestablished. Complete lifecycle/dependency publication and targetless API policy remain unfinished.')
    references = {str((OLD / 'FILES.json').relative_to(ROOT)): digest(OLD / 'FILES.json'),
                  inputs['acceptance_path']: inputs['acceptance_sha256'],
                  str((signing / 'native-selection.json').relative_to(ROOT)): digest(signing / 'native-selection.json')}
    references[str(shape_path.relative_to(ROOT))] = digest(shape_path)
    for kind in receipts:
        p = signing / f'{kind}-receipt.json'
        references[str(p.relative_to(ROOT))] = digest(p)
    assert f'| **Total** | **{new_count}** |' in text
    assert text.count(f'| {new_fix} |') == 1
    outputs = {'ACCEPTED-FIXES.json': data,
               'COMMIT-CHECK.json': {'head': head, 'native_fixes': new_count, 'unique_checked_commits': len(checks), 'checks': checks},
               'REFERENCES.json': references,
               'CHECK.json': {'status': 'PASS', 'head': head, 'accepted_rows': new_count, 'held120_excluded': True,
                              'new_fix': new_fix, 'target_pass': 8, 'observed_repairs': 8, 'regressions_unchanged': 90, 'ends_unchanged': 16, 'supplemental_pass': 8, 'supplemental_repairs': 2, 'supplemental_controls': 6, 'supplemental_ends': 1, 'deleted_metadata_verified': True, 'accepted_dependencies': [],
                              'prior_native_shape_audit_root_reported': shape,
                              'fresh_signature_browser_compiler_or_Lean_execution': False}}
    assert not any((HERE / name).exists() for name in (*outputs, 'README.md'))
    for name, value in outputs.items():
        (HERE / name).write_text(json.dumps(value, indent=2) + '\n')
    (HERE / 'README.md').write_text(text)
    print(json.dumps({'head': head, 'accepted': new_count, 'tracked': new_fix, 'group_counts': data['group_counts']}))


if __name__ == '__main__':
    main()
