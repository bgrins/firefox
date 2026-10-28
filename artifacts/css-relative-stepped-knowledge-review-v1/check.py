import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PROPOSAL = ROOT / "artifacts/css-relative-stepped-zero-repair-proposal-v1"
name = "servo/components/style/values/generics/calc.rs"
base = (PROPOSAL / "base" / name).read_text()
candidate = (PROPOSAL / "candidate" / name).read_text()
assert (HERE / "current" / name).read_text() == base
for path, digest in json.loads((HERE / "REFERENCES.json").read_text()).items():
    assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == digest
for path, digest in json.loads((HERE / "SOURCE-PINS.json").read_text()).items():
    assert hashlib.sha256((HERE / "current" / path).read_bytes()).hexdigest() == digest
reconstructed = candidate
for left, right in (("value", "step"), ("dividend", "divisor")):
    guard = f"""                if {left}
                    .as_leaf()
                    .and_then(|leaf| leaf.canonical_value())
                    .is_none()
                    || {right}
                        .as_leaf()
                        .and_then(|leaf| leaf.canonical_value())
                        .is_none()
                {{
                    return SimplificationResult::Unchanged;
                }}

"""
    assert reconstructed.count(guard) == 1
    reconstructed = reconstructed.replace(guard, "", 1)
assert reconstructed == base
assert "if value.is_nan() || step.is_nan() || step.is_zero()" in candidate
assert "if result == 0.0 { -0.0 } else { result }" in candidate
assert "let value = op.apply(dividend, divisor);" in candidate
assert "let div = value / step;" in candidate
records = json.loads((HERE / "lean-replay/RESULT.json").read_text())
assert [r["exit"] for r in records["records"]] == [0, 1, 1]
assert records["scratch_removed"]
assert records["records"][0]["stdout"].count("propext") == 2
assert "sorryAx" not in records["records"][0]["stdout"]
rows = json.loads((HERE / "KNOWN-QUOTIENT-REPLAY.json").read_text())["rows"]
assert rows[0]["runtime_lower"] != rows[0]["simplifier_lower"]
assert rows[1]["runtime_upper"] != rows[1]["simplifier_upper"]
print(json.dumps({"references_authenticated": True, "exact_two_guard_only_delta": True,
                  "accepted_125_126_128_bodies_preserved": True,
                  "known_quotient_risk_still_present": True,
                  "lean_claims": 5, "false_controls_rejected": 2,
                  "native_compiled": False, "browser_executed": False}, indent=2))
