import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
GIT = ['git', '-c', 'core.fsmonitor=false']


def git(*args, env=None, data=None):
    return subprocess.check_output(GIT + list(args), cwd=ROOT, env=env, input=data)


def text(*args, env=None):
    return git(*args, env=env).decode().strip()


def paths(commit):
    return git('diff-tree', '--no-commit-id', '--name-only', '--no-renames', '-r', '-z', commit).split(b'\0')[:-1]


def identity(tree, path):
    return git('ls-tree', '-z', tree, '--', path.decode())


def main():
    plan = json.loads((HERE / 'PLAN.json').read_text())
    assert not (ROOT / '.jj').exists()
    for name in ['CONSTRUCTION.json', 'RANGE-DIFF.txt', 'RESULT.json']:
        path = str((HERE / name).relative_to(ROOT))
        assert text('check-ignore', path) == path
        assert not (HERE / name).exists(), ('preexisting output', name)
    branch = text('symbolic-ref', 'HEAD')
    assert branch == plan['branch'] and text('rev-parse', 'HEAD') == plan['old_head']
    assert not git('diff', '--name-only') and not git('diff', '--cached', '--name-only')
    untracked = git('ls-files', '--others', '--exclude-standard', '-z')
    index = hashlib.sha256(git('ls-files', '--stage', '-z')).hexdigest()
    expected = text('rev-list', '--reverse', plan['base'] + '..' + plan['old_head']).splitlines()
    originals = [old for leaf in plan['leaves'] for old in leaf['originals']]
    assert len(originals) == len(set(originals)) and set(originals) == set(expected)
    assert not text('log', '--format=%H', '--grep=^Differential Revision:', plan['base'] + '..' + plan['old_head'])
    git('branch', plan['backup_branch'], plan['old_head'])
    records = []
    parent = plan['base']
    with tempfile.TemporaryDirectory(prefix='css-keyframe-rebuild-') as temp:
        env = dict(os.environ, GIT_INDEX_FILE=str(Path(temp) / 'index'))
        signer = text('config', 'user.signingkey')
        if Path(signer).is_file():
            signer = Path(signer).read_text().strip()
        allowed = Path(temp) / 'allowed_signers'
        allowed.write_text(text('config', 'user.email') + ' ' + signer + '\n')
        for leaf in plan['leaves']:
            git('read-tree', parent, env=env)
            for original in leaf['originals']:
                current = text('write-tree', env=env)
                for path in paths(original):
                    assert identity(current, path) == identity(original + '^', path), ('unexpected overlap', path)
                patch = git('diff', '--binary', '--no-renames', original + '^', original)
                git('apply', '--cached', '--check', '--whitespace=nowarn', env=env, data=patch)
                git('apply', '--cached', '--whitespace=nowarn', env=env, data=patch)
            tree = text('write-tree', env=env)
            source = leaf['originals'][0]
            author = text('show', '-s', '--format=%an%n%ae%n%aI', source).splitlines()
            message = leaf.get('message') or git('show', '-s', '--format=%B', source).decode()
            message_file = Path(temp) / 'message'
            message_file.write_text(message.rstrip() + '\n')
            signing_env = dict(env, GIT_AUTHOR_NAME=author[0], GIT_AUTHOR_EMAIL=author[1], GIT_AUTHOR_DATE=author[2])
            commit = text('commit-tree', '-S', tree, '-p', parent, '-F', str(message_file), env=signing_env)
            git('-c', 'gpg.ssh.allowedSignersFile=' + str(allowed), 'verify-commit', commit)
            assert text('show', '-s', '--format=%an%n%ae%n%aI', commit).splitlines() == author
            changed = [p.decode() for p in paths(commit)]
            if leaf['kind'] == 'research':
                assert all(p.startswith('artifacts/') for p in changed)
            else:
                assert leaf['kind'] == 'fix' and set(changed) == set(plan['native_paths'])
            native_reference = plan['old_head'] if leaf['native_fixed'] else plan['base']
            assert not git('diff', '--name-only', native_reference, commit, '--', '.', ':(exclude)artifacts')
            records.append({'originals': leaf['originals'], 'commit': commit, 'tree': tree,
                            'kind': leaf['kind'], 'changed_paths': changed, 'native_reference': native_reference})
            parent = commit
            (HERE / 'CONSTRUCTION.json').write_text(json.dumps(records, indent=2) + '\n')
            print(commit, leaf['kind'], flush=True)
    assert text('rev-parse', parent + '^{tree}') == text('rev-parse', plan['old_head'] + '^{tree}')
    assert text('rev-parse', 'HEAD') == plan['old_head']
    assert text('symbolic-ref', 'HEAD') == branch
    assert not git('diff', '--name-only') and not git('diff', '--cached', '--name-only')
    assert git('ls-files', '--others', '--exclude-standard', '-z') == untracked
    assert hashlib.sha256(git('ls-files', '--stage', '-z')).hexdigest() == index
    git('update-ref', '-m', 'Combine validated keyframe group-order repair', branch, parent, plan['old_head'])
    assert text('symbolic-ref', 'HEAD') == branch and text('rev-parse', 'HEAD') == parent
    assert not git('diff', plan['backup_branch'], 'HEAD')
    assert not git('diff', '--name-only') and not git('diff', '--cached', '--name-only')
    assert git('ls-files', '--others', '--exclude-standard', '-z') == untracked
    assert hashlib.sha256(git('ls-files', '--stage', '-z')).hexdigest() == index
    (HERE / 'RANGE-DIFF.txt').write_bytes(git('range-diff', '-s', plan['base'], plan['backup_branch'], 'HEAD'))
    report = {'status': 'PASS', 'old_head': plan['old_head'], 'new_head': parent,
              'backup_branch': plan['backup_branch'], 'identical_tree': True,
              'real_index_untouched': True, 'untracked_files_preserved': len(untracked.split(b'\0')) - 1,
              'all_rebuilt_commits_signed_and_verified': True, 'leaves': records}
    (HERE / 'RESULT.json').write_text(json.dumps(report, indent=2) + '\n')


if __name__ == '__main__':
    main()
