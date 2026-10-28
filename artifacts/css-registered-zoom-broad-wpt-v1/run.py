import sys

if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise SystemExit("Require python3 -I -S -B without optimization")
sys.dont_write_bytecode = True

import configparser
import hashlib
import importlib.util
import json
import os
import re
from pathlib import Path
import shutil
import signal
import stat
import subprocess
import tempfile
import time
from types import SimpleNamespace

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
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


def require_compiled_transition(epoch, role):
    transition = epoch.get("registered_number_transition")
    need(isinstance(transition, dict) and transition.get("role") == role and
         transition.get("variant") == ("committed-head" if role == "original" else "zoom-normalization-v3") and transition.get("compiled") is True,
         "phase requires matching successful original or zoom-normalization-v3 compilation")


def application_target(path):
    entry = path.lstat()
    need(stat.S_ISREG(entry.st_mode) or stat.S_ISLNK(entry.st_mode), "application.ini entry is not a file or symlink")
    target = path.resolve(strict=True)
    need(stat.S_ISREG(target.lstat().st_mode), "application.ini target is not a regular file")
    return target


def resource_fingerprint(helper, root, name, application_ini):
    if name == application_ini:
        return sha(application_target(root / name))
    return helper.fingerprint(root, name)


def application_metadata(path, epoch_head):
    target = application_target(path)
    entry = path.lstat()
    data = target.read_bytes()
    parsed = configparser.ConfigParser(interpolation=None)
    parsed.read_string(data.decode("utf-8"))
    build_id = parsed.get("App", "BuildID")
    need(bool(build_id), "application.ini BuildID missing")
    identity = target.stat()
    return {"path": str(path), "resolved": str(target),
            "entry_identity": [entry.st_dev, entry.st_ino],
            "entry_type": stat.S_IFMT(entry.st_mode),
            "symlink_target": os.readlink(path) if stat.S_ISLNK(entry.st_mode) else None,
            "identity": [identity.st_dev, identity.st_ino],
            "sha256": hashlib.sha256(data).hexdigest(),
            "browser_build_id": build_id, "revision": epoch_head}


def main():
    need(len(sys.argv) == 8, "Usage: run.py CAPSULE_SHA PHASE EPOCH_PATH EPOCH_SHA ABSENT_OUTPUT [ORIGINAL_ASSESSMENT ORIGINAL_SHA]")
    authenticate(HERE, sys.argv[1])
    policy = read(HERE / "POLICY.json")
    succession = load("signed_head_succession", HERE / "succession.py")
    succession_receipt = succession.validate(ROOT, HERE, policy, SimpleNamespace(**globals()))
    phase = sys.argv[2]
    need(re.fullmatch(r"candidate-[1-9][0-9]*", phase), "candidate-only phase label")
    role = phase.split("-")[0]
    need(len(sys.argv) == (6 if role == "original" else 8), "original/candidate baseline arguments")
    epoch_path = Path(sys.argv[3])
    need(epoch_path.is_absolute() and not epoch_path.is_symlink(), "absolute regular epoch")
    need(sha(epoch_path) == sys.argv[4] == succession_receipt["current_epoch_sha256"], "externally supplied epoch digest")
    epoch = read(epoch_path)
    require_compiled_transition(epoch, role)
    need(epoch["registered_number_transition"].get("accepted") is False and
         epoch["registered_number_transition"].get("last_phase") == "zoom-normalization-build-2", "unaccepted compiled zoom build2")
    need(epoch["semantic_index"]["head"] == policy["frozen_head"], "epoch HEAD differs from frozen comparison HEAD")
    app_metadata = application_metadata(ROOT / policy["application_ini"], epoch["semantic_index"]["head"])
    original, baseline_path, adopted = None, None, None
    if role == "candidate":
        baseline_path = Path(sys.argv[6])
        need(baseline_path.is_absolute() and not baseline_path.is_symlink() and
             sha(baseline_path) == sys.argv[7], "externally supplied original assessment")
        original = read(baseline_path)
        if original.get("capsule_manifest_sha256") != sys.argv[1]:
            adoption = load("original_adoption", HERE / "adoption.py")
            adopted = adoption.validate(ROOT, HERE, baseline_path, sys.argv[7], policy, SimpleNamespace(**globals()))
        need(original["complete"] and original["execution_preserved"] and
             original["phase"].startswith("original-") and
             (original["capsule_manifest_sha256"] == sys.argv[1] or adopted is not None) and
             original["native_sources"] == policy["source_roles"]["original"], "matching complete original")
        need(original["run_binding"]["revision"] == epoch["semantic_index"]["head"] or
             (adopted is not None and original["run_binding"]["revision"] == policy["original_frozen_head"] and epoch["semantic_index"]["head"] == policy["frozen_head"]),
             "original/candidate epoch HEAD must be frozen")
    for name, pin in read(HERE / "REFERENCES.json").items():
        need(sha(ROOT / name) == pin, "helper/source binding: " + name)
    for name, pin in policy["source_roles"][role].items():
        need(sha(ROOT / name) == pin and epoch["pins"].get(name) == pin, "phase native source binding: " + name)
    out = Path(sys.argv[5])
    need(out.is_absolute() and not out.exists() and not out.is_symlink(), "output must be absent")
    out = out.resolve()
    need(out.parent == ROOT / "artifacts" and out.name.startswith("css-registered-zoom-broad-wpt-runtime-"), "owned artifact output")
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
    source_pins = read(HERE / "SOURCE-PINS.json")
    resource_pins = {item["origin"]: item.get("sha256") for item in source_pins.values()}
    fingerprint_resource = lambda name: resource_fingerprint(h, ROOT, name, policy["application_ini"])
    resource_pins.update(policy["live_oracle_sources"])
    resource_pins.update(policy["unchanged_native_sources"])
    resource_pins.update({name: fingerprint_resource(name) for name in policy["runtime_inputs"]})
    for directory in policy["profile_directories"]:
        for path in sorted((ROOT / directory).rglob("*")):
            if path.is_file():
                name = str(path.relative_to(ROOT))
                resource_pins[name] = fingerprint_resource(name)
    need({n: fingerprint_resource(n) for n in resource_pins} == resource_pins, "source/resource/metadata inputs")
    binary_pins = {name: h.fingerprint(ROOT, name) for name in policy["normal_binaries"]}
    need(all(pin and epoch["pins"][name] == pin for name, pin in binary_pins.items()), "normal built binary bindings")
    if role == "candidate":
        need(binary_pins == succession_receipt["candidate_binaries"], "candidate build2 binaries changed after signing")
    out.mkdir()
    save(out / "HEAD-SUCCESSION.json", succession_receipt)
    if adopted is not None:
        save(out / "ORIGINAL-ADOPTION.json", adopted)
    save(out / "EPOCH.json", epoch)
    save(out / "PRE.json", before)
    save(out / "INDEX-FLAGS.json", flags)
    save(out / "INPUT-PINS.json", resource_pins)
    save(out / "NORMAL-BINARIES.json", binary_pins)
    need(resource_pins[policy["application_ini"]] == app_metadata["sha256"], "application metadata pre-pin")
    save(out / "APPLICATION-METADATA.json", app_metadata)
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
        destination.write_bytes((HERE / item["capture"]).read_bytes())
        need(sha(destination) == item["sha256"], "copied input: " + name)
    (tests_root / "tools").symlink_to(ROOT / "testing/web-platform/tests/tools", target_is_directory=True)
    server = read(ROOT / "testing/web-platform/tests/config.json")
    server["ports"] = {protocol: ["auto"] * count for protocol, count in policy["server_protocols"].items()}
    save(tests_root / "config.json", server)
    save(metadata / "MANIFEST.json", read(HERE / "SUBSET-MANIFEST.json"))
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
    tmp = Path(tempfile.mkdtemp(prefix="css-registered-zoom-broad-wpt-", dir="/private/tmp"))
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
                                "wrapper_manifest_sha256": sys.argv[1], "epoch_sha256": sys.argv[4], "epoch_path": str(epoch_path), "phase": phase,
                                "original_assessment": str(baseline_path) if baseline_path else None,
                                "original_assessment_sha256": sys.argv[7] if baseline_path else None})
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
            need(sha(epoch_path) == sys.argv[4], "externally bound epoch changed")
            if baseline_path is not None:
                need(sha(baseline_path) == sys.argv[7], "original assessment changed")
            need({n: fingerprint_resource(n) for n in resource_pins} == resource_pins, "resources changed")
            post_app_metadata = application_metadata(ROOT / policy["application_ini"], epoch["semantic_index"]["head"])
            save(out / "APPLICATION-METADATA-POST.json", post_app_metadata)
            need(post_app_metadata == app_metadata, "application metadata bytes/identity/BuildID changed")
            need({n: sha(out / n) for n in copied} == copied, "owned input changed")
            need((tests_root / "tools").is_symlink() and
                 (tests_root / "tools").resolve() == ROOT / "testing/web-platform/tests/tools", "owned tools link changed")
            for name, pin in read(HERE / "REFERENCES.json").items():
                need(sha(ROOT / name) == pin, "helper/source changed: " + name)
            if adopted is not None:
                need(adoption.validate(ROOT, HERE, baseline_path, sys.argv[7], policy, SimpleNamespace(**globals())) == adopted, "adopted original changed")
            need(succession.validate(ROOT, HERE, policy, SimpleNamespace(**globals())) == succession_receipt, "signed succession changed")
            authenticate(HERE, sys.argv[1])
            save(out / "POST.json", post)
        except BaseException as exc:
            post_error = repr(exc)
    assessment = None
    try:
        need(raw.is_file() and not raw.is_symlink() and raw.stat().st_size <= 128 * 1024 * 1024, "missing/oversized raw log")
        events = [json.loads(line) for line in raw.read_text().splitlines()]
        assessment = parser.assess(events, code, policy, checks, original, app_metadata)
        assessment.update(phase=phase, capsule_manifest_sha256=sys.argv[1],
                          epoch_sha256=sys.argv[4], native_sources=policy["source_roles"][role], original_adoption=adopted,
                          execution_preserved=bool(error is None and post_error is None and
                              cleanup.get("owned_group_absent") and cleanup.get("temporary_root_removed")))
        save(out / "ASSESSMENT.json", assessment)
    except BaseException as exc:
        error = error or repr(exc)
    passed = (error is None and post_error is None and cleanup.get("owned_group_absent")
              and cleanup.get("temporary_root_removed") and assessment and assessment["complete"]
              and (role == "original" or assessment["comparison_gate_passed"]))
    result = {"exit": code, "execution_error": error, "preservation_error": post_error,
              "phase": phase, "observation_gate_passed": bool(passed),
              "comparison_gate_passed": bool(passed and role == "candidate"),
              "native_fix_acceptance": False, "explicit_corrected_oracle_in_both_phases": True,
              "original_adoption": adopted}
    save(out / "RESULT.json", result)
    print(json.dumps(result, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
