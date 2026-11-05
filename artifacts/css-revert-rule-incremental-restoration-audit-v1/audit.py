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
owner_observation = read(RUNTIME / 'RESULT.json')
assert owner_observation['restoration_verified'] and owner_observation['native_fix_acceptance'] is False
assert not (RUNTIME / 'backups').exists() and not (RUNTIME / 'backups').is_symlink()
allowed_process_files = [
    'build/build-PROCESS.json', 'build/WAKE-PROCESS.json',
    'browser/correctness/PROCESS.json', 'browser/controls/PROCESS.json',
    'browser/occurrence/PROCESS.json',
    'browser/long_timing/repeat-1/PROCESS.json', 'browser/long_timing/repeat-2/PROCESS.json',
    'browser/single_timing/repeat-1/PROCESS.json', 'browser/single_timing/repeat-2/PROCESS.json',
]
discovered = {str(path.relative_to(RUNTIME)) for path in RUNTIME.rglob('*PROCESS.json')}
assert discovered <= set(allowed_process_files), discovered - set(allowed_process_files)
process_files = [name for name in allowed_process_files if name in discovered]
processes = {}
for name in process_files:
    path = RUNTIME / name
    assert path.is_file() and not path.is_symlink()
    row = read(path)
    assert type(row['pid']) is int and row['pid'] > 0
    assert type(row['pgid']) is int and row['pgid'] == row['pid']
    processes[name] = row
if 'build/WAKE-PROCESS.json' in processes:
    assert 'build/build-PROCESS.json' in processes
    assert processes['build/WAKE-PROCESS.json']['build_pid'] == processes['build/build-PROCESS.json']['pid']
process_hashes = {name: sha(RUNTIME / name) for name in process_files}
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
assert owner_observation == read(RUNTIME / 'RESULT.json')
assert process_hashes == {name: sha(RUNTIME / name) for name in process_files}
assert discovered == {str(path.relative_to(RUNTIME)) for path in RUNTIME.rglob('*PROCESS.json')}
observation_files = []
observations, observation_errors = {}, []
possible = ['browser/RESULT.json', 'build/build-RESULT.json', 'build/WAKE-RESULT.json', 'FAILURE.json']
possible += ['browser/' + lane + '/RESULT.json' for lane in
             ('correctness', 'controls', 'occurrence', 'long_timing', 'single_timing')]
possible += ['browser/' + lane + '/repeat-' + str(repeat) + '/' + name
             for lane in ('long_timing', 'single_timing') for repeat in (1, 2)
             for name in ('RESULT.json', 'BENCHMARK-REPORT.json')]
for name in possible:
    path = RUNTIME / name
    if path.exists():
        observation_files.append(name)
        try:
            value = read(path)
            if not isinstance(value, dict):
                raise ValueError('Expected observation object')
            observations[name] = value
        except (ValueError, OSError) as exc:
            observation_errors.append(name + ': ' + repr(exc))
primary = observations.get('browser/RESULT.json')
if owner_observation.get('experiment') is not None and owner_observation['experiment'] != primary:
    observation_errors.append('Owner experiment differs from saved browser aggregate')
if primary is not None:
    lane_rows = primary.get('lanes', {})
    if not isinstance(lane_rows, dict):
        observation_errors.append('Invalid aggregate lane mapping')
    else:
        for lane, value in lane_rows.items():
            if lane not in ('correctness', 'controls', 'occurrence', 'long_timing', 'single_timing'):
                observation_errors.append('Unknown aggregate lane: ' + lane)
            if observations.get('browser/' + lane + '/RESULT.json') != value:
                observation_errors.append('Aggregate differs from child lane: ' + lane)
missing_receipts = [name for name in allowed_process_files if name not in discovered]
for name in missing_receipts:
    child_result = str(Path(name).parent / 'RESULT.json')
    if child_result in observations:
        observation_errors.append('Result exists without a process receipt: ' + child_result)
record = {'restoration_verified': True, 'owner_execution': {'launch': args.owner_launch, 'session': args.owner_session, 'terminal': args.owner_terminal, 'exit': args.owner_exit},
          'audit_script_sha256': sha(Path(__file__)), 'sources': source_rows,
          'library_sources_preserved': before['library_sources'], 'context_sources_preserved': config['context_sources'], 'head': before['head'], 'git': git_observed,
          'app_semantics_preserved': True, 'app_entries': len(app_now), 'extra_semantics_preserved': True,
          'extras': list(extras_now), 'source_transition_lock_absent': True, 'backup_removed': True,
          'process_before': process_before, 'process_after': process_after,
          'owner_observation': owner_observation, 'experiment_observations': observations,
          'observation_errors': observation_errors,
          'recorded_processes': processes, 'missing_process_receipts': missing_receipts,
          'process_coverage': 'All recorded PID/PGIDs checked; missing receipts do not prove a process never started.',
          'experiment_complete_claim': bool(primary and primary.get('complete_observation')),
          'validation_passed_claim': bool(primary and primary.get('validation_passed')),
          'native_fix_acceptance': False,
          'references': {str(path.relative_to(ROOT)): sha(path) for path in [config_path, helper,
              RUNTIME / 'BEFORE.json', RUNTIME / 'APP-BEFORE.json', RUNTIME / 'EXTRAS-BEFORE.json',
              RUNTIME / 'RESTORED.json', RUNTIME / 'RESULT.json',
              *[RUNTIME / f for f in observation_files], *[RUNTIME / f for f in process_files]]}}
with result_path.open('x') as stream:
    json.dump(record, stream, indent=2)
    stream.write('\n')
print(json.dumps({'restoration_verified': True, 'sources': len(source_rows), 'library_files': len(before['library_sources']),
                  'app_entries': len(app_now), 'extra_files': len(extras_now), 'owned_groups_absent': sorted(owned_groups),
                  'result_sha256': sha(result_path)}), flush=True)
