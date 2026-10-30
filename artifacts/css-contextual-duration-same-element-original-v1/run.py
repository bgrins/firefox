import hashlib
import importlib.util
import json
import os
from pathlib import Path
import signal
import secrets
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
    assert policy["original_only"] is True
    assert policy["candidate_execution_enabled"] is False
    for name, expected in policy["references"].items():
        assert sha(ROOT / name) == expected, name
    load("progress_binding", str(HERE / "check.py")).check_binding(policy)
    if sys.argv[1] == "--run":
        assert policy["execution_enabled"] is True
        assert policy["activation_pending"] == []
        assert policy["head"] == policy["wpt"]["harness_revision"]
        assert set(policy["controls"]) == {"CURRENT-EPOCH.json", "OWNED.json", "ROLE.json"}
        assert set(policy["restoration_binding"]) == {"terminal", "refresh"}
        for record in policy["restoration_binding"].values():
            assert policy["references"][record["path"]] == record["sha256"]
        for name, expected in policy["deferred_nonartifact_references"].items():
            assert sha(ROOT / name) == expected, name
        assert policy["head"] and policy["prepared_application_metadata"] and policy["build_epoch"]
        assert {name: sha(RUNTIME / name) for name in policy["controls"]} == policy["controls"]
        assert not (RUNTIME / "SOURCE-TRANSITION.lock").exists()
    return policy


def main():
    assert len(sys.argv) == 3 and sys.argv[1] in ("--check", "--run")
    policy = authenticate(sys.argv[2])
    if sys.argv[1] == "--check":
        load("progress_static_check", str(HERE / "check.py")).check(policy)
        print("Static progress baseline checks passed; no browser or full state verification performed")
        return
    env = dict(os.environ, GIT_OPTIONAL_LOCKS="0", PYTHONDONTWRITEBYTECODE="1",
               MOZCONFIG=str(ROOT / "mozconfig"), MOZ_OBJDIR=str(ROOT / "objdir-full.noindex"),
               MOZ_HEADLESS="1", MOZ_SKIP_PATH_PERFORMANCE_CHECK="1")
    assert not any(os.environ.get(k) for k in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_OBJECT_DIRECTORY", "GIT_ALTERNATE_OBJECT_DIRECTORIES"))
    state = load("progress_state", policy["state_helper"])
    epoch = read(RUNTIME / "CURRENT-EPOCH.json")
    assert epoch["semantic_index"]["head"] == policy["head"] and epoch["staged_working"] == {}
    assert epoch["accepted_pow_special_value"]["fix"] == 150
    assert epoch["pow_special_value_transition"]["accepted"]
    assert epoch["pins"]["servo/components/style/values/generics/calc.rs"] == policy["accepted_calc_sha256"]
    built = read(ROOT / policy["build_epoch"])
    assert built["semantic_index"]["head"] == policy["wpt"]["phase_revisions"]["original"]
    bound = [name for name in built["pins"]
             if name.startswith(("servo/", "layout/", "dom/")) or name in policy["rebuilt_binaries"]]
    assert bound and all(epoch["pins"][name] == built["pins"][name] for name in bound)

    assert len(policy["accepted_current_payloads"]) == 29
    for name, claim in policy["accepted_current_payloads"].items():
        assert epoch["pins"][name] == claim["sha256"] and epoch["installed_identities"][name] == claim["identity"]

    def verify():
        authenticate(sys.argv[2])
        for name, pin in policy["source_role_pins"].items():
            assert sha(ROOT / name) == pin, name
            if name in built["pins"]:
                assert epoch["pins"][name] == built["pins"][name] == pin, name
            else:
                assert name in policy["build_unpinned_sources"], name
                assert name not in built["modified_native_paths"]
                assert built["semantic_index"]["head"] == policy["wpt"]["phase_revisions"]["original"]
                assert epoch["pins"].get(name, pin) == pin
                for revision in (policy["head"], policy["wpt"]["phase_revisions"]["original"]):
                    body = state.h.git(ROOT, env, "show", revision + ":" + name)
                    assert hashlib.sha256(body).hexdigest() == pin, (name, revision)
        return state.a.verify_current(state.h, ROOT, env, epoch)

    metadata = load("progress_metadata", policy["wpt"]["metadata_helper"])
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
    runner = load("progress_wpt", policy["wpt_helper"])
    owned = {}
    initial = verify()
    runner.save(output / "PRE.json", initial)
    records = output / "progress-records"
    records.mkdir(mode=0o700)
    binding = {"directory": str(records), "identity": [records.stat().st_dev, records.stat().st_ino], "run_id": secrets.token_hex(24)}
    runner.save(output / "PROGRESS-BINDING.json", binding)
    env.update(DURATION_PROGRESS_RECORD_DIR=str(records), DURATION_PROGRESS_RUN_ID=binding["run_id"])
    phase = runner.run(ROOT, HERE, output / "original-wpt", "original", policy,
                       env, verify, owned, lambda: stopped[0])
    assert not owned
    assessment = read(output / "original-wpt/ASSESSMENT.json")
    assert assessment["complete"] and assessment["observed_subtest_count"] == 2
    observed = {page: [row["subtest"] for row in assessment["rows"] if row["test"] == page]
                for page in policy["wpt"]["expected_subtests"]}
    runner.save(output / "OBSERVED-ROSTER.json", {
        "expected_subtests": observed, "observed_subtest_count": 2,
        "phase": phase, "owner_sha256": sys.argv[2],
        "source_roster_sha256": policy["references"][policy["source_roster"]],
        "candidate_authorized": False,
    })
    collection = load("progress_record_collection", str(HERE / "records.py")).collect(ROOT, records, binding, policy, assessment)
    runner.save(output / "PROGRESS-RECORDS.json", collection)
    after = verify()
    assert initial == after and not owned
    assert read(output / "original-wpt/PRE.json") == read(output / "original-wpt/POST.json") == initial
    assert read(output / "original-wpt/APPLICATION-METADATA.json") == read(output / "original-wpt/APPLICATION-METADATA-POST.json") == policy["prepared_application_metadata"]
    runner.save(output / "POST.json", after)
    runner.save(output / "RESULT.json", {
        "phase": phase, "build_native_and_binary_pin_count": len(bound),
        "lifecycle_complete": True, "observation_complete": collection["complete"],
        "callbacks_passed": sum(row["status"] == "PASS" for row in assessment["rows"]),
        "callbacks_failed": sum(row["status"] == "FAIL" for row in assessment["rows"]),
        "all_callbacks_passed": all(row["status"] == "PASS" for row in assessment["rows"]),
        "records_complete": collection["complete"], "record_errors": collection["errors"],
        "numeric_or_convergence_oracle": False,
        "preservation_verified": True, "native_fix_accepted": False,
        "source_or_canonical_mutation": False,
    })
    assert not collection["errors"], collection["errors"]
    print("Completed original progress observation; outcomes recorded without acceptance", flush=True)


if __name__ == "__main__":
    main()
