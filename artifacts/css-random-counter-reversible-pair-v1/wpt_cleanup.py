import json
import os
from pathlib import Path
import signal
import subprocess
import time


def no_launch(output):
    assert not output.is_symlink(), 'WPT output cannot be a symlink'
    return not output.exists() or not (output / 'COMMAND.json').exists() and not (output / 'PROCESS.json').exists()


def finish(process, output, role, policy, control):
    if process is not None and process.poll() is None:
        try:
            os.killpg(process.pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
        try:
            process.wait(timeout=45)
        except subprocess.TimeoutExpired:
            pass
    wrapper = control.terminate(process)
    assert wrapper['owned_group_absent']
    if no_launch(output):
        return {'wrapper': wrapper, 'no_browser_launch_certified': True, 'restoration_safe': True, 'temporary_root_removed': None}
    command_path, process_path = output / 'COMMAND.json', output / 'PROCESS.json'
    assert not command_path.is_symlink() and not process_path.is_symlink()
    command = json.loads(command_path.read_bytes())
    child = json.loads(process_path.read_bytes())
    assert command['wrapper_manifest_sha256'] == policy['wpt_manifest'] and command['phase'] == role + '-1'
    assert child['pid'] == child['pgid'] and isinstance(child['pgid'], int) and child['pgid'] > 1 and child['pgid'] != os.getpgrp()
    pgid = child['pgid']
    cleanup_path = output / 'CLEANUP.json'
    if cleanup_path.exists():
        assert not cleanup_path.is_symlink()
        cleanup = json.loads(cleanup_path.read_bytes())
        if cleanup.get('owned_group_absent') and cleanup.get('temporary_root_removed'):
            assert not control.group_members(pgid)
            return {'wrapper': wrapper, 'child': cleanup, 'restoration_safe': True, 'temporary_root_removed': True}
    temporary = Path(command['temporary_root'])
    assert temporary.parent == Path('/private/tmp') and temporary.name.startswith('css-line-height-wpt-')
    members = control.group_members(pgid)
    for sig, delay in ((signal.SIGTERM, 10), (signal.SIGKILL, 10)):
        if not members:
            break
        try:
            os.killpg(pgid, sig)
        except ProcessLookupError:
            pass
        deadline = time.monotonic() + delay
        while time.monotonic() < deadline:
            members = control.group_members(pgid)
            if not members:
                break
            time.sleep(0.1)
    assert not members, 'Recorded owned WPT group remains'
    removed = not temporary.exists() and not temporary.is_symlink()
    return {'wrapper': wrapper, 'child_pgid': pgid, 'forced_child_cleanup': True, 'owned_group_absent': True, 'temporary_root_removed': removed, 'retained_temporary_root': None if removed else str(temporary), 'retention_reason': None if removed else 'Creation identity is owned by the WPT wrapper and cannot be reconstructed after forced termination', 'restoration_safe': True}
