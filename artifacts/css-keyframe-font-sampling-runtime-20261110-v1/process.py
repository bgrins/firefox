import json
import os
import signal
import subprocess
import time

ACTIVE = set()
ROOT = None

def save(path, value):
    path.write_text(json.dumps(value, indent=2) + "\n")

def group_members(pgid):
    rows = subprocess.check_output(["ps", "-axo", "pgid=,stat=,pid="], text=True)
    return [
        int(parts[2])
        for line in rows.splitlines()
        if len(parts := line.split()) == 3
        and int(parts[0]) == pgid
        and not parts[1].startswith("Z")
    ]


def run(command, log, env, timeout):
    process = None
    with log.open("w") as output:
        try:
            process = subprocess.Popen(
                command,
                cwd=ROOT,
                env=env,
                stdout=output,
                stderr=subprocess.STDOUT,
                start_new_session=True,
            )
            ACTIVE.add(process.pid)
            save(
                log.with_suffix(".process.json"),
                {
                    "command": command,
                    "pgid": process.pid,
                    "timeout_seconds": timeout,
                    "state": "running",
                },
            )
            code = process.wait(timeout=timeout)
        finally:
            if process is not None:
                for sig in [signal.SIGTERM, signal.SIGKILL]:
                    if not group_members(process.pid):
                        break
                    try:
                        os.killpg(process.pid, sig)
                    except ProcessLookupError:
                        pass
                    for _ in range(30):
                        if not group_members(process.pid):
                            break
                        time.sleep(0.1)
                process.wait(timeout=10)
                assert not group_members(process.pid), (
                    "Owned process group still active"
                )
                ACTIVE.remove(process.pid)
                save(
                    log.with_suffix(".process.json"),
                    {
                        "command": command,
                        "pgid": process.pid,
                        "timeout_seconds": timeout,
                        "state": "terminal",
                        "exit_code": process.returncode,
                        "group_absent": True,
                    },
                )
    return {
        "command": command,
        "exit_code": code,
        "pgid": process.pid,
        "group_absent": True,
    }

