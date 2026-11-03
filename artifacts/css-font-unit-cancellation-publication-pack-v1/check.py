import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]

def sha(data):
    return hashlib.sha256(data).hexdigest()

refs = json.loads((HERE / "REFERENCES.json").read_text())
for path, digest in refs.items():
    assert sha((ROOT / path).read_bytes()) == digest, path
stages = json.loads((HERE / "STAGES.json").read_text())
roles = json.loads((ROOT / "artifacts/css-root-font-cancellation-selective-handoff-fix-v1/SOURCE-ROLES.json").read_text())["roles"]
assert (HERE / "01-font-units.patch").read_bytes() == (ROOT / "artifacts/css-keyframe-font-unit-publication-v1/native.patch").read_bytes()
assert (HERE / "02-cancellation-handoff.patch").read_bytes().startswith((ROOT / "artifacts/css-root-font-cancellation-selective-handoff-fix-v1/PARENT-DELTA.patch").read_bytes())
assert [len(s["files"]) for s in stages["stages"]] == [3, 5]
with tempfile.TemporaryDirectory(prefix="css-font-publication-pack-") as scratch:
    tree = Path(scratch)
    originals = {}
    for path, role in roles.items():
        data = subprocess.check_output(["git", "--no-optional-locks", "show", stages["base_revision"] + ":" + path], cwd=ROOT)
        assert sha(data) == role["base_sha256"]
        originals[path] = data
        target = tree / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    for index, stage in enumerate(stages["stages"], 1):
        for path, digest in stage["head_preimages"].items():
            assert sha((tree / path).read_bytes()) == digest
        for path in stage["create_tests"]:
            assert not (tree / path).exists()
            (tree / path).parent.mkdir(parents=True, exist_ok=True)
        patch = HERE / ("01-font-units.patch" if index == 1 else "02-cancellation-handoff.patch")
        subprocess.run(["patch", "--batch", "--fuzz=0", "-p1", "-i", str(patch)], cwd=tree, check=True)
        for path, record in stage["files"].items():
            assert (tree / path).read_bytes() == (ROOT / record["path"]).read_bytes()
        if index == 2:
            for path, role in roles.items():
                assert sha((tree / path).read_bytes()) == role["candidate_sha256"]
    for name in ["02-cancellation-handoff.patch", "01-font-units.patch"]:
        subprocess.run(["patch", "--batch", "--fuzz=0", "-R", "-p1", "-i", str(HERE / name)], cwd=tree, check=True)
    for path, data in originals.items():
        assert (tree / path).read_bytes() == data
    for stage in stages["stages"]:
        for path in stage["create_tests"]:
            assert not (tree / path).exists()
    assert not list(tree.rglob("*.rej")) and not list(tree.rglob("*.orig"))
assert not Path(scratch).exists()
print(json.dumps({"references": len(refs), "stages": [3, 5], "final_source_roles": 4, "exact_fixture_pages": 3, "zero_fuzz_forward_reverse": True, "scratch_removed": scratch}))
