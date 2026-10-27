import os
import signal
import subprocess
import time


def group_members(pgid):
    result = subprocess.run(['ps', '-axo', 'pid=,pgid='], check=True,
                            capture_output=True, text=True, timeout=5)
    members = []
    saw_self = False
    for line in result.stdout.splitlines():
        fields = line.split()
        if len(fields) != 2 or not all(field.isdecimal() for field in fields):
            raise RuntimeError('invalid process-group census')
        pid, group = map(int, fields)
        saw_self = saw_self or pid == os.getpid()
        if group == pgid:
            members.append(pid)
    if not saw_self:
        raise RuntimeError('process-group census lacks current-process calibration')
    return sorted(members)


def terminate(process):
    if process is None:
        return {'method': 'no-process-created', 'owned_group_absent': True}
    try:
        for sig in (signal.SIGTERM, signal.SIGKILL):
            try:
                os.killpg(process.pid, sig)
            except ProcessLookupError:
                break
            time.sleep(0.2)
        process.wait(timeout=10)
        try:
            os.killpg(process.pid, 0)
        except ProcessLookupError:
            return {'method': 'killpg', 'owned_group_absent': True}
        raise RuntimeError('owned benchmark process group remains')
    except PermissionError as error:
        permission_error = repr(error)
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=10)
        else:
            process.wait(timeout=10)
        deadline = time.monotonic() + 5
        while True:
            members = group_members(process.pid)
            if not members:
                return {'method': 'direct-process-reap-and-pgid-census',
                        'group_operation_error': permission_error,
                        'owned_group_absent': True, 'remaining_members': []}
            if time.monotonic() >= deadline:
                raise RuntimeError('owned group members remain after direct-process cleanup: ' + repr(members))
            time.sleep(0.1)


