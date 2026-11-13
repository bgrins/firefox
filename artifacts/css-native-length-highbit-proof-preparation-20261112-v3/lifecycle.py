import os
import signal
import subprocess
import time


def validate_owned_group(pgid, own_group=os.getpgrp):
    if type(pgid) is not int or pgid <= 1 or pgid == own_group():
        raise ValueError('Invalid owned process group')


def parse_members(output, pgid):
    rows = output.splitlines()
    if not rows:
        raise ValueError('Empty process-inspection output')
    members = []
    for row in rows:
        columns = row.split()
        if len(columns) != 3:
            raise ValueError('Malformed process-inspection row')
        pid, group, rss = map(int, columns)
        if group == pgid:
            members.append((pid, rss * 1024))
    return members


def inspect_group(pgid):
    validate_owned_group(pgid)
    output = subprocess.check_output(
        ['/bin/ps', '-axo', 'pid=,pgid=,rss='], text=True, timeout=5
    )
    return parse_members(output, pgid)


def settle_group(process, inspect=inspect_group, kill=os.killpg, sleep=time.sleep,
                 own_group=os.getpgrp):
    validate_owned_group(process.pid, own_group)
    errors = []
    signals = []

    def absent():
        try:
            return not inspect(process.pid)
        except Exception as error:
            errors.append(repr(error))
            return False

    def outcome(confirmed):
        return dict(group_absent=confirmed, inspection_errors=errors, cleanup_signals=signals)

    def signal_and_reap(sig):
        try:
            validate_owned_group(process.pid, own_group)
            kill(process.pid, sig)
            signals.append(sig.name)
        except ProcessLookupError:
            signals.append(sig.name + ':already-absent')
        except Exception as error:
            errors.append('signal:' + repr(error))
        try:
            process.wait(timeout=2)
        except subprocess.TimeoutExpired:
            pass
        except Exception as error:
            errors.append('wait:' + repr(error))
        sleep(0.05)

    if absent():
        return outcome(True)
    signal_and_reap(signal.SIGTERM)
    if absent():
        return outcome(True)
    signal_and_reap(signal.SIGKILL)
    for _ in range(10):
        if absent():
            return outcome(True)
        sleep(0.1)
    return outcome(False)
