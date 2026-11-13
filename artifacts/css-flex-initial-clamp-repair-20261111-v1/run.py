import hashlib
import json
import os
from pathlib import Path
import runpy
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
stage = sys.argv[1]
assert stage in ["baseline", "build", "focused", "all-chrome"]
out = HERE / stage
out.mkdir()
pins = {**json.loads((HERE / "AFTER.json").read_text()), **json.loads((HERE / "PROTECTED.json").read_text())}
def authenticate():
    for name, expected in pins.items():
        assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == expected, name

def binaries():
    result = {}
    for name in ["firefox", "XUL"]:
        path = ROOT / "objdir-full.noindex/dist/Nightly.app/Contents/MacOS" / name
        digest = hashlib.sha256()
        with path.open("rb") as inp:
            for data in iter(lambda: inp.read(1024*1024), b""):
                digest.update(data)
        result[str(path.relative_to(ROOT))] = {"sha256":digest.hexdigest(), "bytes":path.stat().st_size}
    return result

authenticate()
(out / "BINARY-BEFORE.json").write_text(json.dumps(binaries(),indent=2)+"\n")
argv = ["/Users/bgrins/venvs/firefox/bin/python", "./mach"]
if stage == "build":
    argv += ["build", "binaries", "-j2"]
else:
    argv += ["mochitest", "--flavor=chrome", "--headless", "--log-raw=" + str((out / "raw.log").relative_to(ROOT)), "dom/flex/test" if stage == "all-chrome" else "dom/flex/test/chrome/test_flex_item_initial_clamp.html"]
(out / "COMMAND.json").write_text(json.dumps(argv,indent=2)+"\n")
env = dict(os.environ, MOZ_SKIP_PATH_PERFORMANCE_CHECK="1", MOZCONFIG=str(ROOT / "mozconfig"), MOZ_OBJDIR=str(ROOT / "objdir-full.noindex"), GIT_OPTIONAL_LOCKS="0")
runner = runpy.run_path(str(HERE / "process.py"))["Runner"](out)
try:
    record, _ = runner.run(argv, ROOT, env, stage, timeout=1200 if stage == "build" else 600)
finally:
    authenticate()
    (out / "BINARY-AFTER.json").write_text(json.dumps(binaries(),indent=2)+"\n")
print(json.dumps(record))
sys.exit(record["exit"])
