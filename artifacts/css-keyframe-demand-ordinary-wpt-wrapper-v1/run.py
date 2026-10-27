import sys

if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise SystemExit("Require python3 -I -S -B without optimization")
sys.dont_write_bytecode = True

import configparser
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import signal
import stat
import subprocess
import tempfile
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ROSTER = ROOT / "artifacts/css-keyframe-demand-ordinary-regressions-v1"
EPOCH = ROOT / "artifacts/css-keyframe-typed-attribute-demand-runtime-v1/CURRENT-EPOCH.json"
PYTHON = "/Users/bgrins/venvs/firefox/bin/python"
read = lambda path: json.loads(path.read_text())


def need(value, message):
    if not value:
        raise RuntimeError(message)


def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def save(path, value):
    with path.open("x") as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write("\n")


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def authenticate(directory, expected):
    need(sha(directory / "FILES.json") == expected, "manifest digest: " + str(directory))
    for name, item in read(directory / "FILES.json").items():
        relative = Path(name)
        need(not relative.is_absolute() and ".." not in relative.parts, "manifest path")
        path = directory / relative
        digest = item["sha256"] if isinstance(item, dict) else item
        need(stat.S_ISREG(path.lstat().st_mode) and sha(path) == digest, "payload: " + name)


def main():
    need(len(sys.argv) == 4, "Usage: run.py WRAPPER_FILES_SHA256 EPOCH_SHA256 ABSENT_OUTPUT_DIRECTORY")
    authenticate(HERE, sys.argv[1])
    policy = read(HERE / "POLICY.json")
    authenticate(ROSTER, policy["roster_manifest_sha256"])
    for name, pin in read(HERE / "REFERENCES.json").items():
        need(sha(ROOT / name) == pin, "helper/source binding: " + name)
    for name, pin in read(ROSTER / "REFERENCES.json").items():
        need(sha(ROOT / name) == pin, "roster reference binding: " + name)
    need(sha(EPOCH) == sys.argv[2], "current completed GTest epoch digest")
    epoch = read(EPOCH)
    need(epoch["semantic_index"]["head"] == policy["head"], "reviewed HEAD")
    need(epoch["typed_demand_transition"]["last_phase"] == policy["completed_phase"], "completed GTest phase")
    out = Path(sys.argv[3])
    need(out.is_absolute() and not out.exists() and not out.is_symlink(), "output must be absent")
    out = out.resolve()
    need(out.parent == ROOT / "artifacts" and out.name.startswith("css-keyframe-demand-ordinary-wpt-runtime-"), "owned artifact output")
    need(all(not os.environ.get(k) for k in policy["forbidden_environment"]), "unexpected build/git/profile environment")
    env = dict(os.environ, GIT_OPTIONAL_LOCKS="0", PYTHONDONTWRITEBYTECODE="1",
               MOZCONFIG=str(ROOT / "mozconfig"), MOZ_OBJDIR=str(ROOT / "objdir-full.noindex"),
               MOZ_HEADLESS="1", MOZ_SKIP_PATH_PERFORMANCE_CHECK="1",
               MOZ_DISABLE_SAFE_MODE_KEY="1", MOZ_DISABLE_UPDATE_PROCESSING="1")
    h = load("ordinary_preservation", ROOT / policy["helpers"]["preservation"])
    guard = load("ordinary_epoch", ROOT / policy["helpers"]["epoch"])
    checks = load("ordinary_checks", ROOT / policy["helpers"]["checks"])
    control = load("ordinary_control", ROOT / policy["helpers"]["control"])
    parser = load("ordinary_assessment", HERE / "assess.py")
    before = guard.verify_current(h, ROOT, env, epoch)
    flags = {name: hashlib.sha256(h.git(ROOT / name, env, "ls-files", "-v", "-z")).hexdigest()
             for name in (".", "artifacts/css-spec-lean")}
    source_pins = read(ROSTER / "SOURCE-PINS.json")
    resource_pins = {name: item.get("sha256") for name, item in source_pins.items()}
    resource_pins.update({name: h.fingerprint(ROOT, name) for name in policy["runtime_inputs"]})
    for directory in policy["profile_directories"]:
        for path in sorted((ROOT / directory).rglob("*")):
            if path.is_file():
                name = str(path.relative_to(ROOT))
                resource_pins[name] = h.fingerprint(ROOT, name)
    need({n: h.fingerprint(ROOT, n) for n in resource_pins} == resource_pins, "source/resource/metadata inputs")
    binary_pins = {name: h.fingerprint(ROOT, name) for name in policy["normal_binaries"]}
    need(all(pin and epoch["pins"][name] == pin for name, pin in binary_pins.items()), "normal built binary bindings")
    out.mkdir()
    save(out / "EPOCH.json", epoch)
    save(out / "PRE.json", before)
    save(out / "INDEX-FLAGS.json", flags)
    save(out / "INPUT-PINS.json", resource_pins)
    save(out / "NORMAL-BINARIES.json", binary_pins)
    tests_root, metadata = out / "tests", out / "metadata"
    tests_root.mkdir()
    metadata.mkdir()
    for name, item in source_pins.items():
        if not item["exists"]:
            continue
        prefix = "testing/web-platform/"
        relative = Path(name.removeprefix(prefix))
        destination = (tests_root if relative.parts[0] == "tests" else metadata).joinpath(*relative.parts[1:])
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes((ROOT / name).read_bytes())
        need(sha(destination) == item["sha256"], "copied input: " + name)
    (tests_root / "tools").symlink_to(ROOT / "testing/web-platform/tests/tools", target_is_directory=True)
    server = {"ports": {protocol: ["auto"] * count for protocol, count in policy["server_protocols"].items()}}
    save(tests_root / "config.json", server)
    source_manifest = read(ROOT / policy["manifest"])
    subset = {"version": source_manifest["version"], "url_base": "/", "items": {"testharness": {}}}
    for test in policy["tests"]:
        parts = Path(test.lstrip("/")).parts
        old, new = source_manifest["items"]["testharness"], subset["items"]["testharness"]
        for part in parts[:-1]:
            old, new = old[part], new.setdefault(part, {})
        new[parts[-1]] = old[parts[-1]]
    save(metadata / "MANIFEST.json", subset)
    config = configparser.ConfigParser(interpolation=None)
    config.read(ROOT / policy["wpt_config"])
    for section in list(config.sections()):
        if section.startswith("manifest:"):
            config.remove_section(section)
    config["paths"]["run_info"] = str(ROOT / "objdir-full.noindex")
    config["paths"]["prefs"] = str(ROOT / "testing/profiles")
    config["web-platform-tests"]["sync_path"] = str(out / "unused-sync")
    config["manifest:upstream"] = {"tests": str(tests_root), "metadata": str(metadata),
                                   "url_base": "/", "manifest": str(metadata / "MANIFEST.json")}
    config_path = out / "wptrunner.ini"
    with config_path.open("x") as stream:
        config.write(stream)
    copied = {str(p.relative_to(out)): sha(p) for top in (tests_root, metadata)
              for p in top.rglob("*") if p.is_file() and "tools" not in p.relative_to(top).parts}
    copied["wptrunner.ini"] = sha(config_path)
    save(out / "OWNED-INPUT-PINS.json", copied)
    tmp = Path(tempfile.mkdtemp(prefix="css-ordinary-wpt-", dir="/private/tmp"))
    tmp_identity = (tmp.stat().st_dev, tmp.stat().st_ino)
    env.update(TMPDIR=str(tmp), TMP=str(tmp), TEMP=str(tmp))
    raw = out / "raw.jsonl"
    command = [PYTHON, "./mach", "wpt", "--headless", "--processes=1",
               "--no-manifest-update", "--no-manifest-download",
               "--binary=" + str(ROOT / policy["normal_binaries"][0]),
               "--config=" + str(config_path), "--run-info=" + str(ROOT / "objdir-full.noindex"),
               "--prefs-root=" + str(ROOT / "testing/profiles"), "--log-raw=" + str(raw),
               *["--include=" + test for test in policy["tests"]]]
    save(out / "COMMAND.json", {"command": command, "temporary_root": str(tmp), "timeout_seconds": 600,
                                "wrapper_manifest_sha256": sys.argv[1], "epoch_sha256": sys.argv[2]})
    process, code, error, cleanup, post_error = None, None, None, None, None
    stopped = [False]
    def stop(signum, frame):
        stopped[0] = True
    for sig in (signal.SIGTERM, signal.SIGINT):
        signal.signal(sig, stop)
    try:
        with (out / "wpt.log").open("x") as log:
            process = subprocess.Popen(command, cwd=ROOT, env=env, stdout=log,
                                       stderr=subprocess.STDOUT, start_new_session=True)
            save(out / "PROCESS.json", {"pid": process.pid, "pgid": process.pid})
            deadline = time.monotonic() + 600
            while process.poll() is None:
                need(not stopped[0] and time.monotonic() < deadline, "cancelled or WPT deadline exceeded")
                time.sleep(0.2)
            code = process.wait()
    except BaseException as exc:
        error = repr(exc)
    finally:
        try:
            cleanup = control.terminate(process)
            need(cleanup["owned_group_absent"], "owned process group remains")
            need((tmp.stat().st_dev, tmp.stat().st_ino) == tmp_identity and not tmp.is_symlink(), "temporary root identity changed")
            cleanup["remaining_temporary_entries"] = sorted(p.name for p in tmp.iterdir())
            shutil.rmtree(tmp)
            cleanup["temporary_root_removed"] = not tmp.exists()
        except BaseException as exc:
            cleanup = {"error": repr(exc), "owned_group_absent": False, "temporary_root_removed": not tmp.exists()}
        save(out / "CLEANUP.json", cleanup)
        try:
            post = guard.verify_current(h, ROOT, env, epoch)
            need(post == before, "root/nested preservation")
            need(flags == {name: hashlib.sha256(h.git(ROOT / name, env, "ls-files", "-v", "-z")).hexdigest()
                           for name in flags}, "index flags changed")
            need(sha(EPOCH) == sys.argv[2], "shared current epoch changed")
            need({n: h.fingerprint(ROOT, n) for n in resource_pins} == resource_pins, "resources changed")
            need({n: sha(out / n) for n in copied} == copied, "owned input changed")
            need((tests_root / "tools").is_symlink() and
                 (tests_root / "tools").resolve() == ROOT / "testing/web-platform/tests/tools", "owned tools link changed")
            for name, pin in read(HERE / "REFERENCES.json").items():
                need(sha(ROOT / name) == pin, "helper/source changed: " + name)
            authenticate(HERE, sys.argv[1])
            authenticate(ROSTER, policy["roster_manifest_sha256"])
            save(out / "POST.json", post)
        except BaseException as exc:
            post_error = repr(exc)
    assessment = None
    try:
        need(raw.is_file() and not raw.is_symlink() and raw.stat().st_size <= 128 * 1024 * 1024, "missing/oversized raw log")
        events = [json.loads(line) for line in raw.read_text().splitlines()]
        assessment = parser.assess(events, code, policy["tests"], policy["expected_failures"], checks)
        save(out / "ASSESSMENT.json", assessment)
    except BaseException as exc:
        error = error or repr(exc)
    passed = (error is None and post_error is None and cleanup.get("owned_group_absent")
              and cleanup.get("temporary_root_removed") and assessment and assessment["regression_gate_passed"])
    result = {"exit": code, "execution_error": error, "preservation_error": post_error,
              "regression_gate_passed": bool(passed), "native_fix_acceptance": False,
              "oracle_caveat_retained": True, "registered_unused_fallback_probe_run": False}
    save(out / "RESULT.json", result)
    print(json.dumps(result, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
