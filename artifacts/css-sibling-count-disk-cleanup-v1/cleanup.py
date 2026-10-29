import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import sys

assert sys.flags.isolated and sys.flags.no_site
assert sys.argv[1:] in (["--check"], ["--run"])
root = Path(__file__).resolve().parents[2]
out = Path(__file__).resolve().parent
base = root / "artifacts/css-line-break-language-proof-v1"
parent = base / "development-build/lf-caller"
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read = lambda p: json.loads(p.read_bytes())
targets = [parent / (name + ".dSYM") for name in ("original", "candidate")]
inventory = read(root / "artifacts/css-owned-build-cleanup-inventory-v1/CANDIDATES.json")
records = {root / row["path"]: row for row in inventory if root / row["path"] in targets}
assert set(records) == set(targets)
receipt = base / "evidence/LF-CALLER-DEVELOPMENT.json"
producer = base / "lf-caller-development.py"
retained = [receipt, producer]
for row in read(receipt)["variants"]:
    assert row["variant"] in ("original", "candidate") and row["cases"] == 480
    source = parent / (row["variant"] + ".cpp")
    assert sha(source) == row["generated_sha256"]
    assert "-g" in row["command"] and str(source) in row["command"]
    assert row["command"][-2:] == ["-o", str(parent / row["variant"])]
    retained.extend([source, parent / row["variant"], parent / (row["variant"] + "-build.log")])
retained_pins = {str(p.relative_to(root)): sha(p) for p in retained}
files, directories = {}, []
for target, record in records.items():
    s = target.lstat()
    assert stat.S_ISDIR(s.st_mode) and [s.st_dev, s.st_ino] == record["identity"]
    expected = {target / row["path"]: row for row in record["files"]}
    actual = set()
    for directory, dirs, names in os.walk(target, followlinks=False):
        directory = Path(directory)
        assert not directory.is_symlink()
        directories.append(directory)
        assert all(not (directory / d).is_symlink() for d in dirs)
        for name in names:
            p = directory / name
            s = p.lstat()
            assert stat.S_ISREG(s.st_mode) and p in expected
            old = expected[p]
            assert [s.st_dev, s.st_ino] == old["identity"] and s.st_size == old["bytes"]
            files[p] = dict(sha256=sha(p), identity=[s.st_dev, s.st_ino], bytes=s.st_size)
            actual.add(p)
    assert actual == set(expected)
assert len(files) == 6
env = dict(os.environ, GIT_OPTIONAL_LOCKS="0")
git = ["git", "--no-optional-locks", "-c", "core.fsmonitor=false"]
relative = [str(p.relative_to(root)) for p in targets]
for args in (["ls-files", "-z"], ["ls-files", "--others", "--exclude-standard", "-z"]):
    assert subprocess.check_output(git + args + ["--"] + relative, cwd=root, env=env) == b""
epoch_path = root / "artifacts/css-registered-number-native-runtime-v1/CURRENT-EPOCH.json"
epoch_pin = sha(epoch_path)
epoch = read(epoch_path)
assert epoch["semantic_index"]["head"] == "19b09cce1a9b03ab19c46addc6fa46242f1544f9"
assert not any(name.startswith(tuple(relative)) for name in epoch["pins"])
assert not (epoch_path.parent / "SOURCE-TRANSITION.lock").exists()
print(json.dumps({"symbols": len(targets), "files": len(files), "allocated_bytes": sum(r["allocated_bytes"] for r in records.values()), "retained": retained_pins}), flush=True)
if sys.argv[1] == "--check":
    raise SystemExit(0)
processes = subprocess.check_output(["ps", "-axo", "pid=,command="], text=True)
assert not any(str(parent) in line or "development-build/lf-caller" in line for line in processes.splitlines())
opened = subprocess.run(["lsof", "+D", str(parent)], capture_output=True, text=True)
assert opened.returncode == 1 and not opened.stdout and not opened.stderr
result = out / "RESULT.json"
assert not result.exists()
before = os.statvfs(root)
with (out / "removed.jsonl").open("x") as journal:
    for p, record in files.items():
        s = p.lstat()
        assert stat.S_ISREG(s.st_mode) and [s.st_dev, s.st_ino] == record["identity"] and sha(p) == record["sha256"]
        p.unlink()
        journal.write(json.dumps({"removed": str(p.relative_to(root)), **record}) + "\n")
        journal.flush()
    for p in sorted(directories, key=lambda p: len(p.parts), reverse=True):
        p.rmdir()
assert all(not p.exists() for p in targets)
assert all(sha(root / p) == pin for p, pin in retained_pins.items())
assert sha(epoch_path) == epoch_pin
after = os.statvfs(root)
result.write_text(json.dumps({"removed_symbols": 2, "removed_files": 6, "retained_verified": retained_pins, "epoch_preserved": epoch_pin, "available_before": before.f_bavail * before.f_frsize, "available_after": after.f_bavail * after.f_frsize}, indent=2) + "\n")
print("Removed only the two obsolete symbol bundles; retained inputs and executables verified.", flush=True)
