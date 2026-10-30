import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
states = json.loads((HERE / "STATES.json").read_text())
for name, pin in json.loads((HERE / "REFERENCES.json").read_text()).items():
    assert sha(ROOT / name) == pin
for state in states.values():
    for pin in state.values():
        assert sha(ROOT / pin["path"]) == pin["sha256"]
assert states["common"]["servo/components/style/properties/cascade.rs"] == states["base"]["servo/components/style/properties/cascade.rs"]
scratch = Path(tempfile.mkdtemp(prefix="color-image-shared-", dir="/private/tmp"))
records = []

def verify(state):
    for name, pin in states[state].items():
        assert sha(scratch / name) == pin["sha256"]

def apply(name, state, reverse=False):
    command = ["/usr/bin/patch", "-f", "-F", "0", "-p1", "-i", str(HERE / name)]
    if reverse:
        command.append("-R")
    result = subprocess.run(command, cwd=scratch, capture_output=True, text=True)
    records.append({"patch": name, "reverse": reverse, "exit": result.returncode, "output": result.stdout + result.stderr})
    assert result.returncode == 0
    verify(state)

try:
    for name, pin in states["base"].items():
        target = scratch / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((ROOT / pin["path"]).read_bytes())
    for first, second, middle in [("01-union-above-shared.patch", "02-image-after-union.patch", "A"), ("01-image-above-shared.patch", "02-union-after-image.patch", "I")]:
        apply("00-shared-native.patch", "common")
        apply(first, middle)
        apply(second, "narrow")
        apply(second, middle, reverse=True)
        apply(first, "common", reverse=True)
        apply("00-shared-native.patch", "base", reverse=True)
finally:
    shutil.rmtree(scratch)
assert not scratch.exists()
result = {"two_orders_exact_narrow": True, "standalone_above_common_exact_A_and_I": True, "common_cascade_unchanged": True, "all_reverse_routes_exact_base": True, "scratch": str(scratch), "scratch_removed": True, "native_compile": False, "neutrality_proved": False, "compiler_warnings_checked": False, "browser": False, "git": False, "operations": records}
(HERE / "REPLAY.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
print(json.dumps({key: value for key, value in result.items() if key != "operations"}))
