import configparser
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "artifacts/css-contextual-duration-feedback-browser-runtime-2"
PYTHON = "/Users/bgrins/venvs/firefox/bin/python"
BINARY = ROOT / "objdir-full.noindex/dist/Nightly.app/Contents/MacOS/firefox"
RUNTIME = ROOT / "artifacts/css-registered-number-native-runtime-v1"


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def save(name, value):
    with (OUTPUT / name).open("x") as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write("\n")


def git(*args):
    return subprocess.check_output(
        ["git", "--no-optional-locks", "-c", "core.fsmonitor=false", *args],
        cwd=ROOT, env=dict(os.environ, GIT_OPTIONAL_LOCKS="0"))


def state():
    assert not (RUNTIME / "SOURCE-TRANSITION.lock").exists()
    names = ["CURRENT-EPOCH.json", "OWNED.json", "ROLE.json"]
    controls = {name: digest(RUNTIME / name) for name in names}
    app = BINARY.parents[1]
    pins = {str(path.relative_to(ROOT)): digest(path) for path in [
        BINARY, BINARY.parent / "XUL", app / "Resources/application.ini",
        ROOT / "servo/components/style/custom_properties.rs"]}
    return {"head": git("rev-parse", "HEAD").decode().strip(),
            "branch": git("branch", "--show-current").decode().strip(),
            "status_sha256": hashlib.sha256(git("status", "--porcelain=v1", "-z", "--untracked-files=all")).hexdigest(),
            "diff_sha256": hashlib.sha256(git("diff", "--binary")).hexdigest(),
            "staged": git("diff", "--cached", "--name-only").decode(),
            "index_sha256": digest(ROOT / ".git/index"), "controls": controls, "pins": pins}


def main():
    assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
    assert len(sys.argv) == 3
    assert not any(name in os.environ for name in (
        "GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_OBJECT_DIRECTORY",
        "GIT_ALTERNATE_OBJECT_DIRECTORIES"))
    fixture = Path(sys.argv[1]).resolve()
    manifest = Path(sys.argv[2]).resolve()
    roster = json.loads((manifest.parent / "ROSTER.json").read_text())
    assert fixture.is_relative_to(ROOT / "artifacts")
    assert manifest.is_relative_to(ROOT / "artifacts")
    assert not OUTPUT.exists()
    before = state()
    assert before["head"] == "ecfe313d582a335c04d80bfd360fd3a591defdb7"
    assert before["branch"] == "stylo-bloom-verification-2" and not before["staged"]
    assert before["controls"]["CURRENT-EPOCH.json"] == "1c63d31d17f335b0988b3183da09d47e7e52cf1dc9a5eca09966582579ce45b8"
    assert before["controls"]["OWNED.json"] == "76bf1cf2881f1d9744ab8007c773df0a8db2157e7ca0f0b98e5daf04829786e5"
    assert before["controls"]["ROLE.json"] == "96358abf09af0d948363a37da3cc1858fa75f1613763171dfa3b442686205682"
    assert before["pins"]["servo/components/style/custom_properties.rs"] == "2675b33b30ac43db5b758d5a80f42fa4530856c32d5a0923882a15f8a8bc5774"
    assert before["pins"]["objdir-full.noindex/dist/Nightly.app/Contents/Resources/application.ini"] == "936bd88f3e47b0106b04b608cda306cc2fdee3bfd502e041b561febdb9643d3a"
    OUTPUT.mkdir()
    save("PRE.json", before)
    (OUTPUT / "records").mkdir(mode=0o700)
    tests = OUTPUT / "tests"
    shutil.copytree(fixture, tests)
    copied_resources = {str(path.relative_to(tests)): digest(path)
                        for path in sorted(tests.rglob("*")) if path.is_file()}
    save("TESTED-RESOURCES.json", copied_resources)
    assert not (tests / "tools").exists()
    (tests / "tools").symlink_to(ROOT / "testing/web-platform/tests/tools", target_is_directory=True)
    server = json.loads((ROOT / "testing/web-platform/tests/config.json").read_text())
    settings = json.loads((ROOT / "artifacts/css-contextual-duration-first-read-trace-browser-v1/POLICY.json").read_text())["wpt"]
    server["ports"] = {key: ["auto"] * count for key, count in settings["server_protocols"].items()}
    (tests / "config.json").write_text(json.dumps(server))
    metadata = OUTPUT / "metadata"
    shutil.copytree(manifest.parent / "meta", metadata)
    shutil.copyfile(manifest, metadata / "MANIFEST.json")
    save("TESTED-METADATA.json", {str(path.relative_to(metadata)): digest(path)
                                  for path in sorted(metadata.rglob("*")) if path.is_file()})
    config = configparser.ConfigParser(interpolation=None)
    config.read(ROOT / settings["wpt_config"])
    for section in list(config.sections()):
        if section.startswith("manifest:"):
            config.remove_section(section)
    config["paths"]["run_info"] = str(ROOT / "objdir-full.noindex")
    config["web-platform-tests"]["sync_path"] = str(OUTPUT / "unused-sync")
    config["manifest:upstream"] = {"tests": str(tests), "metadata": str(metadata),
                                   "url_base": "/", "manifest": str(metadata / "MANIFEST.json")}
    with (OUTPUT / "wptrunner.ini").open("x") as stream:
        config.write(stream)
    command = [PYTHON, "./mach", "wpt", "--headless", "--processes=1",
               "--no-manifest-update", "--no-manifest-download", "--binary=" + str(BINARY),
               "--config=" + str(OUTPUT / "wptrunner.ini"),
               "--run-info=" + str(ROOT / "objdir-full.noindex"),
               "--prefs-root=" + str(ROOT / "testing/profiles"),
               "--log-raw=" + str(OUTPUT / "raw.jsonl")]
    command.extend("--include=" + test for test in roster["tests"])
    temporary = Path(tempfile.mkdtemp(prefix="css-duration-feedback-", dir="/private/tmp"))
    temporary_identity = (temporary.stat().st_dev, temporary.stat().st_ino)
    env = dict(os.environ, TMPDIR=str(temporary), TMP=str(temporary), TEMP=str(temporary),
               MOZ_DISABLE_SAFE_MODE_KEY="1", MOZ_DISABLE_UPDATE_PROCESSING="1", GIT_OPTIONAL_LOCKS="0",
               MOZ_SKIP_PATH_PERFORMANCE_CHECK="1",
               DURATION_PROGRESS_RECORD_DIR=str(OUTPUT / "records"),
               DURATION_PROGRESS_RUN_ID="css-duration-feedback-original-v2")
    env.pop("MOZ_DURATION_FIRST_READ_TRACE", None)
    control_path = ROOT / settings["control_helper"]
    spec = importlib.util.spec_from_file_location("feedback_process_control", control_path)
    control = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(control)
    save("COMMAND.json", {"argv": command, "timeout_seconds": 180,
                          "fixture": str(fixture), "manifest_sha256": digest(manifest),
                          "control_helper_sha256": digest(control_path), "temporary": str(temporary)})
    process, exit_code, error, cleanup = None, None, None, None
    def stop(signum, frame):
        raise InterruptedError("Interrupted diagnostic WPT: " + str(signum))
    signal.signal(signal.SIGTERM, stop)
    try:
        with (OUTPUT / "wpt.log").open("x") as log:
            process = subprocess.Popen(command, cwd=ROOT, env=env, stdout=log,
                                       stderr=subprocess.STDOUT, start_new_session=True)
            save("PROCESS.json", {"pid": process.pid, "pgid": process.pid})
            exit_code = process.wait(timeout=180)
    except BaseException as exc:
        error = repr(exc)
    finally:
        cleanup = control.terminate(process)
        assert cleanup["owned_group_absent"]
        assert not temporary.is_symlink()
        assert (temporary.stat().st_dev, temporary.stat().st_ino) == temporary_identity
        shutil.rmtree(temporary)
        save("CLEANUP.json", cleanup)
    after = state()
    save("POST.json", after)
    events = [json.loads(line) for line in (OUTPUT / "raw.jsonl").read_text().splitlines()]
    callbacks = [event for event in events if event.get("action") == "test_status"]
    endings = [event for event in events if event.get("action") == "test_end"]
    expected_callbacks = sorted((test, name) for test, names in roster["tests"].items() for name in names)
    complete = (sorted((event["test"], event["subtest"]) for event in callbacks) == expected_callbacks
                and sorted(event["test"] for event in endings) == sorted(roster["tests"])
                and all(event["status"] == "OK" for event in endings)
                and sorted(path.name for path in (OUTPUT / "records").iterdir()) == sorted(roster["records"]))
    save("ASSESSMENT.json", {"complete": complete,
                             "callbacks": [{key: event.get(key) for key in ("test", "subtest", "status", "message")} for event in callbacks],
                             "endings": [{key: event.get(key) for key in ("test", "status")} for event in endings]})
    save("RESULT.json", {"exit": exit_code, "error": error, "state_preserved": before == after,
                         "complete_browser_evidence": complete, "native_fix_acceptance": False})
    print(json.dumps({"exit": exit_code, "error": error, "state_preserved": before == after, "complete": complete}))
    assert before == after
    assert error is None
    assert complete, "Incomplete diagnostic capture"


if __name__ == "__main__":
    main()
