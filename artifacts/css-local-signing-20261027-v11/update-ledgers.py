import copy, hashlib, importlib.util, json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
read = lambda p: json.loads(p.read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
def ref(p): return {"path": str(p.relative_to(ROOT)), "sha256": sha(p)}
spec = importlib.util.spec_from_file_location("fallback_state", ROOT / "artifacts/css-attr-non-type-fallback-native-runtime-v2/state.py")
s = importlib.util.module_from_spec(spec)
spec.loader.exec_module(s)
epoch = read(HERE / "CURRENT-EPOCH.json")
s.a.verify_current(s.h, ROOT, s.ENV, epoch)
native = read(HERE / "native-fix-receipt.json")
research = read(HERE / "fallback-validation-receipt.json")
tools = read(HERE / "fallback-tools-receipt.json")
assert all(x["signature_verified"] for x in [native, research, tools])
assert native["parent"] == research["commit"] and research["parent"] == tools["commit"]
acceptance_path = ROOT / "artifacts/css-attr-non-type-fallback-validation-v1/ACCEPTANCE.json"
a = read(acceptance_path)
assert a["status"] == "READY_FOR_STANDALONE_SIGNED_COMMIT" and a["fix"] == 137
entry = read(ROOT / "artifacts/css-attr-non-type-fallback-ledger-plan-v1/ENTRY-TEMPLATE.json")
entry.update(status="COMMITTED_NATIVE_WPT", native_commit=native["commit"], research_commit=research["commit"], companion_commit=research["commit"], terminal_review=a["terminal_review"], acceptance=ref(acceptance_path), commit_verification=ref(HERE / "native-fix-receipt.json"), research_commit_verification=ref(HERE / "fallback-validation-receipt.json"), candidate_source_installed=True, browser_binary_contains_fix=True, signature_verified=True)
assert sorted(native["paths"]) == sorted(entry["native_paths"])
paths = ["artifacts/stylo-bloom-tools/CURRENT-COMMITS.json", "artifacts/css-fix-readout-20261023/GROUPS.json", "artifacts/stylo-bloom-tools/BUGFIX-COMMITS.md", "artifacts/css-fix-readout-20261023/README.md", "artifacts/stylo-bloom-tools/PLAN-OF-RECORD.md"]
old = {n: (ROOT / n).read_bytes() for n in paths}
ledger = json.loads(old[paths[0]])
previous_queue = copy.deepcopy(ledger["new_queue"])
assert ledger["committed_native_fixes"] == 135 and all(x.get("fix") != 137 for x in previous_queue)
assert ledger["accepted_pending_native_fixes_on_hold"] == 1 and ledger["accepted_pending_native_fixes_excluding_holds"] == 0
ledger["new_queue"].append(entry)
ledger["committed_native_fixes"] = 136
ledger.setdefault("local_signing_history", []).append(ledger["latest_signing"])
ledger["latest_signing"] = {"status": "SIGNED_VERIFIED_LOCAL", "fix": 137, "native_commit": native["commit"], "research_commit": research["commit"], "verification": ref(HERE / "native-fix-receipt.json")}
ledger.setdefault("research_signing_history", []).append(ledger["latest_research_signing"])
ledger["previous_research_signing"] = copy.deepcopy(ledger["latest_research_signing"])
ledger["latest_research_signing"] = {"status": "SIGNED_VERIFIED_LOCAL", "commits": {"fallback-tools": tools["commit"], "fallback-validation": research["commit"]}, "directory": str(HERE.relative_to(ROOT))}
ledger["latest_research_signing"]["commits"]["raw-proposal"] = read(HERE / "raw-proposal-receipt.json")["commit"]
ledger.setdefault("verified_working_epoch_history", []).append(ledger["latest_verified_working_epoch"])
ledger["latest_verified_working_epoch"] = {"path": str((HERE / "CURRENT-EPOCH.json").relative_to(ROOT)), "status": "Signed used-fallback fix; full native build and controlled original/candidate WPT comparison passed", "browser_binary_contains_fixes": [133,134,135,136,137]}
ledger["latest_attribute_fallback_fix"] = {"fix": 137, "acceptance": ref(acceptance_path), "commit_verification": ref(HERE / "native-fix-receipt.json")}
ledger.setdefault("cycle_repair_queue_history", []).append(copy.deepcopy(ledger["cycle_repair_queue"]))
ledger["cycle_repair_queue"]["used_attr_fallback"] = copy.deepcopy(entry)
ledger["cycle_repair_queue"]["status"] = "USED_FALLBACK_COMMITTED_OTHER_LEADS_UNACCEPTED"
ledger["cycle_repair_queue"]["next"] = "Validate raw-nested repair with explicit two-oracle review, then continue registered-number and pending-provider integration work."
ledger["signing_next_action"] = "Keep fix137 standalone; validate the raw-nested repair next and preserve independent research/native commits."
assert ledger["new_queue"][:-1] == previous_queue
groups = json.loads(old[paths[1]])
previous_groups = copy.deepcopy(groups)
assert groups["committed"] == groups["accepted"] == 135 and groups["tracked"] == 136
for group in groups["groups"]:
    if group["group"] == "Attributes and custom properties":
        assert group["committed"] == group["total"] == 16
        group["fixes"].append(copy.deepcopy(entry))
        group["committed"] = group["total"] = 17
assert sum(g["committed"] for g in groups["groups"]) == 136
groups.update(head=native["commit"], committed=136, accepted=136, tracked=137)
assert groups["held"] == previous_groups["held"]
assert groups["formal_library_checkpoint"] == previous_groups["formal_library_checkpoint"]
assert groups["formal_library_checkpoint_history"] == previous_groups["formal_library_checkpoint_history"]
for before, after in zip(previous_groups["groups"], groups["groups"]):
    assert before["fixes"] == (after["fixes"][:-1] if after["group"] == entry["group"] else after["fixes"])
new = {paths[0]: (json.dumps(ledger, indent=2, ensure_ascii=False)+"\n").encode(), paths[1]: (json.dumps(groups, indent=2, ensure_ascii=False)+"\n").encode()}
summary = f"Fix 137, used non-type attribute fallback cycles, is committed as `{native['commit']}` after research `{research['commit']}`. The original/candidate comparison changes 15 PASS + 19 FAIL to 34 PASS; all 154 existing assertions and six reftests remain passing. Native build and WPT lint pass. Tentative P3 CSS correctness. Source audit and browser reproduction found the defect; the separate Lean guard model supports normalized cycle semantics, not native refinement. The upstream export documents overlap with numeric fix 499c0c6 and has transport/syntax validation only. Existing raw-nested expectations remain unchanged. No new canonical Lean coverage is claimed."
stale = "The signed animation research now includes owned provider completion, demand-aware endpoint substitution and typed-attribute/context demands with 22 proposed real-resolver calls. Native integration remains unfinished and the new proposal code is not compiled or enabled. The versioned fallback-cycle trace confirms ordinary Stylo already skips unused fallback edges. The canonical Lean coverage counts are unchanged."
current = "The typed-demand prototype passes its full native build, 20 native tests including 22 real-resolver calls, and four ordinary WPTs (253 PASS and three existing expected FAIL). Production pending-provider integration remains unfinished and disabled; the single-collector and disposable-context proposals remain uncompiled. Canonical Lean coverage counts are unchanged."
for name in paths[2:]:
    text = old[name].decode()
    title, body = text.split("\n", 1)
    text = title + "\n\n" + summary + "\n" + body
    for before, after in [("**135 accepted fixes: 135 committed locally, 0 accepted pending, and 1 additional held repair excluded.**", "**136 accepted fixes: 136 committed locally, 0 accepted pending, and 1 additional held repair excluded.**"), ("| Attributes and custom properties | 16 | 0 |", "| Attributes and custom properties | 17 | 0 |"), ("| **Total** | **135** | **0** |", "| **Total** | **136** | **0** |")]:
        assert before in text, (name, before)
        text = text.replace(before, after, 1)
    text = text.replace(stale, current, 1)
    if name.endswith("PLAN-OF-RECORD.md"):
        before = "Both attribute-cycle leads reproduce in release Firefox 158 and local Nightly 160: five raw-nested disagreements with eight controls, and seven used bare/unit fallback disagreements with six controls. A registered-number comparison shows seven shared discrepancies and one additional local prototype control failure. These are repair targets, not accepted fixes."
        assert before in text
        text = text.replace(before, "The used bare/unit attribute fallback defect is now fixed and committed as fix 137. The raw-nested lead still has five reproduced discrepancies and eight controls; its reviewed proposal explicitly corrects two old WPT expectations and adds 29 tests, but is not browser-validated. Registered-number comparison still shows seven shared discrepancies and one additional local prototype control failure. Those remaining leads are unaccepted.", 1)
        text = text.replace("1. Validate and commit a minimal used bare/unit attribute fallback cycle repair with its WPT and preceding evidence. Preserve quote fix 135 and counter fix 136 separately.", "1. Preserve signed fix 137 and its original/candidate evidence, alongside independently reviewable quote fix 135 and counter fix 136.", 1)
        text = text.replace("2. Repair raw nested attribute false cycles after explicit review of the existing WPT oracle.", "2. Build and validate the reviewed raw-nested repair and 29-case WPT, including explicit correction of two historical attr-cycle expectations.", 1)
        text = text.replace("## Execution order", "The separate attribute guard model also passes 13 general laws, 23 kernel examples and nine rejected false claims. It distinguishes selected fallback cycles from opaque raw strings; parsing, namespaces, invalidation and native correspondence remain outside that model.\n\n## Execution order", 1)
    else:
        marker = "| 136: Contained counter append |"
        assert marker in text
        text = text.replace(marker, f"| 137: Used non-type attr fallback cycles | `{native['commit']}` | `{research['commit']}` |\n" + marker, 1)
    new[name] = text.encode()
backup = HERE / "ledger-preimages"
backup.mkdir()
for name in paths:
    (backup / Path(name).name).write_bytes(old[name])
    (ROOT / name).write_bytes(new[name])
updated = copy.deepcopy(epoch)
for name in paths:
    for key in ["pins", "staged_working", "committed_research_working_payloads"]:
        if name in updated[key]: updated[key][name] = sha(ROOT / name)
state = s.h.index_state(ROOT, s.ENV)
updated["semantic_index"] = s.h.semantic_index(state)
updated["raw_index_observation"]["current"] = state["raw_index"]
s.a.verify_current(s.h, ROOT, s.ENV, updated)
(HERE / "CURRENT-EPOCH.json").write_text(json.dumps(updated, indent=2, sort_keys=True)+"\n")
s.save(HERE / "LEDGER-UPDATE.json", {"native_commit": native["commit"], "research_commit": research["commit"], "accepted_committed":136, "tracked":137, "held":1, "attributes_group":17, "prior_entries_preserved":True, "canonical_checkpoint_preserved":True, "files":paths, "full_preservation_verified":True})
print("Updated five ledgers: 136 committed fixes; held120 excluded", flush=True)
