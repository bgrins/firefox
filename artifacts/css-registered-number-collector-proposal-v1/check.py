#!/usr/bin/env python3
import hashlib, json, re, shutil, subprocess, tempfile
from pathlib import Path
ROOT = Path(__file__).resolve().parent
PATH = "servo/components/style/properties_and_values/value.rs"
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def run(args, cwd):
    result = subprocess.run(args, cwd=cwd, text=True, capture_output=True)
    assert result.returncode == 0, (args, result.stdout, result.stderr)
    return result
pins = json.loads((ROOT / "SOURCE-PINS.json").read_text())
for path, pin in pins["paths"].items():
    assert digest(ROOT / "base" / path) == pin["sha256"]
assert pins["paths"][PATH]["sha256"] == pins["paths"][PATH]["head_sha256"]
method = (ROOT / "collector-method.rs.txt").read_text()
source = (ROOT / "candidate" / PATH).read_text()
assert method.strip() in source
base = (ROOT / "base" / PATH).read_text()
assert source.replace(method, "", 1).replace("AttrTaint, ComputedValue as ComputedPropertyValue, ReferenceFlags", "AttrTaint, ComputedValue as ComputedPropertyValue") == base
variants = {}
for path, declaration, prefix in [
 ("values/generics/calc.rs", "pub enum GenericCalcNode<L> {", "CalcNode"),
 ("values/specified/calc.rs", "pub enum Leaf {", "Leaf"),
]:
    text = (ROOT / "base/servo/components/style" / path).read_text()
    body = text.split(declaration, 1)[1].split("\n}", 1)[0]
    names = set(re.findall(r"^    ([A-Z][A-Za-z0-9_]*)\s*[(,{]", body, re.M))
    covered = set(re.findall(prefix + r"::([A-Z][A-Za-z0-9_]*)", method))
    assert names == covered, (names - covered, covered - names)
    variants[prefix] = sorted(names)
assert len(variants["CalcNode"]) == 27
assert len(variants["Leaf"]) == 9
with tempfile.TemporaryDirectory(prefix="number-collector-transport-") as tmp:
    target = Path(tmp) / PATH
    target.parent.mkdir(parents=True)
    shutil.copyfile(ROOT / "base" / PATH, target)
    run(["git", "apply", "--check", str(ROOT / "native.patch")], tmp)
    run(["git", "apply", str(ROOT / "native.patch")], tmp)
    assert target.read_bytes() == (ROOT / "candidate" / PATH).read_bytes()
    run(["git", "apply", "--reverse", str(ROOT / "native.patch")], tmp)
    assert target.read_bytes() == (ROOT / "base" / PATH).read_bytes()
run(["rustfmt", "--edition", "2024", "--config-path", str(ROOT / "rustfmt.toml"), "--check", str(ROOT / "candidate" / PATH)], ROOT)
result = {"status": "STATIC_TRANSPORT_AND_SYNTAX_PASS", "candidate_sha256": digest(ROOT / "candidate" / PATH), "patch_sha256": digest(ROOT / "native.patch"), "variants": variants, "head_and_live_value_base_identical": True, "native_compilation": False, "browser_tests": False, "controls_executed": False}
print(json.dumps(result, indent=2))
