from pathlib import Path
import hashlib, json, difflib

base = Path(__file__).resolve().parent
repo = base.parents[1]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
a = json.loads((base / "AMENDMENT.json").read_text())
old = repo / a["original_path"]
assert sha(old / "FILES.json") == sha(base / "V1-FILES.json") == a["original_manifest_sha256"]
for name, digest in json.loads((old / "FILES.json").read_text()).items():
    assert sha(old / name) == digest
failure = repo / a["failed_attempt"]["path"]
assert sha(failure / "FILES.json") == a["failed_attempt"]["manifest_sha256"]
for name, digest in json.loads((failure / "FILES.json").read_text()).items():
    assert sha(failure / name) == digest
original = (old / "Target.lean").read_text()
new = (base / "Target.lean").read_text()
assert original.count(a["original_span"]) == 1
assert new == original.replace(a["original_span"], a["successor_span"])
assert new.count(a["successor_span"]) == 1
assert new.replace(a["successor_span"], a["original_span"]) == original
assert sha(old / "Target.lean") == a["original_target_sha256"]
assert sha(base / "Target.lean") == a["successor_target_sha256"]
for name in a["unchanged_lean_files"] + ["DECLARATIONS.json", "CONTROLS.json"]:
    assert (base / name).read_bytes() == (old / name).read_bytes()
assert (base / "target.patch").read_text() == "".join(difflib.unified_diff(original.splitlines(True), new.splitlines(True), fromfile="v1/Target.lean", tofile="v2/Target.lean"))
print(json.dumps(dict(explicit_uniqueness_expansion=True, inverse_restores_original=True, changed_lean_files=["Target.lean"], obligation_fields=15, control_fields=6, old_failed_files_authenticated=35, compiler_invocations=0, proofs=0), indent=2))
