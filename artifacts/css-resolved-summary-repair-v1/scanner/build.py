import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parent
parser = argparse.ArgumentParser()
parser.add_argument("--output", required=True, type=Path)
args = parser.parse_args()
out = args.output.resolve()
out.mkdir(parents=True, exist_ok=True)
tool = json.loads((ROOT / "TOOLCHAIN.json").read_text())
rustc = Path(tool["rustc"])
assert hashlib.sha256(rustc.read_bytes()).hexdigest() == tool["rustc_sha256"]
commands = []

def run(command):
    commands.append(command)
    result = subprocess.run(command, cwd=out, capture_output=True, text=True)
    (out / "commands.json").write_text(json.dumps(commands, indent=2))
    with (out / "compiler.log").open("a") as log:
        log.write(result.stdout + result.stderr)
    assert result.returncode == 0, (command, result.stderr)
    return result.stdout

for name, edition, dependencies in [
    ("dtoa", "2015", []), ("dtoa-short", "2015", ["dtoa"]),
    ("itoa", "2018", []), ("smallvec", "2018", []),
    ("bitflags", "2021", []),
    ("cssparser", "2024", ["dtoa-short", "itoa", "smallvec"]),
]:
    crate = name.replace("-", "_")
    command = [str(rustc), "--crate-name", crate, "--crate-type", "rlib", "--edition", edition,
               "-C", "opt-level=1", "-L", "dependency=" + str(out),
               str(ROOT / "vendor" / name / "src/lib.rs"), "-o", str(out / ("lib" + crate + ".rlib"))]
    for dependency in dependencies:
        dependency = dependency.replace("-", "_")
        command += ["--extern", dependency + "=" + str(out / ("lib" + dependency + ".rlib"))]
    run(command)
source = (ROOT.parent / "candidate/custom_properties.rs").read_text()
records = []
def extract(start, end):
    begin = source.index(start)
    finish = source.index(end, begin) + len(end)
    text = source[begin:finish]
    records.append({"start": start, "sha256": hashlib.sha256(text.encode()).hexdigest()})
    return text
helper = extract("fn resolved_token_dependencies(", "\n}")
units = extract("    fn from_unit(value:", "\n    }")
flags = extract("bitflags! {\n    impl ReferenceFlags", "\n}")
enum = extract("pub enum SubstitutionFunctionKind {", "\n}")
length = (ROOT / "source/servo/components/style/values/specified/length.rs").read_text()
constants = []
for name in ["EM", "EX", "CH", "CAP", "IC", "LH", "REM", "REX", "RCH", "RCAP", "RIC", "RLH"]:
    matches = re.findall(r"    pub const " + name + r": &'static str = \"[^\"]+\";", length)
    assert len(matches) == 1, name
    constants.append(matches[0])
code = "use cssparser::{CowRcStr, Parser, Token};\nuse bitflags::bitflags;\n"
code += "#[derive(Clone, Copy, Debug, Default, PartialEq, Eq)]\npub struct ReferenceFlags(u8);\n" + flags
code += "\nstruct NoCalcLength;\nimpl NoCalcLength {\n" + "\n".join(constants) + "\n}\n"
code += "impl ReferenceFlags {\n" + units + "\n}\n" + enum + "\n"
code += """impl SubstitutionFunctionKind {
    fn from_ident(ident: &str) -> Result<Self, ()> {
        cssparser::match_ignore_ascii_case! { ident,
            "var" => Ok(Self::Var),
            "env" => Ok(Self::Env),
            "attr" => Ok(Self::Attr),
            _ => Err(()),
        }
    }
}
""" + helper + "\nfn main() {\n"
cases = json.loads((ROOT / "CASES.json").read_text())
for i, case in enumerate(cases):
    assert '\"####' not in case["css"]
    value = "None" if case["expected"] is None else "Some(" + str(case["expected"]) + ")"
    code += 'assert_eq!(resolved_token_dependencies(r####"' + case["css"] + '"####).map(|f| f.0), ' + value + ', "case ' + str(i) + '");\n'
code += """let deep = "f([{".repeat(100000) + "1em 1lh 1rlh" + &"}])".repeat(100000);
let observed = std::thread::Builder::new().stack_size(65536).spawn(move || {
    resolved_token_dependencies(&deep).map(|f| f.0)
}).unwrap().join().unwrap();
assert_eq!(observed, Some(15));
println!("SCANNER_PASS deep_groups=100000 depth=300000 stack=65536");
}
"""
(out / "harness.rs").write_text(code)
(out / "SOURCE-BINDINGS.json").write_text(json.dumps(records, indent=2))
run([str(rustc), "--edition", "2024", "-C", "opt-level=1", "-L", "dependency=" + str(out),
     "--extern", "cssparser=" + str(out / "libcssparser.rlib"),
     "--extern", "bitflags=" + str(out / "libbitflags.rlib"), str(out / "harness.rs"), "-o", str(out / "scanner")])
print("FIXED_CASES", len(cases))
print(run([str(out / "scanner")]), end="")
