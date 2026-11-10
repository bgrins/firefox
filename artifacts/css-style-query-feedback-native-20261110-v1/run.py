import hashlib
import importlib.util
import json
import os
import shutil
import signal
import subprocess
import sys
import time
import traceback
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
APP = ROOT / "objdir-full.noindex/dist/Nightly.app"
FIXTURE = (
    ROOT
    / "testing/web-platform/tests/css/css-conditional/container-queries/style-query-timeline-feedback.html"
)
EXTRAS = [
    "objdir-full.noindex/dist/bin/gtest/XUL",
    "objdir-full.noindex/build/application.ini",
    "objdir-full.noindex/_tests/web-platform/wptrunner.local.ini",
]
PYTHON = "/Users/bgrins/venvs/firefox/bin/python"
ACTIVE = set()
sys.dont_write_bytecode = True


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, value):
    path.write_text(json.dumps(value, indent=2) + "\n")


def git(*args):
    return subprocess.check_output(
        ["git", "-c", "core.fsmonitor=false", *args], cwd=ROOT
    )


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


def main():
    if not sys.flags.isolated or sys.flags.optimize:
        raise RuntimeError("Run with python -I and without -O")
    output = HERE / sys.argv[1]
    output.mkdir()
    roles = json.loads((HERE / "SOURCE-ROLES.json").read_text())
    for path, role in roles.items():
        assert sha(ROOT / path) == role["base"]
        assert sha(HERE / "candidate" / path) == role["candidate"]
    assert not FIXTURE.exists()
    assert (
        not git("diff", "--name-only").strip()
        and not git("diff", "--cached", "--name-only").strip()
    )
    head = git("rev-parse", "HEAD").decode().strip()
    index = hashlib.sha256(git("ls-files", "--stage", "-z")).hexdigest()
    baseline = json.loads(
        (
            ROOT / "artifacts/css-style-query-current-build-20261110-v1/build-result.json"
        ).read_text()
    )
    for path, digest in baseline["binaries"].items():
        assert sha(ROOT / path) == digest
    helper_path = (
        ROOT / "artifacts/css-round-context-quotient-reversible-pair-v2/bundle.py"
    )
    spec = importlib.util.spec_from_file_location("bundle", helper_path)
    bundle = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(bundle)
    app_before = bundle.scan(APP)
    extras = {path: bundle.entry(ROOT / path) for path in EXTRAS}
    backup_size = sum(row.get("size", 0) for row in app_before.values()) + sum(
        row["size"] for row in extras.values()
    )
    space = os.statvfs(ROOT)
    assert space.f_bavail * space.f_frsize - backup_size > 10 * 1024**3
    backups = output / "backups"
    backups.mkdir()
    app_map = bundle.backup(APP, app_before, backups / "app")
    extra_map = bundle.backup(ROOT, extras, backups / "extras")
    save(
        output / "BEFORE.json",
        {
            "head": head,
            "index": index,
            "sources": roles,
            "app": app_before,
            "extras": extras,
            "bundle_helper_sha256": sha(helper_path),
            "backup_bytes": backup_size,
            "baseline_binaries": baseline["binaries"],
        },
    )
    save(output / "BACKUPS.json", {"app": app_map, "extras": extra_map})
    env = dict(
        os.environ,
        MOZ_SKIP_PATH_PERFORMANCE_CHECK="1",
        MOZCONFIG=str(ROOT / "mozconfig"),
        PYTHONDONTWRITEBYTECODE="1",
        MOZ_HEADLESS="1",
    )
    touched = {}
    failure = None
    results = {}

    def cancel(*_):
        raise KeyboardInterrupt("Diagnostic cancelled")

    signal.signal(signal.SIGTERM, cancel)
    try:
        for path, role in roles.items():
            assert sha(ROOT / path) == role["base"]
            try:
                (ROOT / path).write_bytes((HERE / "candidate" / path).read_bytes())
            finally:
                touched[path] = sha(ROOT / path)
        FIXTURE.write_bytes(
            (HERE / "style-query-timeline-feedback.html").read_bytes()
        )
        results["build"] = run(
            [PYTHON, "./mach", "build", "binaries", "-j6"],
            output / "build.log", env, 1800)
        save(output / "BUILD.json", results["build"])
        assert results["build"]["exit_code"] == 0
        binaries = {path: sha(ROOT / path) for path in baseline["binaries"]}
        save(output / "CANDIDATE-BINARIES.json", binaries)
        print("Running instrumented query-timeline feedback", flush=True)
        browser_env = dict(
            env,
            STYLO_THREADS="1",
            MOZ_CRASHREPORTER_DISABLE="1",
            MOZ_CSS_FEEDBACK_TRACE="1",
        )
        command = [
            PYTHON,
            "./mach",
            "wpt",
            "--headless",
            "--processes=1",
            "--manifest-update",
            "--no-manifest-download",
            "--no-install-fonts",
            "--no-enable-webtransport-h3",
            "--setpref=dom.window.dump.enabled=true",
            "--setpref=layout.css.display-animations.enabled=false",
            "--setpref=layout.css.scroll-driven-animations.enabled=true",
            "--setpref=layout.css.style-queries.enabled=true",
            f"--binary={APP / 'Contents/MacOS/firefox'}",
            f"--log-raw={output / 'wpt-raw.jsonl'}",
            str(FIXTURE.relative_to(ROOT)),
        ]
        results["wpt"] = run(command, output / "wpt.log", browser_env, 120)
        save(output / "WPT.json", results["wpt"])
        assert {path: sha(ROOT / path) for path in binaries} == binaries
        assert results["wpt"]["exit_code"] in (0, 1)
        rows = [
            json.loads(line)
            for line in (output / "wpt-raw.jsonl").read_text().splitlines()
        ]
        tests = [row for row in rows if row["action"] == "test_status"]
        endings = [row for row in rows if row["action"] == "test_end"]
        expected = {
            "Style-query timeline feedback: opposed",
            "Style-query timeline feedback: aligned",
            "Style-query timeline feedback: constant-query",
            "Style-query timeline feedback: stable-underlying",
        }
        assert len(tests) == 4 and {row["subtest"] for row in tests} == expected
        assert len(endings) == 1 and endings[0]["status"] == "OK"
        save(
            output / "TEST-RESULTS.json",
            {
                "subtests": [
                    {
                        "name": row["subtest"],
                        "status": row["status"],
                        "message": row.get("message"),
                    }
                    for row in tests
                ],
                "harness_status": "OK",
                "all_pass": all(row["status"] == "PASS" for row in tests),
            },
        )
    except BaseException:
        failure = traceback.format_exc()
        save(output / "FAILURE.json", {"traceback": failure})
    finally:
        assert not ACTIVE, "Process cleanup incomplete; leave candidate for recovery"
        print("Restoring the original sources and browser", flush=True)
        for path, written in touched.items():
            assert sha(ROOT / path) == written
            (ROOT / path).write_bytes((HERE / "base" / path).read_bytes())
        if FIXTURE.exists():
            assert sha(FIXTURE) == sha(
                HERE / "style-query-timeline-feedback.html"
            )
            FIXTURE.unlink()
        bundle.restore(APP, app_before, bundle.scan(APP), backups / "app", app_map)
        for path, original in extras.items():
            current = bundle.entry(ROOT / path)
            if bundle.semantic({path: current}) != bundle.semantic({path: original}):
                bundle.restore_file(
                    ROOT / path,
                    current,
                    backups / "extras" / extra_map[path],
                    original,
                    ROOT,
                )
        assert bundle.semantic(bundle.scan(APP)) == bundle.semantic(app_before)
        assert bundle.semantic({
            path: bundle.entry(ROOT / path) for path in extras
        }) == bundle.semantic(extras)
        assert git("rev-parse", "HEAD").decode().strip() == head
        assert hashlib.sha256(git("ls-files", "--stage", "-z")).hexdigest() == index
        for path, role in roles.items():
            assert sha(ROOT / path) == role["base"]
        assert {path: sha(ROOT / path) for path in baseline["binaries"]} == baseline[
            "binaries"
        ]
        shutil.rmtree(backups)
        save(
            output / "RESTORED.json",
            {
                "source_and_application_restored": True,
                "index_preserved": True,
                "temporary_fixture_removed": not FIXTURE.exists(),
                "backup_removed": not backups.exists(),
                "backup_bytes": backup_size,
            },
        )
    save(
        output / "RESULT.json",
        {
            "commands": results,
            "error": failure,
            "restoration_verified": True,
            "native_fix_acceptance": False,
        },
    )
    if failure:
        raise RuntimeError("Diagnostic failed; baseline restored; see FAILURE.json")


if __name__ == "__main__":
    main()
