import sys

if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise SystemExit("Use python3 -I -S -B without optimization")
sys.dont_write_bytecode = True

import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import signal
import stat

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def need(value, message):
    if not value:
        raise RuntimeError(message)


def sha(path):
    need(stat.S_ISREG(path.lstat().st_mode), "regular file: " + str(path))
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def parent_pins(root, path):
    need(path.is_relative_to(root), "path inside checkout")
    result = {}
    cursor = path.parent
    while True:
        info = cursor.lstat()
        need(stat.S_ISDIR(info.st_mode), "regular parent directory: " + str(cursor))
        result[str(cursor)] = [info.st_dev, info.st_ino]
        if cursor == root:
            return result
        cursor = cursor.parent


def create_owned(helper, root, name, parents):
    path = root / name
    need(parent_pins(root, path) == parents, "parent identities")
    fd = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        info = os.fstat(fd)
        need([info.st_dev, info.st_ino] == parents[str(path.parent)], "opened parent")
        target = os.open(path.name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o644, dir_fd=fd)
        try:
            os.fchmod(target, 0o644)
            info = os.fstat(target)
            identity = [info.st_dev, info.st_ino]
        finally:
            os.close(target)
    finally:
        os.close(fd)
    return {"path": name, "identity": identity, "owned_sha256": hashlib.sha256(b"").hexdigest()}


def updated_epoch(epoch, name, item, digest):
    need(name not in epoch["pins"] and name not in epoch["installed_identities"], "new WPT epoch entry")
    result = copy.deepcopy(epoch)
    result["pins"][name] = digest
    result["installed_identities"][name] = item["identity"]
    result["counts"]["roles"] = len(result["pins"])
    result["counts"]["installed_identities"] = len(result["installed_identities"])
    return result


def main():
    need(len(sys.argv) == 5, "Usage: install.py MANIFEST_SHA EPOCH_SHA RESULT_SHA ABSENT_OUTPUT")
    need(sha(HERE / "FILES.json") == sys.argv[1], "installer manifest")
    for name, pin in json.loads((HERE / "FILES.json").read_text()).items():
        need(Path(name).name == name and sha(HERE / name) == pin, "installer payload")
    policy = json.loads((HERE / "POLICY.json").read_text())
    need(policy["execution_enabled"], "installation held: candidate zoom regression unresolved")
    for name, pin in policy["references"].items():
        need(sha(ROOT / name) == pin, "helper input: " + name)
    h = load("wpt_install_ownership", ROOT / policy["ownership_helper"])
    runtime = ROOT / policy["runtime"]
    state = h.load_state(runtime)
    env = dict(os.environ, GIT_OPTIONAL_LOCKS="0", PYTHONDONTWRITEBYTECODE="1")
    need(all(not os.environ.get(n) for n in policy["forbidden_environment"]), "unexpected environment")
    epoch_path = runtime / "CURRENT-EPOCH.json"
    epoch_bytes = h.body(epoch_path)
    need(h.digest(epoch_bytes) == sys.argv[2] == policy["epoch_sha256"], "frozen epoch")
    epoch = json.loads(epoch_bytes)
    need(epoch["semantic_index"]["head"] == policy["head"], "frozen HEAD")
    need(epoch["registered_number_transition"] == policy["transition"], "compiled unaccepted candidate")
    h.authenticate(ROOT / policy["capsule"], policy["capsule_manifest_sha256"])
    h.authenticate(ROOT / policy["fixture"], policy["fixture_manifest_sha256"])
    evidence = ROOT / policy["evidence"]
    need(sha(evidence / "RESULT.json") == sys.argv[3] == policy["result_sha256"], "external comparison result")
    need(sha(evidence / "ASSESSMENT.json") == policy["assessment_sha256"], "comparison assessment")
    result, assessment = h.read(evidence / "RESULT.json"), h.read(evidence / "ASSESSMENT.json")
    need(result["comparison_gate_passed"] and result["execution_error"] is None and result["preservation_error"] is None, "comparison passed")
    need(assessment["complete"] and assessment["execution_preserved"] and assessment["comparison_gate_passed"], "complete comparison")
    need(assessment["epoch_sha256"] == sys.argv[2] and h.read(evidence / "EPOCH.json") == epoch, "tested epoch")
    need(assessment["native_sources"] == policy["native_sources"] and assessment["capsule_manifest_sha256"] == policy["capsule_manifest_sha256"], "tested roles and capsule")
    need(h.read(evidence / "CLEANUP.json")["owned_group_absent"] and h.read(evidence / "CLEANUP.json")["temporary_root_removed"], "browser cleanup")
    h.group_absent(h.read(evidence / "PROCESS.json")["pgid"])
    name, wanted = policy["wpt_path"], policy["wpt_sha256"]
    path = ROOT / name
    for captured in policy["tested_copies"]:
        need(sha(ROOT / captured) == wanted, "exact tested WPT copy")
    data = h.body(ROOT / policy["tested_copies"][0])
    need(not os.path.lexists(path), "WPT destination absent")
    need(not state.h.git(ROOT, env, "ls-files", "--", name), "WPT absent from index")
    need(not state.h.git(ROOT, env, "ls-tree", "HEAD", "--", name), "WPT absent from HEAD")
    parents = parent_pins(ROOT, path)
    before = state.a.verify_current(state.h, ROOT, env, epoch)
    flags = {n: state.h.git(ROOT / n, env, "ls-files", "-v", "-z") for n in [".", "artifacts/css-spec-lean"]}
    controls = {n: h.body(runtime / n) for n in ["OWNED.json", "ROLE.json"]}
    restoration = h.read(runtime / "RESTORATION-PLAN.json")
    need(len(restoration["paths"]) == 50, "50 parked prototypes")

    def preserve():
        for n, pin in restoration["paths"].items():
            need(sha(runtime / "prototype-original" / n) == pin["prototype_original"], "parked prototype: " + n)
        need(all(h.body(runtime / n) == value for n, value in controls.items()), "unchanged runtime role/ownership")
        need(all(state.h.git(ROOT / n, env, "ls-files", "-v", "-z") == value for n, value in flags.items()), "root/nested index flags")
        need(parent_pins(ROOT, path) == parents, "unchanged parent identities")

    preserve()
    out = Path(sys.argv[4])
    need(out.is_absolute() and out.parent == ROOT / "artifacts" and out.name.startswith("css-registered-admission-wpt-install-runtime-"), "owned output path")
    need(not os.path.lexists(out), "output absent")
    out.mkdir()
    h.save(out / "PRE-EPOCH.json", epoch)
    h.save(out / "PRE.json", before)
    h.save(out / "PARENTS.json", parents)
    for n, value in controls.items():
        (out / ("PRE-" + n)).write_bytes(value)
    epoch_owner = h.claim(ROOT, str(epoch_path.relative_to(ROOT)), sys.argv[2])
    lock = runtime / "SOURCE-TRANSITION.lock"
    lock_owner = create_owned(h, ROOT, str(lock.relative_to(ROOT)), parent_pins(ROOT, lock))
    owned = None
    try:
        need(state.a.verify_current(state.h, ROOT, env, epoch) == before, "pre-write preservation")
        preserve()
        h.claim(ROOT, epoch_owner["path"], sys.argv[2], epoch_owner["identity"])
        owned = create_owned(h, ROOT, name, parents)
        h.write_owned(ROOT, owned, data)
        current = updated_epoch(epoch, name, owned, wanted)
        need(state.a.verify_current(state.h, ROOT, env, current) == before, "post-install index preservation")
        preserve()
        h.write_owned(ROOT, epoch_owner, h.encoded(current))
        need(state.a.verify_current(state.h, ROOT, env, h.read(epoch_path)) == before, "published epoch preservation")
        preserve()
        h.save(out / "EPOCH.json", current)
        h.save(out / "OWNERSHIP.json", owned)
        h.save(out / "POST.json", before)
        h.save(out / "RESULT.json", {"completed": True, "preservation_verified": True, "epoch_sha256": sha(epoch_path), "installed_path": name, "installed_sha256": wanted, "identity": owned["identity"], "mode": "100644", "accepted": False, "lint_required": True, "comparison_result_sha256": sys.argv[3]})
    except BaseException as error:
        failures = []
        try:
            if owned is not None:
                h.claim(ROOT, name, owned["owned_sha256"], owned["identity"])
                path.unlink()
            h.write_owned(ROOT, epoch_owner, epoch_bytes)
            need(state.a.verify_current(state.h, ROOT, env, epoch) == before, "rollback snapshot")
            preserve()
        except BaseException as rollback:
            failures.append(repr(rollback))
        h.save(out / "FAILURE.json", {"error": repr(error), "rollback_errors": failures, "manual_recovery_required": bool(failures), "owned_wpt": owned, "owned_epoch": epoch_owner})
        raise
    finally:
        h.claim(ROOT, lock_owner["path"], lock_owner["owned_sha256"], lock_owner["identity"])
        lock.unlink()


if __name__ == "__main__":
    def interrupted(signum, frame):
        raise RuntimeError("interrupted: " + str(signum))
    signal.signal(signal.SIGINT, interrupted)
    signal.signal(signal.SIGTERM, interrupted)
    main()
