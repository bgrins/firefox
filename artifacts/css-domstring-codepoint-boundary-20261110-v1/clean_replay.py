import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent
parser = argparse.ArgumentParser()
parser.add_argument("--lean", type=Path, required=True)
parser.add_argument("--out", type=Path, required=True)
args = parser.parse_args()
manifest = json.loads((ROOT / "SOURCE-ONLY.json").read_text())
with tempfile.TemporaryDirectory(prefix="clean-source-", dir=ROOT) as directory:
    source = Path(directory)
    for name, expected in manifest["files"].items():
        data = (ROOT / name).read_bytes()
        if hashlib.sha256(data).hexdigest() != expected:
            raise ValueError("Source hash mismatch: " + name)
        target = source / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    subprocess.run([sys.executable, "-O", "check.py", "--lean", str(args.lean.resolve()),
                    "--out", str(args.out.resolve())], cwd=source, check=True)
print(f"Clean replay passed from exactly {len(manifest['files'])} copied source files; temporary sources removed")
