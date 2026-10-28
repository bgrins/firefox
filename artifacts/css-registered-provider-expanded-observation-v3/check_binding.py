import copy
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

runner = load("candidate_runner", HERE / "run.py")
binding = load("candidate_binding", HERE / "bindings.py")
policy = runner.read(HERE / "POLICY.json")
epoch = runner.read(HERE / "OBSERVATION-EPOCH.json")
positive = binding.validate_phase(ROOT, HERE, policy, epoch, runner)
rejected = []
def reject(name, change):
    altered = copy.deepcopy(epoch)
    change(altered)
    try:
        binding.validate_phase(ROOT, HERE, policy, altered, runner)
    except RuntimeError:
        rejected.append(name)
    else:
        raise AssertionError(name)

reject("wrong role", lambda e: e["registered_number_transition"].update(role="original"))
reject("wrong variant", lambda e: e["registered_number_transition"].update(variant="zoom-standalone-v1"))
reject("uncompiled", lambda e: e["registered_number_transition"].update(compiled=False))
reject("premature acceptance", lambda e: e["registered_number_transition"].update(accepted=True))
reject("wrong build", lambda e: e["registered_number_transition"].update(last_phase="wrong"))
reject("wrong HEAD", lambda e: e["semantic_index"].update(head="0" * 40))
reject("wrong dirty scope", lambda e: e.update(modified_native_paths=[]))
reject("candidate body drift", lambda e: e["pins"].update({"servo/components/style/custom_properties.rs": "0" * 64}))
reject("accepted zoom drift", lambda e: e["pins"].update({"servo/components/style/values/computed/length.rs": "0" * 64}))
reject("binary drift", lambda e: e["pins"].update({policy["normal_binaries"][0]: "0" * 64}))
reject("accepted test drift", lambda e: e["pins"].update({next(iter(policy["installed_tests"])): "0" * 64}))
reject("accepted fix drift", lambda e: e["accepted_registered_zoom"].update(fix=140))
reject("unrecorded staged payload", lambda e: e["staged_working"].update({"servo/components/style/custom_properties.rs": "0" * 64}))
reject("unrecorded staged index", lambda e: e["semantic_index"].update(cached_diff="0" * 64))
reject("unrecorded identity", lambda e: e["installed_identities"].update({"servo/components/style/custom_properties.rs": [0, 0]}))
(HERE / "BINDING-CHECK.json").write_text(json.dumps({"actual_saved_build": positive, "rejected": rejected, "main_executed": False}, indent=2) + "\n")
print(json.dumps({"saved_build_positive": True, "rejected": len(rejected)}))
