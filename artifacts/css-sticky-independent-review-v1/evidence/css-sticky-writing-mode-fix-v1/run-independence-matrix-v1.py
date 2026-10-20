import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import traceback

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
SOURCE = ROOT / "layout/generic/StickyScrollContainer.cpp"
PYTHON = "/Users/bgrins/venvs/firefox/bin/python"
ENV = {**os.environ, "MOZ_SKIP_PATH_PERFORMANCE_CHECK": "1"}
OUTPUT = HERE / "INDEPENDENCE-MATRIX-v1.json"
assert not OUTPUT.exists()


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def save(record):
    OUTPUT.write_text(json.dumps(record, indent=2) + "\n")


packaging = json.loads((HERE / "standalone-apply-v1.json").read_text())
variants = {name: (HERE / ("variant-" + name + ".cpp")).read_bytes()
            for name in packaging["variants_sha256"]}
for name, content in variants.items():
    assert hashlib.sha256(content).hexdigest() == packaging["variants_sha256"][name]
assert SOURCE.read_bytes() == variants["combined"]
paths = set()
for name in ("wpt-candidate-v1", "regressions-candidate-v1", "timelines-candidate-v1"):
    receipt = json.loads((HERE / (name + "-receipt.json")).read_text())
    assert receipt["all_inputs_unchanged"] and receipt["exit_code"] == 0
    paths.update(p for p in receipt["pins_before"] if not p.startswith("objdir-"))
changed = subprocess.check_output(
    ["git", "-c", "core.fsmonitor=false", "diff", "--name-only", "--",
     "layout", "gfx", "dom", "servo"], cwd=ROOT, text=True).splitlines()
paths.update(changed)
paths.remove(str(SOURCE.relative_to(ROOT)))
paths.add(str(Path(__file__).relative_to(ROOT)))
paths.add(str((HERE / "run-matrix-wpt-v1.py").relative_to(ROOT)))


def pins():
    return {name: digest(ROOT / name) for name in sorted(paths)}


fixed = pins()
record = {"status": "RUNNING", "fixed_inputs_before": fixed,
          "variants": packaging["variants_sha256"], "runs": [],
          "scope": "Four StickyScrollContainer source variants in the same combined project worktree; not clean-base Firefox builds."}
save(record)


def build(name):
    path = HERE / ("matrix-build-" + name + "-v1.log")
    assert not path.exists()
    command = [PYTHON, "./mach", "build", "binaries"]
    with path.open("w") as output:
        result = subprocess.run(command, cwd=ROOT, env=ENV, stdout=output,
                                stderr=subprocess.STDOUT)
    info = {"variant": name, "command": command, "exit_code": result.returncode,
            "log_sha256": digest(path), "source_sha256": digest(SOURCE),
            "monitor_export_keyerrors": path.read_text().count("KeyError: 'export'")}
    return info


def expected(name):
    auto = {"PASS": 216, "OK": 1} if name in ("auto-only", "combined") else {"PASS": 198, "FAIL": 18, "OK": 1}
    writing = {"PASS": 1080, "OK": 1} if name in ("writing-only", "combined") else {"PASS": 912, "FAIL": 168, "OK": 1}
    return {"/css/css-position/sticky/position-sticky-auto-inset-reduction.html": auto,
            "/css/css-position/sticky/position-sticky-containing-block-writing-mode.html": writing}


failure = None
combined_built = False
try:
    for name in ("original", "auto-only", "writing-only", "combined"):
        assert pins() == fixed
        SOURCE.write_bytes(variants[name])
        current = {"variant": name, "build": build(name)}
        record["runs"].append(current)
        save(record)
        assert current["build"]["exit_code"] == 0, current
        combined_built = name == "combined"
        phase = "matrix-" + name + "-v1"
        log = HERE / (phase + "-runner.log")
        with log.open("w") as output:
            result = subprocess.run([PYTHON, str(HERE / "run-matrix-wpt-v1.py"), phase],
                                    cwd=ROOT, env=ENV, stdout=output, stderr=subprocess.STDOUT)
        receipt_path = HERE / (phase + "-receipt.json")
        receipt = json.loads(receipt_path.read_text())
        current.update({"wpt_exit": result.returncode, "counts": receipt["counts"],
                        "receipt_sha256": digest(receipt_path), "runner_log_sha256": digest(log),
                        "stable_wpt_inputs": receipt["all_inputs_unchanged"],
                        "matches_expected": receipt["counts"] == expected(name),
                        "stable_other_sources": pins() == fixed})
        save(record)
        print(json.dumps(current), flush=True)
        assert result.returncode == (0 if name == "combined" else 1)
        assert receipt["suite_end_count"] == 1 and receipt["all_inputs_unchanged"]
        assert receipt["absent_before"] == receipt["absent_after"]
        assert current["matches_expected"] and current["stable_other_sources"]
except BaseException:
    failure = traceback.format_exc()
finally:
    if SOURCE.read_bytes() != variants["combined"] or not combined_built:
        SOURCE.write_bytes(variants["combined"])
        record["recovery_build"] = build("restore-combined")
        combined_built = record["recovery_build"]["exit_code"] == 0
    record.update({"failure": failure, "final_source_sha256": digest(SOURCE),
                   "final_combined_build_succeeded": combined_built,
                   "fixed_inputs_after": pins(),
                   "status": "PASS" if failure is None and combined_built and pins() == fixed else "FAIL"})
    save(record)
print(json.dumps({k: record[k] for k in ("status", "failure", "final_source_sha256", "final_combined_build_succeeded")}), flush=True)
sys.exit(0 if record["status"] == "PASS" else 1)
