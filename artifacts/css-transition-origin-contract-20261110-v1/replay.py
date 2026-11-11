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
    parser.add_argument("--lean", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parent
    manifest = root / "SOURCE-ONLY.json"
    files = json.loads(manifest.read_text())
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    with tempfile.TemporaryDirectory(prefix="css-transition-source-") as temporary:
        scratch = Path(temporary)
        for name, expected in files.items():
            relative = Path(name)
            assert not relative.is_absolute() and ".." not in relative.parts
            source = root / relative
            assert hashlib.sha256(source.read_bytes()).hexdigest() == expected, name
            target = scratch / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
        shutil.copyfile(manifest, scratch / "SOURCE-ONLY.json")
        with (out / "stdout.log").open("wb") as stdout, (out / "stderr.log").open("wb") as stderr:
            result = subprocess.run([sys.executable, "-I", "-B", str(scratch / "check.py"),
                                     "--lean", str(args.lean.resolve()), "--out", str(out / "check")],
                                    stdout=stdout, stderr=stderr)
        assert result.returncode == 0, result.returncode
    (out / "REPLAY.json").write_text(json.dumps({
        "source_manifest_sha256": hashlib.sha256(manifest.read_bytes()).hexdigest(),
        "inputs": len(files), "temporary_source_copy_removed": not scratch.exists(), "status": "PASS",
    }, indent=2) + "\n")


if __name__ == "__main__":
    main()
