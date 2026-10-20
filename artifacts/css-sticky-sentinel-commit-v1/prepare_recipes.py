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
    value = {"id": "sticky-sentinel-" + name + "-v1", "expected_head": "PENDING_PRECEDING_SIGNED_COMMIT",
             "message": "No bug - " + subject, "files": names,
             "source_pins": {n: sha(ROOT / n) for n in names}}
    write(name + ".json", value)
    return {"recipe": name, "files": len(names), "bytes": sum(p.stat().st_size for p in paths)}


acceptance = ROOT / "artifacts/css-sticky-sentinel-proof-root-v3/ACCEPTANCE.json"
assert sha(acceptance) == "4843049391a69408e5022227d143bdd961add885935fac48b9b5131eceef0e24"
assert json.loads(acceptance.read_text())["status"] == "ACCEPTED_PENDING_SIGNED_COMMITS"
packaging = json.loads((HERE / "PACKAGING.json").read_text())
assert packaging["head_index_worktree_preserved"]
assert all(b["same_guard_transform"] and b["combined_matches_live_source"] and b["exact_apply_reverse"] for b in packaging["bases"])
summary = [
    recipe("evidence", "Record large-coordinate sticky inset regression evidence", [
        "css-sticky-sentinel-probe-v1", "css-sticky-sentinel-fix-v1", "css-sticky-sentinel-review-v1"],
        ["README.md", "prepare_native.py", "prepare_recipes.py", "PACKAGING.json", "prepare-native.log"] +
        [Path(b["integration_patch"]).name for b in packaging["bases"]]),
    recipe("formal-history", "Preserve preliminary sticky positional-consumer proofs", [
        "css-sticky-sentinel-proof-v1", "css-sticky-sentinel-proof-v2", "css-sticky-sentinel-proof-review-v2"]),
    recipe("formal", "Verify sticky positional guards and indexed updates", [
        "css-sticky-sentinel-proof-v3", "css-sticky-sentinel-proof-independent-v3", "css-sticky-sentinel-proof-root-v3"]),
]
first = packaging["bases"][0]
assert sha(ROOT / first["integration_patch"]) == first["integration_sha256"]
write("native.json", {"id": "sticky-sentinel-native-v1", "expected_head": "PENDING_PRECEDING_SIGNED_COMMIT",
                      "message": "No bug - Apply sticky position constraints only for specified insets r?#layout-reviewers",
                      "files": first["native_paths"], "patch": first["integration_patch"],
                      "patch_sha256": first["integration_sha256"]})
write("QUEUE.json", {"after": "artifacts/css-flex-cross-baseline-overflow-commit-v1/QUEUE.json",
                     "order": [str((HERE / (n + ".json")).relative_to(ROOT)) for n in ["evidence", "formal-history", "formal", "native"]],
                     "signing_required": True,
                     "acceptance": {"path": str(acceptance.relative_to(ROOT)), "sha256": sha(acceptance)},
                     "execution": "Set expected_head to the verified preceding signed commit before invoking commit-item-v2.py.",
                     "final_step": "Record signed IDs and exact native parent delta in the main bugfix ledger."})
write("RECIPE-SUMMARY.json", {"bundles": summary, "native_files": 2, "index_or_worktree_mutations": False})
print(json.dumps(summary, indent=2))
