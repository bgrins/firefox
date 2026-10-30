import hashlib
import importlib.util
import json
import os
from pathlib import Path
import signal
import sys

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RUNTIME = ROOT / "artifacts/css-registered-number-native-runtime-v1"
read = lambda p: json.loads(p.read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def authenticate(pin):
    assert sha(HERE / "FILES.json") == pin
    for name, expected in read(HERE / "FILES.json").items():
        assert sha(HERE / name) == expected, name
    policy = read(HERE / "POLICY.json")
    assert policy["execution_enabled"] is True and policy["original_only"] is True
    for name, expected in policy["references"].items():
        assert sha(ROOT / name) == expected, name
    assert {name: sha(RUNTIME / name) for name in policy["controls"]} == policy["controls"]
    assert not (RUNTIME / "SOURCE-TRANSITION.lock").exists()
    return policy


def main():
    assert len(sys.argv) == 3 and sys.argv[1] in ("--check", "--run")
    policy = authenticate(sys.argv[2])
    if sys.argv[1] == "--check":
        load("log_static_check", str(HERE / "check.py")).check(policy)
        print("Static combined baseline checks passed; no browser or full state verification performed")
        return
    env = dict(os.environ, GIT_OPTIONAL_LOCKS="0", PYTHONDONTWRITEBYTECODE="1",
               MOZCONFIG=str(ROOT / "mozconfig"), MOZ_OBJDIR=str(ROOT / "objdir-full.noindex"),
               MOZ_HEADLESS="1", MOZ_SKIP_PATH_PERFORMANCE_CHECK="1")
    assert not any(os.environ.get(k) for k in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_OBJECT_DIRECTORY", "GIT_ALTERNATE_OBJECT_DIRECTORIES"))
    state = load("log_state", policy["state_helper"])
    epoch = read(RUNTIME / "CURRENT-EPOCH.json")
    assert epoch["semantic_index"]["head"] == policy["head"] and epoch["staged_working"] == {}
    assert epoch["accepted_pow_special_value"]["fix"] == 150
    assert epoch["pow_special_value_transition"]["accepted"]
    assert epoch["pins"]["servo/components/style/values/generics/calc.rs"] == policy["accepted_calc_sha256"]
    built = read(ROOT / policy["build_epoch"])
    bound = [name for name in built["pins"]
             if name.startswith(("servo/", "layout/", "dom/")) or name in policy["rebuilt_binaries"]]
    assert bound and all(epoch["pins"][name] == built["pins"][name] for name in bound)

    def verify():
        authenticate(sys.argv[2])
        return state.a.verify_current(state.h, ROOT, env, epoch)

    metadata = load("log_metadata", policy["wpt"]["metadata_helper"])
    prepared = metadata.application_metadata(ROOT / policy["wpt"]["application_ini"], policy["wpt"]["phase_revisions"]["original"])
    prepared.update(build_revision=prepared["revision"], harness_revision=policy["wpt"]["harness_revision"], source_role="original")
    assert prepared == policy["prepared_application_metadata"]
    verify()
    output = ROOT / policy["output"]
    assert not output.exists() and not output.is_symlink()
    output.mkdir()
    stopped = [False]
    for sig in (signal.SIGINT, signal.SIGTERM):
        signal.signal(sig, lambda signum, frame: stopped.__setitem__(0, True))
    runner = load("log_wpt", policy["wpt_helper"])
    owned = {}
    phase = runner.run(ROOT, HERE, output / "original-wpt", "original", policy,
                       env, verify, owned, lambda: stopped[0])
    assert not owned
    assessment = read(output / "original-wpt/ASSESSMENT.json")
    assert assessment["complete"] and assessment["observed_subtest_count"] == 578
    observed = {page: [row["subtest"] for row in assessment["rows"] if row["test"] == page]
                for page in policy["wpt"]["expected_subtests"]}
    runner.save(output / "OBSERVED-ROSTER.json", {
        "expected_subtests": observed, "observed_subtest_count": 578,
        "phase": phase, "owner_sha256": sys.argv[2],
        "source_roster_sha256": policy["references"][policy["source_roster"]],
        "candidate_authorized": False,
    })
    runner.save(output / "RESULT.json", {
        "phase": phase, "build_native_and_binary_pin_count": len(bound),
        "preservation_verified": True, "native_fix_accepted": False,
        "source_or_canonical_mutation": False,
    })
    print("Completed original combined MinMax/log observation; outcomes recorded without acceptance", flush=True)


if __name__ == "__main__":
    main()
