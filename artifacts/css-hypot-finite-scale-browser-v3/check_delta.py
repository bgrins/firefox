import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
OLD = HERE.parent / "css-hypot-finite-scale-browser-v2"
read = lambda p: json.loads(p.read_bytes())
for name in ("baseline.py", "candidate.py", "assess.py", "check_assessor.py", "wpt.py", "SOURCE-ROLES.json"):
    assert (HERE / name).read_bytes() == (OLD / name).read_bytes(), name
old = read(OLD / "POLICY.json")
new = read(HERE / "POLICY.json")
assert new["execution_enabled"] is True and new["candidate_execution_enabled"] is False
assert new["baseline_binding"] is None and new["baseline_capsule"] is None
allowed = {("head",), ("controls", "CURRENT-EPOCH.json"),
           ("prepared_flag_hashes", "root"), ("prepared_flag_hashes", "nested"),
           ("wpt", "harness_revision"), ("wpt", "phase_revisions", "candidate"),
           ("execution_enabled",), ("activation_pending",), ("references",)}
changes = []
def compare(a, b, path=()):
    if a == b:
        return
    if path in allowed:
        changes.append("/".join(path))
        return
    assert isinstance(a, dict) and isinstance(b, dict) and set(a) == set(b), path
    for key in a:
        compare(a[key], b[key], path + (key,))
compare(old, new)
assert new["head"] == new["wpt"]["harness_revision"] == new["wpt"]["phase_revisions"]["candidate"]
assert all(new["references"].get(name) == pin for name, pin in old["references"].items())
print(json.dumps({"changed_policy_fields": sorted(changes), "runner_bodies_and_roles_byteidentical": True,
                  "candidate_execution_enabled": False, "browser_execution_performed": False}, sort_keys=True))
