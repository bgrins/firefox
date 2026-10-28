import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()

for name, digest in json.loads((HERE / "REFERENCES.json").read_text()).items():
    assert sha(ROOT / name) == digest, name
roles = json.loads((HERE / "COMBINED-SOURCE-ROLES.json").read_text())
assert len(roles["base"]) == len(roles["candidate"]) == 2
for role in roles.values():
    for name, pin in role.items():
        assert sha(ROOT / pin["capture"]) == pin["sha256"], name
records = []
with tempfile.TemporaryDirectory(prefix="registered-admission-proposal-check-", dir="/private/tmp") as temp:
    scratch = Path(temp)
    for name, pin in roles["base"].items():
        dest = scratch / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / pin["capture"], dest)
    for args in (["--check"], [], ["--reverse", "--check"], ["--reverse"], ["--check"], []):
        command = ["git", "apply", *args, str(HERE / "combined-native.patch")]
        result = subprocess.run(command, cwd=scratch, capture_output=True, text=True, timeout=20)
        records.append({"args": args, "exit": result.returncode, "stderr": result.stderr})
        assert result.returncode == 0, records[-1]
        if args in ([], ["--reverse"]):
            role = "base" if args else "candidate"
            for name, pin in roles[role].items():
                assert sha(scratch / name) == pin["sha256"], name
    for name in roles["candidate"]:
        command = ["rustfmt", "--edition", "2024", "--config", "match_block_trailing_comma=true,reorder_imports=false", "--emit", "stdout", str(scratch / name)]
        result = subprocess.run(command, cwd=scratch, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True, timeout=20)
        assert result.returncode == 0 and not result.stderr, result.stderr
assert not scratch.exists()
print(json.dumps({"status": "CAPTURED_TWO_PATH_TRANSPORT_AND_SYNTAX_PASS", "records": records, "source_roles": roles, "scratch_removed": True, "native_typecheck": False, "native_build": False, "browser": False}, indent=2))
