from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


here = Path(__file__).resolve().parent
probe = here.parent / "css-fontface-provider-probe-v1"
gate = json.loads((here / "ROOT-NATIVE-WPT-v1.json").read_text())
verified = {}
for pair_name, pair in gate["pairs"].items():
    names = pair_name.split(" -> ")
    receipts = []
    for name in names:
        receipt_path = probe / (name + "-receipt.json")
        key = "artifacts/css-fontface-provider-probe-v1/" + receipt_path.name
        assert digest(receipt_path) == pair["receipts"][key]
        receipt = json.loads(receipt_path.read_text())
        assert receipt["pins_before"] == receipt["pins_after"]
        assert receipt["absent_before"] == receipt["absent_after"]
        for path, expected in receipt["pins_before"].items():
            if path.startswith("objdir-full.noindex/"):
                continue
            assert digest(probe / (name + "-sources") / path.replace("/", "__")) == expected
        events = [json.loads(line) for line in (probe / (name + ".jsonl")).read_text().splitlines()]
        statuses = [event for event in events if event["action"] in {"test_end", "test_status"}]
        assert statuses == receipt["statuses"]
        assert sum(event["action"] == "suite_end" for event in events) == receipt["suite_end_count"] == 1
        counts = defaultdict(Counter)
        for event in statuses:
            counts[event["test"]][event["status"]] += 1
        assert dict(counts) == receipt["counts"]
        receipts.append(receipt)
    before, after = receipts
    changes = {name for name in before["pins_before"]
               if before["pins_before"][name] != after["pins_before"][name]}
    assert changes == set(pair["changed_pins"])
    assert before["counts"] == pair["before_counts"]
    assert after["counts"] == pair["after_counts"]
    def outcomes(receipt):
        return {(e["test"], e.get("subtest")): (e["status"], e.get("expected", e["status"]))
                for e in receipt["statuses"]}
    old, new = outcomes(before), outcomes(after)
    assert old.keys() == new.keys()
    if "regression" in pair_name:
        assert old == new
    else:
        assert sum(status == "FAIL" for status, _ in old.values()) == 4
        assert sum(status == "PASS" for status, _ in new.values()) == 16
        assert all(status in {"PASS", "OK"} for status, _ in new.values())
    verified[pair_name] = {"changed_pins": sorted(changes), "before": before["counts"], "after": after["counts"]}
build = json.loads((here / "BUILD-v1.json").read_text())
assert build["exit_code"] == 0
assert digest(here / "build-candidate-v1.log") == build["log_sha256"]
metadata = json.loads((here / "WPT-METADATA-v2.json").read_text())
assert digest(here / "fix-candidate-v2.patch") == metadata["patch_sha256"]
assert digest(here / "final-wpt-v2.js") == metadata["final_wpt_sha256"]
proof = json.loads((here / "root-proof-replay-v2/RESULT.json").read_text())
assert proof["exit_code"] == 0
assert digest(here / "root-proof-replay-v2/replay.log") == proof["replay_log_sha256"]
record = {"status": "PASS", "pairs": verified, "proof_replay": proof,
          "limits": "Authenticates recorded browser/build runs and fresh proof replay; does not rerun a browser or native build."}
(here / "ROOT-EVIDENCE-CHECK-v1.json").write_text(json.dumps(record, indent=2) + "\n")
print("Recorded build and paired WPT evidence authenticated; fresh source-only proof replay passed.")
