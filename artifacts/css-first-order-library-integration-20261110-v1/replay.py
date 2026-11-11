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
    sources = json.loads((root / "SOURCE-ONLY.json").read_text())
    for name, expected in sources.items():
        if hashlib.sha256((root / name).read_bytes()).hexdigest() != expected:
            raise ValueError("Changed source: " + name)
    with tempfile.TemporaryDirectory(prefix="css-first-order-integration-") as directory:
        work = Path(directory)
        for prefix in ["base/", "overlay/"]:
            for name in sources:
                if name.startswith(prefix):
                    target = work / name[len(prefix):]
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(root / name, target)
        subprocess.run([sys.executable, "-B", str(work / "derivation_check.py"),
                        "--lean", str(args.lean.resolve()), "--out", str(args.out.resolve())], check=True)
    for name, expected in sources.items():
        if hashlib.sha256((root / name).read_bytes()).hexdigest() != expected:
            raise ValueError("Source changed during replay: " + name)


if __name__ == "__main__":
    main()
