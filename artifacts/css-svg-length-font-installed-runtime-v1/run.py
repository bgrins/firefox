import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise SystemExit("Require python3 -I -S without optimization")
sys.dont_write_bytecode = True
import os
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
need(all(isinstance(settings[n], str) and settings[n] for n in ("epoch", "epoch_manifest_sha256", "root_receipt_sha256", "acceptance", "acceptance_sha256")), "unbound epoch")
need(not any((HERE / n).exists() or (HERE / n).is_symlink() for n in
             ("STATE.json", "BEFORE.json", "FINAL.json", "SUMMARY.json", "PRIOR-EXPERIMENT.json", "wpt-font")), "already started")
proposal = ROOT / settings["proposal"]
authenticate(read(proposal / "FILES.json"), proposal)
need((HERE / "fixture.html").read_bytes() == (proposal / "probe.html").read_bytes(), "exact sealed six-test fixture")
epoch = ROOT / settings["epoch"]
need(sha(epoch / "FILES.json") == settings["epoch_manifest_sha256"], "actual comparison seal")
authenticate(read(epoch / "FILES.json"), epoch)
need(sha(epoch / "ROOT-FINAL-CHECK.json") == settings["root_receipt_sha256"], "actual root receipt")
prior_state, receipt = read(epoch / "STATE.json"), read(epoch / "ROOT-FINAL-CHECK.json")
expected, pins, c = read(epoch / "FINAL.json"), read(epoch / "FINAL-PINS.json"), read(epoch / "CONFIG.json")
installation = read(epoch / "INSTALLATION.json")
acceptance = ROOT / settings["acceptance"]
need(sha(acceptance) == settings["acceptance_sha256"] == installation["acceptance_sha256"], "accepted installation join")
accepted = read(acceptance)
need(accepted["status"] == "SCOPED_ACCEPTED", "root scoped acceptance")
repair = ROOT / settings["repair_proposal"]
authenticate(read(repair / "FILES.json"), repair)
patch = accepted.get("patch")
patch_hash = patch.get("sha256") if isinstance(patch, dict) else accepted.get("native_patch_sha256")
need(patch_hash == sha(repair / "standalone.patch"), "accepted exact repair")
repair_sources = read(repair / "SOURCE-PINS.json")
original_sources = {n:v["before_sha256"] for n,v in repair_sources.items()}
candidate_sources = {n:v["candidate_sha256"] for n,v in repair_sources.items()}
need(prior_state["status"] == "terminal" and prior_state["installed"] is True
     and "failure" not in prior_state and prior_state["build_exit"] == prior_state["lint_exit"] == 0
     and prior_state["recovery_errors"] == [] and prior_state["subtests"] == {"PASS":9,"FAIL":0}
     and prior_state["files_ok"] == 1, "successful nine-case installation required")
need(expected == installation["after"] and read(epoch / "BEFORE.json") == installation["before"]
     and receipt["status"] == "INSTALLED_VERIFIED" and receipt["exit"] == 0
     and receipt["state_sha256"] == sha(epoch / "STATE.json")
     and receipt["final_sha256"] == sha(epoch / "FINAL.json")
     and receipt["installed_binary_pins"] == prior_state["installed_binary_pins"] == installation["binary_pins"], "installation/source/binary receipt join")
need(installation["original_source_pins"] == original_sources
     and installation["installed_source_pins"] == candidate_sources
     and len(candidate_sources) == 2, "exact accepted two-source installation")
need(expected["sources"] == {**installation["before"]["sources"], **candidate_sources}
     and all(installation["before"]["sources"][n] == h for n,h in original_sources.items())
     and all(expected[k] == installation["before"][k] for k in ("head","index_diff_sha256","index_entries_sha256")), "only accepted source changes")
need(pins == {**read(epoch / "RESOURCES.json"), **expected["sources"], **prior_state["installed_binary_pins"],
              installation["owned_test"]:installation["owned_test_sha256"]}, "complete installed roles")
need(len(expected["sources"]) == receipt["source_count"] == len(c["guard_sources"]) == 52
     and len(pins) == receipt["pin_count"] and receipt["staged_paths_preserved"] == 925, "installed role counts")
installed_tests = dict(c["installed_tests"])
need(len(installed_tests) == 3 and installation["owned_test"] not in installed_tests, "distinct fourth test")
for directory in ("css-cssom-client-install-runtime-v1", "css-cssom-offset-scroll-install-runtime-v1", "css-hidden-svg-matrix-install-runtime-v1"):
    prior = ROOT / "artifacts" / directory
    authenticate(read(prior / "FILES.json"), prior)
    item = read(prior / "INSTALLATION.json")
    need(installed_tests[item["owned_test"]] == {"identity":item["owned_test_identity"], "sha256":item["owned_test_sha256"]}, "prior installed test ownership join")
installed_tests[installation["owned_test"]] = {"identity":installation["owned_test_identity"], "sha256":installation["owned_test_sha256"]}
need(all(pins[n] == item["sha256"] for n,item in installed_tests.items()), "all four installed test role joins")
need(installation["owned_test"] in c["install"]
     and (ROOT / c["proposal"] / "candidate" / installation["owned_test"]).read_bytes() == (repair / "candidate" / installation["owned_test"]).read_bytes()
     and pins[installation["owned_test"]] == sha(repair / "candidate" / installation["owned_test"]), "exact installed nine-case test")
c["modified_native_paths"] = sorted(set(c["modified_native_paths"]) | set(candidate_sources))
need(len(c["modified_native_paths"]) == 29, "installed native roster")
c["existing_tests"] = sorted(installed_tests)
c["existing_test_pins"] = {n:item["sha256"] for n,item in installed_tests.items()}
need(c["tracked_existing_tests"] == [], "installed tests remain untracked")
source_inputs = read(proposal / "SOURCE-PINS.json")["files"]
for name, digest in source_inputs.items():
    if name in candidate_sources:
        need(digest == original_sources[name], "original font audit input join")
        digest = candidate_sources[name]
    need(name not in pins or pins[name] == digest, "font source conflicts with installed roles")
    pins[name] = digest
owned_test = settings["owned_test"]
owned_metadata = settings["owned_metadata"]
need(owned_test not in pins and owned_test not in installed_tests, "distinct diagnostic ownership")
need(not (ROOT / owned_test).exists() and not (ROOT / owned_test).is_symlink(), "diagnostic exists")
need(not (ROOT / owned_metadata).exists() and not (ROOT / owned_metadata).is_symlink(), "diagnostic metadata exists")
pins[owned_metadata] = None
c["guard_sources"] = sorted(expected["sources"])
c["must_be_absent"] = sorted(set(c["must_be_absent"]))
c["install"] = {}
wpt = load("length_wpt", ROOT / settings["helpers"] / "run_wpt.py")
bindings = load("length_bindings", ROOT / settings["helpers"] / "bindings.py")
tests = load("font_wpt_tests", ROOT / settings["tests_helper"])
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
             and sha(ROOT / name) == item["sha256"], "installed four-test inode/hash")
    need(not wpt.git("ls-files", "--", *installed_tests).strip(), "installed tests became tracked")


verify()
bindings.index_state(wpt)
need(not wpt.git("ls-files", "--", owned_test).strip(), "owned test tracked")
wpt.save("BEFORE.json", {"snapshot": expected, "pins": pins})
wpt.save("PRIOR-EXPERIMENT.json", {"epoch": settings["epoch"], "state": prior_state, "root_receipt": receipt,
                                 "installed_build_used": True, "candidate_acceptance_required": True})
state = {"status": "starting", "complete": False, "preserved": False, "native_changes": False,
         "source_role": "accepted SVGLength repair installed with prior113 and mixed prototypes",
         "prior_experiment_failed": "failure" in prior_state}
owned_identity = None
fixture = (HERE / "fixture.html").read_bytes()
wpt.save("STATE.json", state)
try:
    with (ROOT / owned_test).open("xb") as stream:
        info = os.fstat(stream.fileno())
        owned_identity = (info.st_dev, info.st_ino)
        need(stream.write(fixture) == len(fixture), "short fixture write")
    need((ROOT / owned_test).read_bytes() == fixture, "fixture body")
    verify()
    c["tests"] = [owned_test]
    c["expected_subtests"] = {settings["test_id"]: settings["names"]}
    phase_pins = {**pins, owned_test: hashlib.sha256(fixture).hexdigest()}
    result = tests.run(wpt, "font", phase_pins)
    need(len(result["rows"]) == 6, "six exact rows")
    need(all(row["status"] == "PASS" for row in result["rows"]), "all six installed font cases must pass")
    summary = {"calibrated":6, "getter_controls_pass":2, "counts":{"PASS":6,"FAIL":0},
               "conversion_failures":[], "rows":result["rows"],
               "all_first_repeat_and_resolved_assertions_passed":True,
               "native_factor_branch_observed":False}
    wpt.save("SUMMARY.json", summary)
    state.update(complete=True, calibrated=6, getter_controls_pass=2, counts=summary["counts"])
except BaseException as error:
    state["failure"] = {"type": type(error).__name__, "message": str(error)}
finally:
    try:
        if owned_identity is not None:
            info = (ROOT / owned_test).lstat()
            need(stat.S_ISREG(info.st_mode) and (info.st_dev, info.st_ino) == owned_identity,
                 "owned test replaced; preserve unexpected file")
            (ROOT / owned_test).unlink()
        need(not (ROOT / owned_test).exists() and not (ROOT / owned_test).is_symlink(), "owned test remains")
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
