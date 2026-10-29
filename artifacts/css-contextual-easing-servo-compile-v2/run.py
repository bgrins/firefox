import contextlib
import hashlib
import io
import json
import os
from pathlib import Path
import runpy
import signal
import stat
import subprocess
import sys
import time

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
read = lambda path: json.loads(path.read_bytes())
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
stopped = False


def save(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write('\n')


def authenticate(directory, expected):
    assert sha(directory / 'FILES.json') == expected
    for name, pin in read(directory / 'FILES.json').items():
        assert not Path(name).is_absolute() and '..' not in Path(name).parts
        assert sha(directory / name) == pin, name


def group_alive(pgid):
    try:
        os.killpg(pgid, 0)
        return True
    except ProcessLookupError:
        return False


def stop_group(process):
    pgid = process.pid
    for signum, grace in ((signal.SIGTERM, 5), (signal.SIGKILL, 5)):
        if not group_alive(pgid):
            break
        try:
            os.killpg(pgid, signum)
        except ProcessLookupError:
            break
        deadline = time.monotonic() + grace
        while time.monotonic() < deadline:
            process.poll()
            if not group_alive(pgid):
                break
            time.sleep(0.1)
    process.wait(timeout=1)
    assert not group_alive(pgid), f'Owned process group remains: {pgid}'


def resources(target, runtime, *, allow_missing=False):
    apparent = allocated = 0
    if target.exists():
        assert target.is_dir() and not target.is_symlink()
        for directory, _, names in os.walk(target, followlinks=False):
            for name in names:
                try:
                    info = (Path(directory) / name).lstat()
                except FileNotFoundError:
                    if allow_missing:
                        continue
                    raise
                if stat.S_ISREG(info.st_mode):
                    apparent += info.st_size
                    allocated += info.st_blocks * 512
    disk = os.statvfs(runtime)
    return {'target_bytes': max(apparent, allocated),
            'free_bytes': disk.f_bavail * disk.f_frsize}


def main():
    assert len(sys.argv) == 3 and sys.argv[1] in ('--check', '--run')
    authenticate(HERE, sys.argv[2])
    policy = read(HERE / 'POLICY.json')
    closure = ROOT / policy['closure']
    authenticate(closure, policy['closure_sha256'])
    for path, expected in policy['tool_pins'].items():
        assert sha(Path(path)) == expected, path
    if sys.argv[1] == '--check':
        print('Authenticated Servo compile capsule; no tool versions, compile, target, or runtime created')
        return
    for name in policy['required_absent_paths']:
        path = ROOT / name
        assert not path.exists() and not path.is_symlink(), name
    runtime = ROOT / policy['runtime']
    assert runtime.parent == ROOT / 'artifacts' and not runtime.exists() and not runtime.is_symlink()
    runtime.mkdir()
    target = runtime / 'target'
    for name in ('cargo-home', 'tmp'):
        (runtime / name).mkdir()
    env = {key: value for key, value in os.environ.items()
           if not key.startswith(('CARGO_', 'RUST', 'PYTHON'))}
    overrides = dict(policy['environment'], CARGO_HOME=str(runtime / 'cargo-home'),
                     CARGO_TARGET_DIR=str(target), TMPDIR=str(runtime / 'tmp'),
                     TMP=str(runtime / 'tmp'), TEMP=str(runtime / 'tmp'))
    env.update(overrides)
    active = None
    phases = {}
    failure = None

    def on_signal(_signum, _frame):
        global stopped
        stopped = True

    for signum in (signal.SIGTERM, signal.SIGINT):
        signal.signal(signum, on_signal)

    def verify(label):
        authenticate(closure, policy['closure_sha256'])
        for name, expected in policy['shared_held_sources'].items():
            assert sha(closure / 'baseline' / name) == sha(closure / 'candidate' / name) == expected
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            runpy.run_path(str(closure / 'verify.py'))
        save(runtime / f'{label}.json', {'verified': True, 'closure_sha256': policy['closure_sha256'],
                                       'verifier_output_scope': 'Verifier behavior only; compile execution is recorded separately in phase results.',
                                       'verifier_output': output.getvalue()})

    def execute(label, command, cwd, timeout):
        nonlocal active
        initial = resources(target, runtime)
        assert initial['free_bytes'] >= policy['min_free_bytes']
        assert initial['target_bytes'] <= policy['max_target_bytes']
        assert not stopped
        directory = runtime / label
        directory.mkdir()
        save(directory / 'COMMAND.json', {'argv': command, 'cwd': str(cwd),
                                         'environment_overrides': overrides, 'timeout_seconds': timeout})
        started = time.monotonic()
        stop_reason = None
        cleanup_error = None
        latest = initial
        with (directory / 'output.log').open('xb') as output, (directory / 'resources.jsonl').open('x') as samples:
            active = subprocess.Popen(command, cwd=cwd, env=env, stdout=output,
                                      stderr=subprocess.STDOUT, start_new_session=True)
            process = active
            save(directory / 'PROCESS.json', {'pid': process.pid, 'pgid': process.pid,
                                             'session_leader': True, 'runner_pid': os.getpid()})
            next_progress = 0
            try:
                while True:
                    elapsed = time.monotonic() - started
                    latest = resources(target, runtime, allow_missing=True)
                    samples.write(json.dumps(dict(latest, elapsed_seconds=elapsed), sort_keys=True) + '\n')
                    samples.flush()
                    if stopped:
                        stop_reason = 'runner_signal'
                    elif latest['free_bytes'] < policy['min_free_bytes']:
                        stop_reason = 'free_space_floor'
                    elif latest['target_bytes'] > policy['max_target_bytes']:
                        stop_reason = 'target_growth_limit'
                    elif elapsed >= timeout:
                        stop_reason = 'phase_timeout'
                    if stop_reason or process.poll() is not None:
                        break
                    if elapsed >= next_progress:
                        print(label, dict(latest, elapsed_seconds=round(elapsed, 1)), flush=True)
                        next_progress = elapsed + 30
                    time.sleep(policy['poll_seconds'])
            finally:
                try:
                    if process.poll() is not None and group_alive(process.pid) and stop_reason is None:
                        stop_reason = 'descendant_group_after_exit'
                    if process.poll() is None or group_alive(process.pid):
                        stop_group(process)
                    else:
                        process.wait()
                    assert not group_alive(process.pid)
                    active = None
                    latest = resources(target, runtime)
                    if latest['free_bytes'] < policy['min_free_bytes']:
                        stop_reason = stop_reason or 'free_space_floor'
                    if latest['target_bytes'] > policy['max_target_bytes']:
                        stop_reason = stop_reason or 'target_growth_limit'
                except BaseException as error:
                    cleanup_error = repr(error)
                record = {'exit': process.returncode, 'stop_reason': stop_reason,
                          'cleanup_error': cleanup_error, 'owned_group_absent': not group_alive(process.pid),
                          'elapsed_seconds': time.monotonic() - started, 'resources': latest}
                record['success'] = record['exit'] == 0 and stop_reason is None and cleanup_error is None
                save(directory / 'RESULT.json', record)
        assert cleanup_error is None, cleanup_error
        return record

    try:
        verify('PRE')
        for name, command in policy['version_commands'].items():
            assert execute(name, command, runtime, 30)['success'], name
        save(runtime / 'RUNNER.json', {'python': sys.version, 'executable': sys.executable,
                                      'capsule_sha256': sys.argv[2], 'closure_sha256': policy['closure_sha256']})
        for role in ('baseline', 'candidate'):
            verify(role + '-PRE')
            command = [policy['cargo'], 'check', '--locked', '--offline', '-p', 'style', '--lib',
                       '--no-default-features', '--features', 'servo', '--jobs', '1',
                       '--target-dir', str(target)]
            phases[role] = execute(role, command, closure / role, policy['phase_timeout_seconds'])
            verify(role + '-POST')
            if not phases[role]['success']:
                break
    except BaseException as error:
        failure = repr(error)
    finally:
        if active is not None:
            try:
                stop_group(active)
                active = None
            except BaseException as error:
                failure = f'{failure}; cleanup: {error!r}'
        preservation_error = None
        try:
            verify('POST')
        except BaseException as error:
            preservation_error = repr(error)
        success = failure is None and preservation_error is None and set(phases) == {'baseline', 'candidate'} and all(p['success'] for p in phases.values())
        save(runtime / 'RESULT.json', {'success': success, 'failure': failure,
                                      'preservation_error': preservation_error, 'phases': phases,
                                      'candidate_skipped': 'candidate' not in phases,
                                      'configuration': 'captured local style configuration; not clean upstream',
                                      'shared_held_sources': policy['shared_held_sources'],
                                      'owned_processes_absent': active is None, 'native_fix_acceptance': False})
    print('Servo compile result', runtime / 'RESULT.json', flush=True)
    assert success, (failure, preservation_error, phases)


if __name__ == '__main__':
    main()
