import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sha = lambda value: hashlib.sha256(value).hexdigest()
read = lambda path: json.loads(path.read_text())
policy = read(HERE / "PAYLOAD.json")
for name, digest in read(HERE / "REFERENCES.json").items():
    assert sha((ROOT / name).read_bytes()) == digest, name
roles = policy["source_roles"]
assert sum(r["kind"] == "native" for r in roles.values()) == 7
assert sum(r["kind"] == "wpt" for r in roles.values()) == 7
for name, role in roles.items():
    assert sha((HERE / role["payload"]).read_bytes()) == role["candidate_sha256"], name
    if role["kind"] == "wpt":
        assert (HERE / role["payload"]).read_bytes() == (ROOT / role["origin"]).read_bytes()
changed = [name for name, role in roles.items() if role.get("cleanup_changed")]
assert changed == ["servo/components/style/values/computed/length_percentage.rs", "servo/components/style/values/specified/length.rs"]
assert (HERE / "CLEANUP.patch").read_text().count("@@ -") == 3
logs = []
def apply(directory, patch, reverse=False):
    cmd = ["/usr/bin/patch", "-p1", "--fuzz=0", "--batch"]
    if reverse:
        cmd.append("-R")
    proc = subprocess.run(cmd, input=patch.read_bytes(), cwd=directory, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    logs.append(proc.stdout.decode())
    assert proc.returncode == 0 and b"offset" not in proc.stdout and b"fuzz" not in proc.stdout, logs[-1]
with tempfile.TemporaryDirectory(prefix="css-zoom139-transport-", dir="/private/tmp") as temporary:
    top = Path(temporary)
    for name, role in roles.items():
        target = top / name
        target.parent.mkdir(parents=True, exist_ok=True)
        if role["base"]:
            target.write_bytes((ROOT / role["base"]).read_bytes())
    apply(top, HERE / "fix.patch")
    for name, role in roles.items():
        assert sha((top / name).read_bytes()) == role["candidate_sha256"]
    apply(top, HERE / "fix.patch", reverse=True)
    for name, role in roles.items():
        if role["base"]:
            assert sha((top / name).read_bytes()) == role["base_sha256"]
        else:
            assert not (top / name).exists()
    for name, role in roles.items():
        if role["kind"] == "native":
            (top / name).write_bytes((ROOT / role["current"]).read_bytes())
    apply(top, HERE / "CLEANUP.patch")
    for name, role in roles.items():
        if role["kind"] == "native":
            assert sha((top / name).read_bytes()) == role["candidate_sha256"]
    apply(top, HERE / "CLEANUP.patch", reverse=True)
    for name, role in roles.items():
        if role["kind"] == "native":
            assert sha((top / name).read_bytes()) == role["current_sha256"]
assert not Path(temporary).exists()
print(json.dumps({"complete": True, "native": 7, "wpt": 7, "cleanup_hunks": 3,
                  "full_patch_forward_reverse": True, "cleanup_forward_reverse": True,
                  "offset_or_fuzz": False, "owned_scratch_removed": True,
                  "live_tree_modified": False, "build_lint_browser_executed": False,
                  "patch_output": logs}, indent=2))
