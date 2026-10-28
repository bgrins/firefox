import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
OLD = ROOT / 'artifacts/css-all-work-readout-20261028-v1'
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
    assert signing.resolve() == ROOT / 'artifacts/css-local-signing-20261028-v39'
    assert digest(OLD / 'FILES.json') == 'dce686fc4bc81a6c334c8dd715189fc1e87f9caf0b7eaa0a0fc11b2d751cd8b5'
    for name, sha in read(OLD / 'FILES.json').items():
        assert digest(OLD / name) == sha
    inputs = read(signing / 'INPUTS.json')
    acceptance_path = ROOT / inputs['acceptance_path']
    assert digest(acceptance_path) == inputs['acceptance_sha256']
    acceptance = read(acceptance_path)
    assert acceptance['status'] == 'READY_FOR_STANDALONE_SIGNED_COMMIT'
    assert acceptance['fix'] == inputs['fix'] == 143
    for gate in ('promoted_build_passed', 'promoted_wpt_passed', 'wpt_lint_passed'):
        assert acceptance[gate] is True
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
    expected = {'servo/components/style/values/specified/easing.rs',
                'testing/web-platform/tests/css/css-easing/linear-contextual-second-position.html'}
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
    entry = copy.deepcopy(acceptance['ledger_entry'])
    entry.update(fix=143, native_commit=native,
                 research_commit=receipts['research']['commit'],
                 validation_commit=receipts['validation']['commit'],
                 acceptance={'path': inputs['acceptance_path'], 'sha256': inputs['acceptance_sha256']},
                 status='COMMITTED_NATIVE_WPT', signature_verified=True)
    subject = git('show', '-s', '--format=%s', native)
    data['fixes'].append({'group': GROUP, 'ledger_record': entry, 'fix': 143,
                         'native_commit': native, 'subject': subject,
                         'evidence_commits': [receipts[k]['commit'] for k in ('research', 'validation')]})
    data.update(head=head, accepted=142, tracked=143)
    data['group_counts'][GROUP] += 1
    assert len(data['fixes']) == sum(data['group_counts'].values()) == 142
    assert data['held_fix_ids'] == [120]
    checks = read(OLD / 'COMMIT-CHECK.json')['checks']
    for receipt in receipts.values():
        checks[receipt['commit']] = {'subject': git('show', '-s', '--format=%s', receipt['commit'])}
    for commit, item in checks.items():
        git('merge-base', '--is-ancestor', commit, head)
        item['ancestor_of_head'] = True
    text = (OLD / 'README.md').read_text()
    oldhead = read(OLD / 'ACCEPTED-FIXES.json')['head']
    text = text.replace('**141 accepted native fixes', '**142 accepted native fixes')
    text = text.replace('IDs run through 142', 'IDs run through 143').replace(oldhead, head)
    text = text.replace('All 141 accepted native commits', 'All 142 accepted native commits')
    text = text.replace('309 distinct commits checked', f'{len(checks)} distinct commits checked')
    text = text.replace('| Animations, timelines and transitions | 16 |', '| Animations, timelines and transitions | 17 |')
    text = text.replace('| **Total** | **141** |', '| **Total** | **142** |')
    text = text.replace('Counts are local repairs,', 'Append the linear guard 143 to Animations, timelines and transitions. Counts are local repairs,')
    title = subject.removeprefix('No bug - ').split('. r?')[0].replace('|', '\\|')
    row = f"| 143 | {title} | `{native[:12]}` | " + ', '.join(f"`{receipts[k]['commit'][:12]}`" for k in ('research', 'validation')) + ' |\n\n'
    text = text.replace('### Text and fonts\n', row + '### Text and fonts\n')
    lines = text.splitlines()
    lines = [line for line in lines if not line.startswith('| linear() second position |')]
    text = '\n'.join(lines) + '\n'
    text = text.replace('## Research and prototypes — excluded from accepted counts',
        'The linear guard 143 eliminates one reproduced content-process crash. Six target callbacks pass in the candidate; the original crashed before completing them, so this is not six FAIL-to-PASS repairs. The calibrated original baseline has 42 subtests and the candidate has 48; twelve existing regression FAIL signatures remain. The repair retains the existing contextual-easing rejection policy. No demonstrated memory corruption, security impact or complete easing-context implementation is claimed.\n\n## Research and prototypes — excluded from accepted counts')
    text = text.replace('prepared for the v38 research checkpoint', 'prepared for the v39 checkpoint after the signed native receipt')
    references = {str((OLD / 'FILES.json').relative_to(ROOT)): digest(OLD / 'FILES.json'),
                  inputs['acceptance_path']: inputs['acceptance_sha256'],
                  str((signing / 'native-selection.json').relative_to(ROOT)): digest(signing / 'native-selection.json')}
    for kind in receipts:
        p = signing / f'{kind}-receipt.json'
        references[str(p.relative_to(ROOT))] = digest(p)
    outputs = {'ACCEPTED-FIXES.json': data,
               'COMMIT-CHECK.json': {'head': head, 'native_fixes': 142, 'unique_checked_commits': len(checks), 'checks': checks},
               'REFERENCES.json': references,
               'CHECK.json': {'status': 'PASS', 'head': head, 'accepted_rows': 142, 'held120_excluded': True,
                              'new_fix': 143, 'single_crash_eliminated': True, 'six_target_fail_repairs_claimed': False,
                              'fresh_signature_browser_compiler_or_Lean_execution': False}}
    assert not any((HERE / name).exists() for name in outputs)
    for name, value in outputs.items():
        (HERE / name).write_text(json.dumps(value, indent=2) + '\n')
    (HERE / 'README.md').write_text(text)
    print(json.dumps({'head': head, 'accepted': 142, 'tracked': 143, 'group_counts': data['group_counts']}))


if __name__ == '__main__':
    main()
