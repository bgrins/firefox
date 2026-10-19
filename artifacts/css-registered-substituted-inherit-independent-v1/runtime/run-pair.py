import hashlib
import json
import os
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
GIT = ["git", "-c", "core.fsmonitor=false"]
NATIVE = ['servo/components/style/custom_properties.rs']
TESTS = ['testing/web-platform/tests/css/css-properties-values-api/registered-substituted-inherit-restyle.html', 'testing/web-platform/tests/css/css-properties-values-api/registered-inherit-invalid.html', 'testing/web-platform/tests/css/css-properties-values-api/registered-initial-computed-value.html', 'testing/web-platform/tests/css/css-properties-values-api/registered-properties-inheritance.html', 'testing/web-platform/tests/css/css-properties-values-api/var-reference-registered-properties-cycles.html']
ENV = dict(os.environ, MOZ_SKIP_PATH_PERFORMANCE_CHECK="1")


def digest(path):
    return hashlib.file_digest(Path(path).open("rb"), "sha256").hexdigest()


def run(command, log):
    with (HERE / log).open("w") as output:
        result = subprocess.run(command, cwd=ROOT, env=ENV, stdout=output,
                                stderr=subprocess.STDOUT)
    print(log, result.returncode, flush=True)
    return result.returncode


def pins(paths):
    return {p: digest(ROOT / p) for p in paths}


changed = subprocess.check_output(GIT + ["diff", "--name-only"], cwd=ROOT).decode().splitlines()
stable_paths = sorted(set(changed + TESTS) - set(NATIVE))
stable = pins(stable_paths)
final_pins = json.loads((HERE / "CANDIDATE-PINS.json").read_text())
for name in NATIVE:
    assert digest(ROOT / name) == json.loads((HERE / "ORIGINAL-PINS.json").read_text())[name], name
    assert digest(HERE / "source/candidate" / name) == final_pins[name]
    assert digest(HERE / "source/original" / name) == json.loads(
        (HERE / "ORIGINAL-PINS.json").read_text())[name]

record = {"head": subprocess.check_output(GIT + ["rev-parse", "HEAD"], cwd=ROOT).decode().strip(),
          "stable_sources": stable, "runs": [],
          "scope": "Paired shared-tree macOS build; not an isolated upstream build."}
try:
    for variant, directory in [("baseline", "original"), ("candidate", "candidate")]:
        assert pins(stable_paths) == stable
        for name in NATIVE:
            (ROOT / name).write_bytes((HERE / "source" / directory / name).read_bytes())
        entry = {"variant": variant, "sources": pins(NATIVE), "tests": TESTS}
        record["runs"].append(entry)
        entry["build_exit"] = run(["./mach", "build", "binaries"], f"final-{variant}-build.log")
        assert entry["build_exit"] == 0, entry
        binaries = ["objdir-full.noindex/dist/Nightly.app/Contents/MacOS/" + n
                    for n in ["firefox", "XUL"]]
        entry["binaries"] = pins(binaries)
        raw = HERE / f"final-{variant}-raw.json"
        command = ["./mach", "wpt", "--headless", "--processes=1", "--log-raw=" + str(raw)] + TESTS
        entry["command"] = command
        entry["test_exit"] = run(command, f"final-{variant}.log")
        assert entry["test_exit"] in [0, 1]
        assert pins(stable_paths) == stable
        assert pins(NATIVE) == entry["sources"]
        assert pins(binaries) == entry["binaries"]
        entry["stable_after"] = True
        (HERE / "FINAL-PAIR.json").write_text(json.dumps(record, indent=2) + "\n")
finally:
    for name in NATIVE:
        candidate = (HERE / "source/candidate" / name).read_bytes()
        if (ROOT / name).read_bytes() != candidate:
            (ROOT / name).write_bytes(candidate)
    record["candidate_sources_restored"] = pins(NATIVE) == {n: final_pins[n] for n in NATIVE}
    (HERE / "FINAL-PAIR.json").write_text(json.dumps(record, indent=2) + "\n")
assert record["runs"][-1]["test_exit"] == 0
