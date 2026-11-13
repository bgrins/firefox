from pathlib import Path
import hashlib, json, re

base = Path(__file__).resolve().parent
repo = base.parents[1]
predecessor = json.loads((base / "PREDECESSOR.json").read_text())
prior = repo / predecessor["path"]
assert hashlib.sha256((prior / "FILES.json").read_bytes()).hexdigest() == predecessor["manifest_sha256"]
for name, digest in json.loads((prior / "FILES.json").read_text()).items():
    assert hashlib.sha256((prior / name).read_bytes()).hexdigest() == digest
for row in json.loads((prior / "SOURCE-INPUTS.json").read_text()):
    path = repo / row["path"]
    assert hashlib.sha256(path.read_bytes()).hexdigest() == row["sha256"]
    assert path.stat().st_size == row["bytes"]
names = json.loads((base / "DECLARATIONS.json").read_text())
target = (base / "Target.lean").read_text()
controls = (base / "Controls.lean").read_text()
fields = re.findall(r"^  ([a-z_]+) :", target, re.M)
control_fields = re.findall(r"^  ([a-z_]+) :", controls.split("structure Controls : Prop where", 1)[1], re.M)
assert fields == names["obligations"] and len(fields) == 15
assert control_fields == names["controls"] and len(control_fields) == 6
assert "goodLength n → n < 5 → admissible n cell" in target
assert "∀ (C : Type) (c : C)" in target
assert "Inhabited" not in target
for source in [target, controls]:
    assert not re.search(r"\b(sorry|axiom|unsafe|native_decide)\b", source)
assert "V : Backing → Prop" in target
assert "from_utf8" not in target and "UTF8" not in target
assert "#check @CssNativeHighBit.Obligations.low_value" in (base / "Types.lean").read_text()
assert json.loads((base / "STATUS.json").read_text())["compiler_invocations"] == 0
print(json.dumps({"obligation_fields": fields, "control_fields": control_fields, "prior_authenticated_files": predecessor["authenticated_files"], "source_only": True, "lean_typechecked": False, "proofs": False}, indent=2))
