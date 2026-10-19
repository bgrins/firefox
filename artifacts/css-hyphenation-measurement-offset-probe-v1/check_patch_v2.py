import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile

here = Path(__file__).resolve().parent
repo = here.parents[1]
git = ["git", "-c", "core.fsmonitor=false"]
patch = here / "fix-coordinate-v1.patch"
assert hashlib.sha256(patch.read_bytes()).hexdigest() == "6764c2f18a3301d81eeba6483e67d3d8449a1f85c8968dbef202add7fe1fc96c"
native = "gfx/thebes/gfxTextRun.cpp"
test = "testing/web-platform/tests/css/css-text/hyphens/hyphenation-text-run-offset.html"
old = b"prevMostRecentWordBoundary < oldHyphenBufferLength"
new = b"prevMostRecentWordBoundary < bufferRange.start"
rows = []
for ref in ["HEAD", "32226ddf3a29d58a52291babebdff2a5a7ce46c6"]:
    revision = subprocess.check_output(git + ["rev-parse", ref], cwd=repo).decode().strip()
    with tempfile.TemporaryDirectory(prefix="coordinate-patch-index-") as tmp:
        env = dict(os.environ, GIT_INDEX_FILE=str(Path(tmp) / "index"))
        def run(*args):
            return subprocess.check_output(git + list(args), cwd=repo, env=env)
        run("read-tree", revision)
        original_tree = run("write-tree")
        before = run("show", ":" + native)
        assert before.count(old) == 1
        run("apply", "--cached", "--check", str(patch))
        run("apply", "--cached", str(patch))
        assert sorted(run("diff", "--cached", "--name-only", revision).decode().splitlines()) == [native, test]
        after = run("show", ":" + native)
        assert after == before.replace(old, new)
        assert run("show", ":" + test) == (repo / test).read_bytes()
        if ref == "HEAD":
            assert after == (repo / native).read_bytes()
        run("apply", "--cached", "--reverse", str(patch))
        assert run("write-tree") == original_tree
        rows.append({"revision": revision, "exact_one_comparison_delta": True,
                     "exact_apply_reverse": True, "test_matches_live": True,
                     "candidate_sha256": hashlib.sha256(after).hexdigest()})
record = {"patch_sha256": hashlib.sha256(patch.read_bytes()).hexdigest(),
          "files": [native, test], "checks": rows,
          "limit": "Exact source application/reversal, not a clean-base browser build."}
(here / "STANDALONE-COORDINATE-v2.json").write_text(json.dumps(record, indent=2) + "\n")
print(json.dumps(record, indent=2))
