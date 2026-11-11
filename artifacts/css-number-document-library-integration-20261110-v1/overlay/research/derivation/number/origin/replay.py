import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--lean", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parent
    manifest = json.loads((root / "SOURCE-ONLY.json").read_text())
    for name, expected in manifest.items():
        if hashlib.sha256((root / name).read_bytes()).hexdigest() != expected:
            raise ValueError("Source changed: " + name)
    with tempfile.TemporaryDirectory(prefix="number-document-source-only-") as directory:
        work = Path(directory)
        for name in list(manifest) + ["SOURCE-ONLY.json"]:
            destination = work / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(root / name, destination)
        subprocess.run([sys.executable, "-B", str(work / "check.py"),
                        "--lean", str(args.lean.resolve()), "--out", str(args.out.resolve())], check=True)
    for name, expected in manifest.items():
        if hashlib.sha256((root / name).read_bytes()).hexdigest() != expected:
            raise ValueError("Source changed during replay: " + name)


if __name__ == "__main__":
    main()
