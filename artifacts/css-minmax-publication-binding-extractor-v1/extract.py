import argparse
import hashlib
import json
import os
from pathlib import Path
import stat
import sys

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RUNTIME = ROOT / "artifacts/css-registered-number-native-runtime-v1"
sha = lambda b: hashlib.sha256(b).hexdigest()
read = lambda p: json.loads(p.read_bytes())


def extract(receipt_path, receipt_pin, branch):
    assert branch.startswith("refs/heads/") and len(branch) > len("refs/heads/")
    receipt_path = receipt_path.resolve()
    relative = str(receipt_path.relative_to(ROOT))
    assert relative.startswith("artifacts/")
    body = receipt_path.read_bytes()
    assert sha(body) == receipt_pin
    receipt = json.loads(body)
    assert receipt["committed"] is True and receipt["signature_verified"] is True
    assert receipt["native_working_diff_preserved"] is True
    assert receipt["accepted_fix_increment"] == 0
    inputs = read(HERE / "INPUTS.json")
    for record in inputs.values():
        assert sha((ROOT / record["path"]).read_bytes()) == record["sha256"]
    previous = read(ROOT / inputs["claim_allowlist"]["path"])
    policy = read(ROOT / inputs["minmax_policy"]["path"])
    controls = {name: (RUNTIME / name).read_bytes()
                for name in ("CURRENT-EPOCH.json", "OWNED.json", "ROLE.json")}
    epoch = json.loads(controls["CURRENT-EPOCH.json"])
    owned = json.loads(controls["OWNED.json"])
    assert sha(controls["CURRENT-EPOCH.json"]) == receipt["epoch_sha256"]
    assert epoch["semantic_index"]["head"] == receipt["head"]
    assert epoch["staged_working"] == {}
    assert epoch["modified_native_paths"] == ["servo/components/style/custom_properties.rs"]
    assert not os.path.lexists(RUNTIME / "SOURCE-TRANSITION.lock")
    assert not os.path.lexists(ROOT / policy["runtime_output"])
    claims = {}
    for name, expected in previous["accepted_current_payloads"].items():
        assert epoch["pins"][name] == expected["sha256"]
        path = ROOT / name
        st = path.lstat()
        assert stat.S_ISREG(st.st_mode) and st.st_nlink == 1
        assert sha(path.read_bytes()) == expected["sha256"]
        identity = [st.st_dev, st.st_ino]
        assert epoch["installed_identities"][name] == identity
        claims[name] = {"sha256": expected["sha256"], "identity": identity}
    assert len(claims) == 29
    source = policy["source_path"]
    assert claims[source]["sha256"] == policy["base_sha256"]
    assert epoch["accepted_pow_special_value"]["files"][source] == policy["base_sha256"]
    assert sha((ROOT / "servo/components/style/custom_properties.rs").read_bytes()) == policy["held_provider_sha256"]
    for name in set(policy["files"]) - {source}:
        assert not os.path.lexists(ROOT / name) and epoch["pins"].get(name) is None
        assert name not in epoch["installed_identities"] and name not in owned
    absent = sorted(name for name, value in epoch["pins"].items()
                    if value is None and name.startswith("testing/web-platform/meta/"))
    for name in absent:
        assert not os.path.lexists(ROOT / name)
        assert name not in epoch["installed_identities"] and name not in owned
    mutable = {"pins", "installed_identities", "semantic_index", "raw_index_observation",
               "modified_native_paths", "counts", "committed_research_working_payloads",
               "minmax_relative_infinity_transition"}
    historical = {name: value for name, value in epoch.items() if name not in mutable}
    assert "minmax_relative_infinity_transition" not in epoch
    assert all((RUNTIME / name).read_bytes() == value for name, value in controls.items())
    assert receipt_path.read_bytes() == body
    return {"head": receipt["head"], "branch": branch,
            "research_receipt": relative, "research_receipt_sha256": receipt_pin,
            "controls": {name: sha(value) for name, value in controls.items()},
            "accepted_claims": claims, "historical_markers": historical,
            "absent_metadata": absent}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("receipt", type=Path)
    parser.add_argument("--receipt-sha256", required=True)
    parser.add_argument("--branch", required=True)
    args = parser.parse_args()
    print(json.dumps(extract(args.receipt, args.receipt_sha256, args.branch), indent=2, sort_keys=True))
