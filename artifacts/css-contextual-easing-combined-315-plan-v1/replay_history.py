from pathlib import Path
from collections import Counter
import hashlib
import json
import types

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
read = lambda path: json.loads(path.read_text())
for name, pin in read(HERE / "REFERENCES.json").items():
    assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == pin, name
capsule = ROOT / "artifacts/css-contextual-easing-reversible-browser-v4"
runtime = ROOT / "artifacts/css-contextual-easing-reversible-browser-runtime-2"
namespace = {}
exec(compile((capsule / "assess.py").read_bytes(), str(capsule / "assess.py"), "exec"), namespace)
assess = namespace["assess"]
helper = ROOT / "artifacts/css-accepted-119-121-122-install-runtime-v1/tests.py"
namespace = {}
exec(compile(helper.read_bytes(), str(helper), "exec"), namespace)
checks = types.SimpleNamespace(**namespace)
previous = None
for phase in ["original-wpt", "candidate-wpt"]:
    path = runtime / phase
    events = [json.loads(line) for line in (path / "raw.jsonl").read_text().splitlines()]
    result = assess(events, read(path / "RESULT.json")["exit"], read(path / "ASSESSMENT-POLICY.json"),
                    checks, original=previous, run_binding=read(path / "APPLICATION-METADATA.json"))
    assert result == read(path / "ASSESSMENT.json") and result["complete"]
    previous = result
    print(json.dumps({"phase": phase, "historical_only": True,
                      "statuses": dict(Counter(row["status"] for row in result["rows"])),
                      "endings": dict(Counter(row["status"] for row in result["ends"])),
                      "regression_signatures": len(result["regression_signature"])}))
assert previous["comparison_gate_passed"]
