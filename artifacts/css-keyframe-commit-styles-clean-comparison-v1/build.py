import json
import os
import signal
import subprocess
import time


def run(WORKTREE, OBJDIR, HERE, env, cancelled, state):
    phase = 'build'
    def save(name, value):
        with (HERE / name).open('x') as stream:
            stream.write(json.dumps(value, indent=2) + '\n')
    def free_bytes():
        value = os.statvfs(WORKTREE)
        return value.f_bavail * value.f_frsize
    assert free_bytes() >= 35 * 1024**3
    argv = ['/Users/bgrins/venvs/firefox/bin/python', './mach', 'build', '-j', '2']
    stop_reason = None
    failure = None
    cleanup_errors = []
    assert not cancelled()
    with (HERE / (phase + '.log')).open('xb') as log, (HERE / (phase + '-disk.jsonl')).open('x') as disk:
        process = None
        wake = None

        def signal_group(value):
            try:
                os.killpg(process.pid, value)
            except ProcessLookupError:
                pass

        try:
            process = subprocess.Popen(argv, cwd=WORKTREE, env=env, stdout=log,
                stderr=subprocess.STDOUT, start_new_session=True)
            state['build'] = process.pid
            save(phase + '-PROCESS.json', dict(pid=process.pid, pgid=process.pid, command=argv,
                cwd=str(WORKTREE), objdir=str(OBJDIR)))
            wake_command = ['/usr/bin/caffeinate', '-s', '-w', str(process.pid)]
            wake = subprocess.Popen(wake_command, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
            state['wake'] = wake.pid
            save('WAKE-PROCESS.json', dict(pid=wake.pid, pgid=wake.pid, command=wake_command, build_pid=process.pid))
            while True:
                available = free_bytes()
                disk.write(json.dumps(dict(time_ns=time.time_ns(), free_bytes=available)) + '\n')
                disk.flush()
                code = process.poll()
                if cancelled():
                    stop_reason = 'TERMINATION_REQUESTED'
                    signal_group(signal.SIGTERM)
                    break
                if code is not None:
                    break
                if wake.poll() is not None:
                    stop_reason = 'WAKE_PROCESS_EXITED_BEFORE_BUILD'
                    signal_group(signal.SIGTERM)
                    break
                if available < 15 * 1024**3:
                    stop_reason = 'DISK_SPACE_CAP'
                    signal_group(signal.SIGINT)
                    break
                time.sleep(1)
            try:
                code = process.wait(timeout=30)
            except subprocess.TimeoutExpired:
                signal_group(signal.SIGTERM)
                try:
                    code = process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    signal_group(signal.SIGKILL)
                    code = process.wait(timeout=10)
        except BaseException as error:
            failure = repr(error)
        finally:
            if process is None:
                save(phase + '-RESULT.json', dict(exit=None, error=failure, process_created=False,
                    free_bytes=free_bytes(), automatic_cleanup=False))
                raise RuntimeError('Process creation did not return an owned handle')
            try:
                signal_group(signal.SIGTERM)
                try:
                    process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    signal_group(signal.SIGKILL)
                    process.wait(timeout=10)
            except BaseException as error:
                cleanup_errors.append('leader reap: ' + repr(error))
            group_absent = False
            try:
                for attempt in range(100):
                    try:
                        os.killpg(process.pid, 0)
                    except ProcessLookupError:
                        group_absent = True
                        state.pop('build', None)
                        break
                    if attempt == 0:
                        signal_group(signal.SIGTERM)
                    elif attempt == 50:
                        signal_group(signal.SIGKILL)
                    time.sleep(0.1)
            except BaseException as error:
                cleanup_errors.append('build group census: ' + repr(error))
            finally:
                wake_absent = wake is None
                if wake is not None:
                    try:
                        if wake.poll() is None:
                            wake.terminate()
                        try:
                            wake.wait(timeout=10)
                        except subprocess.TimeoutExpired:
                            wake.kill()
                            wake.wait(timeout=10)
                        try:
                            os.killpg(wake.pid, 0)
                        except ProcessLookupError:
                            wake_absent = True
                            state.pop('wake', None)
                    except BaseException as error:
                        cleanup_errors.append('wake process: ' + repr(error))
                    save('WAKE-RESULT.json', dict(exit=wake.poll(), owned_group_absent=wake_absent))
                if not wake_absent:
                    cleanup_errors.append('wake group remains')
            if cancelled():
                stop_reason = 'TERMINATION_REQUESTED'
            save(phase + '-RESULT.json', dict(exit=process.poll(), stop_reason=stop_reason,
                error=failure, cleanup_errors=cleanup_errors, owned_group_absent=group_absent,
                free_bytes=free_bytes(), automatic_cleanup=False))
    assert process.returncode == 0 and stop_reason is None and failure is None
    assert group_absent and not cleanup_errors and not cancelled()

