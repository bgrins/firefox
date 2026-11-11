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
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    manifest = json.loads((root / "SOURCE-ONLY.json").read_text())
    for name, expected in manifest.items():
        if hashlib.sha256((root / name).read_bytes()).hexdigest() != expected:
            raise ValueError("Changed source: " + name)
    commands = {}
    with tempfile.TemporaryDirectory(prefix="document-library-source-only-") as directory:
        work = Path(directory)
        for prefix in ["base/", "overlay/"]:
            for name in manifest:
                if name.startswith(prefix):
                    target = work / name[len(prefix):]
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(root / name, target)
        for checker, label in [("derivation_check.py", "first-order"), ("document_check.py", "document")]:
            p = subprocess.run([sys.executable, "-B", str(work / checker), "--lean",
                                str(args.lean.resolve()), "--out", str(out / label)],
                               cwd=work, capture_output=True, text=True)
            output = p.stdout + p.stderr
            (out / (label + ".log")).write_text(output)
            commands[label] = {"exit": p.returncode, "sha256": hashlib.sha256(output.encode()).hexdigest()}
            if p.returncode:
                raise ValueError(label + "\n" + output)
            print(output.strip(), flush=True)
    for name, expected in manifest.items():
        if hashlib.sha256((root / name).read_bytes()).hexdigest() != expected:
            raise ValueError("Source changed during replay: " + name)
    (out / "report.json").write_text(json.dumps({"status": "pass", "source_sha256": manifest,
        "commands": commands, "temporary_builds_removed": True, "default_css_target_built": False}, indent=2) + "\n")


if __name__ == "__main__":
    main()
