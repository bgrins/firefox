import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise SystemExit("Require python3 -I -S without optimization")
sys.dont_write_bytecode = True
import hashlib
import json
from pathlib import Path
import subprocess

root = Path(__file__).resolve().parent
if len(sys.argv) != 2:
    raise SystemExit("Expected external FILES SHA256")
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
assert sha(root / "FILES.json") == sys.argv[1]
files = json.loads((root / "FILES.json").read_text())
actual = set()
for path in root.rglob("*"):
    assert not path.is_symlink()
    if path.is_file():
        actual.add(str(path.relative_to(root)))
assert actual == set(files) | {"FILES.json"}
for name, expected in files.items():
    assert sha(root / name) == expected, name
result = subprocess.run([sys.executable, "-I", "-S", str(root / "recount.py")],
                        text=True, capture_output=True)
assert result.returncode == 0, result.stderr
assert not result.stderr
assert json.loads(result.stdout) == json.loads((root / "RECOUNT.json").read_text())
print(result.stdout.strip())
