import ast
import copy
import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
spec = importlib.util.spec_from_file_location("grid_projection", HERE / "projection.py")
projection = importlib.util.module_from_spec(spec)
spec.loader.exec_module(projection)
policy = json.loads((HERE / "POLICY.json").read_text())
assert policy["execution_enabled"] is False
canonical = ROOT / policy["canonical_epoch"]
assert hashlib.sha256(canonical.read_bytes()).hexdigest() == policy["canonical_epoch_sha256"]
epoch = json.loads(canonical.read_text())
observed = dict(epoch["semantic_index"], raw_index="local-stat-only-observation")
before = copy.deepcopy(epoch)
projected = projection.derive(epoch, observed)
assert epoch == before and projected["raw_index_observation"]["current"] == observed["raw_index"]
assert projected["semantic_index"] == epoch["semantic_index"]
mutants = []
for name in epoch["semantic_index"]:
    changed = dict(observed); changed[name] = "wrong"
    mutants.append((epoch, changed))
changed = copy.deepcopy(epoch); changed["staged_working"] = {"artifacts/foreign": "pin"}
mutants.append((changed, observed))
changed = dict(observed); changed.pop("working_diff")
mutants.append((epoch, changed))
changed = dict(observed, extra="field")
mutants.append((epoch, changed))
for args in mutants:
    try:
        projection.derive(*args)
    except AssertionError:
        pass
    else:
        raise AssertionError("accepted changed semantic state")
roles = json.loads((HERE / "SOURCE-ROLES.json").read_text())
assert set(roles) == {"servo/components/style/parser.rs", "servo/components/style/properties_and_values/value.rs", "servo/components/style/values/specified/calc.rs", "servo/components/style/properties/shorthands.rs"}
for name, role in roles.items():
    for kind in ("base", "candidate"):
        assert hashlib.sha256((ROOT / role[kind]).read_bytes()).hexdigest() == role[kind + "_sha256"]
assert (HERE / "epoch.py").read_bytes() == (ROOT / "artifacts/css-keyframe-operation-descriptor-post-signing-proposal-v2/epoch.py").read_bytes()
for f in HERE.glob("*.py"):
    ast.parse(f.read_text(), filename=str(f))
print(json.dumps({"projection_positive": 1, "semantic_rejections": len(mutants), "exact_four_source_pins": True, "empty_index_guard_unchanged": True, "python_syntax": True, "main_or_live_guard_executed": False}))
