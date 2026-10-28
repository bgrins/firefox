import sys
sys.dont_write_bytecode = True
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


adopt = load("adoption_subject", HERE / "adopt.py")
policy = adopt.read(HERE / "POLICY.json")
capsule = ROOT / policy["staged_capsule"]
old = adopt.read(ROOT / policy["runtime"] / "provider-default-candidate-build-2/EPOCH.json")
observed = adopt.read(capsule / "OBSERVATION-EPOCH.json")
staging = adopt.read(capsule / "STAGING.json")
role = {"role": "candidate", "variant": "registered-provider-default-v4", "built": True,
        "last_build": "provider-default-candidate-build-2"}
assert adopt.validate_adoption(policy, old, observed, staging, role) == observed
rejected = []


def reject(name, change):
    args = copy.deepcopy([policy, old, observed, staging, role])
    change(*args)
    try:
        adopt.validate_adoption(*args)
    except AssertionError:
        rejected.append(name)
    else:
        raise AssertionError(name)


reject("old HEAD", lambda p, o, n, s, r: o["semantic_index"].update(head="0" * 40))
reject("observed HEAD", lambda p, o, n, s, r: n["semantic_index"].update(head="0" * 40))
reject("native body projection", lambda p, o, n, s, r: n["pins"].update({"servo/components/style/custom_properties.rs": "0" * 64}))
reject("binary projection", lambda p, o, n, s, r: n["pins"].update({"objdir-full.noindex/dist/Nightly.app/Contents/MacOS/XUL": "0" * 64}))
reject("extra staged body", lambda p, o, n, s, r: n["staged_working"].update({"artifacts/extra": "0" * 64}))
reject("missing staged body", lambda p, o, n, s, r: n["staged_working"].pop(next(iter(n["staged_working"]))))
reject("changed staged hash", lambda p, o, n, s, r: n["staged_working"].update({next(iter(n["staged_working"])): "0" * 64}))
reject("wrong cached diff", lambda p, o, n, s, r: n["semantic_index"].update(cached_diff="0" * 64))
reject("working diff projection", lambda p, o, n, s, r: s["semantic_index"].update(working_diff="0" * 64))
reject("old staging already present", lambda p, o, n, s, r: o.update(staged_working={"artifacts/x": "0" * 64}))
reject("uncompiled source", lambda p, o, n, s, r: o["registered_number_transition"].update(compiled=False))
reject("premature acceptance", lambda p, o, n, s, r: o["registered_number_transition"].update(accepted=True))
reject("wrong role", lambda p, o, n, s, r: r.update(variant="other"))
reject("unbuilt role", lambda p, o, n, s, r: r.update(built=False))
reject("different build", lambda p, o, n, s, r: r.update(last_build="other"))
reject("wrong observation digest", lambda p, o, n, s, r: s.update(observation_epoch_sha256="0" * 64))
reject("wrong build digest", lambda p, o, n, s, r: s.update(build_epoch_sha256="0" * 64))
reject("missing staged filename", lambda p, o, n, s, r: s["staged_files"].pop())
reject("duplicate staged filename", lambda p, o, n, s, r: s["staged_files"].__setitem__(0, s["staged_files"][1]))
reject("nested repository drift", lambda p, o, n, s, r: n["nested_semantic_index"].update(head="0" * 40))
reject("ownership drift", lambda p, o, n, s, r: n["installed_identities"].update({"unexpected": [1, 2]}))

ownership = load("owned_write_subject", ROOT / "artifacts/css-registered-number-source-transition-v4/transition.py")
with tempfile.TemporaryDirectory(prefix="css-staged-adoption-check-", dir="/private/tmp") as name:
    scratch = Path(name)
    target = scratch / "CURRENT-EPOCH.json"
    initial, replacement = b'{"original":true}\n', b'{"staged":true}\n'
    target.write_bytes(initial)
    claim = ownership.claim(scratch, target.name, hashlib.sha256(initial).hexdigest())
    identity = target.stat().st_ino
    ownership.write_owned(scratch, claim, replacement)
    assert target.read_bytes() == replacement
    ownership.write_owned(scratch, claim, initial)
    assert target.read_bytes() == initial and target.stat().st_ino == identity
    for label in ["../escape", "/absolute", "a/b", "..", ""]:
        try:
            adopt.absent_output(scratch, label)
        except AssertionError:
            rejected.append("output label " + repr(label))
        else:
            raise AssertionError(label)
    assert adopt.absent_output(scratch, "provider-staging-adoption-1").parent == scratch
    for name in ["exists", "dangling"]:
        path = scratch / name
        path.mkdir() if name == "exists" else path.symlink_to("missing")
        try:
            adopt.absent_output(scratch, name)
        except AssertionError:
            rejected.append("occupied output " + name)
        else:
            raise AssertionError(name)
assert not scratch.exists()
result = {"saved_epoch_derivation_passed": True, "corruptions_rejected": rejected,
          "owned_write_and_restore_same_inode": True, "scratch_removed": True,
          "main_executed": False, "live_guard_executed": False, "runtime_mutated": False}
(HERE / "CHECK.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps({"saved_derivation_passed": True, "rejected": len(rejected), "owned_write_restore": True}))
