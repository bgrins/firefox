from pathlib import Path
import subprocess, os, hashlib, json
root = Path(__file__).resolve().parents[2]
p = Path(__file__).resolve().parent
patch = p / "fix-utf16-complex-v1.patch"
files = ["third_party/rust/icu_segmenter/src/line.rs", "third_party/rust/icu_segmenter/.cargo-checksum.json", "testing/web-platform/tests/css/css-text/line-breaking/complex-prefix-lf-partition.html"]
git = ["git", "-c", "core.fsmonitor=false"]
rows = []
for label, ref in [("head", "11482ee213bf63c749b6d205c2c7591d783bdaa8"), ("base", "32226ddf3a29d58a52291babebdff2a5a7ce46c6")]:
    env = {**os.environ, "GIT_INDEX_FILE": str(p / (label + "-patch-check.index"))}
    for args in [["read-tree", ref], ["apply", "--cached", "--check", str(patch)], ["apply", "--cached", str(patch)]]:
        subprocess.run(git + args, env=env, cwd=root, check=True)
    for f in files:
        assert subprocess.check_output(git + ["show", ":" + f], env=env, cwd=root) == (root / f).read_bytes(), f
    for args in [["apply", "--cached", "--reverse", "--check", str(patch)], ["apply", "--cached", "--reverse", str(patch)]]:
        subprocess.run(git + args, env=env, cwd=root, check=True)
    assert not subprocess.check_output(git + ["diff", "--cached", ref, "--"], env=env, cwd=root)
    rows.append({"revision": ref, "apply_reverse_exact": True})
result = {"patch_sha256": hashlib.sha256(patch.read_bytes()).hexdigest(), "files": files, "source_apply_checks": rows, "limit": "Exact source application/reversal, not isolated clean-base Firefox build", "signing": "No commit attempted; existing staged companion unchanged"}
(p / "STANDALONE-v1.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, indent=2))
