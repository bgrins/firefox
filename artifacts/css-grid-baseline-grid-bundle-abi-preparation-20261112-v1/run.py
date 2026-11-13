import argparse
import hashlib
import json
import os
import shlex
import subprocess
import time
from pathlib import Path

import lifecycle
import layouts

HERE = Path(__file__).resolve().parent


def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def save(path, value):
    path.write_text(json.dumps(value, indent=2) + "\n")


def authenticate():
    sealed = json.loads((HERE / "FILES.json").read_text())["files"]
    for name, row in sealed.items():
        assert sha(HERE / name) == row["sha256"], name
    pins = json.loads((HERE / "INPUTS.json").read_text())
    for name, row in pins.items():
        path = Path(name)
        assert str(path.resolve()) == row["resolved"], name
        assert sha(path) == row["sha256"], name
    return pins


def validate_authorization(auth, out):
    assert auth["authorized"] is True
    assert auth["preparation_manifest_sha256"] == sha(HERE / "FILES.json")
    assert Path(auth["out"]).resolve() == out
    assert auth["commands"] == 2
    assert auth["seconds_per_command"] == 180
    assert auth["rss_bytes"] == 2147483648
    assert auth["stdout_stderr_bytes_per_command"] == 67108864


def command(request, out):
    label = request["label"]
    argv = [arg.replace("{OUT}", str(out)) for arg in request["argv"]]
    started = time.monotonic()
    row = dict(label=label, argv=argv, cwd=request["cwd"], exit=None,
               peak_rss_bytes=0, termination_reason=None, group_absent=False)
    stdout = out / (label + ".stdout")
    stderr = out / (label + ".stderr")
    proc = None
    try:
        with stdout.open("xb") as stream, stderr.open("xb") as error_stream:
            proc = subprocess.Popen(argv, cwd=request["cwd"], stdout=stream,
                                    stderr=error_stream, start_new_session=True)
            row.update(pid=proc.pid, pgid=proc.pid)
            save(out / (label + "-PID.json"), row)
            while proc.poll() is None:
                rss = sum(rss for _, rss in lifecycle.inspect_group(proc.pid))
                row["peak_rss_bytes"] = max(row["peak_rss_bytes"], rss)
                if rss > 2147483648:
                    raise RuntimeError("sampled process-group RSS limit")
                if time.monotonic() - started > 180:
                    raise RuntimeError("180-second command limit")
                if stdout.stat().st_size + stderr.stat().st_size > 67108864:
                    raise RuntimeError("64-MiB output limit")
                time.sleep(0.1)
    except BaseException as error:
        row["termination_reason"] = repr(error)
    finally:
        if proc is not None:
            row.update(lifecycle.settle_group(proc))
            row["exit"] = proc.poll()
        row["seconds"] = time.monotonic() - started
        row["limits"] = dict(seconds=180, sampled_group_rss_bytes=2147483648,
                             stdout_stderr_bytes=67108864)
        save(out / (label + "-COMMAND.json"), row)
    assert row["exit"] == 0 and row["termination_reason"] is None, row
    assert row["group_absent"] and not row["inspection_errors"], row
    assert stderr.read_bytes() == b"", "unexpected compiler diagnostic"
    assert stdout.stat().st_size + stderr.stat().st_size <= 67108864
    return row


def dependencies(request, out, pins):
    overlay = json.loads((HERE / (request["label"] + "-overlay.json")).read_text())
    replacements = {entry["name"]: entry["external-contents"] for entry in overlay["roots"]}
    for entry in overlay["roots"]:
        replacements[str(Path(entry["name"]).resolve())] = entry["external-contents"]
    data = (out / (request["label"] + ".d")).read_text().replace("\\\n", "")
    names = shlex.split(data.splitlines()[0].split(":", 1)[1])
    assert names
    result = {}
    for name in names:
        path = Path(os.path.abspath(Path(request["cwd"]) / name))
        target = Path(replacements.get(str(path), str(path)))
        if str(path) not in replacements:
            assert str(path) in pins, ("unadmitted dependency", str(path))
            assert sha(path) == pins[str(path)]["sha256"]
        result[str(path)] = dict(effective_source=str(target), sha256=sha(target))
    save(out / (request["label"] + "-DEPENDENCIES.json"), result)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--authorization", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    out = args.out.resolve()
    authorization = json.loads(args.authorization.read_text())
    validate_authorization(authorization, out)
    pins = authenticate()
    out.mkdir(exist_ok=False)
    (out / "AUTHORIZATION.json").write_bytes(args.authorization.read_bytes())
    save(out / "PREPARATION.json", dict(path=str(HERE), manifest_sha256=sha(HERE / "FILES.json")))
    result = dict(status="FAIL", commands=[], layouts={}, no_live_install=True)
    try:
        requests = json.loads((HERE / "REQUESTS.json").read_text())
        assert [request["label"] for request in requests] == ["baseline", "candidate"]
        for request in requests:
            authenticate()
            row = command(request, out)
            result["commands"].append(row)
            authenticate()
            dependencies(request, out, pins)
            result["layouts"][request["label"]] = layouts.extract(
                (out / (request["label"] + ".stdout")).read_text(), request["types"])
        for metric in ("size", "align"):
            assert result["layouts"]["baseline"]["frame"][metric] == result["layouts"]["candidate"]["frame"][metric]
        result["status"] = "PASS actual-TU syntax and ABI only"
    except BaseException as error:
        result["failure"] = repr(error)
    finally:
        try:
            authenticate()
            result["inputs_unchanged"] = True
            groups = []
            for path in sorted(out.glob("*-PID.json")):
                pgid = json.loads(path.read_text())["pgid"]
                members = lifecycle.inspect_group(pgid)
                groups.append(dict(pgid=pgid, members=members))
                assert not members
            result["fresh_groups"] = groups
        except BaseException as error:
            result["status"] = "FAIL"
            result["final_check_failure"] = repr(error)
        save(out / "RESULT.json", result)
    print(json.dumps(result, indent=2))
    return 0 if result["status"].startswith("PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
