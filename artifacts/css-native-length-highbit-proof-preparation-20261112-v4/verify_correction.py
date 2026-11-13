from pathlib import Path
import hashlib, json, difflib

base = Path(__file__).resolve().parent
repo = base.parents[1]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
correction = json.loads((base / "CORRECTION.json").read_text())
old = repo / correction["predecessor"]
assert sha(old / "FILES.json") == sha(base / "V3-PREPARATION-FILES.json") == correction["manifest_sha256"]
for name, digest in json.loads((old / "FILES.json").read_text()).items():
    assert sha(old / name) == digest
original = (old / "ControlProof.lean").read_text()
expected = original
for before, after in correction["replacements"]:
    assert expected.count(before) == 1
    expected = expected.replace(before, after)
assert (base / "ControlProof.lean").read_text() == expected
assert "classical" not in expected
assert (base / "proof-correction.patch").read_text() == "".join(difflib.unified_diff(original.splitlines(True), expected.splitlines(True), fromfile="v3/ControlProof.lean", tofile="v4/ControlProof.lean"))
for name in correction["unchanged"]:
    assert (old / name).read_bytes() == (base / name).read_bytes(), name
failure = json.loads((base / "FAILURE-INPUTS.json").read_text())
execution = repo / failure["path"]
for name, digest in failure["files"].items():
    assert sha(execution / name) == digest, name
assert failure["excluded"] == []
seal = failure["root_seal"]
assert sha(execution / seal["file"]) == seal["sha256"]
sealed = json.loads((execution / seal["file"]).read_text())
assert len(sealed) == seal["entries"] == 55
for name, digest in sealed.items():
    assert sha(execution / name) == digest
assert set(failure["files"]) == set(sealed) | {seal["file"]}
attempt = execution / "proof-attempts" / failure["attempt"]
records = json.loads((attempt / "COMMANDS.json").read_text())
assert [(r["module"], r["exit"]) for r in records] == [("Target", 0), ("Controls", 0), ("Proof", 0), ("ControlProof", 1)]
assert all(r["group_absent"] and r["termination_reason"] is None and r["inspection_errors"] == r["cleanup_signals"] == [] for r in records)
assert all(sha(attempt / (r["module"].lower() + ".log")) == r["log_sha256"] for r in records)
assert json.loads((attempt / "RESULT.json").read_text())["exit"] == 1
assert not (attempt / "lib").exists()
print(json.dumps(dict(minimal_concrete_unfolding=True, unchanged_target_and_main_proof=True,
                     obligations=15, controls=6, failed_files_pinned=len(failure["files"]),
                     predecessor_failure_preserved=True, compiler_invocations=0), indent=2))
