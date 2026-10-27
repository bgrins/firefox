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
review = settings["final_review"]
need(isinstance(review, dict) and set(review) == {"path", "sha256"}, "unbound independent review")
review_path = ROOT / review["path"]
need(sha(review_path) == review["sha256"], "independent review seal")
authenticate(read(review_path), review_path.parent)
need(all(isinstance(settings[n], str) and settings[n] for n in ("epoch", "epoch_manifest_sha256", "root_receipt_sha256")), "unbound epoch")
need(not any((HERE / n).exists() or (HERE / n).is_symlink() for n in
             ("STATE.json", "BEFORE.json", "FINAL.json", "SUMMARY.json", "PRIOR-EXPERIMENT.json", "wpt-hidden-provider")), "already started")
proposal = ROOT / settings["proposal"]
authenticate(read(proposal / "FILES.json"), proposal)
need((HERE / "fixture.html").read_bytes() == (proposal / "probe.html").read_bytes(), "exact sealed four-test fixture")
epoch = ROOT / settings["epoch"]
need(sha(epoch / "FILES.json") == settings["epoch_manifest_sha256"], "actual comparison seal")
authenticate(read(epoch / "FILES.json"), epoch)
need(sha(epoch / "ROOT-FINAL-CHECK.json") == settings["root_receipt_sha256"], "actual root receipt")
gate = load("q_epoch_gate", HERE / "epoch_gate.py")
prior_state, receipt, expected, pins, c, installed_tests = gate.bind(ROOT, epoch, settings, read, sha, authenticate, load, need)
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
             and sha(ROOT / name) == item["sha256"], "installed eight-test inode/hash")
    need(not wpt.git("ls-files", "--", *installed_tests).strip(), "installed tests became tracked")


verify()
bindings.index_state(wpt)
need(not wpt.git("ls-files", "--", owned_test).strip(), "owned test tracked")
wpt.save("BEFORE.json", {"snapshot": expected, "pins": pins})
wpt.save("PRIOR-EXPERIMENT.json", {"epoch": settings["epoch"], "state": prior_state, "root_receipt": receipt,
                                 "installed_build_used": True, "expanded114_acceptance_required": True})
state = {"status": "starting", "complete": False, "preserved": False, "native_changes": False,
         "source_role": "installed expanded114 plus115 and mixed prototypes; hidden iframe provider diagnostic",
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
    result = tests.run(wpt, "hidden-provider", phase_pins)
    classifier = load("hidden_provider_classifier", HERE / "classify.py")
    summary = classifier.classify(result["rows"], settings["names"], need)
    wpt.save("SUMMARY.json", summary)
    state.update(complete=True, calibrated=4, counts=summary["counts"])
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
