import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
NATIVE = ROOT / "servo/components/style/custom_properties_map.rs"
PINS = json.loads((HERE / "SOURCE-PINS.json").read_text())
ENV = {**os.environ, "MOZ_SKIP_PATH_PERFORMANCE_CHECK": "1"}


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def run(command, name):
    with (HERE / name).open("w") as output:
        result = subprocess.run(command, cwd=ROOT, env=ENV, stdout=output,
                                stderr=subprocess.STDOUT)
    print(name, result.returncode, flush=True)
    return result.returncode


assert digest(NATIVE) == PINS["combined"]
git = ["git", "-c", "core.fsmonitor=false"]
changed = subprocess.check_output(git + ["diff", "--name-only"], cwd=ROOT).decode().splitlines()
stable_files = [ROOT / name for name in changed if ROOT / name != NATIVE]
stable_files += list((ROOT / "testing/web-platform/tests/css/css-variables").joinpath(name) for name in [
    "invalid-custom-property-enumeration.html", "resurrected-custom-property-enumeration.html",
    "custom-property-enumeration-shadowing.html"])
stable = {str(path.relative_to(ROOT)): digest(path) for path in stable_files}
record = {"head": subprocess.check_output(git + ["rev-parse", "HEAD"], cwd=ROOT).decode().strip(),
          "stable_sources_tests": stable, "runs": [], "scope": "Three local shared-tree builds, no isolated-upstream runtime claim."}
try:
    for variant in ["original", "count-only", "combined"]:
        assert all(digest(ROOT / name) == pin for name, pin in stable.items())
        snapshot = HERE / "source" / (variant + ".rs")
        assert digest(snapshot) == PINS[variant]
        NATIVE.write_bytes(snapshot.read_bytes())
        entry = {"variant": variant, "source": PINS[variant]}
        record["runs"].append(entry)
        entry["build_exit"] = run(["./mach", "build", "binaries"], variant + "-build.log")
        assert entry["build_exit"] == 0
        assert digest(NATIVE) == PINS[variant]
        entry["binaries"] = {name: digest(ROOT / "objdir-full.noindex/dist/Nightly.app/Contents/MacOS" / name)
                             for name in ["firefox", "XUL"]}
        entry["runner_exit"] = run([sys.executable, str(HERE / "run.py"), variant], variant + "-driver.log")
        assert entry["runner_exit"] == 0
        assert all(digest(ROOT / name) == pin for name, pin in stable.items())
        assert digest(NATIVE) == PINS[variant]
        (HERE / "BUILD-MATRIX.json").write_text(json.dumps(record, indent=2) + "\n")
finally:
    if digest(NATIVE) != PINS["combined"]:
        NATIVE.write_bytes((HERE / "source/combined.rs").read_bytes())
    record["combined_source_restored"] = digest(NATIVE) == PINS["combined"]
    (HERE / "BUILD-MATRIX.json").write_text(json.dumps(record, indent=2) + "\n")
