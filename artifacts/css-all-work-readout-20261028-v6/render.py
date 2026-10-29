import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
OLD = ROOT / 'artifacts/css-all-work-readout-20261028-v5'
GROUP = 'Selectors, Bloom filters and scoping'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text())


def git(*args):
    env = dict(os.environ, GIT_OPTIONAL_LOCKS='0')
    return subprocess.check_output(['git', *args], cwd=ROOT, env=env, text=True).strip()


def main():
    signing = ROOT / sys.argv[1]
    assert signing.resolve() == ROOT / 'artifacts/css-local-signing-20261028-v49'
    assert digest(OLD / 'FILES.json') == '3ac8b1f460a660edb436a0816b14afdf020cfd46e657e57a6dfeef91e6b5ea9f'
    for name, sha in read(OLD / 'FILES.json').items():
        assert digest(OLD / name) == sha
    inputs = read(signing / 'INPUTS.json')
    acceptance_path = ROOT / inputs['acceptance_path']
    assert digest(acceptance_path) == inputs['acceptance_sha256']
    acceptance = read(acceptance_path)
    assert acceptance['status'] == 'READY_FOR_STANDALONE_SIGNED_COMMIT'
    assert acceptance['fix'] == inputs['fix'] == 146
    for gate in ('promoted_build_passed', 'promoted_wpt_passed', 'wpt_lint_passed'):
        assert acceptance[gate] is True
    assert acceptance['target_pass'] == 2
    assert acceptance['repaired_target_subtests'] == 2
    assert acceptance['accepted_dependencies'] == []
    assert acceptance['group'] == inputs['accepted_group'] == GROUP
    assert acceptance['regressions_unchanged'] == 34
    assert acceptance['ends_unchanged'] == 7
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
    expected = {'servo/components/style/values/computed/mod.rs',
                'testing/web-platform/tests/css/css-values/tree-counting/sibling-count-cross-parent-invalidation.html'}
    native = receipts['native-fix']['commit']
    selection = read(signing / 'native-selection.json')
    assert digest(signing / 'native-selection.json') == acceptance['payload_sha256']
    assert set(selection['source_pins']) == set(selection['files']) == expected
    assert set(receipts['native-fix']['files']) == expected
    assert set(git('diff-tree', '--no-commit-id', '--name-only', '-r', native).splitlines()) == expected
    for name, sha in selection['source_pins'].items():
        body = subprocess.check_output(['git', 'show', native + ':' + name], cwd=ROOT,
                                       env=dict(os.environ, GIT_OPTIONAL_LOCKS='0'))
        assert hashlib.sha256(body).hexdigest() == sha
    head = git('rev-parse', 'HEAD')
    assert head == native
    data = read(OLD / 'ACCEPTED-FIXES.json')
    assert data['accepted'] == 144 and data['tracked'] == 145
    assert len(data['fixes']) == 144 and all(item['fix'] != 146 for item in data['fixes'])
    entry = copy.deepcopy(acceptance['ledger_entry'])
    entry.update(fix=146, native_commit=native,
                 research_commit=receipts['research']['commit'],
                 validation_commit=receipts['validation']['commit'],
                 acceptance={'path': inputs['acceptance_path'], 'sha256': inputs['acceptance_sha256']},
                 status='COMMITTED_NATIVE_WPT', signature_verified=True)
    subject = git('show', '-s', '--format=%s', native)
    data['fixes'].append({'group': GROUP, 'ledger_record': entry, 'fix': 146,
                         'native_commit': native, 'subject': subject,
                         'evidence_commits': [receipts[k]['commit'] for k in ('research', 'validation')]})
    data.update(head=head, accepted=145, tracked=146)
    data['group_counts'][GROUP] += 1
    assert len(data['fixes']) == sum(data['group_counts'].values()) == 145
    assert data['held_fix_ids'] == [120]
    checks = read(OLD / 'COMMIT-CHECK.json')['checks']
    for receipt in receipts.values():
        checks[receipt['commit']] = {'subject': git('show', '-s', '--format=%s', receipt['commit'])}
    for commit, item in checks.items():
        git('merge-base', '--is-ancestor', commit, head)
        item['ancestor_of_head'] = True
    text = (OLD / 'README.md').read_text()
    oldhead = read(OLD / 'ACCEPTED-FIXES.json')['head']
    text = text.replace('**144 accepted native fixes', '**145 accepted native fixes')
    text = text.replace('IDs run through 145', 'IDs run through 146').replace(oldhead, head)
    text = text.replace('All 144 accepted native commits', 'All 145 accepted native commits')
    text = text.replace('318 distinct commits checked', f'{len(checks)} distinct commits checked')
    text = text.replace('| Selectors, Bloom filters and scoping | 10 |', '| Selectors, Bloom filters and scoping | 11 |')
    text = text.replace('| **Total** | **144** |', '| **Total** | **145** |')
    text = text.replace('Counts are local repairs,', 'Append sibling-count reset-cache repair 146 to Selectors, Bloom filters and scoping. Counts are local repairs,')
    title = subject.removeprefix('No bug - ').split('. r?')[0].replace('|', '\\|')
    row = f"| 146 | {title} | `{native[:12]}` | " + ', '.join(f"`{receipts[k]['commit'][:12]}`" for k in ('research', 'validation')) + ' |\n\n'
    assert text.count('### Cascade, layers and shorthands\n') == 1
    text = text.replace('\n\n### Cascade, layers and shorthands\n', '\n' + row + '### Cascade, layers and shorthands\n')
    scope = ('Fix 146 excludes sibling-count-dependent reset values from the rule cache. '
             'The standalone commit contains one Rust file and a two-case WPT page for width and opacity across equal-style parents, including count mutations and restoration. '
             'The earlier six-case experiment repaired both reset-property targets while preserving four index/inherited controls. '
             'The focused original and candidate each ran 36 callbacks on seven pages: both landing targets improved, all 34 control signatures and seven endings were preserved. '
             'Final installed validation has both targets PASS, with 35 PASS and the one existing nested-pseudo-element FAIL overall. '
             'No semantic prerequisite among earlier accepted fixes was established for this one-line patch; existing tree-counting implementation is assumed. No clean-upstream build or independent cherry-pick execution is claimed. '
             'These local builds retain the unrelated held provider prototype and configured feature preferences. '
             'The equal-font abstract cache-alias witness and exclusion-lifetime lemmas clarify omitted-input and collection obligations; they are not a Gecko cache-hit proof or native refinement and add no canonical Lean coverage.\n\n')
    text = text.replace('## Research and prototypes — excluded from accepted counts', scope + '## Research and prototypes — excluded from accepted counts')
    text = text.replace('prepared for the v42 checkpoint', 'prepared for the v49 checkpoint')
    references = {str((OLD / 'FILES.json').relative_to(ROOT)): digest(OLD / 'FILES.json'),
                  inputs['acceptance_path']: inputs['acceptance_sha256'],
                  str((signing / 'native-selection.json').relative_to(ROOT)): digest(signing / 'native-selection.json')}
    for kind in receipts:
        p = signing / f'{kind}-receipt.json'
        references[str(p.relative_to(ROOT))] = digest(p)
    outputs = {'ACCEPTED-FIXES.json': data,
               'COMMIT-CHECK.json': {'head': head, 'native_fixes': 145, 'unique_checked_commits': len(checks), 'checks': checks},
               'REFERENCES.json': references,
               'CHECK.json': {'status': 'PASS', 'head': head, 'accepted_rows': 145, 'held120_excluded': True,
                              'new_fix': 146, 'target_pass': 2, 'observed_repairs': 2, 'accepted_dependencies': [],
                              'fresh_signature_browser_compiler_or_Lean_execution': False}}
    assert not any((HERE / name).exists() for name in outputs)
    for name, value in outputs.items():
        (HERE / name).write_text(json.dumps(value, indent=2) + '\n')
    (HERE / 'README.md').write_text(text)
    print(json.dumps({'head': head, 'accepted': 145, 'tracked': 146, 'group_counts': data['group_counts']}))


if __name__ == '__main__':
    main()
