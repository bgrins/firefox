import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
check = json.loads((HERE / "ROOT-COMMIT-CHECK.json").read_text())
assert check["signed_commits"] == 48 and check["native_fixes"] == 14
current = ROOT / "artifacts/stylo-bloom-tools/CURRENT-COMMITS.json"
data = json.loads(current.read_text())
assert data["committed_native_fixes"] == 87
assert data["accepted_pending_native_fixes"] == len(data["pending_queue"]) == 14
native = [c for c in check["checks"] if c["native"]]
companions = []
groups = {}
for item in check["checks"]:
    if item["native"]:
        groups[item["commit"]] = companions
        companions = []
    else:
        companions.append(item["commit"])
rows = []
for number, (entry, signed) in enumerate(zip(data["pending_queue"], native), 88):
    entry = dict(entry)
    if "native_paths" not in entry:
        assert entry["repair"] == "flex-relative-item-exported-baseline"
        entry["native_paths"] = [
            "layout/generic/nsFlexContainerFrame.cpp",
            "testing/web-platform/tests/css/css-flexbox/flexbox-relative-item-exported-baseline.html",
        ]
    assert sorted(entry["native_paths"]) == sorted(signed["paths"])
    entry["status"] = "COMMITTED_NATIVE_WPT"
    entry["native_commit"] = signed["commit"]
    entry["companion_commit"] = signed["parent"]
    entry["preceding_evidence_commits"] = groups[signed["commit"]]
    entry["pending"] = []
    entry["commit_verification"] = str((HERE / "ROOT-COMMIT-CHECK.json").relative_to(ROOT))
    data["new_queue"].append(entry)
    rows.append(f"| {number} | {entry['repair']} | `{signed['commit']}` | `{signed['parent']}` |")
data["pending_queue"] = []
data["committed_native_fixes"] = 101
data["accepted_pending_native_fixes"] = 0
data["latest_signing"] = {k: v for k, v in check.items() if k != "checks"}
data["latest_signing"]["verification"] = str((HERE / "ROOT-COMMIT-CHECK.json").relative_to(ROOT))
data["pending_native_worktree"]["note"] = "The 14 accepted repairs are now signed commits. Remaining local changes include unaccepted research prototypes and later evidence; the earlier path-count fields describe historical checkpoints. Signing remains enabled."
current.write_text(json.dumps(data, indent=2) + "\n")
table = "| Fix | Repair | Native + WPT commit | Preceding companion |\n| --- | --- | --- | --- |\n" + "\n".join(rows)
ledger = ROOT / "artifacts/stylo-bloom-tools/BUGFIX-COMMITS.md"
text = ledger.read_text()
start = text.index("Current checkpoint:")
end = text.index("## Current flex verification checkpoint", start)
text = text[:start] + "Current checkpoint: **101 committed fixes; no accepted repairs await signing.**\n\n" + "## Latest signed fixes: 88–101\n\n" + table + "\n\nAll 48 queue commits contain signatures. Each of the 14 native commits matches its\naccepted patch against its actual parent and includes its WPT; research and proofs\nare in preceding commits. No new build or test results are claimed by signing.\n[Commit verification](../css-signing-resume-20261020-v1/ROOT-COMMIT-CHECK.json).\n\nThe sections below retain earlier research checkpoints. Their pending-signing\nstatements are historical; use the current count and table above.\n\n" + text[end:]
ledger.write_text(text)
plan = ROOT / "artifacts/stylo-bloom-tools/PLAN-OF-RECORD.md"
text = plan.read_text()
start = text.index("- **Fourteen accepted repairs await signing:")
end = text.index("- **Latest fixes:", start)
text = text[:start] + "- **101 committed native/WPT fixes; no accepted repairs await signing.** The\n  14-fix queue is complete, including its 34 preceding evidence/proof commits.\n  All 48 signatures and exact native parent deltas were checked. See\n  [BUGFIX-COMMITS.md](BUGFIX-COMMITS.md) and\n  [CURRENT-COMMITS.json](CURRENT-COMMITS.json) for management identifiers.\n" + text[end:]
text = text.replace("- Earlier signing succeeded for the committed fixes; the current queue is blocked by the configured 1Password signer. Signing stays enabled. Nothing has been pushed or submitted externally.", "- Signing succeeded for the complete accepted queue. Signing stays enabled. Nothing has been pushed or submitted externally. Later signing-blocker statements describe earlier checkpoints.")
plan.write_text(text)
retry = ROOT / "artifacts/css-view-transition-type-invalidation-commit-v1/RETRY-STATE.json"
old = json.loads(retry.read_text())
retry.write_text(json.dumps({"retry_status": "succeeded", "retry_log": "retry-returned-user-v15.log", "retry_exit": 0, "session_id": 78579, "signing_enabled": True, "preserved_initial_head": old["expected_head"], "preserved_initial_staged_diff_sha256": old["staged_diff_sha256"], "initial_staged_file_count": 297, "initial_evidence_commit": check["checks"][0]["commit"], "queue_head": check["head"], "queue_signed_commits": 48, "queue_native_fixes": 14, "index_empty_after_queue": True}, indent=2) + "\n")
(HERE / "README.md").write_text("# Signed queue completion\n\n101 native/WPT fixes are now committed locally. This batch adds 14 fixes and\n34 preceding evidence/proof commits. No accepted fixes remain pending signing.\nNo pushes, submissions, or new runtime verification were performed by this step.\n\n" + table + "\n\n[Verification](ROOT-COMMIT-CHECK.json) checks signatures are present, exact file\nrosters, parent relationships, and native patches applied and reversed against\nthe actual parents in disposable indexes. It does not re-run browser tests.\n\nThe six preexisting unaccepted repair candidates remain excluded. Two newer\ninvestigations are also excluded: reached signed table arithmetic overflow and\na reduced CSSOM rectangle precision discrepancy. Neither has an accepted repair\nor demonstrated security impact.\n")
print("Updated ledger to 101 committed fixes, zero pending signing.")
