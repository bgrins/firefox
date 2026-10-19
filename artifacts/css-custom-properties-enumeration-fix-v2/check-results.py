import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE_PINS = json.loads((HERE / "SOURCE-PINS.json").read_text())
MATRIX = json.loads((HERE / "BUILD-MATRIX.json").read_text())
BUILDS = {entry["variant"]: entry for entry in MATRIX["runs"]}
NATIVE = "servo/components/style/custom_properties_map.rs"
summary = {}
baseline_keys = None
stable_pins = None

for variant in ["original", "count-only", "combined"]:
    source = (HERE / "source" / (variant + ".rs")).read_bytes()
    assert hashlib.sha256(source).hexdigest() == SOURCE_PINS[variant]
    run = json.loads((HERE / (variant + "-RUN.json")).read_text())
    assert run["stable_after"] and run["exit"] in {0, 1}
    build = BUILDS[variant]
    assert build["build_exit"] == 0
    assert run["pins"][NATIVE] == SOURCE_PINS[variant]
    assert build["source"] == SOURCE_PINS[variant]
    assert run["head"] == MATRIX["head"]
    for binary in ["firefox", "XUL"]:
        name = "objdir-full.noindex/dist/Nightly.app/Contents/MacOS/" + binary
        assert run["pins"][name] == build["binaries"].get(name, build["binaries"].get(binary))
    stable = {name: pin for name, pin in run["pins"].items()
              if name != NATIVE and not name.startswith("objdir-full.noindex/")}
    if stable_pins is None:
        stable_pins = stable
    assert stable == stable_pins, variant
    rows = [json.loads(line) for line in (HERE / (variant + "-raw.json")).read_text().splitlines()]
    subtests = [row for row in rows if row.get("action") == "test_status"]
    ends = [row for row in rows if row.get("action") == "test_end"]
    keys = {(row["test"], row["subtest"]) for row in subtests}
    assert len(subtests) == len(keys) == 41, (variant, len(subtests), len(keys))
    if baseline_keys is None:
        baseline_keys = keys
    assert keys == baseline_keys
    assert len(ends) == 7 and all(row["status"] == "OK" for row in ends)
    assert sum(row.get("action") == "suite_end" for row in rows) == 1
    assert all(row["status"] in {"PASS", "FAIL"} for row in subtests)
    failures = [{"test": row["test"], "subtest": row["subtest"], "message": row.get("message")}
                for row in subtests if row["status"] == "FAIL"]
    if variant == "combined":
        assert not failures and run["exit"] == 0
    else:
        assert failures and run["exit"] == 1
    summary[variant] = {"pass": len(subtests) - len(failures), "fail": len(failures),
                        "harnesses_ok": len(ends), "failures": failures}

result = {"runs": summary, "stable_sources_and_tests": stable_pins,
          "scope": "41 exact shared-tree WPT observations per variant; finite runtime evidence, not a universal or isolated-upstream proof."}
(HERE / "OBSERVATIONS.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps({name: {key: value for key, value in entry.items() if key != "failures"}
                  for name, entry in summary.items()}, indent=2))
