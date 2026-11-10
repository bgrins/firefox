import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--lean", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    sources = json.loads((ROOT / "SOURCE-ONLY.json").read_text())
    with tempfile.TemporaryDirectory(prefix="typed-codec-source-replay-", dir=out) as directory:
        work = Path(directory)
        for name, digest in sources.items():
            data = (ROOT / name).read_bytes()
            if hashlib.sha256(data).hexdigest() != digest:
                raise ValueError("Source hash mismatch: " + name)
            destination = work / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(data)
        command = ["python3", str(work / "check.py"), "--lean", str(args.lean.resolve()),
                   "--out", str(out / "verification")]
        process = subprocess.run(command, cwd=work, capture_output=True, text=True)
        (out / "check.log").write_text(process.stdout + process.stderr)
        if process.returncode:
            raise ValueError("Source-only replay failed")
    (out / "report.json").write_text(json.dumps({
        "status": "pass", "source_files": sources, "temporary_sources_removed": True,
        "verification": "verification/report.json"}, indent=2) + "\n")
    print(f"Source-only replay passed from {len(sources)} files; temporary sources removed")


if __name__ == "__main__":
    main()
