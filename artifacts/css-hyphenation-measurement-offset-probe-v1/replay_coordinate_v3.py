import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

here = Path(__file__).resolve().parent
repo = here.parents[1]
source = here.parent / "css-hyphenation-coordinate-companion-v3"
expected = "fb3ece607d89bb1524bcf7dc8ee5b630bed41351ea1d46972d4bb50ccbf59ec2"
assert hashlib.sha256((source / "MANIFEST.json").read_bytes()).hexdigest() == expected
files = json.loads((source / "MANIFEST.json").read_text())["files"]
record = here / "root-coordinate-replay-v3"
record.mkdir()
temporary = Path(tempfile.mkdtemp(prefix="hyphen-coordinate-root-", dir="/private/tmp"))
capsule = temporary / "capsule"
capsule.mkdir()
for name in set(files) | {"MANIFEST.json", "FREEZE.json"}:
    relative = Path(name)
    assert not relative.is_absolute() and ".." not in relative.parts
    original = source / relative
    assert not original.is_symlink()
    if name in files:
        assert hashlib.sha256(original.read_bytes()).hexdigest() == files[name], name
    target = capsule / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(original, target)
output = temporary / "output"
lean = repo / "artifacts/stylo-bloom-tools/lean-4.35.0-rc4-darwin_aarch64/bin/lean"
command = ["python3", "-I", "-S", "-B", str(capsule / "check.py"),
           "--manifest-sha", expected, "--lean", str(lean), "--output", str(output)]
launch = {"source_manifest_sha256": expected, "input_files": len(files),
          "fresh_relocated_source_only": True, "command": command, "output": str(output)}
(record / "LAUNCH.json").write_text(json.dumps(launch, indent=2) + "\n")
with (record / "driver.log").open("w") as log:
    result = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT)
for name in ["RESULT.json", "COMMANDS.json"]:
    if (output / name).exists():
        shutil.copy2(output / name, record / name)
for pattern in ["*.stdout", "*.stderr"]:
    for path in output.glob(pattern):
        shutil.copy2(path, record / path.name)
process = {"exit_code": result.returncode, "launch": launch,
           "driver_sha256": hashlib.sha256((record / "driver.log").read_bytes()).hexdigest()}
(record / "PROCESS.json").write_text(json.dumps(process, indent=2) + "\n")
print("Fresh coordinate replay exit", result.returncode, "output", output)
raise SystemExit(result.returncode)
