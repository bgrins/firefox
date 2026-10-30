import collections
import hashlib
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
AUDIT = ROOT / 'artifacts/css-obsolete-build-target-audit-v1'
REVIEW = ROOT / 'artifacts/css-spec-lean/.lake/research-review'
ENV = dict(os.environ, GIT_OPTIONAL_LOCKS='0')
GIT = ['git', '--no-optional-locks', '-c', 'core.fsmonitor=false']
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def save(name, value):
    with (HERE / name).open('x') as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n')


def fingerprint(target):
    counts = collections.Counter()
    size = allocated = files = 0
    for current, dirs, names in os.walk(target, followlinks=False):
        for name in dirs:
            assert stat.S_ISDIR((Path(current) / name).lstat().st_mode)
        for name in names:
            path = Path(current) / name
            info = path.lstat()
            assert stat.S_ISREG(info.st_mode)
            assert path.suffix in {'.c', '.hash', '.ilean', '.json', '.olean', '.trace'}
            assert path.suffix != '.json' or path.name.endswith('.setup.json')
            counts[path.suffix] += 1
            files += 1
            size += info.st_size
            allocated += info.st_blocks * 512
    return {'file_count': files, 'apparent_file_bytes': size,
            'allocated_file_bytes': allocated, 'extensions': dict(counts)}


def state():
    runtime = ROOT / 'artifacts/css-registered-number-native-runtime-v1'
    result = {'controls': {n: sha(runtime / n) for n in ('CURRENT-EPOCH.json', 'OWNED.json', 'ROLE.json')}}
    for label, root in [('root', ROOT), ('lean', ROOT / 'artifacts/css-spec-lean')]:
        result[label] = {name: hashlib.sha256(subprocess.check_output(GIT + args, cwd=root, env=ENV)).hexdigest()
                        for name, args in [('head', ['rev-parse', 'HEAD']), ('status', ['status', '--porcelain=v1', '--untracked-files=all'])]}
    return result


def no_users(targets):
    processes = subprocess.check_output(['ps', '-axo', 'pid=,comm=,args='], text=True)
    for line in processes.splitlines():
        fields = line.strip().split(None, 2)
        if len(fields) < 2:
            continue
        assert Path(fields[1]).name not in ('lean', 'lake'), 'Lean/Lake process is active'
        assert str(REVIEW) not in line, 'Review process is active'
    cwd = subprocess.run(['lsof', '-nP', '-a', '-d', 'cwd', '-Fpn'], capture_output=True, text=True, timeout=30)
    assert cwd.returncode in (0, 1) and not cwd.stderr
    assert not any(line.startswith('n' + str(REVIEW)) for line in cwd.stdout.splitlines()), 'Review cwd is active'
    command = ['lsof', '-nP', '-Fpfn']
    for target in targets:
        command.extend(['+D', str(target)])
    result = subprocess.run(command, capture_output=True, text=True, timeout=90)
    assert result.returncode == 1 and not result.stdout and not result.stderr, (result.returncode, result.stdout, result.stderr)
    return {'no_lean_or_lake_process': True, 'no_review_command': True, 'no_review_cwd': True,
            'no_open_files_or_cwd_in_targets': True, 'lsof_exit': result.returncode}


def main():
    assert sys.argv[1:] == ['--run']
    assert not any(os.environ.get(k) for k in ('GIT_DIR', 'GIT_WORK_TREE', 'GIT_INDEX_FILE', 'GIT_OBJECT_DIRECTORY', 'GIT_ALTERNATE_OBJECT_DIRECTORIES'))
    assert not (HERE / 'RESULT.json').exists()
    assert sha(AUDIT / 'FILES.json') == 'b125c3bccd9375992088952a8dd0f375713c4f89fab90819dec85eb6d97b1fd1'
    for name, pin in json.loads((AUDIT / 'FILES.json').read_bytes()).items():
        assert sha(AUDIT / name) == (pin['sha256'] if isinstance(pin, dict) else pin)
    report = json.loads((AUDIT / 'REPORT.json').read_bytes())
    rows = [row for row in report['targets'] if row['eligible_after_fresh_root_checks']]
    assert len(rows) == 12
    targets = []
    retained = dict(report['canonical_dependency_declarations_have_no_research_review_reference'])
    epoch = json.loads((ROOT / 'artifacts/css-registered-number-native-runtime-v1/CURRENT-EPOCH.json').read_bytes())
    for row in rows:
        target = ROOT / row['target']
        assert target.resolve() == target and target.is_relative_to(REVIEW)
        assert target.relative_to(REVIEW).parts[1:] == ('.lake', 'build')
        assert row['recorded_completed_exit_code'] == 0
        info = target.lstat()
        assert stat.S_ISDIR(info.st_mode) and [info.st_dev, info.st_ino] == row['identity']
        assert fingerprint(target) == {k: row[k] for k in ('file_count', 'apparent_file_bytes', 'allocated_file_bytes', 'extensions')}
        for repo in (ROOT, ROOT / 'artifacts/css-spec-lean'):
            assert not subprocess.check_output(GIT + ['ls-files', '-z', '--', str(target.relative_to(repo))], cwd=repo, env=ENV)
        for field in ('pins', 'staged_working', 'committed_research_working_payloads'):
            assert not any(p == row['target'] or p.startswith(row['target'] + '/') for p in epoch[field])
        retained.update(row['retained_evidence'])
        targets.append(target)
    for name, record in retained.items():
        path = ROOT / name
        assert not any(path.is_relative_to(target) for target in targets)
        assert sha(path) == record['sha256'] and path.stat().st_size == record['bytes']
    before = state()
    free_before = shutil.disk_usage(ROOT).free
    observation = no_users(targets)
    assert not (ROOT / 'artifacts/css-registered-number-native-runtime-v1/SOURCE-TRANSITION.lock').exists()
    save('PRE.json', {'state': before, 'targets': rows, 'process_observation': observation, 'free_bytes': free_before})
    for index, (target, row) in enumerate(zip(targets, rows)):
        info = target.lstat()
        assert [info.st_dev, info.st_ino] == row['identity']
        assert fingerprint(target) == {k: row[k] for k in ('file_count', 'apparent_file_bytes', 'allocated_file_bytes', 'extensions')}
        shutil.rmtree(target)
        assert not target.exists()
        save('REMOVED-' + str(index + 1) + '.json', {'path': row['target'], 'allocated_file_bytes': row['allocated_file_bytes']})
    assert state() == before
    assert all(sha(ROOT / name) == record['sha256'] for name, record in retained.items())
    save('RESULT.json', {'removed_directories': len(targets), 'removed_allocated_file_bytes': sum(row['allocated_file_bytes'] for row in rows),
                         'retained_evidence_verified': True, 'git_and_canonical_state_unchanged': True,
                         'free_bytes_before': free_before, 'free_bytes_after': shutil.disk_usage(ROOT).free})
    print('Removed only twelve completed Lean review build caches; sources and evidence preserved', flush=True)


if __name__ == '__main__':
    main()
