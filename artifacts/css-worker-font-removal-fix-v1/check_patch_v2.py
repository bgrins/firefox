import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
GIT = ["git", "-c", "core.fsmonitor=false"]
PATCH = HERE / "fix-candidate-v2.patch"
FILES = ["layout/style/FontFaceSetWorkerImpl.cpp", "testing/web-platform/tests/css/css-font-loading/fontfaceset-remove-canvas.any.js"]
rows = []
for ref in ["HEAD", "32226ddf3a29d58a52291babebdff2a5a7ce46c6"]:
    revision = subprocess.check_output(GIT + ["rev-parse", ref], cwd=ROOT).decode().strip()
    with tempfile.TemporaryDirectory(prefix="css-worker-font-index-") as tmp:
        env = dict(os.environ, GIT_INDEX_FILE=str(Path(tmp) / "index"))
        def run(*args):
            return subprocess.check_output(GIT + list(args), cwd=ROOT, env=env)
        run("read-tree", revision)
        before = run("write-tree")
        run("apply", "--cached", "--check", str(PATCH))
        run("apply", "--cached", str(PATCH))
        assert sorted(run("diff", "--cached", "--name-only", revision).decode().splitlines()) == sorted(FILES)
        for name in FILES:
            assert run("show", ":" + name) == (ROOT / name).read_bytes(), name
        run("apply", "--cached", "--reverse", str(PATCH))
        assert run("write-tree") == before
        rows.append({"revision": revision, "exact_apply_reverse": True})
record = {"patch_sha256": hashlib.sha256(PATCH.read_bytes()).hexdigest(), "files": FILES, "checks": rows,
          "limit": "Source application and reversal, not an isolated clean-base Firefox build."}
(HERE / "STANDALONE-v2.json").write_text(json.dumps(record, indent=2) + "\n")
print(json.dumps(record, indent=2))
