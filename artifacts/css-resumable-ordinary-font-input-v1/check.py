import difflib
import hashlib
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PARENT = ROOT / "artifacts/css-resumable-font-selection-integrated-v2"

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def block(text, needle):
    start = text.index(needle)
    opening = text.index("{", start)
    depth, end = 1, opening + 1
    while depth:
        depth += (text[end] == "{") - (text[end] == "}")
        end += 1
    return text[start:end]

refs = json.loads((HERE / "REFERENCES.json").read_text())
for name, record in refs.items():
    path = ROOT / name
    assert digest(path) == record["sha256"] and path.stat().st_size == record["bytes"], name
for directory, expected in [
    (PARENT, "8edb8fa1972b9408c1349d1a074adc6831bf28fffc964a3c578ed8f71cc41460"),
    (ROOT / "artifacts/css-ordinary-font-input-e86-source-snapshot-v1", "2d844b926404aa3cf2f2743b6f50457612f4661068889fa982e19b98ad34c3ee"),
    (ROOT / "artifacts/css-minimum-font-ordinary-input-stall-review-v1", "ee5ca70b90b329c0621834c20535cb17b581e812ce76bc86af6807c1cfb894b5"),
]:
    assert digest(directory / "FILES.json") == expected
    manifest = json.loads((directory / "FILES.json").read_text())
    for name, record in manifest.get("files", manifest).items():
        path = directory / name
        assert digest(path) == record["sha256"] and path.stat().st_size == record["bytes"]
roles = json.loads((HERE / "SOURCE-ROLES.json").read_text())
parent_patch, native_patch = [], []
for role, records in roles.items():
    for record in records.values():
        assert digest(ROOT / record["path"]) == record["sha256"]
    new = (ROOT / records["candidate"]["path"]).read_text()
    old = (ROOT / records["parent"]["path"]).read_text()
    base = (ROOT / records["base"]["path"]).read_text()
    parent_patch.extend(difflib.unified_diff(old.splitlines(True), new.splitlines(True), fromfile="a/" + role, tofile="b/" + role))
    native_patch.extend(difflib.unified_diff(base.splitlines(True), new.splitlines(True), fromfile="a/" + role, tofile="b/" + role))
    if role.endswith("cascade.rs"):
        source = new
        normalized = new.replace("OrdinaryFontInput", "Synthesis").replace("perform_font_input_action", "perform_synthesis_action").replace("is_retained_font_input", "is_synthesis_longhand")
        for name in ["FontKerning", "FontOpticalSizing", "FontVariantLigatures"]:
            line = "            | LonghandId::" + name + "\n"
            assert normalized.count(line) == 1
            normalized = normalized.replace(line, "")
        assert normalized == old
    else:
        assert new == old
assert "".join(parent_patch) == (HERE / "PARENT-DELTA.patch").read_text()
assert "".join(native_patch) == (HERE / "native.patch").read_text()
predicate = block(source, "fn is_retained_font_input(")
action = block(source, "fn perform_font_input_action(")
extracted = (HERE / "ActionTests.rs").read_text().replace("// EXACT-PREDICATE", predicate).replace("// EXACT-ACTION", action)
assert extracted == (HERE / "ACTION-EXTRACTED.rs").read_text()
policy = (HERE / "POLICY-EXTRACTED.rs").read_text()
for needle in ["fn is_retained_font_input(", "fn font_publication_demand(", "enum PublicationDemand {"]:
    assert block(policy, needle) == block(source, needle)
action_check = json.loads((HERE / "ACTION-CHECK.json").read_text())
assert len(action_check["results"]) == 6
for result in action_check["results"]:
    assert result["compile_exit"] == 0 and result["exit"] == (0 if result["variant"] == "positive" else 101)
for name, text in [("predicate", predicate), ("action", action)]:
    assert hashlib.sha256(text.encode()).hexdigest() == action_check["extracted_function_sha256"][name]
policy_check = json.loads((HERE / "POLICY-CHECK.json").read_text())
assert policy_check["compile_exit"] == 0 and len(policy_check["results"]) == 4
assert all(row["exit"] == 0 for row in policy_check["results"])
for record in [action_check, policy_check]:
    assert record["scratch_removed"] and not Path(record["scratch"]).exists()
formatted = subprocess.run(["rustfmt", "--edition", "2024", "--check", str(HERE / "candidate/servo/components/style/properties/cascade.rs")], capture_output=True, text=True)
assert formatted.returncode == 0, formatted.stdout + formatted.stderr
scratch = Path(tempfile.mkdtemp(prefix="css-ordinary-input-roundtrip-", dir="/private/tmp"))
try:
    for role, record in roles.items():
        path = scratch / role
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes((ROOT / record["base"]["path"]).read_bytes())
    for reverse in [False, True]:
        args = ["patch", "--batch", "--fuzz=0", "-p1", "-i", str(HERE / "native.patch")]
        if reverse:
            args.append("-R")
        patched = subprocess.run(args, cwd=scratch, capture_output=True, text=True)
        assert patched.returncode == 0 and "offset" not in patched.stdout and "fuzz" not in patched.stdout, patched.stdout + patched.stderr
        for role, record in roles.items():
            assert digest(scratch / role) == record["base" if reverse else "candidate"]["sha256"]
finally:
    shutil.rmtree(scratch)
print(json.dumps({"references": len(refs), "source_roles": len(roles), "exact_parent_normalization": True, "exact_action_and_policy_extraction": True, "full_patch_forward_reverse": True, "format": True, "saved_controller_tests": 5, "saved_compiled_mutants": 5, "saved_policy_controls": 10, "saved_new_policy_cases": 3, "scratch_removed": not scratch.exists(), "native_or_browser_execution": False}))
