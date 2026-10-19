import hashlib, json, os, subprocess, sys, tempfile
from pathlib import Path
root = Path(__file__).resolve().parents[2]
here = Path(__file__).resolve().parent
item = json.loads(Path(sys.argv[1]).read_text())
git = ["git", "-c", "core.fsmonitor=false"]
def get(*args, env=None):
    return subprocess.check_output(git + list(args), cwd=root, env=env).decode().strip()
def run(*args, env=None, **kwargs):
    return subprocess.run(git + list(args), cwd=root, env=env, check=True, **kwargs)
assert get("config", "--get", "commit.gpgsign") == "true"
assert get("rev-parse", "HEAD") == item["stack_head"]
assert not get("diff", "--cached", "--name-only")
assert subprocess.run(git + ["show-ref", "--verify", "--quiet", item["ref"]], cwd=root).returncode == 1
patch = root / item["patch"]
assert hashlib.sha256(patch.read_bytes()).hexdigest() == item["patch_sha256"]
with tempfile.TemporaryDirectory(prefix="css-standalone-index-") as tmp:
    env = dict(os.environ, GIT_INDEX_FILE=str(Path(tmp) / "index"))
    run("read-tree", item["base"], env=env)
    records = []
    names = item["artifacts"]
    assert len(names) == len(set(names)) and all(n.startswith("artifacts/") for n in names)
    assert not get("ls-tree", "-r", item["base"], "--", *names)
    raw = subprocess.check_output(git + ["ls-tree", "-rz", item["stack_head"], "--", *names], cwd=root)
    found = set()
    for record in raw.split(b"\0"):
        if not record:
            continue
        metadata, name = record.split(b"\t", 1)
        mode, kind, oid = metadata.split()
        assert kind == b"blob" and name.decode() in names
        found.add(name.decode())
        records.append(mode + b" " + oid + b"\t" + name + b"\0")
    assert found == set(names)
    run("update-index", "-z", "--index-info", env=env, input=b"".join(records))
    tree = get("write-tree", env=env)
    message = Path(tmp) / "message"
    message.write_text(item["companion_message"] + "\n")
    companion = get("commit-tree", "-S", tree, "-p", item["base"], "-F", str(message))
    run("apply", "--cached", "--check", str(patch), env=env)
    run("apply", "--cached", str(patch), env=env)
    tree = get("write-tree", env=env)
    assert sorted(get("diff-tree", "--no-commit-id", "--name-only", "-r", companion, tree).splitlines()) == sorted(item["native_paths"])
    for n, expected in item["native_pins"].items():
        blob = subprocess.check_output(git + ["show", tree + ":" + n], cwd=root)
        assert hashlib.sha256(blob).hexdigest() == expected, n
    message.write_text(item["native_message"] + "\n")
    native = get("commit-tree", "-S", tree, "-p", companion, "-F", str(message))
    run("apply", "--cached", "--reverse", str(patch), env=env)
    assert get("write-tree", env=env) == get("rev-parse", companion + "^{tree}")
    for oid in [companion, native]:
        assert b"gpgsig " in subprocess.check_output(git + ["cat-file", "commit", oid], cwd=root)
    run("update-ref", item["ref"], native, "0" * 40)
assert get("rev-parse", "HEAD") == item["stack_head"]
assert not get("diff", "--cached", "--name-only")
receipt = dict(base=item["base"], ref=item["ref"], companion_commit=companion, native_commit=native, stack_head=item["stack_head"], signatures_present=True, isolated_base_build_browser="NOT_RUN")
(here / "STANDALONE-COMMIT.json").write_text(json.dumps(receipt, indent=2) + "\n")
print(json.dumps(receipt, indent=2))
