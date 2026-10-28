import sys

if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise SystemExit("Require python3 -I -S -B without optimization")
sys.dont_write_bytecode = True

import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import importlib.util
import json
import os
from pathlib import Path
import re
import secrets
import shutil
import signal
import subprocess
import threading
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def authenticate(directory, expected):
    manifest_path = directory / "FILES.json"
    if manifest_path.is_symlink() or hashlib.sha256(manifest_path.read_bytes()).hexdigest() != expected:
        fail("manifest binding")
    for name, item in json.loads(manifest_path.read_text()).items():
        relative = Path(name)
        if relative.is_absolute() or ".." in relative.parts:
            fail("manifest path")
        path = directory / relative
        if path.is_symlink() or not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != item["sha256"]:
            fail("manifest payload: " + name)


def main():
    if len(sys.argv) != 8:
        raise SystemExit("Usage: run.py MANIFEST_SHA PHASE EPOCH_PATH EPOCH_SHA CALIBRATION_ASSESSMENT CALIBRATION_SHA ABSENT_OUTPUT")
    authenticate(HERE, sys.argv[1])
    policy = json.loads((HERE / "POLICY.json").read_text())
    if policy.get("execution_enabled") is not True:
        fail("observer disabled pending exact candidate calibration assessment")
    wrapper_path = ROOT / policy["wpt_capsule"]
    expected_wrapper = policy["wpt_capsule_manifest_sha256"]
    need = lambda value, message: None if value else fail(message)
    authenticate(wrapper_path, expected_wrapper)
    helper = load("pinned_wpt_runner", wrapper_path / "run.py")
    phase = sys.argv[2]
    need(re.fullmatch(r"zoom-normalization-[1-9][0-9]*", phase), "phase")
    role = "candidate"
    for name, expected in helper.read(HERE / "REFERENCES.json").items():
        need(helper.sha(ROOT / name) == expected, "reference: " + name)
    for name, expected in helper.read(wrapper_path / "REFERENCES.json").items():
        need(helper.sha(ROOT / name) == expected, "WPT reference: " + name)
    epoch_path, normative_path = Path(sys.argv[3]), Path(sys.argv[5])
    for path, expected in ((epoch_path, sys.argv[4]), (normative_path, sys.argv[6])):
        need(path.is_absolute() and path.is_file() and not path.is_symlink() and helper.sha(path) == expected, "external evidence binding")
    need(normative_path == ROOT / policy["calibration_assessment"] and sys.argv[6] == policy["calibration_assessment_sha256"], "exact candidate calibration assessment")
    epoch, normative = helper.read(epoch_path), helper.read(normative_path)
    need(sys.argv[4] == policy["epoch_sha256"], "exact epoch")
    need(epoch["semantic_index"]["head"] == policy["frozen_head"], "frozen HEAD")
    for name, expected in policy["fixed_native_sources"].items():
        need(helper.sha(ROOT / name) == expected, "fixed native source: " + name)
    helper.require_compiled_transition(epoch, role)
    transition = epoch["registered_number_transition"]
    need(transition.get("accepted") is False and transition.get("last_phase") == "zoom-normalization-build-2", "unaccepted zoom-normalization build2")
    need(normative["complete"] and normative["execution_preserved"] and normative["phase"] == "zoom-normalization-1" and normative["source_role"] == "zoom-normalization-v3" and normative["observation_only"] is True,
         "matching complete preserved calibration phase")
    need(normative["epoch_sha256"] == sys.argv[4] and normative["capsule_manifest_sha256"] == expected_wrapper,
         "calibration phase capsule/epoch")
    need(normative["native_sources"] == policy["source_roles"][role], "normative source role")
    for name, expected in policy["source_roles"][role].items():
        need(helper.sha(ROOT / name) == expected and epoch["pins"].get(name) == expected, "native source: " + name)
    metadata = helper.application_metadata(ROOT / policy["application_ini"], epoch["semantic_index"]["head"])
    need(metadata == normative["run_binding"], "same application metadata as calibration phase")
    out = Path(sys.argv[7])
    need(out.is_absolute() and not out.exists() and not out.is_symlink(), "absent output")
    out = out.resolve()
    need(out.parent == ROOT / "artifacts" and out.name.startswith("css-registered-container-zoom-runtime-"), "owned output")
    need(all(not os.environ.get(name) for name in policy["forbidden_environment"]), "unexpected environment")
    env = dict(os.environ, GIT_OPTIONAL_LOCKS="0", PYTHONDONTWRITEBYTECODE="1", MOZ_HEADLESS="1",
               MOZ_DISABLE_SAFE_MODE_KEY="1", MOZ_DISABLE_UPDATE_PROCESSING="1")
    h = helper.load("preservation", ROOT / policy["helpers"]["preservation"])
    guard = helper.load("epoch_guard", ROOT / policy["helpers"]["epoch"])
    control = helper.load("process_control", ROOT / policy["helpers"]["control"])
    validation = helper.load("observation_validation", HERE / "validate.py")
    baseline = helper.load("observer_baseline", HERE / "baseline.py")
    original = baseline.validate(ROOT, HERE, policy, helper, validation)
    before = guard.verify_current(h, ROOT, env, epoch)
    flags = {name: hashlib.sha256(h.git(ROOT / name, env, "ls-files", "-v", "-z")).hexdigest()
             for name in (".", "artifacts/css-spec-lean")}
    binaries = {name: h.fingerprint(ROOT, name) for name in policy["normal_binaries"]}
    need(all(value and epoch["pins"].get(name) == value for name, value in binaries.items()), "built binary epoch")
    need(binaries == policy["candidate_binaries"], "exact build2 binary pins")
    out.mkdir()
    helper.save(out / "BASELINE-BINDING.json", {"directory":policy["baseline_directory"], "pins":helper.read(HERE / "BASELINE-PINS.json"), "phase":original["phase"]})
    for name, value in (("EPOCH.json", epoch), ("PRE.json", before), ("INDEX-FLAGS.json", flags),
                        ("NORMAL-BINARIES.json", binaries), ("APPLICATION-METADATA.json", metadata)):
        helper.save(out / name, value)
    profile = out / "profile"
    profile.mkdir()
    identity = (profile.stat().st_dev, profile.stat().st_ino)
    token = secrets.token_urlsafe(24)
    rows, network_errors = [], []
    base = "/" + token + "/"

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def do_GET(self):
            route = {base: ("report.html", "text/html"), base + "report.js": ("report.js", "text/javascript"),
                     }
            route_path = self.path.split("?", 1)[0]
            if route_path not in route:
                self.send_error(404)
                return
            name, mime = route[route_path]
            body = (HERE / name).read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", mime + "; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        def do_POST(self):
            try:
                self.connection.settimeout(5)
                length = int(self.headers.get("Content-Length", "0"))
                need(self.path == base + "result" and 0 < length < 1_000_000 and not rows, "result request")
                need(self.headers.get("Origin") == origin, "result origin")
                payload = json.loads(self.rfile.read(length))
                self.send_response(204)
                self.end_headers()
                self.wfile.flush()
                rows.append(payload)
            except Exception as error:
                network_errors.append(repr(error))
                self.send_error(400)

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    server.daemon_threads = True
    origin = "http://127.0.0.1:" + str(server.server_port)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    command = [str(ROOT / policy["normal_binaries"][0]), "-headless", "-no-remote", "-profile", str(profile), origin + base + "?submit=1"]
    helper.save(out / "COMMAND.json", {"command": command, "phase": phase, "epoch_path": str(epoch_path),
                "epoch_sha256": sys.argv[4], "normative_assessment": str(normative_path), "normative_sha256": sys.argv[6],
                "manifest_sha256": sys.argv[1], "source_role": "zoom-normalization-v3", "observation_only": True})
    stopped = [False]
    def stop(signum, frame):
        stopped[0] = True
    for sig in (signal.SIGTERM, signal.SIGINT):
        signal.signal(sig, stop)
    process, error, post_error, cleanup, natural_exit = None, None, None, {}, None
    thread.start()
    try:
        with (out / "browser.log").open("x") as log:
            process = subprocess.Popen(command, cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
            helper.save(out / "PROCESS.json", {"pid": process.pid, "pgid": process.pid})
            deadline = time.monotonic() + policy["timeout_seconds"]
            while not rows:
                need(not stopped[0] and process.poll() is None and time.monotonic() < deadline, "cancelled, browser exited or observation timeout")
                time.sleep(0.1)
            natural_exit = process.poll()
    except BaseException as exc:
        error = repr(exc)
    finally:
        try:
            cleanup = control.terminate(process)
            need(cleanup["owned_group_absent"], "owned group remains")
            need(not profile.is_symlink() and (profile.stat().st_dev, profile.stat().st_ino) == identity, "profile identity")
            shutil.rmtree(profile)
            cleanup["profile_removed"] = not profile.exists()
        except BaseException as exc:
            cleanup = {"error": repr(exc), "owned_group_absent": False, "profile_removed": not profile.exists()}
        server.shutdown()
        thread.join(timeout=10)
        server.server_close()
        cleanup["server_thread_stopped"] = not thread.is_alive()
        helper.save(out / "CLEANUP.json", cleanup)
        try:
            post = guard.verify_current(h, ROOT, env, epoch)
            need(post == before, "full preservation")
            need(flags == {name: hashlib.sha256(h.git(ROOT / name, env, "ls-files", "-v", "-z")).hexdigest() for name in flags}, "index flags")
            for path, expected in ((epoch_path, sys.argv[4]), (normative_path, sys.argv[6])):
                need(helper.sha(path) == expected, "external evidence changed")
            need({name: h.fingerprint(ROOT, name) for name in binaries} == binaries, "binaries changed")
            post_metadata = helper.application_metadata(ROOT / policy["application_ini"], epoch["semantic_index"]["head"])
            need(post_metadata == metadata, "application metadata changed")
            for name, expected in policy["fixed_native_sources"].items():
                need(helper.sha(ROOT / name) == expected, "fixed native source changed: " + name)
            helper.save(out / "APPLICATION-METADATA-POST.json", post_metadata)
            helper.authenticate(HERE, sys.argv[1])
            helper.authenticate(wrapper_path, expected_wrapper)
            for name, expected in helper.read(wrapper_path / "REFERENCES.json").items():
                need(helper.sha(ROOT / name) == expected, "WPT reference changed: " + name)
            for name, expected in helper.read(HERE / "REFERENCES.json").items():
                need(helper.sha(ROOT / name) == expected, "reference changed: " + name)
            need(baseline.validate(ROOT, HERE, policy, helper, validation) == original, "saved baseline changed")
            helper.save(out / "POST.json", post)
        except BaseException as exc:
            post_error = repr(exc)
    helper.save(out / "RAW.json", {"payloads": rows, "network_errors": network_errors})
    summary, comparison = None, None
    try:
        need(len(rows) == 1 and not network_errors, "single complete observation payload")
        summary = validation.summarize(rows[0])
        comparison = baseline.compare(original["summary"], summary, validation)
    except BaseException as exc:
        error = error or repr(exc)
    preserved = error is None and post_error is None and cleanup.get("owned_group_absent") and cleanup.get("profile_removed") and cleanup.get("server_thread_stopped")
    result = {"complete": bool(preserved and summary), "execution_preserved": bool(preserved),
              "phase": phase, "manifest_sha256": sys.argv[1], "epoch_sha256": sys.argv[4],
              "normative_assessment_sha256": sys.argv[6], "normative_phase": normative["phase"], "native_sources": policy["source_roles"][role],
              "application_metadata": metadata, "normal_binaries": binaries, "summary": summary, "comparison": comparison,
              "browser_exit": process.returncode if process else None, "natural_exit_before_cleanup": natural_exit,
              "termination_requested_for_owned_cleanup": process is not None, "error": error, "preservation_error": post_error,
              "profile_configuration": "fresh default profile; WPT preferences are not imported",
              "normative_verdict": "not evaluated", "native_fix_acceptance": False, "source_role": "zoom-normalization-v3", "observation_only": True}
    helper.save(out / "RESULT.json", result)
    print(json.dumps(result, indent=2))
    return 0 if result["complete"] else 1


def fail(message):
    raise RuntimeError(message)


if __name__ == "__main__":
    raise SystemExit(main())
