import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
VARIANT = sys.argv[1]
assert VARIANT in {"iterator-only", "original", "count-only", "combined"}
GIT = ["git", "-c", "core.fsmonitor=false"]
TESTS = ["testing/web-platform/tests/css/css-variables/" + name for name in [
    "invalid-custom-property-enumeration.html",
    "resurrected-custom-property-enumeration.html",
    "custom-property-enumeration-shadowing.html",
]]
TESTS += ["testing/web-platform/tests/css/" + name for name in [
    "cssom/cssstyledeclaration-custom-properties.html",
    "cssom/cssstyledeclaration-registered-custom-properties.html",
    "css-properties-values-api/registered-inherit-invalid.html",
    "css-properties-values-api/registered-substituted-inherit-restyle.html",
]]
BINARIES = ["objdir-full.noindex/dist/Nightly.app/Contents/MacOS/" + name
            for name in ["firefox", "XUL"]]


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


changed = subprocess.check_output(GIT + ["diff", "--name-only"], cwd=ROOT).decode().splitlines()
files = sorted(set(changed + TESTS + BINARIES))
pins = {name: digest(ROOT / name) for name in files}
record_path = HERE / (VARIANT + "-RUN.json")
assert not record_path.exists(), "Do not overwrite prior evidence"
command = ["./mach", "wpt", "--headless", "--processes=1",
           "--log-raw=" + str(HERE / (VARIANT + "-raw.json"))] + TESTS
with (HERE / (VARIANT + "-wpt.log")).open("w") as output:
    result = subprocess.run(command, cwd=ROOT, stdout=output, stderr=subprocess.STDOUT,
                            env={**os.environ, "MOZ_SKIP_PATH_PERFORMANCE_CHECK": "1"})
stable = all(digest(ROOT / name) == pin for name, pin in pins.items())
record_path.write_text(json.dumps({
    "variant": VARIANT, "command": command, "exit": result.returncode,
    "head": subprocess.check_output(GIT + ["rev-parse", "HEAD"], cwd=ROOT).decode().strip(),
    "pins": pins, "stable_after": stable,
    "scope": "Shared-tree local build; source-to-binary association requires the corresponding build receipt."
}, indent=2) + "\n")
print(VARIANT, result.returncode, "stable", stable, flush=True)
assert stable
assert result.returncode in {0, 1}
