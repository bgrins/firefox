import ast
import hashlib
import json
from pathlib import Path
import re
import runpy
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sha = lambda data: hashlib.sha256(data).hexdigest()
scope = runpy.run_path(str(HERE / "extract.py"))
source = scope["source"].rsplit("\n", 1)[0]
parent_tests = (scope["H"] / "Tests.rs").read_text()
assert source.endswith(parent_tests.rstrip("\n"))
source = source[: -len(parent_tests.rstrip("\n"))]

data_path = ROOT / "servo/components/style/properties/data.py"
data_bytes = data_path.read_bytes()
assert sha(data_bytes) == "946b6ce730f8e79ea7ac4d7fc3c122b2922cdf37b38bf34d9ba9b02b84470d3d"
tree = ast.parse(data_bytes)
dependencies = next(ast.literal_eval(n.value) for n in tree.body if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "PRIORITARY_PROPERTY_DEPENDENCIES" for t in n.targets))
names = {key: "".join(x.capitalize() for x in key.split("-")) for key in dependencies}
names["-x-lang"] = "XLang"
names["-x-text-scale"] = "XTextScale"
ids = list(names.values())
extras = ["FontSynthesisWeight", "FontSynthesisStyle", "FontSynthesisSmallCaps", "FontSynthesisPosition", "FontFeatureSettings"]
source = re.sub(r"pub enum LonghandId \{[^}]+\}", "pub enum LonghandId {" + ",".join(ids + extras) + "}", source, count=1)
source = re.sub(r"pub enum PrioritaryPropertyId \{[^}]+\}", "pub enum PrioritaryPropertyId {" + ",".join(ids) + "}", source, count=1)
source = source.replace("struct PrioritaryPropertyIdSet(u16)", "struct PrioritaryPropertyIdSet(u32)")
source = re.sub(r"let ids=\[[^;]+; let bits=", "let ids=[" + ",".join("PrioritaryPropertyId::" + x for x in ids) + "]; let bits=", source, count=1)
start = source.index("impl PrioritaryPropertyId {")
end = source.index("\nimpl LonghandId {", start)
impl = "impl PrioritaryPropertyId {\nfn to_longhand(self)->LonghandId {match self {" + ",".join("Self::" + x + "=>LonghandId::" + x for x in ids) + "}}\n"
impl += "fn from_longhand(id:LonghandId)->Option<Self>{match id {" + ",".join("LonghandId::" + x + "=>Some(Self::" + x + ")" for x in ids) + ",_=>None}}\n"
impl += "fn dependencies(self)-> &'static PrioritaryPropertyIdSet {match self {"
for key, value in dependencies.items():
    mask = sum(1 << ids.index(names[x]) for x in value)
    impl += "Self::" + names[key] + "=> &PrioritaryPropertyIdSet(" + str(mask) + "),"
impl += "}}}\n"
source = source[:start] + impl + source[end:]
source = source.replace("[DeclarationPosition;11]", f"[DeclarationPosition;{len(ids)}]").replace(" };11]", f" }};{len(ids)}]")
old = 'fn apply_prioritary_property(&mut self,id:PrioritaryPropertyId,_:&mut AttributeTracker){self.computed_context.events.push(format!("priority:{id:?}"));self.cascade.completed_prioritary.insert(id);}'
assert source.count(old) == 1
actual_apply = scope["function"]("        fn apply_prioritary_property(")
source = source.replace(old, actual_apply)
source += (HERE / "NoActionTests.rs").read_text()

variants = {"positive": source,
 "omit_snapshot": source.replace('let progress_name = match progress {', 'return; let progress_name = match progress {'),
 "misreport_no_action": source.replace('None => "not-driven",', 'None => "references",'),
}

records = {}
with tempfile.TemporaryDirectory(prefix="typed-attr-pending-review-") as directory:
    scratch = Path(directory)
    lib = scratch / "libbitflags.rlib"
    bitflags = ROOT / "third_party/rust/bitflags/src/lib.rs"
    compiler = str(scope["rustc"])
    result = subprocess.run([compiler, "--edition=2021", "--crate-name", "bitflags", "--crate-type", "rlib", str(bitflags), "-o", str(lib)], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    for name, body in variants.items():
        path = scratch / (name + ".rs")
        path.write_text(body)
        command = [compiler, "--edition=2024", "-C", "debug-assertions=no", "--test", str(path), "--extern", "bitflags=" + str(lib), "-o", str(scratch / name)]
        compiled = subprocess.run(command, capture_output=True, text=True)
        row = {"source_sha256": sha(body.encode()), "compile_command": command, "compile_exit": compiled.returncode, "compile_stderr": compiled.stderr}
        if compiled.returncode == 0:
            tested = subprocess.run([str(scratch / name), "--nocapture"], capture_output=True, text=True)
            row.update(run_exit=tested.returncode, stdout=tested.stdout, stderr=tested.stderr)
        records[name] = row
report = {"candidate_sha256": sha(scope["s"].encode()), "provider_sha256": sha(scope["provider"].encode()), "generated_source": str(data_path.relative_to(ROOT)), "generated_source_sha256": sha(data_bytes), "generated_dependencies": dependencies, "actual_context_apply": actual_apply, "extracted_parts_sha256": {k: sha(v.encode()) for k,v in scope["parts"].items()}, "inputs_sha256": {p.name:sha(p.read_bytes()) for p in (HERE / "test_no_action.py", HERE / "extract.py", HERE / "NoActionTests.rs")}, "records": records, "scratch": str(scratch), "scratch_removed": not scratch.exists()}
(HERE / "NO-ACTION-RESULT.json").write_text(json.dumps(report, indent=2) + "\n")
for name,row in records.items():
    assert row["compile_exit"] == 0, (name,row["compile_stderr"])
    assert (row["run_exit"] == 0) == (name == "positive"), (name,row)
print(json.dumps({"positive": records["positive"]["stdout"], "compiled_false_controls": len(records)-1, "scratch_removed": not scratch.exists()}))
