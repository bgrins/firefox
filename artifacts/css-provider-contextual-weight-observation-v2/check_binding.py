import copy
import hashlib
import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


run = load("binding_runner", HERE / "run.py")
binding = load("binding_module", HERE / "bindings.py")
original_policy = run.read(HERE / "POLICY.json")
original_epoch = run.read(ROOT / "artifacts/css-registered-provider-expanded-observation-v3/OBSERVATION-EPOCH.json")
original_epoch["registered_number_transition"] = {
    "role": "candidate", "variant": "registered-provider-default-v5", "compiled": True,
    "accepted": False, "last_phase": "provider-default-candidate-build-3"}
original_epoch["modified_native_paths"] = ["servo/components/style/custom_properties.rs"]
original_epoch["counts"]["native_modified_paths"] = 1
for name, pin in original_policy["source_roles"]["candidate"].items():
    original_epoch["pins"][name] = pin
for name in original_policy["phase_binaries"]:
    original_epoch["pins"][name] = "b" * 64
original_policy.update(epoch_sha256="e" * 64, build_epoch_sha256="e" * 64, build_result_sha256="r" * 64)
original_policy["phase_binaries"] = {name: "b" * 64 for name in original_policy["phase_binaries"]}
result = {"source_role": "candidate", "command_success": True, "preservation_verified": True,
          "error": None, "owned_processes": [], "publication_errors": []}


def check(policy, epoch, compiled=None, build_result=None):
    compiled = epoch if compiled is None else compiled
    values = {ROOT / policy["build_result"]: result if build_result is None else build_result,
              ROOT / policy["build_epoch"]: compiled, HERE / "OBSERVATION-EPOCH.json": epoch}
    hashes = {ROOT / policy["build_result"]: "r" * 64, ROOT / policy["build_epoch"]: "e" * 64,
              HERE / "OBSERVATION-EPOCH.json": "e" * 64}
    helper = SimpleNamespace(**vars(run))
    helper.read = lambda path: values[path] if path in values else run.read(path)
    helper.sha = lambda path: hashes[path] if path in hashes else run.sha(path)
    return binding.validate_phase(ROOT, HERE, policy, epoch, helper)


check(copy.deepcopy(original_policy), copy.deepcopy(original_epoch))
rejected = []
mutations = {
    "wrong-variant": lambda p,e: e["registered_number_transition"].update(variant="registered-provider-default-v4"),
    "uncompiled": lambda p,e: e["registered_number_transition"].update(compiled=False),
    "accepted": lambda p,e: e["registered_number_transition"].update(accepted=True),
    "wrong-role": lambda p,e: e["registered_number_transition"].update(role="original"),
    "wrong-build-label": lambda p,e: p.update(build_label="provider-default-candidate-build-2"),
    "extra-dirty-source": lambda p,e: e["modified_native_paths"].append("servo/components/style/properties/cascade.rs"),
    "custom-source-drift": lambda p,e: e["pins"].update({"servo/components/style/custom_properties.rs":"bad"}),
    "zoom-source-drift": lambda p,e: e["pins"].update({"servo/components/style/properties_and_values/value.rs":"bad"}),
    "native-identity-missing": lambda p,e: e["installed_identities"].pop("servo/components/style/custom_properties.rs"),
    "head-drift": lambda p,e: e["semantic_index"].update(head="0"*40),
    "staging-drift": lambda p,e: e["staged_working"].pop(next(iter(e["staged_working"]))),
    "binary-drift": lambda p,e: e["pins"].update({next(iter(p["phase_binaries"])):"bad"}),
    "target-roster-drift": lambda p,e: p.update(target_subtests={}),
}
for label, mutate in mutations.items():
    policy, epoch = copy.deepcopy(original_policy), copy.deepcopy(original_epoch)
    mutate(policy, epoch)
    try:
        check(policy, epoch)
    except (RuntimeError, AssertionError, KeyError):
        rejected.append(label)
    else:
        raise AssertionError(label)
compiled = copy.deepcopy(original_epoch)
compiled["raw_index_observation"]["current"] = "different"
try:
    check(original_policy, original_epoch, compiled=compiled)
except (RuntimeError, AssertionError, KeyError):
    rejected.append("saved-build-epoch-projection")
else:
    raise AssertionError("saved-build-epoch-projection")
failed = dict(result, command_success=False)
try:
    check(original_policy, original_epoch, build_result=failed)
except (RuntimeError, AssertionError, KeyError):
    rejected.append("unsuccessful-build")
else:
    raise AssertionError("unsuccessful-build")
receipt = {"positive": 1, "rejected": rejected, "synthetic_future_build_only": True,
           "actual_future_epoch_or_binary_attestation": False, "live_queries": False,
           "browser_execution": False, "native_or_index_mutations": False}
run.save(HERE / "BINDING-CONTROLS.json", receipt)
print(json.dumps(receipt))
