import hashlib, json, shutil, subprocess, tempfile
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
s = json.loads((HERE / "SOURCE.json").read_text())
for path, pin in json.loads((HERE / "REFERENCES.json").read_text()).items():
    assert sha(ROOT / path) == pin["sha256"]
for target, role in s["roles"].items():
    for pin in role.values():
        assert sha(ROOT / pin["path"]) == pin["sha256"]
assert sha(ROOT / s["test"]["source"]) == s["test"]["sha256"]
scratch = Path(tempfile.mkdtemp(prefix="attr-fallback-patch-"))
result = {"native_compilation": False, "browser_execution": False, "scratch": str(scratch)}
try:
    for target, role in s["roles"].items():
        dest = scratch / target
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / role["base"]["path"], dest)
    patch = HERE / "native.patch"
    for reverse in [False, True]:
        cmd = ["patch", "-p1", "--fuzz=0", "--batch", "-i", str(patch)]
        if reverse:
            cmd.append("-R")
        proc = subprocess.run(cmd, cwd=scratch, capture_output=True, text=True)
        print(proc.stdout, proc.stderr)
        assert proc.returncode == 0
        assert "offset" not in proc.stdout and "fuzz" not in proc.stdout
        for target, role in s["roles"].items():
            assert sha(scratch / target) == role["base" if reverse else "candidate"]["sha256"]
        if reverse:
            assert not (scratch / s["test"]["target"]).exists()
        else:
            assert sha(scratch / s["test"]["target"]) == s["test"]["sha256"]
    prep = json.loads((HERE / "PREPARE-RESULT.json").read_text())
    assert prep["success"] and prep["scratch_removed"] and prep["callbacks"] == 28
    result.update(success=True, exact_roundtrips=2, source_roles=1, test_files=1)
finally:
    shutil.rmtree(scratch)
    result["scratch_removed"] = not scratch.exists()
    (HERE / "CHECK-RESULT.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result))
