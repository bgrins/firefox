"""Readiness probe only; no preference changes, installs, or profile access.

Run with python3 -I -B probe.py. Output is exclusively created beside this file.
Safari admission is distinct from expression support or fixture correctness.
"""

import http.client
import json
import os
from pathlib import Path
import signal
import socket
import subprocess
import sys
import time


OUTPUT = Path(__file__).resolve().parent
DRIVER = "/System/Cryptexes/App/usr/bin/safaridriver"


def save(name, value):
    with (OUTPUT / name).open("x") as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write("\n")


def request(port, method, path, body=None, timeout=15):
    connection = http.client.HTTPConnection("127.0.0.1", port, timeout=timeout)
    try:
        payload = None if body is None else json.dumps(body).encode()
        connection.request(method, path, body=payload,
                           headers={"Content-Type": "application/json"})
        response = connection.getresponse()
        raw = response.read(1024 * 1024 + 1)
        if len(raw) > 1024 * 1024:
            raise ValueError("WebDriver response exceeded 1 MiB")
        return {"status": response.status, "body": json.loads(raw)}
    finally:
        connection.close()


def group_exists(pgid):
    try:
        os.killpg(pgid, 0)
        return True
    except ProcessLookupError:
        return False


def stop_group(process):
    if process is None:
        return {"started": False, "owned_group_absent": True}
    pgid = process.pid
    for sig in (signal.SIGTERM, signal.SIGKILL):
        process.poll()
        if not group_exists(pgid):
            break
        try:
            os.killpg(pgid, sig)
        except ProcessLookupError:
            pass
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline:
            process.poll()
            if not group_exists(pgid):
                break
            time.sleep(0.05)
    code = process.wait(timeout=5)
    return {"started": True, "pid": process.pid, "pgid": pgid,
            "exit_code": code, "owned_group_absent": not group_exists(pgid)}


def main():
    assert sys.flags.isolated and sys.flags.dont_write_bytecode
    assert not any((OUTPUT / name).exists() for name in
                   ("DRIVER.log", "PROCESS.json", "RESULT.json"))
    result = {"admitted": False, "observation_complete": False,
              "preference_changes": False, "browser_fixture_executed": False}
    process = None
    session = None
    port = None

    def interrupted(signum, frame):
        raise InterruptedError("Probe interrupted by signal " + str(signum))

    signal.signal(signal.SIGTERM, interrupted)
    signal.signal(signal.SIGINT, interrupted)
    try:
        with socket.socket() as reservation:
            reservation.bind(("127.0.0.1", 0))
            port = reservation.getsockname()[1]
        command = [DRIVER, "--port=" + str(port)]
        result["command"] = command
        with (OUTPUT / "DRIVER.log").open("x") as log:
            process = subprocess.Popen(command, stdin=subprocess.DEVNULL,
                                       stdout=log, stderr=subprocess.STDOUT,
                                       start_new_session=True)
        save("PROCESS.json", {"pid": process.pid, "pgid": process.pid,
                              "port": port, "command": command})
        deadline = time.monotonic() + 10
        while True:
            if process.poll() is not None:
                raise RuntimeError("Owned driver exited before status admission")
            try:
                status = request(port, "GET", "/status", timeout=1)
                assert status["status"] == 200
                assert isinstance(status["body"]["value"]["ready"], bool)
                assert process.poll() is None
                result["status"] = status
                break
            except (OSError, http.client.HTTPException):
                if time.monotonic() >= deadline:
                    raise TimeoutError("Owned driver did not answer /status")
                time.sleep(0.1)
        if not status["body"]["value"]["ready"]:
            raise RuntimeError("Driver reports not ready; no new session requested")
        created = request(port, "POST", "/session", {
            "capabilities": {"alwaysMatch": {"browserName": "safari"}}}, timeout=30)
        result["new_session"] = created
        value = created["body"].get("value", {})
        session = value.get("sessionId")
        if not (isinstance(session, str) and session
                and all(char.isalnum() or char == "-" for char in session)):
            session = None
            raise RuntimeError("Safari automation session not admitted")
        result["admitted"] = True
        assert created["status"] == 200
        navigated = request(port, "POST", "/session/" + session + "/url",
                            {"url": "about:blank"})
        result["blank_navigation"] = navigated
        assert navigated["status"] == 200
        observed = request(port, "POST", "/session/" + session + "/execute/sync", {
            "script": "return {url:location.href,userAgent:navigator.userAgent,"
                      "supports:{em16:CSS.supports('animation-duration','calc(1em / 16px * 1s)'),"
                      "em32:CSS.supports('animation-duration','calc(1em / 32px * 1s)'),"
                      "lh:CSS.supports('animation-duration','calc(1lh / 16px * 1s)')}};",
            "args": []})
        result["observation"] = observed
        assert observed["status"] == 200
        value = observed["body"]["value"]
        assert value["url"] == "about:blank"
        assert isinstance(value["userAgent"], str)
        assert set(value["supports"]) == {"em16", "em32", "lh"}
        assert all(isinstance(item, bool) for item in value["supports"].values())
        result["observation_complete"] = True
    except BaseException as error:
        result["error"] = repr(error)
    finally:
        signal.signal(signal.SIGTERM, signal.SIG_IGN)
        signal.signal(signal.SIGINT, signal.SIG_IGN)
        if session is not None:
            try:
                result["delete_session"] = request(
                    port, "DELETE", "/session/" + session, timeout=10)
            except BaseException as error:
                result["delete_session_error"] = repr(error)
        try:
            result["cleanup"] = stop_group(process)
        except BaseException as error:
            result["cleanup"] = {"error": repr(error), "owned_group_absent": False}
        save("RESULT.json", result)
    print(json.dumps(result, sort_keys=True))
    deleted = result.get("delete_session", {}).get("status") == 200
    return 0 if (result["observation_complete"] and deleted
                 and result["cleanup"]["owned_group_absent"]) else 1


if __name__ == "__main__":
    raise SystemExit(main())
