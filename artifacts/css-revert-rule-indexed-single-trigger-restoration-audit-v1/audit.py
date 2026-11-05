from pathlib import Path
import hashlib
import argparse
import importlib.util
import json
import os
import stat
import subprocess
import time
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('--runtime', required=True)
parser.add_argument('--config', required=True)
parser.add_argument('--result', required=True)
parser.add_argument('--browser-process', action='append', required=True)
parser.add_argument('--owner-launch', required=True)
parser.add_argument('--owner-session', type=int, required=True)
parser.add_argument('--owner-terminal', required=True)
parser.add_argument('--owner-exit', type=int, required=True)
args = parser.parse_args()
assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
RUNTIME = (ROOT / args.runtime).resolve()
config_path = (ROOT / args.config).resolve()
result_path = (HERE / args.result).resolve()
assert RUNTIME.parent == ROOT / 'artifacts'
assert config_path.parent.parent == ROOT / 'artifacts'
assert result_path.parent == HERE and not result_path.exists()
read = lambda p: json.loads(p.read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
before = read(RUNTIME / 'BEFORE.json')
assert sha(config_path) == before['config_sha256']
config = read(config_path)
assert sha(config_path.parent / 'run.py') == before['runner_sha256']
assert config['output'] == str(RUNTIME.relative_to(ROOT))
helper = ROOT / config['helpers']['bundle_helper']
assert sha(helper) == config['helper_hashes'][str(helper.relative_to(ROOT))]
spec = importlib.util.spec_from_file_location('audit_bundle', helper)
bundle = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bundle)
assert args.browser_process == ['browser/repeat-1/PROCESS.json', 'browser/repeat-2/PROCESS.json']
assert all(Path(n).parts[0] == 'browser' and '..' not in Path(n).parts and
           Path(n).name == 'PROCESS.json' for n in args.browser_process)
process_files = ['build/build-PROCESS.json', 'build/WAKE-PROCESS.json', *args.browser_process]
processes = {name: read(RUNTIME / name) for name in process_files}
owned_pids = {row['pid'] for row in processes.values()}
owned_groups = {row['pgid'] for row in processes.values()}


def absent_processes():
    result = subprocess.run(['/bin/ps', '-axo', 'pid=,pgid='], check=True, capture_output=True, text=True, timeout=10)
    rows = [tuple(map(int, line.split())) for line in result.stdout.splitlines()]
    assert any(pid == os.getpid() for pid, group in rows)
    remaining = [(pid, group) for pid, group in rows if pid in owned_pids or group in owned_groups]
    assert not remaining, remaining
    return {'time_ns': time.time_ns(), 'owned_pids': sorted(owned_pids),
            'owned_groups': sorted(owned_groups), 'remaining': [], 'self_calibration': True}


def sources():
    result = {}
    for name, digest in before['sources'].items():
        path = ROOT / name
        info = path.lstat()
        assert stat.S_ISREG(info.st_mode)
        assert [info.st_dev, info.st_ino] == before['identities'][name]
        assert sha(path) == digest
        result[name] = {'sha256': digest, 'identity': before['identities'][name]}
    for name, digest in before['library_sources'].items():
        assert sha(ROOT / name) == digest
    for name, digest in config['context_sources'].items():
        assert sha(ROOT / name) == digest
    return result


process_before = absent_processes()
source_rows = sources()
env = dict(os.environ, GIT_OPTIONAL_LOCKS='0')
assert not any(os.environ.get(k) for k in ('GIT_DIR', 'GIT_WORK_TREE', 'GIT_INDEX_FILE'))
git = lambda *args: subprocess.check_output(['git', '-c', 'core.fsmonitor=false', *args], cwd=ROOT, env=env)
assert git('rev-parse', 'HEAD').decode().strip() == before['head']
git_observed = {key: hashlib.sha256(git(*args)).hexdigest() for key, args in {
    'index_entries': ['ls-files', '--stage', '-z'],
    'cached_diff': ['diff', '--cached', '--binary'],
    'unrelated_working_diff': ['diff', '--binary', '--', '.', *[':(exclude)' + n for n in before['sources']]],
}.items()}
assert git_observed == before['git']
app_before = read(RUNTIME / 'APP-BEFORE.json')
extras_before = read(RUNTIME / 'EXTRAS-BEFORE.json')
app_now = bundle.scan(ROOT / config['app_path'])
extras_now = {name: bundle.entry(ROOT / name) for name in config['extra_paths']}
assert bundle.semantic(app_now) == bundle.semantic(app_before)
assert bundle.semantic(extras_now) == bundle.semantic(extras_before)
lock = ROOT / 'artifacts/css-registered-number-native-runtime-v1/SOURCE-TRANSITION.lock'
assert not lock.exists() and not lock.is_symlink()
assert not (RUNTIME / 'backups').exists() and not (RUNTIME / 'backups').is_symlink()
assert sources() == source_rows
process_after = absent_processes()
observation = read(RUNTIME / 'RESULT.json')
assert observation['restoration_verified'] and observation['native_fix_acceptance'] is False
primary = read(RUNTIME / 'browser/RESULT.json')
assert primary['repetitions_requested'] == primary['repetitions_completed'] == primary['repetitions_recorded'] == 2
assert [row['directory'] for row in primary['runs']] == ['repeat-1', 'repeat-2']
assert primary['report_paths'] == ['repeat-1/BENCHMARK-REPORT.json', 'repeat-2/BENCHMARK-REPORT.json']
repetitions = {str(Path(n).parent): read(RUNTIME / Path(n).parent / 'RESULT.json') for n in args.browser_process}
for row in primary['runs']:
    assert row['result'] == repetitions['browser/' + row['directory']]
    assert row['report'] == row['directory'] + '/BENCHMARK-REPORT.json'
record = {'restoration_verified': True, 'owner_execution': {'launch': args.owner_launch, 'session': args.owner_session, 'terminal': args.owner_terminal, 'exit': args.owner_exit},
          'audit_script_sha256': sha(Path(__file__)), 'sources': source_rows,
          'library_sources_preserved': before['library_sources'], 'context_sources_preserved': config['context_sources'], 'head': before['head'], 'git': git_observed,
          'app_semantics_preserved': True, 'app_entries': len(app_now), 'extra_semantics_preserved': True,
          'extras': list(extras_now), 'source_transition_lock_absent': True, 'backup_removed': True,
          'process_before': process_before, 'process_after': process_after,
          'primary_observation': primary, 'repetition_observations': repetitions, 'native_fix_acceptance': False,
          'references': {str(path.relative_to(ROOT)): sha(path) for path in [config_path, helper,
              RUNTIME / 'BEFORE.json', RUNTIME / 'APP-BEFORE.json', RUNTIME / 'EXTRAS-BEFORE.json',
              RUNTIME / 'RESTORED.json', RUNTIME / 'RESULT.json', RUNTIME / 'browser/RESULT.json', *[RUNTIME / Path(n).parent / 'RESULT.json' for n in args.browser_process], *[RUNTIME / Path(n).parent / 'BENCHMARK-REPORT.json' for n in args.browser_process], *[RUNTIME / f for f in process_files]]}}
with result_path.open('x') as stream:
    json.dump(record, stream, indent=2)
    stream.write('\n')
print(json.dumps({'restoration_verified': True, 'sources': len(source_rows), 'library_files': len(before['library_sources']),
                  'app_entries': len(app_now), 'extra_files': len(extras_now), 'owned_groups_absent': sorted(owned_groups),
                  'result_sha256': sha(result_path)}), flush=True)
