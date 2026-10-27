import copy
import hashlib
import json
from pathlib import Path

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


for path in HERE.glob("*.py"):
    compile(path.read_text(), str(path), "exec")
authenticate(read(HERE / "REFERENCES.json"), ROOT)
settings = read(HERE / "CONFIG.json")
assert settings["ready_for_execution"] is False and settings["final_review"] is None
actual = ROOT / settings["epoch"]
assert sha(actual / "FILES.json") == settings["epoch_manifest_sha256"]
assert sha(actual / "ROOT-FINAL-CHECK.json") == settings["root_receipt_sha256"]
authenticate(read(actual / "FILES.json"), actual)
gate = load("gate", HERE / "epoch_gate.py")
result = gate.bind(ROOT, actual, settings, read, sha, authenticate, load, need)
assert len(result[2]["sources"]) == 53 and len(result[4]["modified_native_paths"]) == 30
assert len(result[5]) == 8
assert all(result[3][name] == value for name, value in read(actual / "FINAL-PINS.json").items())
assert (HERE / "fixture.html").read_bytes() == (ROOT / settings["proposal"] / "probe.html").read_bytes()
files = ["STATE.json", "ROOT-FINAL-CHECK.json", "FINAL.json", "FINAL-PINS.json", "CONFIG.json", "INSTALLATION.json"]
original = {n: read(actual / n) for n in files}
rejected = []
for label, edit in [
    ("not-installed", lambda d: d["STATE.json"].update(installed=False)),
    ("failed-build", lambda d: d["STATE.json"].update(build_exit=1)),
    ("recovery-errors", lambda d: d["STATE.json"].update(recovery_errors=["test"])),
    ("wrong-binaries", lambda d: d["ROOT-FINAL-CHECK.json"].update(installed_binary_pins={})),
    ("missing-eighth-test", lambda d: d["INSTALLATION.json"].update(owned_tests={})),
    ("missing-staged-count", lambda d: d["ROOT-FINAL-CHECK.json"].pop("staged_paths")),
    ("wrong-stage-count", lambda d: d["ROOT-FINAL-CHECK.json"].update(staged_paths=924)),
    ("wrong-native-count", lambda d: d["ROOT-FINAL-CHECK.json"].update(native_modified_paths=29)),
    ("old-candidate-source", lambda d: d["INSTALLATION.json"]["installed_source_pins"].update({"dom/svg/DOMSVGLength.cpp": "0" * 64})),
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
classifier = load("classifier", HERE / "classify.py")
rows = [{"subtest": name, "status": "PASS", "message": None} for name in settings["names"]]
assert classifier.classify(rows, settings["names"], need)["counts"] == {"PASS": 4, "FAIL": 0}
message = "assert_equals: first value under current-viewport hypothesis expected 40 but got 20"
failed = copy.deepcopy(rows)
failed[1].update(status="FAIL", message=message)
assert classifier.classify(failed, settings["names"], need)["counts"] == {"PASS": 3, "FAIL": 1}
negatives = []
for index, text in [(0, message), (2, message), (3, message),
                    (1, "assert_equals: revealed value calibration expected 40 but got 20"),
                    (1, "assert_equals: repeat value expected 20 but got 40"),
                    (1, message.replace("got 20", "got NaN")),
                    (1, message.replace("got 20", "got 0")),
                    (1, message.replace("expected 40", "expected 30"))]:
    bad = copy.deepcopy(rows)
    bad[index].update(status="FAIL", message=text)
    negatives.append(bad)
negatives += [rows[:-1], rows[::-1], [rows[0]] * 4]
for bad in negatives:
    try:
        classifier.classify(bad, settings["names"], need)
    except RuntimeError:
        pass
    else:
        raise AssertionError(bad)
print(json.dumps({"installed_expanded114_archive_gate": True, "preserved_original_pins": 392,
                  "audit_extended_pins": len(result[3]), "sources": 53, "native_paths": 30,
                  "installed_test_identities": 8, "gate_rejections": rejected,
                  "classifier_negative_controls": len(negatives), "exact_fixture": True,
                  "ready_for_execution": False, "final_review": None,
                  "browser_or_native_actions": False}, indent=2))
