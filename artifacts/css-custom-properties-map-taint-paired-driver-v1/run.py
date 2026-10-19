import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
BINARY_DIR = "objdir-full.noindex/dist/Nightly.app/Contents/MacOS/"
NINE = "/css/css-values/map-taint-equality.html"
ATTR = "/css/css-values/attr-security.html"

def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()

def authenticate():
    manifest = json.loads((HERE / "MANIFEST.json").read_text())
    freeze = json.loads((HERE / "FREEZE.json").read_text())
    assert digest(HERE / "MANIFEST.json") == freeze["manifest_sha256"]
    for name, expected in manifest["files"].items():
        assert digest(HERE / name) == expected, name

def read_results(raw, expected):
    rows, ends, suite_ends = {}, {}, 0
    for line in raw.read_text().splitlines():
        event = json.loads(line)
        action = event.get("action")
        if action == "test_status":
            key = (event["test"], event["subtest"])
            assert key not in rows, "duplicate subtest identity"
            rows[key] = {k: event.get(k) for k in ["test", "subtest", "status", "expected", "message", "stack"]}
        elif action == "test_end":
            assert event["test"] not in ends, "duplicate harness identity"
            ends[event["test"]] = {k: event.get(k) for k in ["test", "status", "expected", "message"]}
        elif action == "suite_end":
            suite_ends += 1
    keys = {(test, name) for test, names in expected.items() for name in names}
    assert set(rows) == keys, "missing or unexpected subtest identities"
    assert set(ends) == set(expected), "missing or unexpected harness identities"
    assert all(row["status"] in {"PASS", "FAIL"} for row in rows.values())
    assert all(row["status"] == "OK" for row in ends.values()), "harness failure/skip"
    assert suite_ends == 1, "suite completion"
    return {"rows": list(rows.values()), "test_ends": list(ends.values()), "suite_ends": suite_ends}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    authenticate()
    repo, out = args.repo.resolve(), args.output.resolve()
    assert not out.exists(), "output must be new"
    source_pins = json.loads((HERE / "SOURCE-PINS.json").read_text())
    native = list(source_pins["original"])
    expected = json.loads((HERE / "EXPECTED.json").read_text())
    assert len(expected) == 9 and sum(map(len, expected.values())) == 82
    tests = ["testing/web-platform/tests" + name for name in expected]
    for name in tests:
        assert digest(repo / name) == digest(HERE / "tests" / name), "test bytes: " + name
    for name, pin in source_pins["original"].items():
        assert digest(repo / name) == pin, "start with original source: " + name
    association = json.loads((HERE / "evidence/BUILD-ASSOCIATION.json").read_text())
    assert digest(HERE / "evidence/BUILD-MATRIX.json") == association["build_matrix_sha256"]
    matrix = json.loads((HERE / "evidence/BUILD-MATRIX.json").read_text())
    assert association["combined_build"] == next(r for r in matrix["runs"] if r["variant"] == "combined")
    assert association["combined_build"]["build_exit"] == 0
    inherited = {**association["source_binary_and_prior_test_pins"], **association["additional_unchanged_tracked_sources"]}
    for name, pin in inherited.items():
        assert digest(repo / name) == pin, "existing build association mismatch: " + name
    git = ["git", "-c", "core.fsmonitor=false"]
    changed = subprocess.check_output(git + ["diff", "--name-only"], cwd=repo).decode().splitlines()
    extras = ["testing/web-platform/tests/resources/testharness.js",
              "testing/web-platform/tests/resources/testharnessreport.js",
              "testing/web-platform/meta/css/css-values/__dir__.ini"]
    directories = {"testing/web-platform/meta", "testing/web-platform/meta/css"}
    directories.update("testing/web-platform/meta" + str(Path(test).parent) for test in expected)
    for directory in sorted(directories):
        path = repo / directory / "__dir__.ini"
        if path.exists():
            extras.append(str(path.relative_to(repo)))
    for optional in ["testing/profiles/web-platform/user.js", "testing/profiles/profiles.json",
                     "objdir-full.noindex/mozinfo.json"]:
        if (repo / optional).exists():
            extras.append(optional)
    for test in expected:
        file_meta = repo / ("testing/web-platform/meta" + test + ".ini")
        if file_meta.exists():
            extras.append(str(file_meta.relative_to(repo)))
    all_paths = sorted(set(inherited) | set(changed) | set(tests) | set(extras))
    initial_pins = {name: digest(repo / name) for name in all_paths}
    stable = {name: pin for name, pin in initial_pins.items() if name not in native and not name.startswith(BINARY_DIR)}
    def check_stable():
        assert all(digest(repo / n) == h for n, h in stable.items()), "protected source/test/config drift"
    def source_matches(variant):
        return all(digest(repo / n) == h for n, h in source_pins[variant].items())
    def binaries():
        return {name: digest(repo / (BINARY_DIR + name)) for name in ["firefox", "XUL"]}
    env = {**os.environ, "MOZ_SKIP_PATH_PERFORMANCE_CHECK": "1"}
    out.mkdir(parents=True)
    record = {"head": subprocess.check_output(git + ["rev-parse", "HEAD"], cwd=repo).decode().strip(),
              "initial_pins": initial_pins, "stable_pins": stable,
              "original_build": "REUSED_AUTHENTICATED_COMBINED_BUILD",
              "association_sha256": digest(HERE / "evidence/BUILD-ASSOCIATION.json"),
              "source_pins": source_pins, "phases": [],
              "scope": "Shared-tree existing baseline and candidate local build; no isolated/upstream runtime claim."}
    def save():
        (out / "PAIR.json").write_text(json.dumps(record, indent=2) + "\n")
    def test_phase(variant):
        check_stable()
        assert source_matches(variant)
        phase = out / variant
        phase.mkdir()
        before = binaries()
        command = ["./mach", "wpt", "--headless", "--processes=1",
                   "--setpref=layout.css.properties-and-values.enabled=true",
                   "--log-raw=" + str(phase / "raw.json")] + tests
        entry = {"variant": variant, "command": command, "source_before": source_pins[variant], "binaries_before": before}
        record["phases"].append(entry)
        save()
        with (phase / "wpt.log").open("w") as log:
            result = subprocess.run(command, cwd=repo, env=env, stdout=log, stderr=subprocess.STDOUT)
        entry["exit"] = result.returncode
        entry["binaries_after"] = binaries()
        entry["source_after"] = {n: digest(repo / n) for n in native}
        entry["raw_sha256"] = digest(phase / "raw.json") if (phase / "raw.json").exists() else None
        save()
        check_stable()
        assert source_matches(variant) and binaries() == before
        assert result.returncode in {0, 1}
        entry["results"] = read_results(phase / "raw.json", expected)
        save()
        return entry
    changed_native = False
    try:
        original = test_phase("original")
        prior = json.loads((HERE / "evidence/prior-nine-RUN.json").read_text())
        old_nine = {r["subtest"]: r["status"] for r in prior["rows"]}
        observed_nine = {r["subtest"]: r["status"] for r in original["results"]["rows"] if r["test"] == NINE}
        assert observed_nine == old_nine, "prior baseline nine outcomes changed"
        assert all(r["status"] == "PASS" for r in original["results"]["rows"] if r["test"] not in {NINE, ATTR})
        check_stable()
        assert source_matches("original")
        changed_native = True
        for name in native:
            (repo / name).write_bytes((HERE / "source/candidate" / name).read_bytes())
        assert source_matches("candidate")
        record["candidate_build"] = {"command": ["./mach", "build", "binaries"],
            "sources_before": {n: digest(repo / n) for n in native}, "binaries_before": binaries()}
        save()
        with (out / "candidate-build.log").open("w") as log:
            build = subprocess.run(["./mach", "build", "binaries"], cwd=repo, env=env,
                                   stdout=log, stderr=subprocess.STDOUT)
        record["candidate_build"].update({"exit": build.returncode, "sources_after": {n: digest(repo / n) for n in native},
            "binaries_after": binaries(), "log_sha256": digest(out / "candidate-build.log")})
        save()
        check_stable()
        assert build.returncode == 0 and source_matches("candidate")
        assert binaries()["XUL"] != original["binaries_before"]["XUL"], "candidate binary was not relinked"
        candidate = test_phase("candidate")
        before = {(r["test"], r["subtest"]): r["status"] for r in original["results"]["rows"]}
        after = {(r["test"], r["subtest"]): r["status"] for r in candidate["results"]["rows"]}
        changes = [{"test": k[0], "subtest": k[1], "before": before[k], "after": after[k]} for k in before if before[k] != after[k]]
        record["comparison"] = {"subtest_keys": len(before), "harness_keys": 9, "changes": changes,
                                "unchanged": len(before) - len(changes)}
        save()
        assert all(after[(NINE, name)] == "PASS" for name in expected[NINE]), "candidate target failure"
        assert all(before[k] == after[k] for k in before if k[0] != NINE), "regression outcome changed"
        record["complete"] = True
    except BaseException as error:
        record["error"] = repr(error)
        raise
    finally:
        if changed_native:
            known = all(digest(repo / n) in {source_pins["original"][n], source_pins["candidate"][n]} for n in native)
            record["known_native_before_restore"] = known
            if known:
                for n in native:
                    if digest(repo / n) != source_pins["candidate"][n]:
                        (repo / n).write_bytes((HERE / "source/candidate" / n).read_bytes())
            record["candidate_source_retained"] = source_matches("candidate")
        else:
            record["original_source_untouched"] = source_matches("original")
        record["final_binaries"] = binaries()
        record["candidate_binary_validated"] = bool(record.get("complete", False))
        save()
    print(json.dumps(record["comparison"]))

if __name__ == "__main__":
    main()
