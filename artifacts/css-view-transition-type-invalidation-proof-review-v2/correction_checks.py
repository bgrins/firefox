import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise RuntimeError("use -I -S without optimization")
sys.dont_write_bytecode = True
from pathlib import Path
import hashlib, json, shutil, subprocess, tempfile
root = Path(__file__).resolve().parent
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
def seal(p):
    rows = [{"path": str(f.relative_to(p)), "bytes": f.stat().st_size, "sha256": sha(f)}
            for f in sorted(p.rglob("*")) if f.is_file() and f not in [p / "FILES.json", p / "FREEZE.json"]]
    (p / "FILES.json").write_text(json.dumps(rows, indent=2) + "\n")
    (p / "FREEZE.json").write_text(json.dumps({"files_sha256": sha(p / "FILES.json"), "checker_sha256": sha(p / "check.py")}, indent=2) + "\n")
records = {}
if list((root / "capsule").rglob("__pycache__")):
    raise RuntimeError("guard import contaminated copied source")
cmd = [sys.executable, "-I", "-S", str(root / "capsule/check.py"), "--help"]
r = subprocess.run(cmd, text=True, capture_output=True)
if r.returncode:
    raise RuntimeError(r.stderr)
records["nested_closed_roster_positive"] = dict(command=cmd, exit=r.returncode, stdout=r.stdout, stderr=r.stderr)
with tempfile.TemporaryDirectory(prefix="view-type-review-correction-", dir="/private/tmp") as tmp:
    copy = Path(tmp) / "copy"
    shutil.copytree(root, copy)
    seal(copy)
    cmd = [sys.executable, "-I", "-S", str(copy / "check.py")]
    r = subprocess.run(cmd, text=True, capture_output=True)
    if r.returncode:
        raise RuntimeError("intact corrected review rejected: " + r.stderr)
    records["outer_intact_positive"] = dict(exit=r.returncode, stdout=r.stdout, stderr=r.stderr)
    old_cache = root.parent / "css-view-transition-type-invalidation-proof-review-v1/capsule/__pycache__/calibration.cpython-313.pyc"
    target = copy / "capsule/__pycache__/calibration.cpython-313.pyc"
    target.parent.mkdir()
    shutil.copyfile(old_cache, target)
    seal(copy)
    r = subprocess.run(cmd, text=True, capture_output=True)
    if r.returncode == 0 or "unexpected nested producer directory: __pycache__" not in r.stderr:
        raise RuntimeError("nested closure failed to reject outer-resealed contamination: " + r.stderr)
    records["outer_resealed_exact_old_cache_negative"] = dict(exit=r.returncode, stdout=r.stdout, stderr=r.stderr, cache_sha256=sha(target), cache_bytes=target.stat().st_size)
records["nested_cache_absent_after_checks"] = not list((root / "capsule").rglob("__pycache__"))
records["temporary_copy_removed"] = True
records["unchanged_full_replay_result"] = json.loads((root / "replay/RESULT.json").read_text()) == json.loads((root / "replay-v2/RESULT.json").read_text())
(root / "CORRECTION-GATES.json").write_text(json.dumps(records, indent=2) + "\n")
print(json.dumps({"correction_gates": "PASS", "fresh_full_replay_unchanged": records["unchanged_full_replay_result"]}))
