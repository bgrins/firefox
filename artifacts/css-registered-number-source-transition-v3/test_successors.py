import copy
import importlib.util
import json
from pathlib import Path
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
spec = importlib.util.spec_from_file_location("successor_test", HERE / "transition.py")
t = importlib.util.module_from_spec(spec)
spec.loader.exec_module(t)
policy = t.read(HERE / "POLICY.json")
source_pins = t.read(ROOT / policy["packages"]["snapshot"]["path"] / "SOURCE-PINS.json")
expected = t.authorized_successors(ROOT, policy, source_pins)
assert len(source_pins) == 140 and len(expected) == 2
records = []


def rejected(name, action):
    try:
        action()
    except RuntimeError:
        records.append({"name": name, "rejected": True})
    else:
        raise AssertionError(name)


with tempfile.TemporaryDirectory(prefix="number-successor-chain-", dir="/private/tmp") as temporary:
    root = Path(temporary)
    config = policy["authorized_successors"]
    directories = [item["signing_directory"] for item in config["checkpoints"]]
    for name in policy["references"]:
        if any(name.startswith(directory + "/") for directory in directories):
            dest = root / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(t.body(ROOT / name))
    assert t.authorized_successors(root, policy, source_pins) == expected
    ledger = config["paths"][0]
    for number, directory in enumerate(directories):
        signing = root / directory
        for label, name, transform in [
            ("unsigned", "checkpoint-receipt.json", lambda d: d.update(signature_verified=False)),
            ("wrong-head", "FINAL-CHECK.json", lambda d: d.update(head="0" * 40)),
            ("incomplete-selection", "checkpoint-selection.json", lambda d: d["files"].pop()),
            ("extra-ledger", "ROADMAP-UPDATE.json", lambda d: d["after"].update({"extra": "bad"})),
            ("wrong-selected-after", "checkpoint-selection.json", lambda d: d["source_pins"].update({ledger: "bad"})),
            ("broken-before-chain", "ROADMAP-UPDATE.json", lambda d: d["before"].update({ledger: "bad"})),
        ]:
            path = signing / name
            original = t.body(path)
            changed = json.loads(original)
            transform(changed)
            path.write_bytes(t.encoded(changed))
            rejected(str(number) + "-" + label, lambda: t.authorized_successors(root, policy, source_pins))
            path.write_bytes(original)
        preimage = signing / "ledger-preimages" / "CURRENT-COMMITS.json"
        original = t.body(preimage)
        preimage.write_bytes(b"changed")
        rejected(str(number) + "-changed-preimage", lambda: t.authorized_successors(root, policy, source_pins))
        preimage.write_bytes(original)
    path = root / directories[1] / "ROADMAP-UPDATE.json"
    original = t.body(path)
    changed = json.loads(original)
    changed["prior_authorized_ledger_update"] = "wrong"
    path.write_bytes(t.encoded(changed))
    rejected("missing-prior-update-link", lambda: t.authorized_successors(root, policy, source_pins))
    path.write_bytes(original)
    drift = dict(source_pins)
    drift[ledger] = "bad"
    rejected("v8-before-mismatch", lambda: t.authorized_successors(root, policy, drift))
    for label, mutate in [
        ("third-authorized-successor", lambda d: d["authorized_successors"]["paths"].append("extra")),
        ("skip-v14", lambda d: d["authorized_successors"]["checkpoints"].pop(0)),
        ("reorder-chain", lambda d: d["authorized_successors"]["checkpoints"].reverse()),
        ("wrong-paired-head", lambda d: d.update(paired_head="0" * 40)),
    ]:
        altered = copy.deepcopy(policy)
        mutate(altered)
        rejected(label, lambda: t.authorized_successors(root, altered, source_pins))
    data = b"authorized successor"
    pin = t.digest(data)
    epoch = {key: {ledger: pin} for key in policy["pin_maps"]}
    t.verify_successor(ledger, pin, data, epoch, policy, data)
    for label, live, head in [("live-byte-drift", b"drift", data), ("head-blob-drift", data, b"drift")]:
        rejected(label, lambda: t.verify_successor(ledger, pin, live, epoch, policy, head))
    for key in policy["pin_maps"]:
        altered_epoch = copy.deepcopy(epoch)
        altered_epoch[key][ledger] = "bad"
        rejected("epoch-conflict-" + key, lambda: t.verify_successor(ledger, pin, data, altered_epoch, policy, data))
    empty = {key: {} for key in policy["pin_maps"]}
    rejected("unpinned-successor", lambda: t.verify_successor(ledger, pin, data, empty, policy, data))
assert not root.exists()
print(json.dumps({"status": "SUCCESSOR_CHAIN_CONTROLS_PASS", "negative_controls": records,
                  "v8_source_pins": len(source_pins), "authorized_successors": expected,
                  "checkpoints": directories, "scratch_removed": True, "actual_live_ledgers_read": False,
                  "live_git_index_binary_query": False, "runtime_transition_executed": False}, indent=2))
