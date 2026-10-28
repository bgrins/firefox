import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RUNTIME = ROOT / "artifacts/css-registered-number-native-runtime-v1"
ENV = dict(os.environ, GIT_OPTIONAL_LOCKS="0")
read = lambda p: json.loads(p.read_bytes())
digest = lambda b: hashlib.sha256(b).hexdigest()


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


state = load("sync_state", "artifacts/css-registered-number-native-runtime-v1/state.py")
ownership = load("sync_ownership", "artifacts/css-registered-number-source-transition-v4/transition.py")
assert not any(os.environ.get(k) for k in ["GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_OBJECT_DIRECTORY", "GIT_ALTERNATE_OBJECT_DIRECTORIES"])
plan = read(HERE / "SYNC-PLAN.json")
controls = {n:(HERE / ("PRE-"+n)).read_bytes() for n in ["CURRENT-EPOCH.json", "ROLE.json", "OWNED.json"]}
assert digest(controls["CURRENT-EPOCH.json"]) == plan["runtime_epoch_before"] == "10893d33655602ae74a20df6302987051711f84281ff6ff154797809be7db3f4"
assert digest(controls["ROLE.json"]) == plan["role_sha256"] and digest(controls["OWNED.json"]) == plan["owned_sha256"]
assert digest((HERE / "INITIAL-EPOCH.json").read_bytes()) == plan["initial_epoch_sha256"]
initial = read(HERE / "INITIAL-EPOCH.json")
normalized = json.loads(controls["CURRENT-EPOCH.json"])
normalized["historical_raw_index_observation"] = copy.deepcopy(normalized["raw_index_observation"])
normalized["raw_index_observation"] = {"current":read(HERE / "BEFORE.json")["index"]["raw_index"], "prior_comparison_raw_drift_cause":"unknown; semantic staging preserved"}
assert normalized == initial
assert initial["semantic_index"]["head"] == plan["initial_head"] == "b04304be4b2083686920e8b3788e8e7614d26496"
current_bytes = (HERE / "CURRENT-EPOCH.json").read_bytes()
epoch = json.loads(current_bytes)
before = state.a.verify_current(state.h, ROOT, ENV, epoch)
assert initial["staged_working"] == epoch["staged_working"] == {}
assert initial["modified_native_paths"] == epoch["modified_native_paths"] == ["servo/components/style/custom_properties.rs"]
assert initial["registered_number_transition"] == epoch["registered_number_transition"] == {"role":"candidate", "variant":"registered-provider-default-v5", "compiled":True, "accepted":False, "last_phase":"provider-default-candidate-build-3"}
assert initial["page_selector_transition"] == epoch["page_selector_transition"] == {"accepted":True,"compiled":True,"last_phase":"candidate-build-1","role":"candidate","variant":"page-selector-name-filter"}
assert "random_counter_transition" not in epoch
assert epoch["pins"]["servo/components/style/custom_properties.rs"] == "2675b33b30ac43db5b758d5a80f42fa4530856c32d5a0923882a15f8a8bc5774"
assert epoch["pins"]["servo/components/style/properties/cascade.rs"] == "2cc7b3d4047b9759277f41809ad7ba7baef99431c26b608bcf459b2d83764656"
ids = plan["receipt_ids"]
assert ids == ["random", "line-height", "checkpoint"]
expected = copy.deepcopy(initial)
expected["semantic_index"] = epoch["semantic_index"]
expected["raw_index_observation"]["current"] = epoch["raw_index_observation"]["current"]
parent = initial["semantic_index"]["head"]
for ident in ids:
    receipt, item = read(HERE / (ident+"-receipt.json")), read(HERE / (ident+"-item.json"))
    assert receipt["signature_verified"] and receipt["working_bodies_and_nested_index_preserved"]
    assert receipt["parent"] == parent and sorted(receipt["files"]) == sorted(item["files"])
    assert set(item["files"]) == set(item["source_pins"])
    assert all(n.startswith("artifacts/") and n != "artifacts/css-spec-lean" and not n.startswith("artifacts/css-spec-lean/") for n in item["files"])
    assert state.h.git(ROOT, ENV, "rev-parse", receipt["commit"]+"^").decode().strip() == parent
    assert state.h.git(ROOT, ENV, "rev-parse", receipt["commit"]+"^{tree}").decode().strip() == receipt["tree"]
    assert sorted(state.h.git(ROOT, ENV, "diff-tree", "--no-commit-id", "--name-only", "-r", receipt["commit"]).decode().splitlines()) == sorted(item["files"])
    with (HERE / (ident+"-resync-signature.log")).open("x") as stream:
        subprocess.run(["git", "--no-optional-locks", "-c", "core.fsmonitor=false", "-c", "gpg.ssh.allowedSignersFile="+str(ROOT / "artifacts/css-local-signing-20261027-v1/allowed-signers"), "verify-commit", receipt["commit"]], cwd=ROOT, env=ENV, stdout=stream, stderr=subprocess.STDOUT, check=True)
    expected["committed_research_working_payloads"].update(item["source_pins"])
    parent = receipt["commit"]
assert parent == epoch["semantic_index"]["head"]
assert epoch["semantic_index"]["working_diff"] == initial["semantic_index"]["working_diff"]
expected["counts"]["committed_research_payloads"] = len(expected["committed_research_working_payloads"])
assert expected == epoch
recovery = ROOT / "artifacts/css-worktree-recovery-20261028-v1"
for name, pin in read(recovery / "SOURCE-PINS.json").items():
    assert digest((ROOT / name).read_bytes()) == pin["sha256"]
    assert (ROOT / name).read_bytes() == (recovery / "working" / name).read_bytes()
installed_receipt = ROOT / plan["installed_wpt_receipt"]["path"]
assert digest(installed_receipt.read_bytes()) == plan["installed_wpt_receipt"]["sha256"]
installed_wpt = read(installed_receipt)
assert installed_wpt == plan["installed_wpt"]
assert set(installed_wpt) == {
    "testing/web-platform/tests/css/css-properties-values-api/registered-random-alternative-indices.tentative.html",
    "testing/web-platform/tests/css/css-values/random-typed-parse-rollback.html",
}
installed_wpt_claims = {}
for name, record in installed_wpt.items():
    source = record["source"]
    assert source.startswith("artifacts/") and not source.startswith("artifacts/css-spec-lean/")
    assert expected["committed_research_working_payloads"][source] == record["sha256"]
    assert digest((ROOT / source).read_bytes()) == record["sha256"]
    assert digest(state.h.git(ROOT, ENV, "show", parent+":"+source)) == record["sha256"]
    assert state.h.git(ROOT, ENV, "ls-files", "--stage", "--", name) == b""
    installed_wpt_claims[name] = ownership.claim(ROOT, name, record["sha256"], record["identity"])
for name, body in controls.items():
    assert (RUNTIME / name).read_bytes() == body
claims = {n:ownership.claim(ROOT,str((RUNTIME/n).relative_to(ROOT)),digest(body)) for n,body in controls.items()}
ownership.quiescent(RUNTIME)
ownership.quiescent(ROOT / "artifacts/css-page-selector-native-runtime-v1")
assert not (ROOT / "artifacts/css-random-counter-native-runtime-v1").exists()
assert not (RUNTIME / "SOURCE-TRANSITION.lock").exists()
try:
    assert state.a.verify_current(state.h, ROOT, ENV, epoch) == before
    for item in claims.values():
        ownership.claim(ROOT,item["path"],item["owned_sha256"],item["identity"])
    for item in installed_wpt_claims.values():
        ownership.claim(ROOT,item["path"],item["owned_sha256"],item["identity"])
    ownership.write_owned(ROOT,claims["CURRENT-EPOCH.json"],current_bytes)
    assert state.a.verify_current(state.h, ROOT, ENV, epoch) == before
    assert all((RUNTIME/n).read_bytes() == controls[n] for n in ["ROLE.json","OWNED.json"])
    for item in installed_wpt_claims.values():
        ownership.claim(ROOT,item["path"],item["owned_sha256"],item["identity"])
except BaseException as error:
    rollback_errors = []
    try:
        ownership.write_owned(ROOT,claims["CURRENT-EPOCH.json"],controls["CURRENT-EPOCH.json"])
    except BaseException as rollback:
        rollback_errors.append(repr(rollback))
    state.save(HERE / "SYNCHRONIZATION-FAILURE.json", {"error":repr(error),"rollback_errors":rollback_errors,"manual_recovery_required":True,"runtime_epoch_synchronized":False,"signed_head":parent,"note":"Old runtime metadata at the new signed HEAD is not certified."})
    raise
state.save(HERE / "FINAL-CHECK.json", {"head":parent,"signature_chain_verified":True,"runtime_epoch_synchronized":True,"native_dirty_paths":1,"provider_candidate_version":"v5 partial ordinary restoration","provider_candidate_compiled":True,"provider_candidate_accepted":False,"accepted_fixes":139,"tracked_fixes":140,"held_excluded":120,"current_epoch_sha256":digest(current_bytes),"unfinished_project_files_archived":75,"installed_wpt_verified_against_committed_research_and_install_receipt":True,"installed_wpt_paths":sorted(installed_wpt),"random_candidate_applied":False,"random_candidate_compiled":False,"line_height_candidate_applied":False,"runtime_binary_provenance":"unchanged historical page/provider builds; research-only signing"})
print("Verified signed research and recovery checkpoint; partial v5 remains unaccepted",parent)
