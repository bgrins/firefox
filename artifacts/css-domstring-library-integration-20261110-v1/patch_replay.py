import argparse
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile

ROOT = Path(__file__).resolve().parent
parser = argparse.ArgumentParser()
parser.add_argument("--library", type=Path, required=True)
parser.add_argument("--lean", type=Path, required=True)
parser.add_argument("--out", type=Path, required=True)
args = parser.parse_args()
library, lean, out = args.library.resolve(), args.lean.resolve(), args.out.resolve()
if out.exists():
    raise ValueError("Fresh output directory required")
changes = json.loads((ROOT / "LIBRARY-CHANGES.json").read_text())
patch = ROOT / "integration.patch"
if hashlib.sha256(patch.read_bytes()).hexdigest() != changes["patch_sha256"]:
    raise ValueError("Patch digest mismatch")
with tempfile.TemporaryDirectory(prefix="patch-source-", dir=ROOT) as directory:
    work = Path(directory)
    archive = subprocess.run(["git", "-C", str(library), "archive", changes["base"]],
                             check=True, capture_output=True).stdout
    with tarfile.open(fileobj=io.BytesIO(archive)) as source:
        source.extractall(work, filter="data")
    environment = dict(os.environ, GIT_CEILING_DIRECTORIES=str(work.parent))
    for mode in [["--check"], []]:
        subprocess.run(["git", "apply", *mode, str(patch)], cwd=work, env=environment, check=True)
    for name, expected in changes["paths"].items():
        if hashlib.sha256((work / name).read_bytes()).hexdigest() != expected:
            raise ValueError("Reconstructed path mismatch: " + name)
    subprocess.run([sys.executable, "-O", str(ROOT / "replay.py"), "--library", str(work),
                    "--lean", str(lean), "--out", str(out)], check=True)
    result = {"status": "pass", "base": changes["base"], "patch_sha256": changes["patch_sha256"],
              "exact_paths": changes["paths"], "git_index_used": False,
              "native_or_browser_work": False, "temporary_archive_tree_removed": True}
(out / "patch-reconstruction.json").write_text(json.dumps(result, indent=2) + "\n")
print(f"Exact {len(changes['paths'])}-path patch reconstructed and checked; temporary source tree removed")
