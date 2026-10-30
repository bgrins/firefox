from pathlib import Path
import difflib
import hashlib
import json
import shutil
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OLD = HERE.with_name("css-registered-selected-color-dependency-proposal-v5")
FORMAT = Path("/Users/bgrins/.rustup/toolchains/1.97.1-aarch64-apple-darwin/bin/rustfmt")
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(FORMAT) == "ab19d01d0a7a3a901c62b6b013a98452d38084b5d7f446ccb20c5e83c10db99f"
for path, row in json.loads((HERE / "REFERENCES.json").read_text()).items():
    assert sha(ROOT / path) == row["sha256"]
for name, row in json.loads((OLD / "FILES.json").read_text()).items():
    assert sha(OLD / name) == row["sha256"]
roles = json.loads((HERE / "SOURCE-ROLES.json").read_text())
delta, patch = [], []
for rel, row in roles.items():
    base, candidate, previous = HERE / "base" / rel, HERE / "candidate" / rel, OLD / "candidate" / rel
    assert sha(base) == row["base_sha256"] == sha(ROOT / row["source"])
    assert sha(candidate) == row["candidate_sha256"] and sha(previous) == row["v5_candidate_sha256"]
    if not rel.endswith("/cascade.rs"):
        assert candidate.read_bytes() == previous.read_bytes()
    result = subprocess.run([str(FORMAT), "--check", "--config-path", str(HERE / "rustfmt.toml"), str(candidate)], capture_output=True, text=True)
    assert result.returncode == 0 and not result.stderr, result
    delta.extend(difflib.unified_diff(previous.read_text().splitlines(True), candidate.read_text().splitlines(True), fromfile="a/"+rel, tofile="b/"+rel))
    patch.extend(difflib.unified_diff(base.read_text().splitlines(True), candidate.read_text().splitlines(True), fromfile="a/"+rel, tofile="b/"+rel))
assert "".join(delta) == (HERE / "V5-DELTA.patch").read_text()
assert "".join(patch) == (HERE / "native.patch").read_text()
rel = "servo/components/style/properties/cascade.rs"
def admission(text):
    start = text.index("fn find_non_custom_references(")
    return text[start:text.index("/// Resolves the custom properties", start)]
assert admission((HERE / "base" / rel).read_text()) == admission((HERE / "candidate" / rel).read_text())
with tempfile.TemporaryDirectory(prefix="css-union-only-patch-") as temporary:
    temporary = Path(temporary)
    shutil.copytree(HERE / "base", temporary / "tree")
    for reverse in [False, True]:
        args = ["patch"] + (["-R"] if reverse else []) + ["-p1", "-i", str(HERE / "native.patch")]
        result = subprocess.run(args, cwd=temporary / "tree", capture_output=True, text=True)
        assert result.returncode == 0, result
        for name in roles:
            assert (temporary / "tree" / name).read_bytes() == (HERE / ("base" if reverse else "candidate") / name).read_bytes()
assert not temporary.exists()
receipt = {"source_pairs":3,"changed_from_v5":1,"provider_and_classifier_unchanged":True,"original_admission_function_identical":True,"exact_delta":True,"patch_forward_reverse":True,"rustfmt_files":3,"formatter_sha256":sha(FORMAT),"scratch":str(temporary),"scratch_removed":True,"native_compile":False,"browser_execution":False,"classifier_tests_rerun":False}
(HERE / "STATIC-CHECK.json").write_text(json.dumps(receipt, indent=2)+"\n")
print(json.dumps(receipt))
