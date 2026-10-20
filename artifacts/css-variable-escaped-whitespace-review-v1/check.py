import hashlib, json, pathlib, subprocess, sys
if not (sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize):
    raise RuntimeError("use python3 -I -S")
r = pathlib.Path(__file__).resolve().parent
files = json.loads((r / "FILES.json").read_text())
actual = {p.relative_to(r).as_posix() for p in r.rglob("*") if p.is_file()}
if actual != set(files) | {"FILES.json", "FREEZE.json"}:
    raise RuntimeError("roster mismatch")
for name, digest in files.items():
    p = r / name
    if p.is_symlink() or hashlib.sha256(p.read_bytes()).hexdigest() != digest:
        raise RuntimeError("input mismatch: " + name)
freeze = json.loads((r / "FREEZE.json").read_text())
if hashlib.sha256((r / "FILES.json").read_bytes()).hexdigest() != freeze["files_sha256"]:
    raise RuntimeError("manifest mismatch")
subprocess.run([sys.executable, "-I", "-S", str(r / "verify.py")], check=True)
