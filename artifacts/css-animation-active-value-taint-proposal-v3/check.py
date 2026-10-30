import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OLD = ROOT / "artifacts/css-animation-active-value-taint-proposal-v2"
read = lambda p: json.loads(p.read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
for name, pin in read(HERE / "REFERENCES.json").items():
    assert sha(ROOT / name) == pin
roles = read(HERE / "SOURCE-ROLES.json")
previous = read(OLD / "SOURCE-ROLES.json")
edits = read(HERE / "EDITS.json")
assert set(roles) == set(previous) and len(roles) == 4
assert set(edits) == {"servo/components/style/properties/cascade.rs"}
for name, role in roles.items():
    assert role["base_capture"] == previous[name]["base_capture"]
    assert role["base_sha256"] == previous[name]["base_sha256"]
    before = ROOT / previous[name]["candidate_capture"]
    assert sha(before) == previous[name]["candidate_sha256"]
    text = before.read_text()
    for old, new in edits.get(name, []):
        assert text.count(old) == 1
        text = text.replace(old, new)
    assert text == (ROOT / role["candidate_capture"]).read_text()
    for kind in ("base", "candidate"):
        assert sha(ROOT / role[kind + "_capture"]) == role[kind + "_sha256"]
clean = read(HERE / "CLEAN-PROVIDER.json")
old_clean = read(OLD / "CLEAN-PROVIDER.json")
text = (ROOT / old_clean["candidate_capture"]).read_text()
for old, new in edits.get("servo/components/style/custom_properties.rs", []):
    assert text.count(old) == 1
    text = text.replace(old, new)
assert text == (ROOT / clean["candidate_capture"]).read_text()
for use_clean in (False, True):
    inputs = {name: clean if use_clean and name.endswith("/custom_properties.rs") else role for name, role in roles.items()}
    with tempfile.TemporaryDirectory(prefix="css-taint-v3-patch-") as directory:
        scratch = Path(directory)
        for name, role in inputs.items():
            path = scratch / name
            path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / role["base_capture"], path)
        for reverse in (False, True):
            patch = HERE / ("native-clean-provider.patch" if use_clean else "native.patch")
            command = ["patch", "--batch", "-p1", "-i", str(patch)] + (["-R"] if reverse else [])
            result = subprocess.run(command, cwd=scratch, capture_output=True, text=True)
            assert result.returncode == 0, result.stdout + result.stderr
            for name, role in inputs.items():
                assert sha(scratch / name) == role["base_sha256" if reverse else "candidate_sha256"]
    assert not scratch.exists()
print(json.dumps({"source_roles": 4, "changed_postimages": 1, "exact_replacements": 1, "held_and_clean_patch_roundtrips": True, "scratch_removed": True, "native_compiled": False, "browser_executed": False}))
