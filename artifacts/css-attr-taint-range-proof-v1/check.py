import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys

if not (sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize):
    raise RuntimeError("Use isolated, nonoptimized Python (-I -S)")

ROOT = Path(__file__).absolute().parent
OUT = Path(sys.argv[1]).resolve()
assert not OUT.exists() and not OUT.is_relative_to(ROOT) and not ROOT.is_relative_to(OUT)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def unique(pairs):
    result = {}
    for key, value in pairs:
        assert key not in result, "duplicate JSON key"
        result[key] = value
    return result


def read(name):
    return json.loads((ROOT / name).read_text(), object_pairs_hook=unique)


assert not any(p.is_symlink() for p in [ROOT, *ROOT.parents])
for path in ROOT.rglob("*"):
    assert not path.is_symlink() and (path.is_file() or path.is_dir())
manifest = read("MANIFEST.json")
seal = read("FREEZE.json")
assert digest(ROOT / "MANIFEST.json") == seal["manifest_sha256"]
assert digest(ROOT / "check.py") == seal["checker_sha256"]
expected = set(manifest) | {"FREEZE.json", "MANIFEST.json"}
assert {str(p.relative_to(ROOT)) for p in ROOT.rglob("*") if p.is_file()} == expected
directories = {str(p) for n in expected for p in Path(n).parents if str(p) != "."}
assert {str(p.relative_to(ROOT)) for p in ROOT.rglob("*") if p.is_dir()} == directories
for name, pin in manifest.items():
    assert not Path(name).is_absolute() and ".." not in Path(name).parts and str(Path(name)) == name
    assert digest(ROOT / name) == pin, name
tool = read("TOOLCHAIN.json")
lean = Path(tool["lean"])
assert digest(lean) == tool["lean_sha256"]
for name, pin in read("TOOLCHAIN-LIBRARY.json").items():
    assert digest(lean.parent.parent / name) == pin, name
rust = read("RUST-TOOLCHAIN.json")
rustc = Path(rust["path"])
assert rustc.is_absolute() and digest(rustc) == rust["sha256"]

OUT.mkdir()
commands = []
env = {k: v for k, v in os.environ.items() if not k.startswith(("LEAN_", "PYTHON"))}
env["LEAN_PATH"] = str(OUT)


def run(command, label):
    result = subprocess.run(command, cwd=OUT, env=env, capture_output=True, text=True)
    (OUT / (label + ".log")).write_text(result.stdout + result.stderr)
    commands.append({"command": command, "exit": result.returncode, "label": label})
    assert result.returncode == 0, label
    return result.stdout


for name in ["Ranges.lean", "Audit.lean"]:
    (OUT / name).write_bytes((ROOT / name).read_bytes())
assert not re.search(r"\b(sorry|admit|axiom|native_decide)\b", (OUT / "Ranges.lean").read_text())
run([str(lean), "-o", "Ranges.olean", "Ranges.lean"], "compile")
audit = run([str(lean), "Audit.lean"], "audit")
reports = re.findall(r"'([^']+)' (?:depends on axioms: \[([^\]]*)\]|does not depend on any axioms)", audit)
assert [name for name, _ in reports] == read("AUDITS.json")
for _, axioms in reports:
    assert {a.strip() for a in axioms.split(",") if a.strip()} <= {"propext", "Quot.sound", "Classical.choice"}

driver = '''
fn main() {
    let mut cases = 0;
    let mut mismatches = 0;
    for a in 0..=5 {
        for b in a..=5 {
            for c in 0..=5 {
                for d in c..=5 {
                    let taint = AttrTaint(vec![AttrTaintedRange { start: a, end: b }]);
                    let url = AttrTaintedRange { start: c, end: d };
                    let expected = (0..5).any(|byte| (a..b).contains(&byte) && (c..d).contains(&byte));
                    mismatches += usize::from(taint.should_disallow_urls_in_range(&url) != expected);
                    cases += 1;
                }
            }
        }
    }
    println!("{} {}", cases, mismatches);
    let max = usize::MAX;
    let cases = [
        (max - 1, max, max - 1, max, true),
        (max, max, max - 1, max, false),
        (max - 2, max - 1, max - 1, max, false),
        (0, max, max, max, false),
        (0, 0, 0, max, false),
    ];
    let actual: Vec<bool> = cases.iter().map(|&(a,b,c,d,_)| {
        AttrTaint(vec![AttrTaintedRange { start: a, end: b }])
            .should_disallow_urls_in_range(&AttrTaintedRange { start: c, end: d })
    }).collect();
    println!("{:?}", actual);
}
'''
bindings = {}
observations = {}
original = (ROOT / "source/original/custom_properties.rs").read_text()
candidate = (ROOT / "source/candidate/custom_properties.rs").read_text()
before = ".any(|r| r.start <= range.end && r.end >= range.start)"
after = ".any(|r| r.start.max(range.start) < r.end.min(range.end))"
assert original.count(before) == 1 and original.replace(before, after) == candidate
for variant in ["original", "candidate"]:
    source = ROOT / "source" / variant / "custom_properties.rs"
    text = source.read_text()
    signature = "    pub fn should_disallow_urls_in_range(&self, range: &AttrTaintedRange) -> bool {"
    assert text.count(signature) == 1
    start = text.index(signature)
    end = text.index("\n    }", start) + len("\n    }")
    method = text[start:end]
    bindings[variant] = {"source_sha256": digest(source), "start_byte": len(text[:start].encode()),
                         "end_byte": len(text[:end].encode()), "method": method}
    extracted = "struct AttrTaintedRange { start: usize, end: usize }\nstruct AttrTaint(Vec<AttrTaintedRange>);\nimpl AttrTaint {\n" + method + "\n}\n" + driver
    (OUT / (variant + ".rs")).write_text(extracted)
    run([str(rustc), "--edition=2021", variant + ".rs", "-o", variant], variant + "-compile")
    observations[variant] = run([str(OUT / variant)], variant + "-run").strip().splitlines()
assert observations["candidate"] == ["441 0", "[true, false, false, false, false]"]
assert observations["original"][0].startswith("441 ") and observations["original"][0] != "441 0"
version = run([str(rustc), "--version", "--verbose"], "rust-version")
assert version == rust["version"]
result = {"audits": len(reports), "bindings": bindings, "observations": observations,
          "commands": commands, "rust_version": version,
          "scope": "Lean natural-number predicate proof plus extracted unchanged Rust methods using Vec storage. Native producers, SmallVec representation and browser integration remain separate."}
(OUT / "CHECK.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps({"audits": len(reports), "observations": observations}))
