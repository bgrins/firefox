import hashlib
import json
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
LAB = ROOT / "artifacts/css-keyframe-group-order-runtime-20261110-v1"
AUTHOR = ROOT / "artifacts/css-css-animation-keyframe-order-candidate-20261110-v1"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*args):
    return subprocess.check_output(["git", "-c", "core.fsmonitor=false", *args], cwd=ROOT)


def main():
    inputs = json.loads((LAB / "RUN-INPUTS.json").read_text())
    for name, expected in inputs.items():
        assert sha(LAB / name) == expected, name
    plan = json.loads((LAB / "RUN-PLAN.json").read_text())
    roles = json.loads((LAB / "SOURCE-ROLES.json").read_text())
    test = "testing/web-platform/tests/css/css-animations/KeyframeEffect-getKeyframes.tentative.html"
    assert set(roles) == {"layout/style/GeckoBindings.cpp", "layout/style/GeckoBindings.h", test}
    for name, role in roles.items():
        assert bool(role.get("install_both")) == (name == test), name
        assert sha(LAB / "source" / name) == role["base"]
        assert sha(LAB / "candidate" / name) == role["candidate"]
        assert (LAB / "candidate" / name).read_bytes() == (AUTHOR / "candidate" / name).read_bytes()
        assert (LAB / "source" / name).read_bytes() == git("show", plan["head"] + ":" + name)
    pins = json.loads((LAB / "runtime-inputs/test-source-pins.json").read_text())
    metadata = test.replace("/tests/", "/meta/", 1) + ".ini"
    assert metadata in pins and metadata not in roles
    for name, expected in pins.items():
        result = subprocess.run(["git", "-c", "core.fsmonitor=false", "show", plan["head"] + ":" + name], cwd=ROOT, capture_output=True)
        if expected is None:
            assert result.returncode != 0, name
        else:
            assert result.returncode == 0 and hashlib.sha256(result.stdout).hexdigest() == expected, name
    assert plan["fixtures"] == {}
    assert len(plan["suites"]) == len(set(plan["suites"])) == 9
    pages = {"/" + x.removeprefix("testing/web-platform/tests/") for x in plan["suites"]}
    baseline_file = ROOT / "artifacts/css-pseudo-animation-snapshot-runtime-20261110-v1/baseline1/TEST-RESULTS.json"
    baseline = json.loads(baseline_file.read_text())
    previous = {(r["test"], r["subtest"]) for r in baseline["subtests"] if r["test"] in pages}
    added = ("/css/css-animations/KeyframeEffect-getKeyframes.tentative.html", "KeyframeEffect.getKeyframes() orders merged percentage groups by their first occurrence while later logical declarations win")
    expected = [tuple(x) for x in json.loads((LAB / "EXPECTED-CALLBACKS.json").read_text())]
    assert len(expected) == len(set(expected)) == 86
    assert set(expected) == previous | {added} and len(previous) == 85
    expected_baseline = json.loads((LAB / "EXPECTED-BASELINE.json").read_text())
    prior_statuses = {(r["test"], r["subtest"]): r["status"] for r in baseline["subtests"] if r["test"] in pages}
    prior_statuses[added] = "FAIL"
    assert len(expected_baseline["subtests"]) == 86
    assert {(r["test"], r["subtest"]): r["status"] for r in expected_baseline["subtests"]} == prior_statuses
    assert len(expected_baseline["harness"]) == 9
    assert {r["test"]: r["status"] for r in expected_baseline["harness"]} == {p: "OK" for p in pages}
    retained = json.loads((LAB / "runtime-inputs/retained-build.json").read_text())
    assert sha(ROOT / retained["origin"]) == retained["origin_sha256"]
    assert retained["mozconfig_sha256"] == plan["mozconfig_sha256"]
    for name, digest in retained["source_sha256"].items():
        assert hashlib.sha256(git("show", plan["head"] + ":" + name)).hexdigest() == digest
    changes = json.loads((LAB / "EXPECTED-CHANGES.json").read_text())
    assert len(changes) == 2
    assert all(r["kind"] == "assertion" and r["baseline"] == "FAIL" and r["candidate"] == "PASS" for r in changes)
    assert {(r["test"], r["subtest"]) for r in changes} == {
        added,
        (added[0], "KeyframeEffect.getKeyframes() returns expected frames for an animation with multiple keyframes for the same time and with different easing functions and composite operations"),
    }
    origins = json.loads((LAB / "WRAPPER-ORIGINS.json").read_text())
    for name, expected_hash in origins["preserved_helpers"].items():
        assert sha(LAB / name) == expected_hash
        assert (LAB / name).read_bytes() == git("show", origins["signed_origin"] + ":" + origins["origin_directory"] + "/" + name)
    controls = subprocess.run([sys.executable, "-I", str(LAB / "parser-controls.py")], capture_output=True, text=True, check=True)
    (HERE / "parser-controls.json").write_text(controls.stdout)
    print(json.dumps({"status": "PASS", "runtime_input_manifest_sha256": sha(LAB / "RUN-INPUTS.json"), "head": plan["head"], "runtime_inputs": len(inputs), "source_roles": len(roles), "test_pins": len(pins), "callbacks": len(expected), "harness_rows": len(pages), "expected_changes": len(changes), "helper_origins_verified": True, "native_or_browser_execution": False}, indent=2))


if __name__ == "__main__":
    main()
