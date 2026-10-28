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


with tempfile.TemporaryDirectory(prefix="number-successor-controls-", dir="/private/tmp") as temporary:
    root = Path(temporary)
    config = policy["authorized_successors"]
    signing = root / config["signing_directory"]
    for name in policy["references"]:
        if name.startswith(config["signing_directory"] + "/"):
            dest = root / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(t.body(ROOT / name))
    assert t.authorized_successors(root, policy, source_pins) == expected
    for name, transform in [
        ("checkpoint-receipt.json", lambda d: d.update(signature_verified=False)),
        ("FINAL-CHECK.json", lambda d: d.update(head=policy["captured_native_head"])),
        ("checkpoint-selection.json", lambda d: d["files"].pop()),
        ("ROADMAP-UPDATE.json", lambda d: d["after"].update({"extra": "bad"})),
        ("checkpoint-selection.json", lambda d: d["source_pins"].update({config["paths"][0]: "bad"})),
    ]:
        path = signing / name
        original = t.body(path)
        changed = json.loads(original)
        transform(changed)
        path.write_bytes(t.encoded(changed))
        rejected("modified-" + name, lambda: t.authorized_successors(root, policy, source_pins))
        path.write_bytes(original)
    drift = dict(source_pins)
    drift[config["paths"][0]] = "bad"
    rejected("v8-before-mismatch", lambda: t.authorized_successors(root, policy, drift))
    altered = copy.deepcopy(policy)
    altered["authorized_successors"]["paths"].append("extra")
    rejected("third-authorized-successor", lambda: t.authorized_successors(root, altered, source_pins))
    preimage = signing / "ledger-preimages" / "CURRENT-COMMITS.json"
    original = t.body(preimage)
    preimage.write_bytes(b"changed")
    rejected("changed-committed-preimage", lambda: t.authorized_successors(root, policy, source_pins))
    preimage.write_bytes(original)
    name = config["paths"][0]
    data = b"authorized successor"
    pin = t.digest(data)
    epoch = {key: {name: pin} for key in policy["pin_maps"]}
    t.verify_successor(name, pin, data, epoch, policy, data)
    for label, live, head in [("live-byte-drift", b"drift", data), ("head-blob-drift", data, b"drift")]:
        rejected(label, lambda: t.verify_successor(name, pin, live, epoch, policy, head))
    for key in policy["pin_maps"]:
        altered_epoch = copy.deepcopy(epoch)
        altered_epoch[key][name] = "bad"
        rejected("epoch-conflict-" + key, lambda: t.verify_successor(name, pin, data, altered_epoch, policy, data))
    empty = {key: {} for key in policy["pin_maps"]}
    rejected("unpinned-successor", lambda: t.verify_successor(name, pin, data, empty, policy, data))
assert not root.exists()
print(json.dumps({"status": "SUCCESSOR_CONTROLS_PASS", "negative_controls": records,
                  "v8_source_pins": len(source_pins), "authorized_successors": expected,
                  "scratch_removed": True, "actual_live_ledgers_read": False,
                  "live_git_index_binary_query": False, "runtime_transition_executed": False}, indent=2))
