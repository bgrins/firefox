import hashlib, json, os, subprocess, sys, tempfile
from pathlib import Path
root = Path(__file__).resolve().parents[2]
here = Path(__file__).resolve().parent
item = json.loads(Path(sys.argv[1]).read_text())
git = ["git", "-c", "core.fsmonitor=false"]
def run(args, **kwargs):
    return subprocess.run(git + args, cwd=root, check=True, **kwargs)
def get(*args):
    return subprocess.check_output(git + list(args), cwd=root).decode().strip()
assert get("config", "--get", "commit.gpgsign") == "true"
already_staged = get("diff", "--cached", "--name-only").splitlines()
previous = get("rev-parse", "HEAD")
assert previous == item["expected_head"]
if already_staged:
    assert sorted(already_staged) == sorted(item["files"])
    if "source_pins" in item:
        for name, expected in item["source_pins"].items():
            assert hashlib.sha256(subprocess.check_output(git + ["show", ":" + name], cwd=root)).hexdigest() == expected, name
elif "patch" in item:
    patch = root / item["patch"]
    assert hashlib.sha256(patch.read_bytes()).hexdigest() == item["patch_sha256"]
    run(["apply", "--cached", "--check", str(patch)])
    run(["apply", "--cached", str(patch)])
else:
    for name, expected in item["source_pins"].items():
        assert hashlib.sha256((root / name).read_bytes()).hexdigest() == expected, name
    with tempfile.TemporaryDirectory(prefix="css-commit-paths-") as tmp:
        paths = Path(tmp) / "paths"
        paths.write_bytes(b"".join(name.encode() + b"\0" for name in item["files"]))
        run(["add", "-f", "--pathspec-from-file=" + str(paths), "--pathspec-file-nul"])
actual = get("diff", "--cached", "--name-only").splitlines()
assert sorted(actual) == sorted(item["files"]), actual
if "patch" in item:
    patch = root / item["patch"]
    assert hashlib.sha256(patch.read_bytes()).hexdigest() == item["patch_sha256"]
    with tempfile.TemporaryDirectory(prefix="css-commit-index-") as tmp:
        env = dict(os.environ, GIT_INDEX_FILE=str(Path(tmp) / "index"))
        run(["read-tree", previous], env=env)
        run(["apply", "--cached", str(patch)], env=env)
        expected_tree = subprocess.check_output(git + ["write-tree"], cwd=root, env=env).decode().strip()
        assert get("write-tree") == expected_tree, "Staged tree differs from exact accepted patch"
        run(["apply", "--cached", "--reverse", str(patch)], env=env)
        restored_tree = subprocess.check_output(git + ["write-tree"], cwd=root, env=env).decode().strip()
        assert restored_tree == get("rev-parse", previous + "^{tree}")
for name, expected in item.get("source_pins", {}).items():
    assert hashlib.sha256(subprocess.check_output(git + ["show", ":" + name], cwd=root)).hexdigest() == expected, name
native_paths = [name for name in actual if not name.startswith("artifacts/")]
if native_paths:
    run(["diff", "--cached", "--check", "--", *native_paths])
message = here / (item["id"] + "-message.txt")
message.write_text(item["message"].rstrip() + "\n")
log = here / (item["id"] + "-commit.log")
with log.open("w") as output:
    result = subprocess.run(git + ["commit", "--file", str(message)], cwd=root, stdout=output, stderr=subprocess.STDOUT)
after = get("rev-parse", "HEAD")
record = {"id":item["id"], "before":previous, "after":after, "exit_code":result.returncode, "files":actual, "message":item["message"]}
if result.returncode == 0:
    assert after != previous
    assert subprocess.check_output(git + ["cat-file", "commit", after], cwd=root).find(b"gpgsig ") >= 0
    assert not get("diff", "--cached", "--name-only")
    record["signature_present"] = True
(here / (item["id"] + "-receipt.json")).write_text(json.dumps(record, indent=2) + "\n")
print(json.dumps(record, indent=2))
print(log.read_text())
sys.exit(result.returncode)
