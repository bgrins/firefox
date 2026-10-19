import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
REF = "refs/heads/stylo-css-animation-endpoint-taint-fix"
GIT = ["git", "-c", "core.fsmonitor=false"]


def git(*args, env=None, data=None):
    return subprocess.check_output(GIT + list(args), cwd=ROOT, env=env, input=data)


head = git("rev-parse", "HEAD").decode().strip()
assert not git("diff", "--cached", "--name-only").strip()
assert subprocess.run(GIT + ["show-ref", "--verify", "--quiet", REF], cwd=ROOT).returncode == 1
pack = json.loads((HERE / "PACKAGING.json").read_text())["standalone"]
patch = ROOT / pack["patch"]
assert hashlib.sha256(patch.read_bytes()).hexdigest() == pack["sha256"]
folders = ["css-animation-endpoint-taint-proof-v1", "css-animation-endpoint-taint-proof-replay-v1",
           "css-animation-endpoint-taint-independent-v1", "css-animation-endpoint-paired-root-v1",
           "css-animation-endpoint-final-root-v1", "css-custom-properties-animation-taint-repair-v1",
           "css-animation-csswide-taint-root-v1"]
paths = ["artifacts/" + folder for folder in folders]
paths += ["artifacts/css-attr-taint-touching-ranges-final-root-v1/candidate/RESULT.json"]
entries = git("ls-tree", "-r", head, "--", *paths).decode().splitlines()
assert entries and all(line.split("\t", 1)[1].startswith("artifacts/") for line in entries)
with tempfile.TemporaryDirectory(prefix="animation-standalone-", dir="/private/tmp") as scratch:
    env = {**os.environ, "GIT_INDEX_FILE": str(Path(scratch) / "index")}
    git("read-tree", pack["base"], env=env)
    index_entries = "".join(line.replace(" blob ", " ", 1) + "\n" for line in entries).encode()
    git("update-index", "--index-info", env=env, data=index_entries)
    tree = git("write-tree", env=env).decode().strip()
    companion = git("commit-tree", "-S", tree, "-p", pack["base"], env=env,
                    data=b"No bug - Record standalone animation endpoint repair evidence r?#firefox-style-system-reviewers\n").decode().strip()
    git("apply", "--cached", "--check", str(patch), env=env)
    git("apply", "--cached", str(patch), env=env)
    actual = git("diff", "--cached", "--name-only", companion, env=env).decode().splitlines()
    assert sorted(actual) == pack["paths"]
    for name, digest in pack["pins"].items():
        assert hashlib.sha256(git("show", ":" + name, env=env)).hexdigest() == digest
    native_tree = git("write-tree", env=env).decode().strip()
    native = git("commit-tree", "-S", native_tree, "-p", companion, env=env,
                 data=b"No bug - Preserve attribute taint when replacing animation endpoints r?#firefox-style-system-reviewers\n").decode().strip()
    for commit in [companion, native]:
        assert b"gpgsig " in git("cat-file", "commit", commit)
    assert sorted(git("diff-tree", "--no-commit-id", "--name-only", "-r", native).decode().splitlines()) == pack["paths"]
    git("update-ref", REF, native, "0" * 40)
assert git("rev-parse", "HEAD").decode().strip() == head
assert not git("diff", "--cached", "--name-only").strip()
record = {"base": pack["base"], "ref": REF, "companion_commit": companion, "native_commit": native,
          "stack_head": head, "companion_files": len(entries), "native_paths": pack["paths"],
          "native_pins": pack["pins"], "signatures_present": True,
          "head_and_index_preserved": True, "isolated_upstream_build_browser": "NOT_RUN"}
(HERE / "STANDALONE-COMMIT.json").write_text(json.dumps(record, indent=2) + "\n")
print(json.dumps(record, indent=2))
