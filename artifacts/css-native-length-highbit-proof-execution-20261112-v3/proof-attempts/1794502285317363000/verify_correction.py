from pathlib import Path
import hashlib, json, difflib

base = Path(__file__).resolve().parent
repo = base.parents[1]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
correction = json.loads((base / "CORRECTION.json").read_text())
old = repo / correction["predecessor"]
assert sha(old / "FILES.json") == sha(base / "V2-PREPARATION-FILES.json") == correction["manifest_sha256"]
for name, digest in json.loads((old / "FILES.json").read_text()).items():
    assert sha(old / name) == digest
patch = []
for name in ["Proof.lean", "ControlProof.lean"]:
    original = (old / name).read_text()
    expected = original.replace("if_true", "ite_true").replace("if_false", "ite_false")
    needle = "UInt8.toNat_ofNat_of_lt' (by have := a.isLt; omega)"
    replacement = "UInt8.toNat_ofNat_of_lt' (by change a.val < 256; have := a.isLt; omega)"
    assert expected.count(needle) == 1
    expected = expected.replace(needle, replacement)
    assert (base / name).read_text() == expected
    patch.append("".join(difflib.unified_diff(original.splitlines(True), expected.splitlines(True), fromfile="v2/" + name, tofile="v3/" + name)))
assert (base / "proof-correction.patch").read_text() == "".join(patch)
for name in correction["unchanged"]:
    assert (old / name).read_bytes() == (base / name).read_bytes(), name
failure = json.loads((base / "FAILURE-INPUTS.json").read_text())
execution = repo / failure["path"]
for name, digest in failure["files"].items():
    assert sha(execution / name) == digest, name
attempt = execution / "proof-attempts" / failure["attempt"]
records = json.loads((attempt / "COMMANDS.json").read_text())
assert [(r["module"], r["exit"]) for r in records] == [("Target", 0), ("Controls", 0), ("Proof", 1)]
assert all(r["group_absent"] and r["termination_reason"] is None and r["inspection_errors"] == r["cleanup_signals"] == [] for r in records)
assert all(sha(attempt / (r["module"].lower() + ".log")) == r["log_sha256"] for r in records)
assert json.loads((attempt / "RESULT.json").read_text())["exit"] == 1
assert not (attempt / "lib").exists()
print(json.dumps(dict(minimal_proof_correction=True, unchanged_targets=True,
                     obligations=15, controls=6, failed_files_pinned=len(failure["files"]),
                     predecessor_failure_preserved=True, compiler_invocations=0), indent=2))
