import copy, hashlib, importlib.util, json, os
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
RUNTIME = ROOT / "artifacts/css-attr-non-type-fallback-native-runtime-v2"
spec = importlib.util.spec_from_file_location("fallback_state", RUNTIME / "state.py")
s = importlib.util.module_from_spec(spec)
spec.loader.exec_module(s)
epoch = s.read(RUNTIME / "CURRENT-EPOCH.json")
assert epoch["attribute_fallback_transition"]["role"] == "candidate"
assert epoch["attribute_fallback_transition"]["compiled"] is True
assert s.read(RUNTIME / "candidate-build-1/RESULT.json")["command_success"] is True
original = ROOT / "artifacts/css-attr-non-type-fallback-wpt-runtime-original-1/ASSESSMENT.json"
candidate = ROOT / "artifacts/css-attr-non-type-fallback-wpt-runtime-candidate-1/ASSESSMENT.json"
a, b = s.read(original), s.read(candidate)
assert a["complete"] and a["execution_preserved"]
assert b["complete"] and b["execution_preserved"] and b["comparison_gate_passed"]
assert a["regression_signature"] == b["regression_signature"]
name = "testing/web-platform/tests/css/css-values/attr-non-type-used-fallback-cycle.html"
source = ROOT / "artifacts/css-attr-non-type-fallback-repair-v3/candidate-head" / name
assert s.sha(source) == "6f966f427d1a6884c0a666e173333d62a26b19ee779dcd70f74b4617d2dbd5a3"
assert not (ROOT / name).exists() and not (ROOT / name).is_symlink()
before = s.a.verify_current(s.h, ROOT, s.ENV, epoch)
s.save(HERE / "INSTALL-PRE.json", before)
with (ROOT / name).open("xb") as stream:
    stream.write(source.read_bytes())
current = copy.deepcopy(epoch)
current["pins"][name] = s.sha(ROOT / name)
info = (ROOT / name).lstat()
current["installed_identities"][name] = [info.st_dev, info.st_ino]
current["counts"]["roles"] = len(current["pins"])
current["counts"]["installed_identities"] = len(current["installed_identities"])
after = s.a.verify_current(s.h, ROOT, s.ENV, current)
s.save(HERE / "INSTALL-POST.json", after)
s.save(HERE / "INSTALL.json", {"fixture": name, "sha256": s.sha(ROOT / name), "identity": [info.st_dev, info.st_ino], "original_assessment_sha256": s.sha(original), "candidate_assessment_sha256": s.sha(candidate), "all_previous_pins_preserved": True, "native_source_changed": False})
(RUNTIME / "CURRENT-EPOCH.json").write_text(json.dumps(current, indent=2, sort_keys=True) + "\n")
print("Installed exact tested WPT; full preservation verified", flush=True)
