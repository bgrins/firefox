import os
import signal
import subprocess
import time

def members(pgid):
    result = subprocess.run(['/bin/ps', '-axo', 'pid=,pgid=,uid=,stat=,lstart='], capture_output=True, text=True, timeout=3, check=True)
    if not result.stdout.strip():
        raise RuntimeError('Empty ps listing cannot establish group absence')
    selected = []
    for line in result.stdout.splitlines():
        if not line.strip():
            continue
        fields = line.split(None, 4)
        if len(fields) != 5:
            raise RuntimeError('Malformed nonblank ps row')
        pid, group, uid = map(int, fields[:3])
        if pid <= 0 or group < 0 or uid < 0:
            raise RuntimeError('Invalid ps numeric identity')
        if group != pgid:
            continue
        try:
            sid, current_group = os.getsid(pid), os.getpgid(pid)
        except ProcessLookupError:
            continue
        selected.append({'pid': pid, 'pgid': group, 'uid': uid, 'state': fields[3],
                         'birth': fields[4], 'sid': sid, 'currentPgid': current_group})
    return selected

def terminate_owned(process, initial):
    pgid = process.pid
    stages, errors = [], []
    known = {(m['pid'], m['birth']) for m in initial}
    def snapshot(stage):
        current = members(pgid)
        stages.append({'stage': stage, 'members': current})
        return current
    def live(current):
        return [m for m in current if not m['state'].startswith('Z')]
    def send_group(sig, stage):
        current = live(snapshot(stage + '-verify'))
        if not current:
            stages.append({'stage': stage, 'action': 'no-live-members-no-signal'})
            return
        if not all(m['uid'] == os.getuid() and m['sid'] == pgid and m['currentPgid'] == pgid for m in current):
            raise RuntimeError('Group ownership/session mismatch')
        if not any((m['pid'], m['birth']) in known for m in current):
            raise RuntimeError('No surviving authenticated group identity; refuse possible reused PGID')
        known.update((m['pid'], m['birth']) for m in current)
        stages.append({'stage':stage, 'signal':int(sig), 'result':'attempt'})
        try:
            os.killpg(pgid, sig)
            stages.append({'stage': stage, 'signal': int(sig), 'result': 'sent'})
        except ProcessLookupError:
            stages.append({'stage': stage, 'signal': int(sig), 'result': 'group-departed'})
    def wait_leader(stage, timeout):
        try:
            status = process.wait(timeout=timeout)
            stages.append({'stage': stage, 'result': 'reaped', 'exit': status})
        except subprocess.TimeoutExpired:
            stages.append({'stage': stage, 'result': 'timeout'})
    def settle(stage, timeout):
        end = time.monotonic() + timeout
        while True:
            current = live(snapshot(stage))
            if not current or time.monotonic() >= end:
                return current
            if any((m['pid'], m['birth']) in known for m in current):
                known.update((m['pid'], m['birth']) for m in current
                             if m['uid'] == os.getuid() and m['sid'] == pgid and m['currentPgid'] == pgid)
            time.sleep(0.1)
    final = None
    try:
        current = snapshot('before-leader-termination')
        if any((m['pid'], m['birth']) in known for m in current):
            known.update((m['pid'], m['birth']) for m in current
                         if m['uid'] == os.getuid() and m['sid'] == pgid and m['currentPgid'] == pgid)
        if process.poll() is None:
            leader = [m for m in current if m['pid'] == pgid]
            if not leader or leader[0]['sid'] != pgid or leader[0]['currentPgid'] != pgid:
                raise RuntimeError('Cannot authenticate live leader before SIGTERM')
            stages.append({'stage':'leader-SIGTERM', 'pid':pgid, 'result':'attempt'})
            process.terminate()
            stages.append({'stage':'leader-SIGTERM', 'pid':pgid, 'result':'sent'})
        else:
            stages.append({'stage':'leader-SIGTERM', 'result':'already-exited', 'exit':process.returncode})
        wait_leader('leader-graceful-wait', 5)
        if live(snapshot('after-leader-wait')):
            send_group(signal.SIGTERM, 'group-SIGTERM')
            if settle('after-group-SIGTERM', 2):
                send_group(signal.SIGKILL, 'group-SIGKILL')
                settle('after-group-SIGKILL', 2)
        wait_leader('final-leader-wait', 3)
    except Exception as error:
        errors.append(repr(error))
        stages.append({'stage':'cleanup-error', 'error':repr(error)})
    finally:
        try:
            final = snapshot('final-owned-group')
        except Exception as error:
            errors.append(repr(error))
            stages.append({'stage':'final-inspection-error', 'error':repr(error)})
    no_live = final is not None and not live(final)
    if process.poll() is None:
        errors.append('leader has not exited/reaped')
    if not no_live:
        errors.append('owned group not verified without live members')
    return {'pid':pgid, 'pgid':pgid, 'initialMembers':initial, 'stages':stages,
            'leaderExit':process.returncode, 'noLiveGroup':no_live,
            'terminal':process.returncode is not None and no_live and not errors,
            'errors':errors,
            'boundary':'Original POSIX process group/session only; processes escaping it are not proven absent.'}
