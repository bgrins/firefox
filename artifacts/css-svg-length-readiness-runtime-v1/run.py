import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise SystemExit("Require python3 -I -S without optimization")
sys.dont_write_bytecode = True
import hashlib
import importlib.util
import json
from pathlib import Path
import stat

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def need(ok, why):
    if not ok:
        raise RuntimeError(why)


def read(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def authenticate(mapping, base):
    for name, digest in mapping.items():
        need(not Path(name).is_absolute() and ".." not in Path(name).parts, "unsafe pin")
        path = base / name
        need(stat.S_ISREG(path.lstat().st_mode) and sha(path) == digest, "pin " + name)


need(len(sys.argv) == 2 and sha(HERE / "DRAFT-FILES.json") == sys.argv[1], "draft seal")
draft, refs, settings = read(HERE / "DRAFT-FILES.json"), read(HERE / "REFERENCES.json"), read(HERE / "CONFIG.json")
authenticate(draft, HERE)
authenticate(refs, ROOT)
need(settings["ready_for_execution"] is True, "disabled draft")
need(all(isinstance(settings[n], str) and settings[n] for n in ("epoch", "epoch_manifest_sha256", "root_receipt_sha256")), "unbound epoch")
need(not any((HERE / n).exists() or (HERE / n).is_symlink() for n in
             ("STATE.json", "BEFORE.json", "FINAL.json", "SUMMARY.json", "PRIOR-EXPERIMENT.json", "capture")), "already started")
proposal = ROOT / settings["proposal"]
authenticate(read(proposal / "FILES.json"), proposal)
need((HERE / "probe.html").read_bytes() == (proposal / "probe.html").read_bytes(), "exact sealed fixture")
epoch = ROOT / settings["epoch"]
need(sha(epoch / "FILES.json") == settings["epoch_manifest_sha256"], "actual comparison seal")
authenticate(read(epoch / "FILES.json"), epoch)
need(sha(epoch / "ROOT-FINAL-CHECK.json") == settings["root_receipt_sha256"], "actual root receipt")
prior_state, receipt = read(epoch / "STATE.json"), read(epoch / "ROOT-FINAL-CHECK.json")
expected, pins, c = read(epoch / "FINAL.json"), read(epoch / "FINAL-PINS.json"), read(epoch / "CONFIG.json")
need(prior_state["status"] == "terminal" and prior_state["restored"] is True
     and prior_state["restore_build_exit"] == 0 and prior_state["recovery_errors"] == [], "successful restoration required")
need(expected == read(epoch / "BEFORE.json") and receipt["status"] == "RESTORED_VERIFIED"
     and (receipt["exit"] == 0 or (receipt["exit"] == 1 and "failure" in prior_state))
     and receipt["state_sha256"] == sha(epoch / "STATE.json")
     and receipt["final_sha256"] == sha(epoch / "FINAL.json")
     and receipt["restored_binary_pins"] == prior_state["restored_binary_pins"], "restoration/source/binary receipt join")
need(pins == {**read(epoch / "RESOURCES.json"), **expected["sources"], **prior_state["restored_binary_pins"]}, "complete restored roles")
need(len(expected["sources"]) == receipt["source_count"] == 50 and len(pins) == receipt["pin_count"] == 355
     and len(c["modified_native_paths"]) == receipt["native_modified_paths_preserved"] == 26
     and receipt["staged_paths_preserved"] == 925 and receipt["installed112_source_and_test_ownership_preserved"] is True
     and receipt["all_owned_process_groups_cleaned"] is True and receipt["both_availability_profiles_removed"] is True,
     "restored comparison roles/ownership")
previous = ROOT / c["epoch"]
need(sha(previous / "FILES.json") == c["epoch_manifest_sha256"], "previous installed trace epoch")
authenticate(read(previous / "FILES.json"), previous)
adapter = load("length_prior_adapter", ROOT / settings["prior_epoch_adapter"])
old, _, _, installed_tests = adapter.bind(ROOT, previous, read, sha, authenticate, load)
need(all(expected[k] == old[k] for k in ("head", "index_diff_sha256", "index_entries_sha256", "native_diff_sha256"))
     and all(expected["sources"][n] == h for n, h in old["sources"].items()), "installed working source join")
source_inputs = read(proposal / "SOURCE-PINS.json")
for name, item in source_inputs.items():
    need(name not in pins or pins[name] == item["sha256"], "length source conflicts with restored roles")
    pins[name] = item["sha256"]
c["guard_sources"] = sorted(expected["sources"])
c["must_be_absent"] = sorted(set(c["must_be_absent"]) | set(c["install"]))
c["install"] = {}
wpt = load("length_wpt", ROOT / settings["helpers"] / "run_wpt.py")
bindings = load("length_bindings", ROOT / settings["helpers"] / "bindings.py")
capture = load("length_capture", ROOT / settings["capture"])
cleanup = load("length_cleanup", ROOT / settings["cleanup"])
validator = load("length_validator", HERE / "validate.py")
wpt.HERE, wpt.CONFIG = HERE, c
for name in ("MOZ_ANCESTOR_CANCELLATION_TRACE", "MOZ_NESTED_EDGE_TRACE"):
    wpt.ENV.pop(name, None)


def verify():
    authenticate(draft, HERE)
    authenticate(refs, ROOT)
    need(wpt.snapshot() == expected and wpt.pins(list(pins)) == pins, "source/index/resource/binary drift")
    need([n for n in wpt.git("diff", "--name-only").decode().splitlines() if not n.startswith("artifacts/")]
         == c["modified_native_paths"], "native roster")
    need(not wpt.git("ls-files", "--others", "--exclude-standard", "--", "layout", "dom", "servo", "mfbt").strip(), "untracked native")
    need(all(not (ROOT / n).exists() and not (ROOT / n).is_symlink() for n in c["must_be_absent"]), "temporary input remains")
    need(wpt.pins(c["existing_tests"]) == c["existing_test_pins"]
         and wpt.git("ls-files", "--", *c["existing_tests"]).decode().splitlines() == c["tracked_existing_tests"], "existing test ownership/bytes")
    for name, item in installed_tests.items():
        s = (ROOT / name).lstat()
        need(stat.S_ISREG(s.st_mode) and [s.st_dev, s.st_ino] == item["identity"]
             and sha(ROOT / name) == item["sha256"], "installed112 inode/hash")
    need(not wpt.git("ls-files", "--", *installed_tests).strip(), "installed112 became tracked")


verify()
bindings.index_state(wpt)
wpt.save("BEFORE.json", {"snapshot": expected, "pins": pins})
wpt.save("PRIOR-EXPERIMENT.json", {"epoch": settings["epoch"], "state": prior_state, "root_receipt": receipt,
                                 "restored_build_used": True, "candidate_acceptance_required": False})
state = {"status": "starting", "complete": False, "preserved": False, "native_changes": False,
         "source_role": "restored mixed working tree after SVG comparison; not normalized HEAD or SVG candidate",
         "prior_experiment_failed": "failure" in prior_state, "prior_candidate_accepted": prior_state.get("accepted_native_repair", False)}
wpt.save("STATE.json", state)
try:
    result = capture.capture(HERE, ROOT, wpt, cleanup, "capture", (HERE / "probe.html").read_bytes(), verify, pins)
    need(result["status"] == "terminal" and len(result["observations"]) == 1
         and result["process_cleanup"]["terminal"] and result["process_cleanup"]["noLiveGroup"]
         and result["profile_removed"] and not result["cleanup_errors"]
         and result["before"] == result["after"] == pins, "capture/cleanup roles")
    summary = validator.validate(result["observations"][0])
    wpt.save("SUMMARY.json", summary)
    need(summary["calibrated"] == summary["stable"] == 6 and summary["getter_controls_pass"] == 2,
         "six calibrated/stable rows and getter controls required")
    state.update(complete=True, calibrated=6, stable=6, getter_controls_pass=2, counts=summary["counts"])
except BaseException as error:
    state["failure"] = {"type": type(error).__name__, "message": str(error)}
finally:
    try:
        verify()
        bindings.index_state(wpt)
        wpt.save("FINAL.json", {"snapshot": wpt.snapshot(), "pins": wpt.pins(list(pins))})
        state["preserved"] = True
    except BaseException as error:
        state["preservation_failure"] = repr(error)
    state["status"] = "terminal"
    wpt.save("STATE.json", state)
print(json.dumps(state, indent=2))
if not state["complete"] or not state["preserved"]:
    raise SystemExit(1)
