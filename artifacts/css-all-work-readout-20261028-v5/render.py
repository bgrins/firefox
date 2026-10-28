import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
OLD = ROOT / 'artifacts/css-all-work-readout-20261028-v4'
GROUP = 'Parsing, tokens and CSS math'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text())


def git(*args):
    env = dict(os.environ, GIT_OPTIONAL_LOCKS='0')
    return subprocess.check_output(['git', *args], cwd=ROOT, env=env, text=True).strip()


def main():
    signing = ROOT / sys.argv[1]
    assert signing.resolve() == ROOT / 'artifacts/css-local-signing-20261028-v42'
    assert digest(OLD / 'FILES.json') == '05bc7a6ff01aae39b24de938abee442f3de2f15bfd30a801470cbe12fbb6b547'
    for name, sha in read(OLD / 'FILES.json').items():
        assert digest(OLD / name) == sha
    inputs = read(signing / 'INPUTS.json')
    acceptance_path = ROOT / inputs['acceptance_path']
    assert digest(acceptance_path) == inputs['acceptance_sha256']
    acceptance = read(acceptance_path)
    assert acceptance['status'] == 'READY_FOR_STANDALONE_SIGNED_COMMIT'
    assert acceptance['fix'] == inputs['fix'] == 145
    for gate in ('promoted_build_passed', 'promoted_wpt_passed', 'wpt_lint_passed'):
        assert acceptance[gate] is True
    assert acceptance['target_pass'] == 25
    assert acceptance['regressions_unchanged'] == 712
    assert acceptance['ends_unchanged'] == 12
    for name, sha in acceptance['evidence_pins'].items():
        assert digest(ROOT / name) == sha
    receipts = {kind: read(signing / f'{kind}-receipt.json')
                for kind in ('research', 'validation', 'native-fix')}
    for receipt in receipts.values():
        assert receipt['signature_verified'] is True
        assert receipt['working_bodies_and_nested_index_preserved'] is True
        assert git('rev-parse', receipt['commit'] + '^{tree}') == receipt['tree']
        assert git('rev-parse', receipt['commit'] + '^') == receipt['parent']
    assert receipts['validation']['parent'] == receipts['research']['commit']
    assert receipts['native-fix']['parent'] == receipts['validation']['commit']
    expected = {'servo/components/style/values/generics/calc.rs',
                'testing/web-platform/tests/css/css-values/round-context-quotient-precision.html'}
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
    data = read(OLD / 'ACCEPTED-FIXES.json')
    assert data['accepted'] == 143 and data['tracked'] == 144
    assert len(data['fixes']) == 143 and all(item['fix'] != 145 for item in data['fixes'])
    entry = copy.deepcopy(acceptance['ledger_entry'])
    entry.update(fix=145, native_commit=native,
                 research_commit=receipts['research']['commit'],
                 validation_commit=receipts['validation']['commit'],
                 acceptance={'path': inputs['acceptance_path'], 'sha256': inputs['acceptance_sha256']},
                 status='COMMITTED_NATIVE_WPT', signature_verified=True)
    subject = git('show', '-s', '--format=%s', native)
    data['fixes'].append({'group': GROUP, 'ledger_record': entry, 'fix': 145,
                         'native_commit': native, 'subject': subject,
                         'evidence_commits': [receipts[k]['commit'] for k in ('research', 'validation')]})
    data.update(head=head, accepted=144, tracked=145)
    data['group_counts'][GROUP] += 1
    assert len(data['fixes']) == sum(data['group_counts'].values()) == 144
    assert data['held_fix_ids'] == [120]
    checks = read(OLD / 'COMMIT-CHECK.json')['checks']
    for receipt in receipts.values():
        checks[receipt['commit']] = {'subject': git('show', '-s', '--format=%s', receipt['commit'])}
    for commit, item in checks.items():
        git('merge-base', '--is-ancestor', commit, head)
        item['ancestor_of_head'] = True
    text = (OLD / 'README.md').read_text()
    oldhead = read(OLD / 'ACCEPTED-FIXES.json')['head']
    text = text.replace('**143 accepted native fixes', '**144 accepted native fixes')
    text = text.replace('IDs run through 144', 'IDs run through 145').replace(oldhead, head)
    text = text.replace('All 143 accepted native commits', 'All 144 accepted native commits')
    text = text.replace('315 distinct commits checked', f'{len(checks)} distinct commits checked')
    text = text.replace('| Parsing, tokens and CSS math | 28 |', '| Parsing, tokens and CSS math | 29 |')
    text = text.replace('| **Total** | **143** |', '| **Total** | **144** |')
    text = text.replace('Counts are local repairs,', 'Append finite Round quotient repair 145 to Parsing, tokens and CSS math. Counts are local repairs,')
    title = subject.removeprefix('No bug - ').split('. r?')[0].replace('|', '\\|')
    row = f"| 145 | {title} | `{native[:12]}` | " + ', '.join(f"`{receipts[k]['commit'][:12]}`" for k in ('research', 'validation')) + ' |\n\n'
    assert text.count('### Attributes and custom properties\n') == 1
    text = text.replace('\n\n### Attributes and custom properties\n', '\n' + row + '### Attributes and custom properties\n')
    scope = ('Fix 145 repairs premature quotient rounding and overflow in finite runtime Round evaluation. '
             'The complete paired 738-case experiment passed all 26 targets with 13 repairs; all 712 controls and twelve endings were preserved. '
             'The standalone commit contains one Rust file and one 21-case WPT page. Four exposure cases remain validation-only. '
             'Final validation runs 737 cases with 25 target PASS, 712 unchanged control signatures and twelve endings: 727 PASS and ten existing FAIL. '
             'The only omitted historical assertion is the redundant both-infinite row, which passed in both complete paired phases and belongs to fix144; the exact one-line projection is authenticated without waiving a failed gate. '
             'No semantic dependency on accepted125/126/128/144 was established for this finite-only patch; those repairs remain preservation controls. No independent cherry-pick or clean-upstream execution is claimed. '
             'Historical fix144 source and commit pins remain immutable, with the later source replacement explicitly recorded. '
             'These local builds include the unrelated held provider prototype. Existing scalar arithmetic checks, conditional interval lemmas and the bounded overflow witness do not establish universal IEEE or native refinement and add no canonical Lean coverage.\n\n')
    text = text.replace('## Research and prototypes — excluded from accepted counts', scope + '## Research and prototypes — excluded from accepted counts')
    text = text.replace('prepared for the v41 checkpoint', 'prepared for the v42 checkpoint')
    references = {str((OLD / 'FILES.json').relative_to(ROOT)): digest(OLD / 'FILES.json'),
                  inputs['acceptance_path']: inputs['acceptance_sha256'],
                  str((signing / 'native-selection.json').relative_to(ROOT)): digest(signing / 'native-selection.json')}
    for kind in receipts:
        p = signing / f'{kind}-receipt.json'
        references[str(p.relative_to(ROOT))] = digest(p)
    outputs = {'ACCEPTED-FIXES.json': data,
               'COMMIT-CHECK.json': {'head': head, 'native_fixes': 144, 'unique_checked_commits': len(checks), 'checks': checks},
               'REFERENCES.json': references,
               'CHECK.json': {'status': 'PASS', 'head': head, 'accepted_rows': 144, 'held120_excluded': True,
                              'new_fix': 145, 'target_pass': 25, 'observed_repairs': 13, 'accepted_dependencies': [],
                              'fresh_signature_browser_compiler_or_Lean_execution': False}}
    assert not any((HERE / name).exists() for name in outputs)
    for name, value in outputs.items():
        (HERE / name).write_text(json.dumps(value, indent=2) + '\n')
    (HERE / 'README.md').write_text(text)
    print(json.dumps({'head': head, 'accepted': 144, 'tracked': 145, 'group_counts': data['group_counts']}))


if __name__ == '__main__':
    main()
