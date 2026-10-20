import hashlib
import json
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
GIT = ["git", "-c", "core.fsmonitor=false"]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, value):
    path.write_text(json.dumps(value, indent=2) + "\n")


def recipe(directory, name, subject, bundles, extra=()):
    paths = [p for bundle in bundles for p in (ROOT / "artifacts" / bundle).rglob("*") if p.is_file()]
    paths.extend(directory / p for p in extra)
    names = sorted(str(p.relative_to(ROOT)) for p in paths)
    assert len(names) == len(set(names))
    for p in paths:
        assert p.is_file() and not p.is_symlink() and not p.stat().st_mode & 0o111
        assert p.suffix not in {".olean", ".ilean", ".o", ".a", ".pyc"}
    prefixes = ["artifacts/" + bundle for bundle in bundles]
    prefixes += [str((directory / p).relative_to(ROOT)) for p in extra]
    tracked = subprocess.check_output(GIT + ["ls-tree", "-r", "--name-only", "HEAD", "--", *prefixes], cwd=ROOT)
    assert not tracked, tracked.decode()
    value = {"id": directory.name.removesuffix("-commit-v1") + "-" + name + "-v1",
             "expected_head": "PENDING_PRECEDING_SIGNED_COMMIT",
             "message": "No bug - " + subject, "files": names,
             "source_pins": {n: sha(ROOT / n) for n in names}}
    write(directory / (name + ".json"), value)
    return {"recipe": name + ".json", "files": len(names),
            "bytes": sum(p.stat().st_size for p in paths)}


def native(directory, subject, patch, paths):
    assert sha(ROOT / patch["path"]) == patch["sha256"]
    write(directory / "native.json", {
        "id": directory.name.removesuffix("-commit-v1") + "-native-v1",
        "expected_head": "PENDING_PRECEDING_SIGNED_COMMIT",
        "message": "No bug - " + subject + " r?#layout-reviewers",
        "patch": patch["path"], "patch_sha256": patch["sha256"], "files": paths,
    })


def queue(directory, after, order, acceptance, summary):
    assert json.loads(acceptance.read_text())["status"] == "ACCEPTED_PENDING_SIGNED_COMMITS"
    write(directory / "QUEUE.json", {
        "after": after, "order": [str((directory / (n + ".json")).relative_to(ROOT)) for n in order],
        "signing_required": True, "acceptance": {"path": str(acceptance.relative_to(ROOT)), "sha256": sha(acceptance)},
        "execution": "Set expected_head to the verified preceding signed commit before invoking commit-item-v2.py.",
        "final_step": "Record signed IDs and exact native parent deltas in the main bugfix ledger.",
    })
    write(directory / "RECIPE-SUMMARY.json", {"bundles": summary, "native_files": len(json.loads((directory / "native.json").read_text())["files"]),
                                             "index_or_worktree_mutations": False})


negative_acceptance = ROOT / "artifacts/css-sticky-negative-inset-overflow-proof-root-v2/ACCEPTANCE.json"
assert sha(negative_acceptance) == "27e57b6bfc4f874c4a864a612a64c882279993bb9fb3592a922bb49fff24b4e5"
packaging = json.loads((HERE / "PACKAGING.json").read_text())
assert packaging["head_index_worktree_preserved"] and all(p["all_round_trips_exact"] for p in packaging["bases"])
extra = ["README.md", "prepare_native.py", "prepare_recipes.py", "PACKAGING.json", "prepare-native.log", "SOURCE-TRANSFER.json", "pending-sentinel-only.diff"]
extra += [p.name for p in HERE.glob("combined-*.cpp")]
extra += [p.name for p in HERE.glob("negative-after-insets-*.patch")]
negative_summary = [
    recipe(HERE, "evidence", "Record negative sticky inset regression evidence", [
        "css-sticky-negative-inset-overflow-probe-v1", "css-sticky-negative-inset-overflow-fix-v1",
        "css-sticky-negative-inset-overflow-review-v1", "css-sticky-negative-inset-overflow-root-v1"], extra),
    recipe(HERE, "formal-history", "Preserve preliminary negative sticky inset proofs", ["css-sticky-negative-inset-overflow-proof-v1"]),
    recipe(HERE, "formal", "Verify negative sticky inset normalization and consumers", [
        "css-sticky-negative-inset-overflow-proof-v2", "css-sticky-negative-inset-overflow-proof-review-v2",
        "css-sticky-negative-inset-overflow-proof-root-v2"]),
]
p = packaging["bases"][0]
native(HERE, "Use wide arithmetic and direct sticky range edges",
       {"path": p["integration_patch"], "sha256": p["integration_sha256"]}, p["native_paths"])
queue(HERE, "artifacts/css-sticky-insets-commit-v1/QUEUE.json",
      ["evidence", "formal-history", "formal", "native"], negative_acceptance, negative_summary)

flex = ROOT / "artifacts/css-flex-cross-baseline-overflow-commit-v1"
flex_acceptance = ROOT / "artifacts/css-flex-cross-baseline-overflow-fix-v2/ACCEPTANCE.json"
assert sha(flex_acceptance) == "e9f0fb7773da7eb305ab96cd05baab7253243d4994410c99dab2a44b21cb2ac5"
packaging = json.loads((flex / "PACKAGING.json").read_text())
assert packaging["head_index_worktree_preserved"] and all(p["all_round_trips_exact"] for p in packaging["bases"])
flex_summary = [
    recipe(flex, "evidence", "Record flex baseline sum regression evidence", [
        "css-flex-cross-baseline-boundary-root-v1", "css-flex-cross-baseline-overflow-fix-v1"],
        ["README.md", "prepare_native.py", "PACKAGING.json", "prepare-native.log"]),
    recipe(flex, "review", "Verify flex baseline sums and numeric range prerequisites", ["css-flex-cross-baseline-overflow-review-v1"]),
    recipe(flex, "corrected-evidence", "Validate portable flex baseline sum regression coverage", ["css-flex-cross-baseline-overflow-fix-v2"]),
]
native(flex, "Use wide sums for flex baseline cross sizes", json.loads(flex_acceptance.read_text())["patch"], packaging["bases"][0]["native_paths"])
queue(flex, "artifacts/css-sticky-negative-inset-overflow-commit-v1/QUEUE.json",
      ["evidence", "review", "corrected-evidence", "native"], flex_acceptance, flex_summary)
print(json.dumps({"negative": negative_summary, "flex": flex_summary}, indent=2))
