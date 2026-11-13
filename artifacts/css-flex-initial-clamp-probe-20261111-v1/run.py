import hashlib
import json
import os
from pathlib import Path
import runpy
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
manifest = ROOT / "dom/flex/test/chrome.toml"
target = ROOT / "dom/flex/test/chrome/test_flex_initial_clamp_probe.html"
original = (HERE / "before/chrome.toml").read_bytes()
probe = (HERE / target.name).read_bytes()
staged = original + b'\n["chrome/test_flex_initial_clamp_probe.html"]\n'
pins = json.loads((HERE / "BEFORE.json").read_text())
for name, expected in pins.items():
    assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == expected, name
assert not target.exists()
assert not (HERE / "COMMAND.json").exists()
relative = HERE.relative_to(ROOT)
argv = ["/Users/bgrins/venvs/firefox/bin/python", "./mach", "mochitest", "--flavor=chrome", "--headless", "--log-raw=" + str(relative / "raw.log"), str(target.relative_to(ROOT))]
(HERE / "COMMAND.json").write_text(json.dumps(argv, indent=2) + "\n")
env = dict(os.environ, MOZ_SKIP_PATH_PERFORMANCE_CHECK="1", MOZCONFIG=str(ROOT / "mozconfig"), MOZ_OBJDIR=str(ROOT / "objdir-full.noindex"), GIT_OPTIONAL_LOCKS="0")
runner = runpy.run_path(str(HERE / "process.py"))["Runner"](HERE)
target.write_bytes(probe)
manifest.write_bytes(staged)
(HERE / "STAGED.json").write_text(json.dumps({str(target.relative_to(ROOT)): hashlib.sha256(probe).hexdigest(),str(manifest.relative_to(ROOT)):hashlib.sha256(staged).hexdigest()},indent=2)+"\n")
try:
    record, _ = runner.run(argv, ROOT, env, "baseline", timeout=600)
finally:
    if runner.safe_cleanup:
        assert target.read_bytes() == probe
        assert manifest.read_bytes() == staged
        manifest.write_bytes(original)
        target.unlink()
        for name, expected in pins.items():
            assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == expected, name
        (HERE / "RESTORED.json").write_text(json.dumps({"status":"PASS","manifest_exact":True,"temporary_test_absent":not target.exists(),"protected_files_exact":len(pins),"groups":runner.groups},indent=2)+"\n")
    else:
        (HERE / "RESTORE-PENDING.json").write_text(json.dumps({"reason":"Owned process absence not established; staged inputs retained","groups":runner.groups},indent=2)+"\n")
print(json.dumps(record))
sys.exit(record["exit"])
