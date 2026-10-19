from pathlib import Path
import argparse
import hashlib
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys

import cases
import mutations

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[1]

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def run(command, logfile, *, cwd=None, env=None):
    process = subprocess.run(command, cwd=cwd, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=180)
    logfile.write_text(process.stdout)
    return process

def native(path):
    return {p[0]: (int(p[1]), int(p[2]), p[3]) for p in (l.split("\t") for l in path.read_text().splitlines())}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    out = args.out.resolve()
    out.mkdir(exist_ok=False)
    for name, digest in json.loads((BASE / "REPLAY-INPUTS-v1.json").read_text()).items():
        assert sha(BASE / name) == digest, name
    for name, digest in json.loads((BASE / "DEPENDENCIES-v1.json").read_text()).items():
        assert sha(ROOT / name) == digest, name
    for entry in json.loads((BASE / "NATIVE-BINDING-v1.json").read_text()):
        assert sha(BASE / entry["original"]) == entry["original_sha256"]
        assert sha(BASE / entry["candidate"]) == entry["candidate_sha256"]
    for path, digest in json.loads((BASE / "OPTIMIZED-SOURCES-v2.json").read_text()).items():
        assert sha(BASE / "optimized-source-v2" / Path(path).name) == digest
    tool = json.loads((BASE / "TOOLCHAIN-v1.json").read_text())
    for name in ("rustc", "cargo", "lean"):
        assert sha(Path(tool[name]["path"])) == tool[name]["sha256"], name
    model = (BASE / "formal-v1/Specificity.lean").read_text()
    assert not re.search(r"\b(sorry|admit|axiom|unsafe|native_decide)\b", model)
    theorem_names = re.findall(r"^theorem (\w+)", model, re.M)
    audit = out / "Audit.lean"
    audit.write_text(model + "\n" + "\n".join("#print axioms Nesting." + n for n in theorem_names) + "\n")
    result = run([tool["lean"]["path"], str(audit)], out / "lean-audit.log")
    assert result.returncode == 0, "Lean theorem audit"
    assert "sorryAx" not in result.stdout and "Lean.ofReduceBool" not in result.stdout
    assert len(result.stdout.splitlines()) == len(theorem_names)
    for line in result.stdout.splitlines():
        if "depends on axioms:" in line:
            names = line.split("[")[1].split("]")[0].split(", ")
            assert set(names) <= {"propext", "Classical.choice", "Quot.sound"}, names
    spec = importlib.util.spec_from_file_location("lean_generator", BASE / "formal-v1/generate.py")
    gen = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gen)
    typed = cases.cases()
    values = out / "Cases.lean"
    values.write_text(model + gen.generate(typed))
    result = run([tool["lean"]["path"], str(values)], out / "lean-cases.log")
    assert result.returncode == 0
    assert len(result.stdout.splitlines()) == len(typed)
    for line, row in zip(result.stdout.splitlines(), typed):
        values = tuple(map(int, re.fullmatch(r"\((\d+), (\d+)\)", line).groups()))
        assert values == (row["specificity"], row["flags"]), row["name"]
    boundary = json.loads((BASE / "boundary-cases.json").read_text())
    inputs = out / "inputs.tsv"
    inputs.write_text("".join(f'{r["name"]}\t{r["parent"]}\t{r["child"]}\n' for r in typed + boundary))
    work = out / "native"
    shutil.copytree(BASE / "companion-source-v1", work)
    (work / ".cargo").mkdir()
    (work / ".cargo/config.toml").write_text('[source.crates-io]\nreplace-with = "vendored-sources"\n[source.vendored-sources]\ndirectory = "' + str(ROOT / "third_party/rust") + '"\n')
    env = os.environ.copy()
    for key in ("NESTING_BENCH", "NESTING_FOCUS", "RUSTFLAGS", "CARGO_ENCODED_RUSTFLAGS"):
        env.pop(key, None)
    env.update(RUSTC=tool["rustc"]["path"], CARGO_TARGET_DIR=str(out / "target"), NESTING_INPUT=str(inputs))
    harness = (BASE / "harness-focus.rs").read_text()
    def execute(name, parser_source, builder_source):
        (work / "selectors/parser.rs").write_text(parser_source + "\n#[cfg(test)]\nmod nesting_capsule {\n" + harness + "\n}\n")
        (work / "selectors/builder.rs").write_text(builder_source)
        output = out / (name + ".tsv")
        env["NESTING_OUTPUT"] = str(output)
        result = run([tool["cargo"]["path"], "test", "--offline", "--locked", "--release", "-p", "selectors", "nesting_capsule", "--", "--nocapture"], out / (name + ".log"), cwd=work, env=env)
        assert result.returncode == 0, name
        rows = native(output)
        assert len(rows) == len(typed) + len(boundary), name
        return rows
    original = execute("original", (BASE / "companion-source-v1/selectors/parser.rs").read_text(), (BASE / "companion-source-v1/selectors/builder.rs").read_text())
    fixed = execute("candidate", (BASE / "optimized-source-v2/parser.rs").read_text(), (BASE / "optimized-source-v2/builder.rs").read_text())
    old_mismatches = []
    for row in typed:
        n = row["name"]
        assert fixed[n][:2] == (row["specificity"], row["flags"]), n
        assert original[n][1:] == fixed[n][1:], n
        if original[n][0] != row["specificity"]: old_mismatches.append(n)
    assert len(old_mismatches) == 42
    known = []
    for row in boundary:
        n = row["name"]
        assert original[n] == fixed[n]
        assert fixed[n][1] == row["flags"]
        if row["domain"] == "B-remains":
            assert fixed[n][0] != row["specificity"]
            known.append(n)
        else: assert fixed[n][0] == row["specificity"]
    native_mutants = []
    for name, (parser_source, builder_source) in mutations.variants().items():
        observed = execute(name, parser_source, builder_source)
        different = [n for n in fixed if observed[n] != fixed[n]]
        assert different, name
        native_mutants.append({"name": name, "selected_inputs": len(fixed), "mismatch_count": len(different), "mismatches": different})
    changes = [
      ("substitute-parent-zero", "| .parent => .leaf parent", "| .parent => .leaf empty"),
      ("where-not-zero", "| .whereZero child => suppress (eval parent child)", "| .whereZero child => eval parent child"),
      ("allow-forbidden-parent", "{ a with pseudo := false, slotted := false, part := false }", "a"),
      ("wrong-packed-weight", "a.classes * 1024 + a.types", "a.classes * 1023 + a.types"),
      ("missing-other-subtotal", "clamp (add (directSum parent items) (clamp (otherSum items)))", "clamp (directSum parent items)"),
      ("double-cached-parent", "add (if direct then parent else zero) (directSum parent rest)", "add (if direct then add parent parent else zero) (directSum parent rest)"),
    ]
    lean_mutants = []
    for name, old, new in changes:
        assert model.count(old) == 1, name
        path = out / (name + ".lean")
        path.write_text(model.replace(old, new))
        result = run([tool["lean"]["path"], str(path)], out / (name + ".log"))
        assert result.returncode != 0 and "error:" in result.stdout, name
        assert "unexpected token" not in result.stdout and "unknown identifier" not in result.stdout, name
        lean_mutants.append(name)
    receipt = {"status": "PASS", "lean_theorems": len(theorem_names), "lean_cases": len(typed), "native_cases_per_variant": len(fixed),
               "original_specificity_mismatches": old_mismatches, "candidate_mismatches": 0, "B_remaining": known,
               "native_mutations": native_mutants, "lean_mutations": lean_mutants,
               "native_candidate_values_sha256": sha(out / "candidate.tsv"), "lean_values_sha256": sha(out / "lean-cases.log")}
    (out / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps(receipt, indent=2))

if __name__ == "__main__": main()
