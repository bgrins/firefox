import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
for name, digest in json.loads((HERE / "REFERENCES.json").read_text()).items():
    assert sha(ROOT / name) == digest, name
pins = json.loads((HERE / "SOURCE-PINS.json").read_text())
for name, pin in pins.items():
    captured = HERE / ("context" if pin.get("role") else "base") / name
    assert sha(captured) == pin["sha256"], name
name = "layout/style/test/gtest/TestKeyframePresentation.cpp"
base = (HERE / "base" / name).read_text()
candidate = (HERE / "candidate" / name).read_text()
end = "}  // namespace\n"
assert base.endswith(end) and candidate.startswith(base[:-len(end)])
added = candidate[len(base) - len(end):]
roster = json.loads((HERE / "ROSTER.json").read_text())
arena = (HERE / "context/layout/style/test/gtest/TestAnimationOperationArena.cpp").read_text()
def names(text):
    return [suite + "." + test for suite, test in re.findall(r"TEST(?:_F)?\(\s*(\w+)\s*,\s*(\w+)\s*\)", text)]
assert names(base) + names(arena) == roster["original_gtests"]
assert names(candidate) + names(arena) == roster["candidate_gtests"]
assert len(roster["original_gtests"]) == 20 and len(roster["candidate_gtests"]) == 22
old_table = base[base.index("TEST_F(KeyframePresentation, RetainedEndpointProviderDemand)"):]
assert len(re.findall(r'^      \{"', old_table, re.M)) == 22
new_table = added[added.index("} cases[] = {"):added.index("  for (const auto& test : cases)")]
assert re.findall(r'^      \{"([^\"]+)"', new_table, re.M) == roster["new_admission_rows"]
assert len(roster["new_admission_rows"]) == 9
math = added[added.index("TEST_F(KeyframePresentation, RegisteredNumberMathDemandCompletion)"):]
assert math.count("ASSERT_NO_FATAL_FAILURE(ExpectPendingNumberResolution(") == 3
assert math.count('"--unrelated"') == 2
records = []
with tempfile.TemporaryDirectory(prefix="registered-number-pending-gtest-", dir="/private/tmp") as temp:
    scratch = Path(temp)
    dest = scratch / name
    dest.parent.mkdir(parents=True)
    shutil.copyfile(HERE / "base" / name, dest)
    for args in (["--check"], [], ["--reverse", "--check"], ["--reverse"], ["--check"], []):
        command = ["git", "apply", *args, str(HERE / "overlay.patch")]
        result = subprocess.run(command, cwd=scratch, text=True, capture_output=True, timeout=20)
        records.append({"args": args, "exit": result.returncode, "stderr": result.stderr})
        assert result.returncode == 0, records[-1]
        if args in ([], ["--reverse"]):
            assert dest.read_text() == (base if args else candidate)
assert not scratch.exists()
print(json.dumps({"status": "PENDING_OVERLAY_ARTIFACT_CHECK_PASS", "source_pins": len(pins), "original_gtests": 20, "candidate_gtests": 22, "old_pending_rows": 22, "added_pending_calls": 12, "expected_pending_calls": 34, "inherits_effect_flag_observed": False, "transport": records, "scratch_removed": True, "compiled_or_executed": False}, indent=2))
