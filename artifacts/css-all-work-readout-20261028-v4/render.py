import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
OLD = ROOT / 'artifacts/css-all-work-readout-20261028-v3'
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
    assert signing.resolve() == ROOT / 'artifacts/css-local-signing-20261028-v41'
    assert digest(OLD / 'FILES.json') == '04c91a55603129ae915ed8a6eec5769e9af774430b2138aaa72fd4be9bbb55d7'
    for name, sha in read(OLD / 'FILES.json').items():
        assert digest(OLD / name) == sha
    inputs = read(signing / 'INPUTS.json')
    acceptance_path = ROOT / inputs['acceptance_path']
    assert digest(acceptance_path) == inputs['acceptance_sha256']
    acceptance = read(acceptance_path)
    assert acceptance['status'] == 'READY_FOR_STANDALONE_SIGNED_COMMIT'
    assert acceptance['fix'] == inputs['fix'] == 144
    for gate in ('promoted_build_passed', 'promoted_wpt_passed', 'wpt_lint_passed'):
        assert acceptance[gate] is True
    assert acceptance['target_pass'] == 23
    assert acceptance['regressions_unchanged'] == 689
    assert acceptance['ends_unchanged'] == 10
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
                'testing/web-platform/tests/css/css-values/round-deferred-infinite-step.html'}
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
    assert data['accepted'] == 142 and data['tracked'] == 143
    assert len(data['fixes']) == 142 and all(item['fix'] != 144 for item in data['fixes'])
    entry = copy.deepcopy(acceptance['ledger_entry'])
    entry.update(fix=144, native_commit=native,
                 research_commit=receipts['research']['commit'],
                 validation_commit=receipts['validation']['commit'],
                 acceptance={'path': inputs['acceptance_path'], 'sha256': inputs['acceptance_sha256']},
                 status='COMMITTED_NATIVE_WPT', signature_verified=True)
    subject = git('show', '-s', '--format=%s', native)
    data['fixes'].append({'group': GROUP, 'ledger_record': entry, 'fix': 144,
                         'native_commit': native, 'subject': subject,
                         'evidence_commits': [receipts[k]['commit'] for k in ('research', 'validation')]})
    data.update(head=head, accepted=143, tracked=144)
    data['group_counts'][GROUP] += 1
    assert len(data['fixes']) == sum(data['group_counts'].values()) == 143
    assert data['held_fix_ids'] == [120]
    checks = read(OLD / 'COMMIT-CHECK.json')['checks']
    for receipt in receipts.values():
        checks[receipt['commit']] = {'subject': git('show', '-s', '--format=%s', receipt['commit'])}
    for commit, item in checks.items():
        git('merge-base', '--is-ancestor', commit, head)
        item['ancestor_of_head'] = True
    text = (OLD / 'README.md').read_text()
    oldhead = read(OLD / 'ACCEPTED-FIXES.json')['head']
    text = text.replace('**142 accepted native fixes', '**143 accepted native fixes')
    text = text.replace('IDs run through 143', 'IDs run through 144').replace(oldhead, head)
    text = text.replace('All 142 accepted native commits', 'All 143 accepted native commits')
    text = text.replace('312 distinct commits checked', f'{len(checks)} distinct commits checked')
    text = text.replace('| Parsing, tokens and CSS math | 27 |', '| Parsing, tokens and CSS math | 28 |')
    text = text.replace('| **Total** | **142** |', '| **Total** | **143** |')
    text = text.replace('Counts are local repairs,', 'Append the infinite-step knowledge guard 144 to Parsing, tokens and CSS math. Counts are local repairs,')
    title = subject.removeprefix('No bug - ').split('. r?')[0].replace('|', '\\|')
    row = f"| 144 | {title} | `{native[:12]}` | " + ', '.join(f"`{receipts[k]['commit'][:12]}`" for k in ('research', 'validation')) + ' |\n\n'
    assert text.count('### Attributes and custom properties\n') == 1
    text = text.replace('\n\n### Attributes and custom properties\n', '\n' + row + '### Attributes and custom properties\n')
    scope = ('Fix 144 retains unresolved values in the literal-infinite-step Round simplifier. '
             'The paired run repairs 19 target failures; all 23 targets pass, while 689 control signatures and ten endings remain unchanged. '
             'The final installed build repeats the exact 712 cases: 702 PASS and ten existing FAIL. '
             'These local runs include the unrelated held provider prototype and accepted overlays; no clean-upstream browser run is claimed. '
             'Accepted fix125 (runtime NaN priority) is a prerequisite. The dual infinite-value/unknown-step branch, finite quotient arithmetic and broader contextual-easing work remain outside this repair. '
             'The four existing knowledge lemmas are reused without new proof-discovery or canonical coverage credit; no native refinement is claimed.\n\n')
    text = text.replace('## Research and prototypes — excluded from accepted counts', scope + '## Research and prototypes — excluded from accepted counts')
    text = text.replace('prepared for the v39 checkpoint', 'prepared for the v41 checkpoint')
    references = {str((OLD / 'FILES.json').relative_to(ROOT)): digest(OLD / 'FILES.json'),
                  inputs['acceptance_path']: inputs['acceptance_sha256'],
                  str((signing / 'native-selection.json').relative_to(ROOT)): digest(signing / 'native-selection.json')}
    for kind in receipts:
        p = signing / f'{kind}-receipt.json'
        references[str(p.relative_to(ROOT))] = digest(p)
    outputs = {'ACCEPTED-FIXES.json': data,
               'COMMIT-CHECK.json': {'head': head, 'native_fixes': 143, 'unique_checked_commits': len(checks), 'checks': checks},
               'REFERENCES.json': references,
               'CHECK.json': {'status': 'PASS', 'head': head, 'accepted_rows': 143, 'held120_excluded': True,
                              'new_fix': 144, 'target_pass': 23, 'observed_repairs': 19, 'prerequisite_fix': 125,
                              'fresh_signature_browser_compiler_or_Lean_execution': False}}
    assert not any((HERE / name).exists() for name in outputs)
    for name, value in outputs.items():
        (HERE / name).write_text(json.dumps(value, indent=2) + '\n')
    (HERE / 'README.md').write_text(text)
    print(json.dumps({'head': head, 'accepted': 143, 'tracked': 144, 'group_counts': data['group_counts']}))


if __name__ == '__main__':
    main()
