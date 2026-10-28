import copy
import importlib.util
import json
from pathlib import Path
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
spec = importlib.util.spec_from_file_location("number_transition_test", HERE / "transition.py")
t = importlib.util.module_from_spec(spec)
spec.loader.exec_module(t)
policy = t.read(HERE / "POLICY.json")
records = []


def rejected(name, action):
    try:
        action()
    except (RuntimeError, FileExistsError):
        records.append({"name": name, "rejected": True})
    else:
        raise AssertionError(name)


head = t.source_roles(ROOT, policy["packages"]["head"]["path"])
live = t.source_roles(ROOT, policy["packages"]["live"]["path"])
pending = t.source_roles(ROOT, policy["packages"]["pending_tests"]["path"], 1, "SOURCE-ROLES.json")
restoration = t.read(ROOT / policy["runtime"] / "RESTORATION-PLAN.json")
plans = {mode: t.expected_sources(policy, mode, restoration, head, live, pending) for mode in policy["modes"]}
assert all(len(pins) == 50 for plan in plans.values() for pins in plan)
assert plans["head-candidate"][2] == plans["prototype-live"][1]
assert plans["prototype-live"][2] == plans["pending-tests"][1]
assert {n for n in plans["head-candidate"][1] if plans["head-candidate"][1][n] != plans["head-candidate"][2][n]} == set(head["candidate"])
assert {n for n in plans["pending-tests"][1] if plans["pending-tests"][1][n] != plans["pending-tests"][2][n]} == set(pending["candidate"])
t.require_enabled_mode(policy, "head-candidate")
t.require_enabled_mode(policy, "prototype-live")
t.require_enabled_mode(policy, "pending-tests")
disabled_policy = dict(policy, pending_overlay_enabled=False)
rejected("pending-overlay-disabled", lambda: t.require_enabled_mode(disabled_policy, "pending-tests"))
rejected("unknown-mode", lambda: t.expected_sources(policy, "other", restoration, head, live, pending))
drifted = copy.deepcopy(pending)
drifted["base"][next(iter(drifted["base"]))]["sha256"] = "bad"
rejected("pending-overlay-base-drift", lambda: t.expected_sources(policy, "pending-tests", restoration, head, live, drifted))

with tempfile.TemporaryDirectory(prefix="number-transition-controls-", dir="/private/tmp") as temporary:
    root = Path(temporary)
    source = root / "source"
    source.write_bytes(b"original")
    owner = t.claim(root, "source", t.digest(b"original"))
    identity = owner["identity"][:]
    t.write_owned(root, owner, b"candidate")
    assert source.read_bytes() == b"candidate" and owner["identity"] == identity
    assert owner["owned_sha256"] == t.digest(b"candidate")
    t.write_owned(root, owner, b"original")
    assert source.read_bytes() == b"original" and owner["identity"] == identity
    rejected("stale-source-hash", lambda: t.claim(root, "source", t.digest(b"candidate"), identity))
    rejected("stale-source-inode", lambda: t.claim(root, "source", t.digest(b"original"), [0, 0]))
    link = root / "link"
    link.symlink_to(source)
    rejected("symlink-file", lambda: t.claim(root, "link", t.digest(b"original")))
    (root / "real").mkdir()
    (root / "real" / "item").write_bytes(b"item")
    (root / "linked-parent").symlink_to(root / "real", target_is_directory=True)
    rejected("symlink-parent", lambda: t.claim(root, "linked-parent/item", t.digest(b"item")))
    rejected("directory-in-place-of-file", lambda: t.claim(root, "real", t.digest(b"")))
    rejected("escape-path", lambda: t.claim(root, "../escaped", t.digest(b"")))
    rejected("absolute-path", lambda: t.claim(root, str(source), t.digest(b"original")))
    (root / "other").write_bytes(b"original")
    (root / "other").replace(source)
    rejected("same-byte-replacement", lambda: t.write_owned(root, owner, b"candidate"))
    assert source.read_bytes() == b"original"
    runtime = root / "runtime"
    runtime.mkdir()
    active = runtime / "active-build"
    active.mkdir()
    t.save(active / "COMMAND.json", {})
    rejected("unfinished-command", lambda: t.quiescent(runtime))
    t.save(active / "RESULT.json", {})
    t.quiescent(runtime)
    evidence = root / "wpt"
    evidence.mkdir()
    epoch = {"semantic_index": {"head": policy["paired_head"]}}
    epoch_sha = t.digest(t.encoded(epoch))
    phase = "original-1"
    result = {"phase": phase, "execution_error": None, "preservation_error": None,
              "observation_gate_passed": True, "comparison_gate_passed": False}
    assessment = {"phase": phase, "complete": True, "execution_preserved": True,
                  "capsule_manifest_sha256": policy["packages"]["wpt"]["manifest_sha256"],
                  "epoch_sha256": epoch_sha, "run_binding": {"revision": policy["paired_head"]},
                  "native_sources": {n: v["sha256"] for n, v in head["base"].items()}}
    command = {"phase": phase, "wrapper_manifest_sha256": assessment["capsule_manifest_sha256"],
               "epoch_sha256": epoch_sha}
    def publish(r=result, a=assessment, c=command, e=epoch):
        for name, value in [("RESULT", r), ("ASSESSMENT", a), ("COMMAND", c), ("EPOCH", e)]:
            (evidence / (name + ".json")).write_bytes(t.encoded(value))
        return t.sha(evidence / "RESULT.json")
    result_sha = publish()
    t.verify_wpt(policy, "head-candidate", evidence, result_sha, epoch, epoch_sha, head)
    rejected("external-result-hash", lambda: t.verify_wpt(policy, "head-candidate", evidence, "bad", epoch, epoch_sha, head))
    rejected("external-epoch-hash", lambda: t.verify_wpt(policy, "head-candidate", evidence, result_sha, epoch, "bad", head))
    for name, field, value in [("incomplete-observation", "complete", False),
                               ("unpreserved-execution", "execution_preserved", False),
                               ("wrong-phase", "phase", "original-2"),
                               ("wrong-capsule", "capsule_manifest_sha256", "bad"),
                               ("wrong-sources", "native_sources", {})]:
        changed = copy.deepcopy(assessment)
        changed[field] = value
        result_sha = publish(a=changed)
        rejected(name, lambda: t.verify_wpt(policy, "head-candidate", evidence, result_sha, epoch, epoch_sha, head))
    changed = copy.deepcopy(assessment)
    changed["run_binding"]["revision"] = policy["captured_native_head"]
    result_sha = publish(a=changed)
    rejected("old-native-capture-head-not-paired-head", lambda: t.verify_wpt(policy, "head-candidate", evidence, result_sha, epoch, epoch_sha, head))
    failed = dict(result, phase="candidate-1", observation_gate_passed=False)
    candidate = dict(assessment, phase="candidate-1", native_sources={n: v["sha256"] for n, v in head["candidate"].items()})
    candidate_command = dict(command, phase="candidate-1")
    result_sha = publish(r=failed, a=candidate, c=candidate_command)
    t.verify_wpt(policy, "prototype-live", evidence, result_sha, epoch, epoch_sha, head)
assert not root.exists()
print(json.dumps({"status": "OWNED_SCRATCH_CONTROLS_PASS", "negative_controls": records,
                  "planned_modes": list(plans), "owned_source_paths_each": 50,
                  "head_candidate_changes": 2, "pending_overlay_changes": 1,
                  "same_inode_write_and_rollback": True, "failed_but_preserved_candidate_restorable": True,
                  "scratch_removed": True, "live_source_or_runtime_mutation": False,
                  "live_git_index_or_binary_query": False, "actual_transition_executed": False}, indent=2))
