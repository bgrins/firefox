import difflib
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
for name, record in json.loads((HERE / "REFERENCES.json").read_text()).items():
    path = ROOT / name
    assert sha(path) == record["sha256"] and path.stat().st_size == record["bytes"]
sources = json.loads((HERE / "SOURCE.json").read_text())["sources"]
for source in sources:
    path = ROOT / source["path"]
    assert sha(path) == source["sha256"]
    lines = path.read_text().splitlines(keepends=True)
    for excerpt in source["excerpts"]:
        assert "".join(lines[excerpt["first"] - 1:excerpt["last"]]) == excerpt["text"]
old = (ROOT / "artifacts/css-computed-size-publication-lean-v1/replay.py").read_text()
new = (HERE / "replay.py").read_text()
assert (HERE / "REPLAY-DELTA.patch").read_text() == "".join(difflib.unified_diff(
    old.splitlines(True), new.splitlines(True),
    fromfile="css-computed-size-publication-lean-v1/replay.py",
    tofile="css-font-settings-conversion-effects-lean-v1/replay.py"))
receipt = json.loads((HERE / "run5/CHECK.json").read_text())
assert receipt["success"] and len(receipt["audited_theorems"]) == 21
assert receipt["false_controls_rejected"] == 7
assert sha(HERE / "Settings.lean") == receipt["source_sha256"]
assert (HERE / "Settings.lean").read_bytes() == (HERE / "run5/Settings.lean").read_bytes()
assert json.loads((HERE / "IMPORT-PINS.json").read_text()) == {}
for run in range(1, 6):
    scratch = Path(json.loads((HERE / f"run{run}/SCRATCH.json").read_text())["path"])
    assert not scratch.exists() and not scratch.is_symlink()
print(json.dumps({"references": 7, "exact_source_files": len(sources),
                  "exact_final_lean": receipt["source_sha256"], "audits": 21,
                  "false_controls": 7, "absent_scratch_directories": 5,
                  "exact_runner_delta": True, "native_refinement": False}))
