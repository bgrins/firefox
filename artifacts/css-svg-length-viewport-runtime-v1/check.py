import ast
import copy
import hashlib
import json
import math
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
read = lambda p: json.loads(p.read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def need(ok, why):
    if not ok:
        raise RuntimeError(why)


def authenticate(mapping, base):
    for name, digest in mapping.items():
        need(sha(base / name) == digest, name)


def load(name, path):
    module = type("Module", (), {})()
    exec(compile(path.read_text(), str(path), "exec"), module.__dict__)
    return module


authenticate(read(HERE / "REFERENCES.json"), ROOT)
settings = read(HERE / "CONFIG.json")
assert settings["ready_for_execution"] is False
actual = ROOT / settings["epoch"]
assert sha(actual / "FILES.json") == settings["epoch_manifest_sha256"]
assert sha(actual / "ROOT-FINAL-CHECK.json") == settings["root_receipt_sha256"]
authenticate(read(actual / "FILES.json"), actual)
gate = load("gate", HERE / "epoch_gate.py")
result = gate.bind(ROOT, actual, settings, read, sha, authenticate, load, need)
assert len(result[2]["sources"]) == 53 and len(result[3]) == 386
assert len(result[4]["modified_native_paths"]) == 30 and len(result[5]) == 7
files = ["STATE.json", "ROOT-FINAL-CHECK.json", "FINAL.json", "FINAL-PINS.json", "CONFIG.json", "INSTALLATION.json"]
original = {n: read(actual / n) for n in files}
rejected = []
for label, edit in [
    ("not-installed", lambda d: d["STATE.json"].update(installed=False)),
    ("failed-build", lambda d: d["STATE.json"].update(build_exit=1)),
    ("recovery-errors", lambda d: d["STATE.json"].update(recovery_errors=["test"])),
    ("wrong-binaries", lambda d: d["ROOT-FINAL-CHECK.json"].update(installed_binary_pins={})),
    ("missing-factor-test", lambda d: d["INSTALLATION.json"]["owned_tests"].pop(next(iter(d["INSTALLATION.json"]["owned_tests"])))),
    ("wrong-staged-key", lambda d: d["ROOT-FINAL-CHECK.json"].pop("staged_paths")),
    ("wrong-stage-count", lambda d: d["ROOT-FINAL-CHECK.json"].update(staged_paths=924)),
    ("old-native-count", lambda d: d["ROOT-FINAL-CHECK.json"].update(native_modified_paths=29)),
]:
    data = copy.deepcopy(original)
    edit(data)
    rd = lambda path: copy.deepcopy(data[path.name]) if path.parent == actual and path.name in data else read(path)
    try:
        gate.bind(ROOT, actual, settings, rd, sha, authenticate, load, need)
    except (RuntimeError, KeyError):
        rejected.append(label)
    else:
        raise AssertionError(label)
repair = ROOT / "artifacts/css-svg-absolute-factor-repair-v1"
before = (repair / "original-SVGLength.cpp").read_text()
after = (repair / "candidate-SVGLength.cpp").read_text()
start = "float SVGLength::GetAbsUnitsPerAbsUnit("
end = "float SVGLength::GetValueInSpecifiedUnit("
assert before.split(start)[0] == after.split(start)[0]
assert before.split(end)[1] == after.split(end)[1]
module = ast.parse((HERE / "run.py").read_text())
loop = next(n for n in next(n for n in module.body if isinstance(n, ast.Try)).body if isinstance(n, ast.For))
classifier = compile(ast.Module(body=[loop], type_ignores=[]), "<copied-classifier>", "exec")


def classify(name, message):
    env = {"result": {"rows": [{"status": "FAIL", "subtest": name, "message": message}]},
           "mismatches": [], "re": re, "math": math, "need": need, "read": read,
           "proposal": ROOT / settings["proposal"]}
    exec(classifier, env)
    return env["mismatches"]


assert classify("vw: get after iframe resize", "assert_approx_equals: first value after iframe resize expected 40 +/- 0.001 but got 20")
negative = [
    ("vw: get after iframe resize", "assert_approx_equals: initial source value expected 20 +/- 0.001 but got 0"),
    ("vw: get after iframe resize", "assert_approx_equals: value after explicit layout expected 40 +/- 0.001 but got 20"),
    ("vw: get after iframe resize", "assert_approx_equals: first value after iframe resize expected 40 +/- 0.001 but got NaN"),
    ("vw: get after iframe resize", "assert_approx_equals: first value after iframe resize expected 40 +/- 0.001 but got 40"),
    ("vw: get after iframe resize", "assert_approx_equals: first value after iframe resize expected 30 +/- 0.001 but got 20"),
    ("px: get after iframe resize", "assert_approx_equals: first value after iframe resize expected 10 +/- 0.001 but got 0"),
]
for name, message in negative:
    try:
        classify(name, message)
    except (RuntimeError, ValueError):
        pass
    else:
        raise AssertionError(message)
print(json.dumps({"actual_installed115_gate": True, "sources": 53,
                  "audit_extended_pins": 386, "native_paths": 30, "installed_test_identities": 7,
                  "gate_rejections": rejected, "classifier_negative_controls": len(negative),
                  "viewport_source_outside_factor_function_unchanged": True,
                  "ready_for_execution": False, "browser_or_native_actions": False}, indent=2))
