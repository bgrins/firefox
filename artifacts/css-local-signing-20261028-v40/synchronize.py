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
config=read(HERE / "EXECUTION.json")
assert config["execution_enabled"] is True
assert digest((HERE/"ROADMAP-PUBLICATION.json").read_bytes()) == config["roadmap_publication_sha256"]
roadmap=read(HERE/"ROADMAP-PUBLICATION.json")
roadmap_name=roadmap["target"]
assert roadmap_name == "artifacts/css-continuation-roadmap-20261028-v1/PLAN.md"
assert digest((HERE/roadmap["preimage"]).read_bytes()) == roadmap["before_sha256"]
assert digest((HERE/roadmap["postimage"]).read_bytes()) == roadmap["after_sha256"]
assert (HERE/roadmap["postimage"]).read_bytes().endswith((HERE/roadmap["preimage"]).read_bytes())
assert (ROOT/roadmap_name).read_bytes() == (HERE/roadmap["postimage"]).read_bytes()
previous = ROOT / "artifacts/css-local-signing-20261028-v39"
assert digest((previous / "FINAL-CHECK.json").read_bytes()) == plan["previous_final_check_sha256"]
assert read(previous / "FINAL-CHECK.json")["head"] == plan["initial_head"]
controls = {n:(HERE / ("PRE-"+n)).read_bytes() for n in ["CURRENT-EPOCH.json", "ROLE.json", "OWNED.json"]}
assert digest(controls["CURRENT-EPOCH.json"]) == plan["runtime_epoch_before"]
assert digest(controls["ROLE.json"]) == plan["role_sha256"] and digest(controls["OWNED.json"]) == plan["owned_sha256"]
assert digest((HERE / "INITIAL-EPOCH.json").read_bytes()) == plan["initial_epoch_sha256"]
initial = read(HERE / "INITIAL-EPOCH.json")
normalized = json.loads(controls["CURRENT-EPOCH.json"])
normalized["historical_raw_index_observation"] = copy.deepcopy(normalized["raw_index_observation"])
normalized["raw_index_observation"] = {"current":read(HERE / "BEFORE.json")["index"]["raw_index"], "prior_comparison_raw_drift_cause":"unknown; semantic staging preserved"}
assert normalized == initial
assert initial["semantic_index"]["head"] == plan["initial_head"]
current_bytes = (HERE / "CURRENT-EPOCH.json").read_bytes()
epoch = json.loads(current_bytes)
before = state.a.verify_current(state.h, ROOT, ENV, epoch)
assert initial["staged_working"] == epoch["staged_working"] == {}
assert initial["modified_native_paths"] == epoch["modified_native_paths"] == ["servo/components/style/custom_properties.rs"]
assert initial["registered_number_transition"] == epoch["registered_number_transition"] == {"role":"candidate", "variant":"registered-provider-default-v5", "compiled":True, "accepted":False, "last_phase":"provider-default-candidate-build-3"}
assert initial["page_selector_transition"] == epoch["page_selector_transition"] == {"accepted":True,"compiled":True,"last_phase":"candidate-build-1","role":"candidate","variant":"page-selector-name-filter"}
assert epoch["accepted_random_counter"] == initial["accepted_random_counter"] and epoch["accepted_random_counter"]["fix"] == 142
assert epoch["random_counter_transition"] == initial["random_counter_transition"] and epoch["random_counter_transition"]["accepted"] and epoch["random_counter_transition"]["compiled"]
assert epoch["accepted_line_height"] == initial["accepted_line_height"] and epoch["accepted_line_height"]["fix"] == 141
assert epoch["line_height_transition"] == initial["line_height_transition"] and epoch["line_height_transition"]["accepted"] and epoch["line_height_transition"]["compiled"]
assert epoch["accepted_linear_guard"] == initial["accepted_linear_guard"] and epoch["accepted_linear_guard"]["fix"] == 143
assert epoch["linear_guard_transition"] == initial["linear_guard_transition"] and epoch["linear_guard_transition"]["accepted"] and epoch["linear_guard_transition"]["compiled"]
assert epoch["pins"]["servo/components/style/custom_properties.rs"] == "2675b33b30ac43db5b758d5a80f42fa4530856c32d5a0923882a15f8a8bc5774"
assert epoch["pins"]["servo/components/style/properties/cascade.rs"] == "2cc7b3d4047b9759277f41809ad7ba7baef99431c26b608bcf459b2d83764656"
ids = plan["receipt_ids"]
assert ids == ["research", "checkpoint"]
assert initial["committed_research_working_payloads"][roadmap_name] == roadmap["before_sha256"]
expected = copy.deepcopy(initial)
for key in ("pins","staged_working"):
    if roadmap_name in expected[key]:
        assert expected[key][roadmap_name] == roadmap["before_sha256"]
        expected[key][roadmap_name] = roadmap["after_sha256"]
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
    if ident == "research":
        assert roadmap_name not in item["files"]
    else:
        assert item["source_pins"][roadmap_name] == roadmap["after_sha256"]
    for name,pin in item["source_pins"].items():
        if name in initial["committed_research_working_payloads"] and pin != initial["committed_research_working_payloads"][name]:
            assert name == roadmap_name and pin == roadmap["after_sha256"]
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
retired = ROOT / 'testing/web-platform/tests/css/css-properties-values-api/registered-random-alternative-indices.tentative.html'
assert not retired.exists() and not retired.is_symlink()
accepted = initial['accepted_line_height']['files'] | initial['accepted_random_counter']['files'] | initial['accepted_linear_guard']['files']
assert set(plan['accepted_payload']) == set(accepted) and len(accepted) == 11
accepted_claims = {}
for name,pin in accepted.items():
    record = plan['accepted_payload'][name]
    assert record == {'sha256':pin,'identity':initial['installed_identities'][name]}
    assert digest(state.h.git(ROOT,ENV,'show',parent+':'+name)) == pin
    accepted_claims[name] = ownership.claim(ROOT,name,pin,record['identity'])
audit = read(ROOT/config['untracked_audit'])
assert digest((ROOT/config['untracked_audit']).read_bytes()) == config['untracked_audit_sha256']
untracked = sorted(n for n in state.h.git(ROOT,ENV,'ls-files','--others','--exclude-standard','-z').decode().split('\0') if n)
assert untracked == audit['paths'] and len(untracked) == audit['count']
project = audit['project_files']
for record in project:
    path = ROOT/record['path']
    info = path.lstat()
    assert not path.is_symlink() and path.is_file()
    assert digest(path.read_bytes()) == record['sha256'] and [info.st_dev,info.st_ino] == record['identity']
    assert info.st_size == record['bytes'] and (info.st_mode & 0o7777) == record['mode']
assert len(project) == audit['project_count'] and len(untracked)-len(project) == audit['unrelated_count']
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
    for item in accepted_claims.values():
        ownership.claim(ROOT,item["path"],item["owned_sha256"],item["identity"])
    ownership.write_owned(ROOT,claims["CURRENT-EPOCH.json"],current_bytes)
    assert state.a.verify_current(state.h, ROOT, ENV, epoch) == before
    assert all((RUNTIME/n).read_bytes() == controls[n] for n in ["ROLE.json","OWNED.json"])
    for item in accepted_claims.values():
        ownership.claim(ROOT,item["path"],item["owned_sha256"],item["identity"])
except BaseException as error:
    rollback_errors = []
    try:
        ownership.write_owned(ROOT,claims["CURRENT-EPOCH.json"],controls["CURRENT-EPOCH.json"])
    except BaseException as rollback:
        rollback_errors.append(repr(rollback))
    state.save(HERE / "SYNCHRONIZATION-FAILURE.json", {"error":repr(error),"rollback_errors":rollback_errors,"manual_recovery_required":True,"runtime_epoch_synchronized":False,"signed_head":parent,"note":"Old runtime metadata at the new signed HEAD is not certified."})
    raise
state.save(HERE / "FINAL-CHECK.json", {"head":parent,"signature_chain_verified":True,"primary_roadmap_updated":True,"roadmap_sha256":roadmap["after_sha256"],"runtime_epoch_synchronized":True,"native_dirty_paths":1,"provider_candidate_accepted":False,"accepted_fixes":142,"tracked_fixes":143,"held_excluded":120,"current_epoch_sha256":digest(current_bytes),"historical_recovery_snapshot_paths":75,"current_untracked_project_files":len(project),"current_untracked_root_files":len(untracked),"unrelated_untracked_files":audit["unrelated_count"],"accepted_payload_bodies_and_identities_verified":True,"accepted_payload_paths":sorted(accepted),"random_counter_fix_accepted":True,"line_height_fix_accepted":True,"accepted_line_height_commit":epoch["accepted_line_height"]["native_commit"],"runtime_binary_provenance":"Unchanged accepted linear-guard build restored after Round experiment; historical build metadata retained"})
print("Verified signed research checkpoint; accepted line-height, random-counter and linear-guard preserved, provider remains held",parent)
