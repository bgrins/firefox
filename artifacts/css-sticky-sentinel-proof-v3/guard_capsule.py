import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise RuntimeError("Require python3 -I -S without optimization")
sys.dont_write_bytecode = True

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
CAPSULE = HERE / "capsule"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def seal(root):
    entries = [{"path": str(p.relative_to(root)), "sha256": sha(p)}
               for p in sorted(root.rglob("*")) if p.is_file()
               and str(p.relative_to(root)) not in ["FILES.json", "FREEZE.json"]]
    (root / "FILES.json").write_text(json.dumps({"files": entries}, indent=2) + "\n")
    digest = sha(root / "FILES.json")
    (root / "FREEZE.json").write_text(json.dumps({"manifest_sha256": digest}) + "\n")
    return digest


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    expected = json.loads((HERE / "CAPSULE-IDENTITY.json").read_text())["manifest_sha256"]
    assert sha(CAPSULE / "FILES.json") == expected
    records = []
    names = ["no-isolation", "site-enabled", "optimized-python", "double-optimized-python", "unsafe-shadow", "wrong-manifest", "changed-lean",
             "missing-cases", "extra-cache", "empty-directory", "symlink", "fifo",
             "nested-cache-resealed-outer", "nested-source-resealed-both", "resealed-toolchain",
             "existing-output", "inside-output"]
    for name in names:
        with tempfile.TemporaryDirectory(prefix="sticky-capsule-guard-") as temporary:
            work = Path(temporary)
            root = work / "capsule"
            shutil.copytree(CAPSULE, root)
            output = work / "output"
            flags = ["-I", "-S"]
            digest = expected
            reason = ""
            if name == "no-isolation":
                flags = ["-S"]
                reason = "Require python3 -I -S"
            elif name == "site-enabled":
                flags = ["-I"]
                reason = "Require python3 -I -S"
            elif name in ["optimized-python", "double-optimized-python"]:
                flags.append("-O" if name == "optimized-python" else "-OO")
                reason = "Require python3 -I -S"
            elif name == "unsafe-shadow":
                flags = ["-S"]
                (root / "json.py").write_text("raise RuntimeError(\"SHADOW_EXECUTED\")\n")
                reason = "Require python3 -I -S"
            elif name == "wrong-manifest":
                digest = "0" * 64
                reason = "external manifest identity"
            elif name == "changed-lean":
                path = root / "lean/MaskedSticky.lean"
                path.write_text(path.read_text() + "\n")
                reason = "file hash: lean/MaskedSticky.lean"
            elif name == "missing-cases":
                (root / "native-source/CASES.json").unlink()
                reason = "closed files"
            elif name in ["extra-cache", "nested-cache-resealed-outer"]:
                base = root / "native-source" if name.startswith("nested") else root
                (base / "__pycache__").mkdir()
                (base / "__pycache__/shadow.pyc").write_bytes(b"guard")
                if name.startswith("nested"):
                    digest = seal(root)
                reason = "closed files"
            elif name == "empty-directory":
                (root / "unused").mkdir()
                reason = "closed directories"
            elif name == "symlink":
                (root / "linked").symlink_to("lean/MaskedSticky.lean")
                reason = "nonregular capsule entry"
            elif name == "fifo":
                os.mkfifo(root / "pipe")
                reason = "nonregular capsule entry"
            elif name == "nested-source-resealed-both":
                path = root / "native-source/core.py"
                path.write_text(path.read_text() + "\n")
                seal(root / "native-source")
                digest = seal(root)
                reason = "external manifest identity"
            elif name == "resealed-toolchain":
                path = root / "LEAN-TOOLCHAIN.json"
                data = json.loads(path.read_text())
                data["entries"][0]["sha256"] = "0" * 64
                path.write_text(json.dumps(data))
                digest = seal(root)
                reason = "Lean inventory identity"
            elif name == "existing-output":
                output.mkdir()
                reason = "new external output required"
            elif name == "inside-output":
                output = root / "output"
                reason = "new external output required"
            command = [sys.executable, *flags, str(root / "check.py"),
                       "--manifest-sha", digest, "--output", str(output)]
            process = subprocess.run(command, cwd=work, capture_output=True, text=True)
            log = process.stdout + process.stderr
            (args.output / (name + ".log")).write_text(log)
            assert process.returncode != 0 and reason in log, name
            assert "SHADOW_EXECUTED" not in log, name
            assert not output.exists() or name == "existing-output", name
            assert not (output / "COMMANDS.json").exists(), name
            records.append({"name": name, "exit": process.returncode, "reason": reason,
                            "before_compiler_dispatch": True})
    result = {"status": "pass", "controls": records, "temporary_copies_removed": True}
    (args.output / "RESULT.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"status": "pass", "controls": len(records)}))


if __name__ == "__main__":
    main()
