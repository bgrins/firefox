import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
TEST = "testing/web-platform/tests/css/css-values/map-taint-equality.html"
TEST_ID = "/css/css-values/map-taint-equality.html"
EXPECTED_MAP = "9ce38cf97e1ae93c134e80a1efc936f307d7311b8d7cf160331e9fa690ff5e9d"

def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--build-receipt", type=Path, required=True)
    args = parser.parse_args()
    repo, out = args.repo.resolve(), args.output.resolve()
    manifest = json.loads((HERE / "MANIFEST.json").read_text())
    freeze = json.loads((HERE / "FREEZE.json").read_text())
    assert digest(HERE / "MANIFEST.json") == freeze["manifest_sha256"]
    for name, expected in manifest["files"].items():
        assert digest(HERE / name) == expected, name
    expected_names = json.loads((HERE / "EXPECTED-IDENTITIES.json").read_text())
    assert digest(repo / TEST) == digest(HERE / "map-taint-equality.html"), "install exact proposal first"
    assert digest(repo / "servo/components/style/custom_properties_map.rs") == EXPECTED_MAP, "requires frozen combined map"
    assert args.build_receipt.resolve().is_file(), "root build association receipt required"
    assert not out.exists(), "preserve existing evidence"
    git = ["git", "-c", "core.fsmonitor=false"]
    changed = subprocess.check_output(git + ["diff", "--name-only"], cwd=repo).decode().splitlines()
    files = sorted(set(changed + [TEST,
        "servo/components/style/custom_properties_map.rs",
        "servo/components/style/custom_properties.rs",
        "servo/components/style/properties/cascade.rs",
        "servo/components/style/properties_and_values/value.rs",
        "servo/components/style/parser.rs",
        "servo/components/style/url/mod.rs",
        "servo/components/style/stylist.rs",
        "servo/ports/geckolib/glue.rs",
        "modules/libpref/init/StaticPrefList.yaml",
        "testing/web-platform/meta/css/css-values/__dir__.ini",
        "objdir-full.noindex/dist/Nightly.app/Contents/MacOS/firefox",
        "objdir-full.noindex/dist/Nightly.app/Contents/MacOS/XUL",
    ]))
    pins = {name: digest(repo / name) for name in files}
    build_pin = digest(args.build_receipt.resolve())
    out.mkdir(parents=True)
    command = ["./mach", "wpt", "--headless", "--processes=1",
               "--setpref=layout.css.properties-and-values.enabled=true",
               "--log-raw=" + str(out / "raw.json"), TEST]
    with (out / "wpt.log").open("w") as log:
        result = subprocess.run(command, cwd=repo, stdout=log, stderr=subprocess.STDOUT,
                                env={**os.environ, "MOZ_SKIP_PATH_PERFORMANCE_CHECK": "1"})
    stable = {name: digest(repo / name) == pin for name, pin in pins.items()}
    rows, ends, suites = [], [], 0
    for line in (out / "raw.json").read_text().splitlines():
        event = json.loads(line)
        if event.get("action") == "test_status":
            rows.append({key: event.get(key) for key in ["test", "subtest", "status", "expected", "message", "stack"]})
        elif event.get("action") == "test_end":
            ends.append({key: event.get(key) for key in ["test", "status", "expected", "message"]})
        elif event.get("action") == "suite_end":
            suites += 1
    record = {"command": command, "exit": result.returncode,
              "head": subprocess.check_output(git + ["rev-parse", "HEAD"], cwd=repo).decode().strip(),
              "pins": pins, "stable_after": stable, "build_receipt": str(args.build_receipt.resolve()),
              "build_receipt_sha256": build_pin,
              "build_receipt_stable": digest(args.build_receipt.resolve()) == build_pin,
              "rows": rows, "test_ends": ends, "suite_ends": suites,
              "scope": "Existing root-owned combined build. Receipt identity alone is not source-to-binary proof; root must adjudicate the supplied build receipt."}
    (out / "RUN.json").write_text(json.dumps(record, indent=2) + "\n")
    assert all(stable.values()) and record["build_receipt_stable"], "input drift"
    assert result.returncode in {0, 1}
    assert len(rows) == len(expected_names) == 9
    assert [r["subtest"] for r in rows] == expected_names, "exact ordered nine identities"
    assert all(r["test"] == TEST_ID and r["status"] in {"PASS", "FAIL"} for r in rows)
    assert len(ends) == 1 and ends[0]["test"] == TEST_ID and ends[0]["status"] == "OK", "harness prerequisite"
    assert suites == 1
    print(json.dumps({"PASS": sum(r["status"] == "PASS" for r in rows),
                      "FAIL": sum(r["status"] == "FAIL" for r in rows),
                      "identities_exact": True, "stable": True}))

if __name__ == "__main__":
    main()
