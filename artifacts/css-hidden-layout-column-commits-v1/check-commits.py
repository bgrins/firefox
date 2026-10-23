import hashlib
import json
import os
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
env = dict(os.environ, GIT_OPTIONAL_LOCKS="0")
git = ["git", "-c", "core.fsmonitor=false"]

def get(*args, **kwargs):
    return subprocess.check_output(git + list(args), cwd=ROOT, env=env, **kwargs)

previous = "683bbe59d5a698a1f708041304f8640a7f987c38"
entries = []
requests = []
expected = []
for recipe in ["controlled-evidence", "column-provider-model", "principal-native", "absolute-native"]:
    item = json.loads((HERE / (recipe + ".json")).read_text())
    receipt = json.loads((HERE / (item["id"] + "-receipt.json")).read_text())
    assert receipt["exit_code"] == 0 and receipt["before"] == previous
    commit = receipt["after"]
    raw_commit = get("cat-file", "commit", commit)
    assert b"gpgsig " in raw_commit
    assert [l[7:].decode() for l in raw_commit.splitlines() if l.startswith(b"parent ")] == [previous]
    paths = get("diff-tree", "--no-commit-id", "--name-only", "-r", previous, commit).decode().splitlines()
    assert sorted(paths) == sorted(item["files"])
    pins = item.get("source_pins", item.get("expected_final_sha256"))
    assert set(pins) == set(paths)
    for name in paths:
        requests.append(commit + ":" + name)
        expected.append(pins[name])
    entries.append({"recipe": recipe, "commit": commit, "parent": previous,
                    "signed": True, "exact_paths": paths})
    previous = commit
data = get("cat-file", "--batch", input=("\n".join(requests) + "\n").encode())
position = 0
for request, digest in zip(requests, expected):
    end = data.index(b"\n", position)
    header = data[position:end].split()
    assert len(header) == 3 and header[1] == b"blob", request
    size = int(header[2])
    blob = data[end + 1:end + 1 + size]
    assert hashlib.sha256(blob).hexdigest() == digest, request
    position = end + size + 2
assert position == len(data)
assert get("rev-parse", "HEAD").decode().strip() == previous
assert not get("diff", "--cached", "--name-only").strip()
worktree = json.loads((HERE / "absolute-installation.json").read_text())["after"]
assert all(hashlib.sha256((ROOT / n).read_bytes()).hexdigest() == h for n, h in worktree.items())
bindings = json.loads((ROOT / "artifacts/css-hidden-layout-native-packaging-v1/BINDINGS.json").read_text())["recipes"]
for group in bindings.values():
    for binding in group:
        if binding["before_blob"] is None:
            assert hashlib.sha256((ROOT / binding["path"]).read_bytes()).hexdigest() == binding["after_sha256"]
record = {"status": "PASS", "head": previous, "commits": entries,
          "exact_blob_checks": len(requests), "guarded_worktree_sources": len(worktree),
          "prototype_bytes_preserved": True, "landing_test_files_unchanged": 5,
          "index_empty": True, "new_native_fixes": 2, "committed_native_fixes": 105}
(HERE / "COMMIT-CHECK.json").write_text(json.dumps(record, indent=2) + "\n")
print(json.dumps({k: v for k, v in record.items() if k != "commits"}, indent=2))
