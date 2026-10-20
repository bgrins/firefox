import hashlib
import json
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(name, value):
    (HERE / name).write_text(json.dumps(value, indent=2) + "\n")


def recipe(name, subject, bundles, extra=()):
    paths = [p for bundle in bundles for p in (ROOT / "artifacts" / bundle).rglob("*") if p.is_file()]
    paths += [HERE / n for n in extra]
    names = sorted(str(p.relative_to(ROOT)) for p in paths)
    assert len(names) == len(set(names))
    for p in paths:
        assert not p.is_symlink() and not p.stat().st_mode & 0o111, p
        assert p.suffix not in {".olean", ".ilean", ".o", ".a", ".pyc"}, p
    prefixes = ["artifacts/" + b for b in bundles] + [str((HERE / n).relative_to(ROOT)) for n in extra]
    assert not subprocess.check_output(["git", "-c", "core.fsmonitor=false", "ls-tree", "-r", "--name-only", "HEAD", "--", *prefixes], cwd=ROOT)
    value = {"id": "flex-line-cross-sum-" + name + "-v1", "expected_head": "PENDING_PRECEDING_SIGNED_COMMIT",
             "message": "No bug - " + subject, "files": names,
             "source_pins": {n: sha(ROOT / n) for n in names}}
    write(name + ".json", value)
    return {"recipe": name, "files": len(names), "bytes": sum(p.stat().st_size for p in paths)}


acceptance = ROOT / "artifacts/css-flex-line-cross-sum-root-v1/ACCEPTANCE.json"
assert sha(acceptance) == "80cbf46ccafac872110c80abba2536201866c67accfbaab8a8304829391713e8"
a = json.loads(acceptance.read_text())
assert a["status"] == "ACCEPTED_PENDING_SIGNED_COMMITS"
packaging = json.loads((HERE / "PACKAGING.json").read_text())
assert packaging["head_index_worktree_preserved"]
assert all(b["exact_apply_reverse"] and b["baseline_patch_commutes"] for b in packaging["bases"])
summary = [
    recipe("evidence", "Record wrapped flex line sum regression evidence", [
        "css-flex-line-cross-sum-probe-v1", "css-flex-line-cross-sum-fix-v1"],
        ["README.md", "prepare_native.py", "prepare_recipes.py", "PACKAGING.json", "prepare-native.log"]),
    recipe("review", "Verify flex line sums and optional size observers", [
        "css-flex-line-cross-sum-review-v1", "css-flex-line-cross-sum-root-v1"]),
]
assert sha(ROOT / a["patch"]["path"]) == a["patch"]["sha256"]
write("native.json", {"id": "flex-line-cross-sum-native-v1", "expected_head": "PENDING_PRECEDING_SIGNED_COMMIT",
                      "message": "No bug - Use wide saturated sums for flex line cross sizes r?#layout-reviewers",
                      "files": packaging["bases"][0]["native_paths"], "patch": a["patch"]["path"],
                      "patch_sha256": a["patch"]["sha256"]})
write("QUEUE.json", {"after": "artifacts/css-sticky-sentinel-commit-v1/QUEUE.json",
                     "order": [str((HERE / (n + ".json")).relative_to(ROOT)) for n in ["evidence", "review", "native"]],
                     "signing_required": True,
                     "acceptance": {"path": str(acceptance.relative_to(ROOT)), "sha256": sha(acceptance)},
                     "execution": "Set expected_head to the verified preceding signed commit before invoking commit-item-v2.py.",
                     "final_step": "Record signed IDs and exact native parent delta in the main bugfix ledger."})
write("RECIPE-SUMMARY.json", {"bundles": summary, "native_files": 2, "index_or_worktree_mutations": False})
print(json.dumps(summary, indent=2))
