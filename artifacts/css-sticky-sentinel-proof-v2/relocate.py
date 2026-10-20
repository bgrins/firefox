import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise RuntimeError("Require python3 -I -S without optimization")
sys.dont_write_bytecode = True

import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
CAPSULE = HERE / "capsule"
identity = json.loads((HERE / "CAPSULE-IDENTITY.json").read_text())
assert hashlib.sha256((CAPSULE / "FILES.json").read_bytes()).hexdigest() == identity["manifest_sha256"]
output = HERE / "relocated-replay-v1"
assert not output.exists()
with tempfile.TemporaryDirectory(prefix="sticky-relocated-source-") as temporary:
    copy = Path(temporary) / "capsule"
    shutil.copytree(CAPSULE, copy)
    before = {str(p.relative_to(copy)): hashlib.sha256(p.read_bytes()).hexdigest()
              for p in copy.rglob("*") if p.is_file()}
    command = [sys.executable, "-I", "-S", str(copy / "check.py"),
               "--manifest-sha", identity["manifest_sha256"], "--output", str(output)]
    with (HERE / "relocated-replay-v1.log").open("w") as log:
        result = subprocess.run(command, cwd=temporary, stdout=log, stderr=subprocess.STDOUT)
    after = {str(p.relative_to(copy)): hashlib.sha256(p.read_bytes()).hexdigest()
             for p in copy.rglob("*") if p.is_file()}
    assert before == after and result.returncode == 0
original = HERE / "combined-replay-v1"
assert json.loads((output / "RESULT.json").read_text()) == json.loads((original / "RESULT.json").read_text())
paths = [str(p.relative_to(original)) for p in original.glob("native/*/raw.jsonl")]
paths += [str(p.relative_to(original)) for p in original.glob("calibration/*.jsonl")]
paths += [str(p.relative_to(original)) for p in original.glob("lifecycle-mutants/*.jsonl")]
assert len(paths) == 20
for name in paths:
    assert (original / name).read_bytes() == (output / name).read_bytes(), name
record = {"exit": result.returncode, "command": command, "source_unchanged": True,
          "temporary_source_copy_removed": True, "identical_raw_streams": paths,
          "manifest_sha256": identity["manifest_sha256"]}
(HERE / "RELOCATION.json").write_text(json.dumps(record, indent=2) + "\n")
print(json.dumps({"exit": result.returncode, "identical_streams": len(paths)}))
