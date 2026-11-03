import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
root = Path.cwd()
here = root / "artifacts/css-research-checkpoint-20261103-v124"
sha = lambda b: hashlib.sha256(b).hexdigest()
spec = importlib.util.spec_from_file_location("checkpoint", here / "commit.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
selected = json.loads((here / "SELECTION.json").read_bytes())
manifest = json.loads((here / "FILES.json").read_bytes())
assert {p.name for p in here.iterdir()} == set(manifest) | {"FILES.json"}
for name, record in manifest.items():
    body = (here / name).read_bytes()
    assert sha(body) == record["sha256"] and len(body) == record["bytes"]
for name in list(manifest) + ["FILES.json"]:
    p = here / name
    selected[str(p.relative_to(root))] = {"sha256": sha(p.read_bytes()), "bytes": p.stat().st_size}
for name, record in selected.items():
    p = root / name
    assert p.is_file() and not p.is_symlink()
    assert sha(p.read_bytes()) == record["sha256"] and p.stat().st_size == record["bytes"]
assert not any(os.environ.get(k) for k in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_OBJECT_DIRECTORY", "GIT_ALTERNATE_OBJECT_DIRECTORIES"))
head = m.git("rev-parse", "HEAD").decode().strip()
assert head == m.HEAD
index = Path(m.git("rev-parse", "--git-path", "index").decode().strip())
raw = index.read_bytes()
controls = {n: (m.RUNTIME / n).read_bytes() for n in ("CURRENT-EPOCH.json", "OWNED.json", "ROLE.json")}
assert not (m.RUNTIME / "SOURCE-TRANSITION.lock").exists()
with tempfile.TemporaryDirectory(prefix="css-v124-stage-preflight-", dir="/private/tmp") as tmp:
    tmp = Path(tmp)
    env = dict(m.ENV, GIT_INDEX_FILE=str(tmp / "index"))
    m.git("read-tree", head, env=env)
    paths = tmp / "paths"
    paths.write_bytes(b"".join(p.encode() + b"\0" for p in sorted(selected)))
    m.git("add", "-f", "--pathspec-from-file=" + str(paths), "--pathspec-file-nul", env=env)
    actual = set(m.git("diff", "--cached", "--name-only", env=env).decode().splitlines())
    assert actual == set(selected), {"missing": sorted(set(selected) - actual), "extra": sorted(actual - set(selected))}
    m.verify_blobs([(":" + p, r) for p, r in selected.items()], env=env)
assert not tmp.exists()
assert index.read_bytes() == raw
assert m.git("rev-parse", "HEAD").decode().strip() == head
assert all((m.RUNTIME / n).read_bytes() == b for n, b in controls.items())
assert not (m.RUNTIME / "SOURCE-TRANSITION.lock").exists()
result = {"head": head, "selected_paths": len(selected), "exact_staged_set": True, "all_staged_blobs_verified": True, "real_index_unchanged": True, "controls_unchanged": True, "scratch_removed": True, "manifest_sha256": sha((here / "FILES.json").read_bytes()), "signing_attempted": False}
with (root / "artifacts/css-research-checkpoint-20261103-v124-root-staging-preflight.json").open("x") as f:
    json.dump(result, f, indent=2)
    f.write("\n")
print(json.dumps(result))
