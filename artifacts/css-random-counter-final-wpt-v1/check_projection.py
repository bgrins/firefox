import copy
import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]

def load(name):
    spec = importlib.util.spec_from_file_location(name, HERE / (name + ".py"))
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value

p = load("projection")
b = load("bindings")
policy = json.loads((HERE / "POLICY.json").read_text())
old = ROOT / policy["pair_capsule"]
old_policy = json.loads((old / "POLICY.json").read_text())
path = "capture/testing/web-platform/tests" + p.PAGE
args = [old_policy, policy, (old / path).read_text(), (HERE / path).read_text()]
roster = dict(old_policy["regression_subtests"], **old_policy["target_subtests"])
rows = [{"test": page, "subtest": name, "status": "PASS"} for page, names in roster.items() for name in names]
original = {"complete": True, "execution_preserved": True, "rows": rows, "regression_signature": [{"status": "PASS", "message": "retained"}]}
candidate = copy.deepcopy(original)
candidate["comparison_gate_passed"] = True
args += [original, candidate]
unchanged = copy.deepcopy(args)
assert p.validate(*args)["requires_fresh_landing_execution"]
assert args == unchanged
rejected = []

def reject(name, mutate):
    values = copy.deepcopy(args)
    mutate(values)
    try:
        p.validate(*values)
    except (RuntimeError, KeyError):
        rejected.append(name)
    else:
        raise AssertionError(name)

reject("unrelated HTML change", lambda x: x.__setitem__(3, x[3] + "changed"))
reject("second target rename", lambda x: x[1]["target_subtests"][p.PAGE].__setitem__(0, "other"))
reject("regression roster change", lambda x: next(iter(x[1]["regression_subtests"].values())).pop())
reject("original stronger control failure", lambda x: next(r for r in x[4]["rows"] if r["subtest"] == p.OLD).__setitem__("status", "FAIL"))
reject("candidate stronger control failure", lambda x: next(r for r in x[5]["rows"] if r["subtest"] == p.OLD).__setitem__("status", "FAIL"))
reject("missing historical row", lambda x: x[4]["rows"].pop())
reject("duplicate historical row", lambda x: x[5]["rows"].append(x[5]["rows"][0]))
reject("pair gate false", lambda x: x[5].__setitem__("comparison_gate_passed", False))
reject("preservation false", lambda x: x[4].__setitem__("execution_preserved", False))
reject("same status changed regression message", lambda x: x[5]["regression_signature"][0].__setitem__("message", "changed"))
reject("another target failure", lambda x: next(r for r in x[5]["rows"] if r["test"] == p.PAGE and r["subtest"] != p.OLD).__setitem__("status", "FAIL"))

baseline = json.loads((old / "SIGNING-BASELINE-EPOCH.json").read_text())
q = copy.deepcopy(policy)
q["promotion_manifest_sha256"] = "0" * 64
q["original_source_identities"] = {}
epoch = copy.deepcopy(baseline)
claims = {}
for i, (name, digest) in enumerate(dict(q["source_roles"]["candidate"], **q["live_oracle_sources"]).items()):
    identity = baseline["installed_identities"].get(name, [1, i + 10])
    claims[name] = {"path": name, "owned_sha256": digest, "identity": identity}
    epoch["pins"][name] = digest
    epoch["installed_identities"][name] = identity
    if name in q["source_roles"]["candidate"]:
        q["original_source_identities"][name] = identity
sources = q["source_roles"]["candidate"]
epoch["modified_native_paths"] = sorted(set(baseline["modified_native_paths"]) | set(sources))
epoch["counts"].update(roles=len(epoch["pins"]), installed_identities=len(epoch["installed_identities"]), native_modified_paths=len(epoch["modified_native_paths"]))
epoch["random_counter_transition"] = {"role": "candidate", "compiled": True, "accepted": False, "manifest_sha256": q["promotion_manifest_sha256"],
    "source_sha256": sources, "last_phase": "candidate-build-1", "variant": "random-parser-counter-rollback"}
h = SimpleNamespace(need=p.require)
b.project_promotion(epoch, baseline, q, claims, h)
mutation_names = []
mutations = {
    "accepted flag": lambda e: e["random_counter_transition"].__setitem__("accepted", True),
    "uncompiled": lambda e: e["random_counter_transition"].__setitem__("compiled", False),
    "extra native": lambda e: e["modified_native_paths"].append("extra.rs"),
    "changed HEAD": lambda e: e["semantic_index"].__setitem__("head", "0" * 40),
    "changed staged state": lambda e: e["staged_working"].__setitem__("x", "y"),
    "accepted LH font changed": lambda e: e["pins"].__setitem__("servo/components/style/values/specified/font.rs", "0" * 64),
    "extra pin": lambda e: e["pins"].__setitem__("extra", "0" * 64),
    "source inode": lambda e: e["installed_identities"].__setitem__(next(iter(sources)), [0, 0]),
    "source body": lambda e: e["pins"].__setitem__(next(iter(sources)), "0" * 64),
}
for name, mutate in mutations.items():
    changed = copy.deepcopy(epoch)
    mutate(changed)
    try:
        b.project_promotion(changed, baseline, q, claims, h)
    except (RuntimeError, KeyError):
        mutation_names.append(name)
    else:
        raise AssertionError(name)
result = {"pure_only": True, "positive_controls": 2, "assertion_projection_rejects": rejected, "promotion_projection_rejects": mutation_names,
          "actual_runtime_evidence_replayed": False}
(HERE / "PROJECTION-CHECK.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result))
