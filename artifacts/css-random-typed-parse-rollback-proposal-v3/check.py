from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
roles = json.loads((HERE / "SOURCE-ROLES.json").read_text())
records = []
with tempfile.TemporaryDirectory(prefix="random-typed-transport-", dir="/private/tmp") as work:
    work = Path(work)
    for name in roles:
        destination = work / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(HERE / "base" / name, destination)
    for reverse in (False, True, False):
        command = ["patch", "-p1", "--fuzz=0", "--batch"] + (["-R"] if reverse else [])
        result = subprocess.run(command, cwd=work, input=(HERE / "native.patch").read_text(), capture_output=True, text=True)
        records.append({"reverse": reverse, "exit": result.returncode, "stdout": result.stdout, "stderr": result.stderr})
        assert result.returncode == 0 and "offset" not in result.stdout and "fuzz" not in result.stdout
        for name, pins in roles.items():
            assert hashlib.sha256((work / name).read_bytes()).hexdigest() == pins["base_sha256" if reverse else "candidate_sha256"]
    for name in roles:
        result = subprocess.run(["rustfmt", "--edition", "2024", "--config", "skip_children=true,match_block_trailing_comma=true", "--check", str(work / name)], capture_output=True, text=True)
        assert result.returncode == 0, result.stdout + result.stderr
    scratch = str(work)
assert not Path(scratch).exists()
(HERE / "CHECK.json").write_text(json.dumps({"transport": records, "exact_four_paths": list(roles), "rustfmt_check": True, "scratch_removed": True, "native_typecheck": False, "browser_test": False}, indent=2) + "\n")
print("Exact four-path forward/reverse/reapply and Rust formatting passed; private scratch removed.")
