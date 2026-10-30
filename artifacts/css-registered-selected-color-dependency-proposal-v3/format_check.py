from pathlib import Path
import difflib
import hashlib
import json
import shutil
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
PREVIOUS = HERE.with_name("css-registered-selected-color-dependency-proposal-v2")
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
for name, row in json.loads((HERE / "REFERENCES.json").read_text()).items():
    assert sha(ROOT / name) == row["sha256"]
for name, row in json.loads((PREVIOUS / "FILES.json").read_text()).items():
    assert sha(PREVIOUS / name) == row["sha256"]
roles = json.loads((HERE / "SOURCE-ROLES.json").read_text())
tools = json.loads((HERE / "TOOLCHAIN.json").read_text())["tools"]
with tempfile.TemporaryDirectory(prefix="css-color-format-replay-") as temporary:
    temporary = Path(temporary)
    delta = []
    for rel, row in roles.items():
        old = PREVIOUS / "candidate" / rel
        new = HERE / "candidate" / rel
        assert sha(old) == row["v2_candidate_sha256"]
        assert sha(new) == row["candidate_sha256"]
        for index, tool in enumerate(tools):
            assert sha(Path(tool["path"])) == tool["sha256"]
            copy = temporary / str(index) / rel
            copy.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(old, copy)
            args = [tool["path"], "--config-path", str(HERE / "rustfmt.toml"), str(copy)]
            for command in [args, args[:1] + ["--check"] + args[1:]]:
                result = subprocess.run(command, capture_output=True, text=True)
                assert result.returncode == 0 and not result.stderr, result
            assert copy.read_bytes() == new.read_bytes()
        delta.extend(difflib.unified_diff(old.read_text().splitlines(True), new.read_text().splitlines(True), fromfile="a/" + rel, tofile="b/" + rel))
    assert "".join(delta) == (HERE / "FORMAT-DELTA.patch").read_text()
assert not temporary.exists()
print(json.dumps({"postimages": len(roles), "formatters": len(tools), "identical_outputs": True, "idempotent_checks": True, "exact_delta": True, "scratch_removed": True}))
