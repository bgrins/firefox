import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parent


def sha(data):
    return hashlib.sha256(data).hexdigest()


def declarations(path):
    namespace = None
    names = []
    for line in path.read_text().splitlines():
        if line.startswith("namespace "):
            if namespace:
                raise ValueError("Nested namespace unsupported")
            namespace = line[10:]
        elif line == "end " + str(namespace):
            namespace = None
        match = re.match(r"(?:@\[[^]]+\] )?theorem (\S+)", line)
        if match:
            if not namespace:
                raise ValueError("Theorem outside namespace")
            names.append(namespace + "." + match[1])
    return names


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--lean", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    lean, out = args.lean.resolve(), args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    source = json.loads((ROOT / "SOURCE-ONLY.json").read_text())
    for name, expected in source.items():
        if sha((ROOT / name).read_bytes()) != expected:
            raise ValueError("Changed source " + name)
    preserved = json.loads((ROOT / "PRESERVED.json").read_text())["sha256"]
    for name, expected in preserved.items():
        if sha((ROOT / name).read_bytes()) != expected:
            raise ValueError("Changed preserved input " + name)
    modules = list(preserved) + ["Model.lean", "Prototype.lean", "Cases.lean"]
    commands = {}

    def run(label, argv, work, reject=False):
        p = subprocess.run([str(x) for x in argv], cwd=work,
                           env=dict(os.environ, LEAN_PATH=str(work)), capture_output=True, text=True)
        output = p.stdout + p.stderr
        (out / (label + ".log")).write_text(output)
        commands[label] = {"exit": p.returncode, "sha256": sha(output.encode())}
        if reject:
            if p.returncode != 1 or "error:" not in output:
                raise ValueError("Wrong rejection " + label)
        elif p.returncode or re.search(r"(?m)^(?:[^\n]*:\d+:\d+: )?(?:warning:|error:|error\()", output):
            raise ValueError(label + "\n" + output)
        return output

    with tempfile.TemporaryDirectory(prefix="document-design-", dir=out) as d:
        work = Path(d)
        version = run("version", [lean, "--version"], work)
        if "version 4.35.0-rc4," not in version:
            raise ValueError("Wrong toolchain")
        names = []
        for name in modules:
            data = (ROOT / name).read_text()
            if re.search(r"\bsorry\b|\badmit\b|\bnative_decide\b|^axiom |^partial |^unsafe ", data, re.M):
                raise ValueError("Unapproved proof escape")
            p = work / name
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(data)
            run("build-" + name.replace("/", "-"), [lean, "-o", name[:-5] + ".olean", name], work)
            names += declarations(p)
        (work / "Audit.lean").write_text("import Cases\n" + "".join(
            "#print axioms " + n + "\n" for n in names))
        output = run("audits", [lean, "Audit.lean"], work)
        audits = {}
        for line in re.sub(r",\n\s*", ", ", output).splitlines():
            match = re.fullmatch(r"'([^']+)' (does not depend on any axioms|depends on axioms: \[(.*)\])", line)
            if not match:
                raise ValueError("Unexpected axiom output")
            axioms = set(match[3].split(", ")) if match[3] else set()
            if not axioms <= {"propext", "Classical.choice", "Quot.sound"} or match[1] in audits:
                raise ValueError("Unexpected axioms")
            audits[match[1]] = sorted(axioms)
        if len(names) != len(set(names)) or set(audits) != set(names):
            raise ValueError("Incomplete axiom roster")
        witness = """import Model
open CssDerivation.DocumentDesign CssDerivation.FirstOrder
example : eval (weakenExpr [.nat] (.foldNat (.cons (.scalar 'x') .nil) (.nat 3)
  (.add (.var (.there .here)) (.var (.there (.there .here)))) : Expr [.nat] .nat))
  (.cons 7 (.cons 900 .nil)) = 10 := by decide
"""
        (work / "Witness.lean").write_text(witness)
        run("witness-positive", [lean, "Witness.lean"], work)
        old = "| .foldNat xs z f => .foldNat (weakenExpr Δ xs) (weakenExpr Δ z) (weakenExpr Δ f)"
        new = "| .foldNat xs z _ => .foldNat (weakenExpr Δ xs) (weakenExpr Δ z) (.nat 0)"
        data = (work / "Model.lean").read_text()
        if data.count(old) != 1:
            raise ValueError("Mutation anchor changed")
        (work / "Model.lean").write_text(data.replace(old, new))
        run("mutant-compiles", [lean, "-o", "Model.olean", "Model.lean"], work)
        run("mutant-laws", [lean, "Prototype.lean"], work, reject=True)
        output = run("mutant-witness", [lean, "Witness.lean"], work, reject=True)
        if "Tactic `decide` proved" not in output or "is false" not in output:
            raise ValueError("Not a semantic rejection")
    for name, expected in source.items():
        if sha((ROOT / name).read_bytes()) != expected:
            raise ValueError("Source changed during verification")
    (out / "report.json").write_text(json.dumps({"status": "pass", "audits": audits,
        "new_laws": declarations(ROOT / "Prototype.lean"), "cases": declarations(ROOT / "Cases.lean"),
        "controls": {"fold-step-erased": "implementation compiles; laws and concrete false witness reject"},
        "commands": commands, "source_sha256": source, "temporary_builds_removed": True,
        "outer_document_reader_implemented": False, "universal_alias_weakening_proved": True}, indent=2) + "\n")
    print(f"PASS: {len(audits)} audits, 7 new laws, 4 cases, 1 compiling semantic mutant")


if __name__ == "__main__":
    main()
