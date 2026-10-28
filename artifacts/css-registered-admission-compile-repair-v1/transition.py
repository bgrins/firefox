import sys

if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise SystemExit("Require python3 -I -S -B without optimization")
sys.dont_write_bytecode = True

import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import signal
import stat

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def need(condition, message):
    if not condition:
        raise RuntimeError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def regular(path):
    info = path.lstat()
    need(stat.S_ISREG(info.st_mode), "not a regular file: " + str(path))
    return info


def body(path):
    regular(path)
    return path.read_bytes()


def sha(path):
    return digest(body(path))


def read(path):
    return json.loads(body(path))


def encoded(value):
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()


def save(path, value):
    with path.open("xb") as stream:
        stream.write(encoded(value))


def relative(name):
    path = Path(name)
    need(not path.is_absolute() and name and ".." not in path.parts, "unsafe relative path")
    return path


def authenticate(directory, expected):
    need(sha(directory / "FILES.json") == expected, "manifest digest: " + str(directory))
    manifest = read(directory / "FILES.json")
    entries = manifest.get("files", manifest)
    for name, item in entries.items():
        path = directory / relative(name)
        wanted = item["sha256"] if isinstance(item, dict) else item
        need(sha(path) == wanted, "payload: " + name)
    return entries


def claim(root, name, expected, identity=None):
    path = root / relative(name)
    cursor = path.parent
    while cursor != root:
        need(not cursor.is_symlink(), "symlink source parent: " + str(cursor))
        cursor = cursor.parent
    info = regular(path)
    actual_identity = [info.st_dev, info.st_ino]
    need(identity is None or identity == actual_identity, "owned identity: " + name)
    need(sha(path) == expected, "owned preimage: " + name)
    return {"path": name, "identity": actual_identity, "owned_sha256": expected}


def write_owned(root, item, data):
    claim(root, item["path"], item["owned_sha256"], item["identity"])
    path = root / item["path"]
    fd = os.open(path, os.O_RDWR | os.O_NOFOLLOW)
    with os.fdopen(fd, "r+b", buffering=0) as stream:
        info = os.fstat(stream.fileno())
        need(stat.S_ISREG(info.st_mode) and [info.st_dev, info.st_ino] == item["identity"],
             "opened owned identity")
        need(digest(stream.read()) == item["owned_sha256"], "opened owned bytes")
        stream.seek(0)
        stream.truncate(0)
        item["owned_sha256"] = digest(b"")
        try:
            written = stream.write(data)
            item["owned_sha256"] = digest(data[:written])
            need(written == len(data), "complete owned write")
            os.fsync(stream.fileno())
        except BaseException:
            stream.seek(0)
            observed = stream.read()
            if data.startswith(observed):
                item["owned_sha256"] = digest(observed)
            raise
    need(sha(path) == item["owned_sha256"], "owned postimage")


def group_absent(pgid):
    need(isinstance(pgid, int) and pgid > 1, "valid owned process group")
    try:
        os.killpg(pgid, 0)
    except ProcessLookupError:
        return
    raise RuntimeError("owned process group still exists: " + str(pgid))


def quiescent(runtime, role=None, wpt=None):
    for directory in runtime.iterdir():
        if directory.is_dir() and (directory / "COMMAND.json").exists():
            need((directory / "RESULT.json").is_file(), "unfinished runtime command: " + directory.name)
    if role is None:
        return
    label = role.get("last_build", "")
    need(bool(re.fullmatch(r"[a-z0-9-]+", label)), "last build label")
    build = runtime / label
    result = read(build / "RESULT.json")
    need(result["owned_processes"] == {} and result["preservation_verified"], "build cleanup/preservation")
    need(result["command_success"], "current role requires a completed build")
    for name in ["build-PROCESS.json", "WAKE-PROCESS.json"]:
        record = read(build / name)
        group_absent(record["pgid"])
    cleanup = read(wpt / "CLEANUP.json")
    need(cleanup.get("owned_group_absent") and cleanup.get("temporary_root_removed"), "WPT cleanup")
    group_absent(read(wpt / "PROCESS.json")["pgid"])


def source_roles(root, package, count=2, filename="COMBINED-SOURCE-ROLES.json"):
    roles = read(root / package / filename)
    need(set(roles) == {"base", "candidate"}, "source roles")
    need(set(roles["base"]) == set(roles["candidate"]) and len(roles["base"]) == count, "exact source paths")
    for items in roles.values():
        for name, pin in items.items():
            relative(name)
            need(sha(root / relative(pin["capture"])) == pin["sha256"], "source capture: " + name)
    return roles


def expected_sources(policy, mode, restoration, head_roles, live_roles, pending_roles):
    need(mode in policy["modes"], "known transition mode")
    original = {name: pin["head_original"] for name, pin in restoration["paths"].items()}
    for name, pin in head_roles["base"].items():
        need(original[name] == pin["sha256"], "head role agrees with restoration")
    head_candidate = dict(original)
    head_candidate.update({name: pin["sha256"] for name, pin in head_roles["candidate"].items()})
    prototype_candidate = {name: pin["prototype_original"] for name, pin in restoration["paths"].items()}
    prototype_candidate.update({name: pin["sha256"] for name, pin in live_roles["candidate"].items()})
    for name, pin in pending_roles["base"].items():
        need(prototype_candidate[name] == pin["sha256"], "pending test original matches preserved prototype")
    if mode == "head-candidate":
        previous = source_roles(ROOT, policy["packages"]["previous_head"]["path"])
        before = dict(original)
        before.update({name: pin["sha256"] for name, pin in previous["candidate"].items()})
        after = head_candidate
        need([name for name in before if before[name] != after[name]] ==
             ["servo/components/style/custom_properties.rs"], "exact lifetime repair path")
    elif mode == "prototype-live":
        before, after = head_candidate, prototype_candidate
    else:
        before, after = prototype_candidate, dict(prototype_candidate)
        after.update({name: pin["sha256"] for name, pin in pending_roles["candidate"].items()})
    need(set(original) == set(before) == set(after), "complete source transition inventory")
    return original, before, after


def verify_wpt(policy, mode, wpt, result_sha, epoch, epoch_sha, head_roles):
    record = read(wpt / "RESULT.json")
    need(sha(wpt / "RESULT.json") == result_sha, "external WPT result digest")
    phase_role = policy["modes"][mode]["wpt_role"]
    need(bool(re.fullmatch(phase_role + r"-[1-9][0-9]*", record["phase"])), "WPT source phase")
    need(record["execution_error"] is None and record["preservation_error"] is None, "WPT lifecycle")
    if mode == "head-candidate":
        need(record["observation_gate_passed"], "complete original WPT observation")
    assessment = read(wpt / "ASSESSMENT.json")
    command = read(wpt / "COMMAND.json")
    need(assessment["phase"] == command["phase"] == record["phase"], "single WPT phase receipt")
    manifest = policy["packages"]["wpt"]["manifest_sha256"]
    need(assessment["complete"] and assessment["execution_preserved"], "complete preserved WPT")
    need(assessment["capsule_manifest_sha256"] == command["wrapper_manifest_sha256"] == manifest,
         "sealed WPT capsule")
    need(assessment["epoch_sha256"] == command["epoch_sha256"] == epoch_sha, "WPT epoch digest")
    need(read(wpt / "EPOCH.json") == epoch, "WPT epoch content")
    need(assessment["run_binding"]["revision"] == policy["paired_head"], "fixed paired HEAD")
    sources = head_roles["base" if phase_role == "original" else "candidate"]
    need(assessment["native_sources"] == {n: v["sha256"] for n, v in sources.items()}, "WPT source roles")
    return record


def load_state(runtime):
    spec = importlib.util.spec_from_file_location("registered_number_transition_state", runtime / "state.py")
    state = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(state)
    return state


def authorized_successors(root, policy, source_pins):
    config = policy["authorized_successors"]
    names = set(config["paths"])
    need(names == {"artifacts/stylo-bloom-tools/CURRENT-COMMITS.json",
                   "artifacts/stylo-bloom-tools/PLAN-OF-RECORD.md"}, "exact authorized ledger successors")
    chain = config["checkpoints"]
    need(len(chain) == 2 and chain[-1]["head"] == policy["paired_head"], "fixed signing successor chain")
    previous = {name: source_pins[name] for name in names}
    previous_update = None
    for checkpoint in chain:
        signing = root / relative(checkpoint["signing_directory"])
        update = read(signing / "ROADMAP-UPDATE.json")
        selection = read(signing / "checkpoint-selection.json")
        receipt = read(signing / "checkpoint-receipt.json")
        final = read(signing / "FINAL-CHECK.json")
        need(set(update["before"]) == set(update["after"]) == names, "exact roadmap change inventory")
        need(update["before"] == previous, "continuous authorized ledger chain")
        if previous_update is not None:
            need(update["prior_authorized_ledger_update"] == previous_update, "explicit prior roadmap link")
        need(receipt["commit"] == final["head"] == final["commits"]["checkpoint"] == checkpoint["head"]
             and receipt["signature_verified"] and final["signatures_verified"], "signed successor checkpoint")
        need(receipt["working_bodies_and_nested_index_preserved"] and final["unfinished_prototypes_preserved"],
             "checkpoint preservation evidence")
        need(set(selection["files"]) == set(selection["source_pins"]) == set(receipt["files"]),
             "checkpoint selected receipt inventory")
        for name in checkpoint["committed_provenance"]:
            need(selection["source_pins"].get(name) == policy["references"][name] == sha(root / relative(name)),
                 "committed successor provenance: " + name)
        for name in names:
            need(update["before"][name] == sha(signing / "ledger-preimages" / Path(name).name),
                 "successor committed preimage: " + name)
            need(selection["source_pins"].get(name) == update["after"][name], "checkpoint successor pin: " + name)
        previous = update["after"]
        previous_update = checkpoint["signing_directory"] + "/ROADMAP-UPDATE.json"
    return previous


def verify_successor(name, expected, data, epoch, policy, head_data):
    pins = [epoch[key][name] for key in policy["pin_maps"] if name in epoch[key]]
    need(pins and all(pin == expected for pin in pins), "current epoch successor pin: " + name)
    need(digest(data) == expected == digest(head_data), "live/HEAD successor: " + name)



def require_enabled_mode(policy, mode):
    need(mode in policy["modes"], "transition mode")
    need(mode != "pending-tests" or policy["pending_overlay_enabled"], policy["pending_overlay_hold"])

def main():
    need(len(sys.argv) == 7, "Usage: transition.py TOOL_SHA MODE EPOCH_SHA ABS_EVIDENCE_DIR EVIDENCE_RESULT_SHA LABEL")
    tool_sha, mode, epoch_sha, evidence_name, result_sha, label = sys.argv[1:]
    authenticate(HERE, tool_sha)
    policy = read(HERE / "POLICY.json")
    require_enabled_mode(policy, mode)
    need(bool(re.fullmatch(mode + r"-[1-9][0-9]*", label)), "unique mode label")
    need(all(not os.environ.get(k) for k in policy["forbidden_env"]), "unexpected build/git environment")
    for name, pin in policy["references"].items():
        need(sha(ROOT / relative(name)) == pin, "preservation helper/restoration binding: " + name)
    for package in policy["packages"].values():
        authenticate(ROOT / package["path"], package["manifest_sha256"])
    runtime = ROOT / policy["runtime"]
    epoch_path = runtime / "CURRENT-EPOCH.json"
    need(sha(epoch_path) == epoch_sha, "external current epoch digest")
    epoch_bytes = body(epoch_path)
    epoch = json.loads(epoch_bytes)
    need(epoch["semantic_index"]["head"] == policy["paired_head"], "paired HEAD cannot advance")
    role_bytes = body(runtime / "ROLE.json")
    role = json.loads(role_bytes)
    route = policy["modes"][mode]
    transition = epoch["registered_number_transition"]
    for field, expected in [("role", route["from_role"]), ("variant", route["from_variant"])]:
        need(role[field] == transition[field] == expected, "current source role: " + field)
    need(not role["built"] and not transition["compiled"] and not transition["accepted"],
         "failed candidate must remain uncompiled and unaccepted")
    need(epoch_sha == policy["failed_epoch_sha256"], "exact failed-build epoch")
    evidence = Path(evidence_name)
    need(evidence.is_absolute() and not evidence.is_symlink(), "absolute evidence directory")
    head_roles = source_roles(ROOT, policy["packages"]["head"]["path"])
    live_roles = source_roles(ROOT, policy["packages"]["live"]["path"])
    pending_roles = source_roles(ROOT, policy["packages"]["pending_tests"]["path"], 1, "SOURCE-ROLES.json")
    for name, pin in pending_roles["base"].items():
        original_test = body(ROOT / pin["capture"])
        candidate_test = body(ROOT / pending_roles["candidate"][name]["capture"])
        ending = b"}  // namespace\n"
        need(original_test.endswith(ending) and candidate_test.startswith(original_test[:-len(ending)]),
             "pending test overlay preserves original prefix")
    if mode == "pending-tests":
        need(evidence.parent == runtime and re.fullmatch(r"prototype-live-[1-9][0-9]*", evidence.name),
             "prototype restoration evidence directory")
        need(sha(evidence / "RESULT.json") == result_sha, "external restoration receipt digest")
        wpt_result = read(evidence / "RESULT.json")
        need(wpt_result["completed"] and wpt_result["mode"] == "prototype-live" and
             wpt_result["preservation_verified"] and not wpt_result["compiled"] and
             wpt_result["epoch_sha256"] == epoch_sha, "successful uncompiled prototype restoration")
        need(read(evidence / "EPOCH.json") == epoch and role["last_transition"] == evidence.name,
             "exact restored source epoch")
        need(epoch["prototype_overlay_state"]["installed"], "prototype must be installed")
        quiescent(runtime)
    else:
        need(evidence == runtime / "head-candidate-build-1", "exact failed build")
        need(sha(evidence / "RESULT.json") == result_sha == policy["failed_result_sha256"], "failed build result")
        failed = read(evidence / "RESULT.json")
        need(not failed["command_success"] and failed["preservation_verified"] and
             failed["owned_processes"] == {} and not failed["publication_errors"], "preserved failed build")
        need(read(evidence / "EPOCH.json") == epoch and role["last_build"] == evidence.name and
             transition["last_phase"] == evidence.name, "failed build source epoch")
        for directory, files in policy["terminal_processes"].items():
            for name in files:
                group_absent(read(ROOT / directory / name)["pgid"])
        wpt_result = {"comparison_gate_passed": False, "failed_build_evidence": str(evidence)}
        quiescent(runtime)
    restoration = read(runtime / "RESTORATION-PLAN.json")
    need(restoration["head"] == policy["captured_native_head"], "restoration provenance")
    head_pins, prior_pins, next_pins = expected_sources(policy, mode, restoration, head_roles, live_roles, pending_roles)
    owned_bytes = body(runtime / "OWNED.json")
    existing_owned = json.loads(owned_bytes)
    expected_owned = set(restoration["paths"])
    need(set(existing_owned) == expected_owned, "current ownership inventory")
    state = load_state(runtime)
    env = dict(os.environ, GIT_OPTIONAL_LOCKS="0", PYTHONDONTWRITEBYTECODE="1")
    before = state.a.verify_current(state.h, ROOT, env, epoch)
    flags = {n: state.h.git(ROOT / n, env, "ls-files", "-v", "-z") for n in [".", "artifacts/css-spec-lean"]}
    collector_roles = read(ROOT / "artifacts/css-registered-value-collector-proposal-v1/SOURCE-ROLES.json")
    need(policy["unchanged_native_sources"] == {name: pin["original"] for name, pin in collector_roles.items()}
         and len(collector_roles) == 6, "exact unchanged collector source roles")
    unchanged = {}
    for name, expected in policy["unchanged_native_sources"].items():
        need(name not in prior_pins, "unchanged source is not an owned mutation path")
        need(digest(state.h.git(ROOT, env, "show", "HEAD:" + name)) == expected, "unchanged HEAD source")
        unchanged[name] = claim(ROOT, name, expected)
    native_owned, originals, desired = {}, {}, {}
    for name, expected in prior_pins.items():
        need(epoch["pins"].get(name) == expected, "current source epoch pin: " + name)
        need(digest(state.h.git(ROOT, env, "show", "HEAD:" + name)) == head_pins[name], "native HEAD unchanged: " + name)
        old = existing_owned.get(name)
        if old:
            need(old["path"] == name and old["owned_sha256"] == expected, "current owner must match current role: " + name)
        native_owned[name] = claim(ROOT, name, expected, old["identity"] if old else None)
        if name in epoch["installed_identities"]:
            need(native_owned[name]["identity"] == epoch["installed_identities"][name], "epoch source identity")
        originals[name] = body(ROOT / name)
        if name in restoration["paths"]:
            need(sha(runtime / "prototype-original" / name) == restoration["paths"][name]["prototype_original"], "preserved prototype: " + name)
        if mode == "prototype-live" and name in restoration["paths"]:
            desired[name] = body(runtime / "prototype-original" / name)
        else:
            desired[name] = originals[name]
    replacement = (head_roles if mode == "head-candidate" else
                   live_roles if mode == "prototype-live" else pending_roles)["candidate"]
    for name, pin in replacement.items():
        desired[name] = body(ROOT / pin["capture"])
    need({n: digest(v) for n, v in desired.items()} == next_pins, "all desired bodies authenticated")
    snapshot = ROOT / policy["packages"]["snapshot"]["path"]
    source_pins = read(snapshot / "SOURCE-PINS.json")
    need(len(source_pins) == 140, "complete v8 recovery inventory")
    successors = authorized_successors(ROOT, policy, source_pins)
    for checkpoint in policy["authorized_successors"]["checkpoints"]:
        for name in checkpoint["committed_provenance"]:
            need(digest(state.h.git(ROOT, env, "show", "HEAD:" + name)) == policy["references"][name],
                 "HEAD successor provenance: " + name)
    for name, pin in source_pins.items():
        source = runtime / "prototype-original" / name if name in restoration["paths"] else ROOT / name
        if name in successors:
            verify_successor(name, successors[name], body(source), epoch, policy,
                             state.h.git(ROOT, env, "show", "HEAD:" + name))
        else:
            need(sha(source) == pin, "preserved unfinished source: " + name)
    prior_modified = sorted(n for n in prior_pins if prior_pins[n] != head_pins[n])
    need(epoch["modified_native_paths"] == prior_modified, "only expected native modifications")
    controls = [runtime / "OWNED.json", runtime / "ROLE.json", epoch_path]
    control_owned, control_bytes = {}, {}
    for path, expected_bytes in zip(controls, [owned_bytes, role_bytes, epoch_bytes]):
        name = str(path.relative_to(ROOT))
        need(all(name not in epoch[key] for key in policy["pin_maps"]), "mutable runtime control unexpectedly pinned")
        control_bytes[name] = body(path)
        need(control_bytes[name] == expected_bytes, "runtime control changed during preflight")
        control_owned[name] = claim(ROOT, name, digest(control_bytes[name]))
    out = runtime / label
    need(not out.exists() and not out.is_symlink(), "output must be absent")
    lock = runtime / "SOURCE-TRANSITION.lock"
    with lock.open("x") as stream:
        stream.write(json.dumps({"pid": os.getpid(), "mode": mode, "epoch_sha256": epoch_sha}) + "\n")
    lock_identity = [lock.stat().st_dev, lock.stat().st_ino]
    touched, changed_controls = [], []
    try:
        out.mkdir()
        save(out / "PRE.json", before)
        save(out / "UNCHANGED-SOURCES.json", unchanged)
        save(out / "PRE-OWNED.json", existing_owned)
        save(out / "PRE-ROLE.json", role)
        save(out / "PRE-EPOCH.json", epoch)
        save(out / "PLAN.json", {"mode": mode, "epoch_sha256": epoch_sha, "tool_manifest_sha256": tool_sha,
                                  "paired_head": policy["paired_head"], "evidence_result": str(evidence / "RESULT.json"),
                                  "evidence_result_sha256": result_sha, "before": prior_pins, "after": next_pins})
        quiescent(runtime)
        for directory, files in policy["terminal_processes"].items():
            for name in files:
                group_absent(read(ROOT / directory / name)["pgid"])
        need(sha(epoch_path) == epoch_sha, "epoch changed before owned writes")
        need(sha(evidence / "RESULT.json") == result_sha, "evidence changed before owned writes")
        for name, item in control_owned.items():
            claim(ROOT, name, digest(control_bytes[name]), item["identity"])
        need(state.a.verify_current(state.h, ROOT, env, epoch) == before, "preservation changed before owned writes")
        for name, item in unchanged.items():
            claim(ROOT, name, item["owned_sha256"], item["identity"])
        for name in sorted(native_owned):
            if prior_pins[name] == next_pins[name]:
                continue
            touched.append(name)
            write_owned(ROOT, native_owned[name], desired[name])
            save(out / ("SOURCE-WRITE-" + str(len(touched)) + ".json"), native_owned[name])
        current = copy.deepcopy(epoch)
        for name, item in native_owned.items():
            for key in policy["pin_maps"]:
                if name in current[key]:
                    current[key][name] = next_pins[name]
            current["installed_identities"][name] = item["identity"]
        index = state.h.index_state(ROOT, env)
        semantic = state.h.semantic_index(index)
        for key in ["head", "entries", "cached_diff"]:
            need(semantic[key] == epoch["semantic_index"][key], "semantic index changed: " + key)
        current["semantic_index"] = semantic
        current["raw_index_observation"]["current"] = index["raw_index"]
        modified = sorted(n for n in state.h.git(ROOT, env, "diff", "--name-only").decode().splitlines() if not n.startswith("artifacts/"))
        need(modified == sorted(n for n in next_pins if next_pins[n] != head_pins[n]), "exact post-transition native diff")
        current["modified_native_paths"] = modified
        current["counts"]["native_modified_paths"] = len(modified)
        current["counts"]["installed_identities"] = len(current["installed_identities"])
        current["registered_number_transition"] = {"role": route["to_role"], "variant": route["to_variant"],
            "compiled": False, "accepted": False, "last_transition": label, "paired_head": policy["paired_head"]}
        current["prototype_overlay_state"] = {"installed": mode != "head-candidate",
            "preserved_epoch": policy["runtime"] + "/INITIAL-EPOCH.json",
            "scope": "Full preserved prototype plus live number candidate; build required" if mode != "head-candidate" else
                     "Committed-HEAD number candidate; all prototype bodies remain parked"}
        current["registered_number_transition"]["pending_gtest_overlay_installed"] = mode == "pending-tests"
        after = state.a.verify_current(state.h, ROOT, env, current)
        need(all(state.h.git(ROOT / n, env, "ls-files", "-v", "-z") == value for n, value in flags.items()), "root/nested index flags")
        need(after["nested_index"] == before["nested_index"], "nested index unchanged")
        for name, item in unchanged.items():
            claim(ROOT, name, item["owned_sha256"], item["identity"])
        save(out / "POST.json", after)
        save(out / "EPOCH.json", current)
        new_role = {"role": route["to_role"], "variant": route["to_variant"], "built": False,
                    "last_transition": label, "paired_head": policy["paired_head"],
                    "pending_gtest_overlay_installed": mode == "pending-tests"}
        updates = [encoded(native_owned), encoded(new_role), encoded(current)]
        for path, data in zip(controls, updates):
            name = str(path.relative_to(ROOT))
            changed_controls.append(name)
            write_owned(ROOT, control_owned[name], data)
        need(state.a.verify_current(state.h, ROOT, env, current) == after, "final preservation")
        for name, item in unchanged.items():
            claim(ROOT, name, item["owned_sha256"], item["identity"])
        save(out / "RESULT.json", {"completed": True, "mode": mode, "written_sources": touched,
            "owned_source_paths": len(native_owned), "epoch_sha256": sha(epoch_path), "compiled": False,
            "accepted": False, "wpt_comparison_gate": wpt_result.get("comparison_gate_passed", wpt_result.get("wpt_comparison_gate")), "preservation_verified": True})
        print((out / "RESULT.json").read_text(), flush=True)
    except BaseException as error:
        rollback_errors = []
        for name in reversed(changed_controls):
            try:
                write_owned(ROOT, control_owned[name], control_bytes[name])
            except BaseException as exc:
                rollback_errors.append(name + ": " + repr(exc))
        for name in reversed(touched):
            try:
                write_owned(ROOT, native_owned[name], originals[name])
            except BaseException as exc:
                rollback_errors.append(name + ": " + repr(exc))
        try:
            need(state.a.verify_current(state.h, ROOT, env, epoch) == before, "restored preservation snapshot")
            for name, item in unchanged.items():
                claim(ROOT, name, item["owned_sha256"], item["identity"])
            need(all(state.h.git(ROOT / n, env, "ls-files", "-v", "-z") == value for n, value in flags.items()),
                 "restored root/nested index flags")
        except BaseException as exc:
            rollback_errors.append("restored epoch: " + repr(exc))
        if out.exists():
            save(out / "FAILURE.json", {"error": repr(error), "rollback_errors": rollback_errors,
                "owned_sources": native_owned, "owned_controls": control_owned,
                "manual_recovery_required": bool(rollback_errors)})
        raise
    finally:
        info = regular(lock)
        need([info.st_dev, info.st_ino] == lock_identity, "transition lock identity")
        lock.unlink()


if __name__ == "__main__":
    def interrupted(signum, frame):
        raise RuntimeError("transition interrupted by signal " + str(signum))
    signal.signal(signal.SIGTERM, interrupted)
    signal.signal(signal.SIGINT, interrupted)
    main()
