import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
import extract

ROOT = Path(__file__).resolve().parent
MODULES = ["CssSemantics/CssCodePointInput", "CssSemantics/CssCodePointInputLaws",
           "DomString", "Correctness", "ScalarChoice", "Examples"]


def sha(data):
    return hashlib.sha256(data).hexdigest()


def audit_records(output):
    result = {}
    combined = re.sub(r",\n\s*", ", ", output)
    for line in combined.splitlines():
        match = re.fullmatch(r"'([^']+)' (does not depend on any axioms|depends on axioms: \[(.*)\])", line)
        if not match:
            raise ValueError("Unexpected audit output: " + line)
        axioms = set(match[3].split(", ")) if match[3] else set()
        if not axioms <= {"propext", "Classical.choice", "Quot.sound"}:
            raise ValueError("Unexpected axiom set")
        if match[1] in result:
            raise ValueError("Duplicate audit")
        result[match[1]] = sorted(axioms)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--lean", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    lean, out = args.lean.resolve(), args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    expected = json.loads((ROOT / "EXPECTED.json").read_text())
    inputs = [ROOT / (m + ".lean") for m in MODULES]
    inputs += [ROOT / n for n in ["check.py", "extract.py", "EXPECTED.json", "SOURCES.json", "CLAUSES.json", "LIBRARY.json"]]
    inputs += sorted((ROOT / "inputs").iterdir())

    def hashes():
        return {str(p.relative_to(ROOT)): sha(p.read_bytes()) for p in inputs}

    before = hashes()
    if extract.extract() != json.loads((ROOT / "CLAUSES.json").read_text()):
        raise ValueError("Clause extraction differs from reviewed mapping")
    for path, value in json.loads((ROOT / "LIBRARY.json").read_text())["copied_sources_sha256"].items():
        if sha((ROOT / path).read_bytes()) != value:
            raise ValueError("Accepted library copy differs: " + path)
    commands = {}

    def run(name, argv, work, success=True):
        result = subprocess.run([str(x) for x in argv], cwd=work,
                                env=dict(os.environ, LEAN_PATH=str(work)), capture_output=True, text=True)
        output = result.stdout + result.stderr
        (out / (name + ".log")).write_text(output)
        commands[name] = {"argv": [str(x) for x in argv], "exit": result.returncode,
                          "log_sha256": sha(output.encode())}
        if success:
            if result.returncode or re.search(r"warning:|error:|sorry", output):
                raise ValueError("Unexpected failure/diagnostic: " + name + "\n" + output)
        elif result.returncode != 1 or "error:" not in output:
            raise ValueError("Unexpected negative diagnostic: " + name + "\n" + output)
        return output

    version = run("toolchain", [lean, "--version"], out).strip()
    if "version 4.35.0-rc4," not in version:
        raise ValueError("Unexpected Lean version")
    names = []
    for module in MODULES:
        text = (ROOT / (module + ".lean")).read_text()
        if re.search(r"\bsorry\b|\badmit\b|^axiom |^unsafe ", text, re.M):
            raise ValueError("Unapproved proof escape")
        namespace = re.findall(r"^namespace (\S+)$", text, re.M)
        if len(namespace) != 1:
            raise ValueError("Audit scanner requires a single namespace")
        names += [namespace[0] + "." + n for n in re.findall(r"^theorem (\S+)", text, re.M)]
    controls = {}
    with tempfile.TemporaryDirectory(prefix="source-check-", dir=out) as directory:
        work = Path(directory)
        for module in MODULES:
            source = work / (module + ".lean")
            source.parent.mkdir(parents=True, exist_ok=True)
            source.write_bytes((ROOT / (module + ".lean")).read_bytes())
            run("build-" + module.replace("/", "-"), [lean, "-o", module + ".olean", module + ".lean"], work)
        (work / "Audit.lean").write_text("import Examples\n" + "".join("#print axioms " + n + "\n" for n in names))
        audits = audit_records(run("axioms", [lean, "Audit.lean"], work))
        if set(audits) != set(names):
            raise ValueError("Audit declaration mismatch")
        (work / "Run.lean").write_text('import Examples\ndef main : IO Unit := do\n  for (name, ok) in CssSemantics.DomStringExamples.checks do\n    IO.println s!"PASS {name}: {ok}"\n')
        output = run("examples", [lean, "--run", "Run.lean"], work)
        if output.splitlines() != ["PASS " + n + ": true" for n in expected]:
            raise ValueError("Executable vector mismatch")
        original = (ROOT / "DomString.lean").read_text()
        mutations = [
            ("premature-replacement",
             "def unitPoint (u : CodeUnit) : CodePoint := ⟨u.val, by have := u.isLt; omega⟩",
             "def unitPoint (u : CodeUnit) : CodePoint := if 0xd800 ≤ u.val ∧ u.val ≤ 0xdfff then ⟨0xfffd, by decide⟩ else ⟨u.val, by have := u.isLt; omega⟩",
             "decodeValues [0xd800] = some [0xd800]", 1),
            ("pair-not-combined",
             "if h : Leading u ∧ Trailing v then pairPoint u v h.1 h.2 :: decode rest",
             "if Leading u ∧ Trailing v then unitPoint u :: decode (v :: rest)",
             "decodeValues [0xd800, 0xdc00] = some [0x10000]", 1),
            ("pair-suffix-lost",
             "then some (pairPoint u v h.1 h.2, rest)", "then some (pairPoint u v h.1 h.2, rest.tail)",
             "nextValues [0xd800, 0xdc00, 0x41] = some (some (0x10000, [0x41]))", 1),
            ("pair-arithmetic",
             "⟨(u.val - 0xd800) * 0x400 +", "⟨(u.val - 0xd800) * 0x3ff +",
             "decodeValues [0xd801, 0xdc00] = some [0x10400]", 1),
        ]
        for name, old, new, witness, count in mutations:
            if original.count(old) != count:
                raise ValueError("Mutation anchor changed: " + name)
            mutant = work / name
            (mutant / "CssSemantics").mkdir(parents=True)
            for module in MODULES[:2]:
                for suffix in [".lean", ".olean"]:
                    (mutant / (module + suffix)).write_bytes((work / (module + suffix)).read_bytes())
            (mutant / "DomString.lean").write_text(original.replace(old, new))
            run(name + "-typecheck", [lean, "-o", "DomString.olean", "DomString.lean"], mutant)
            (mutant / "Correctness.lean").write_bytes((ROOT / "Correctness.lean").read_bytes())
            run(name + "-proof", [lean, "Correctness.lean"], mutant, False)
            (mutant / "Witness.lean").write_text("import DomString\nopen CssSemantics.DomString\nexample : " + witness + " := by decide\n")
            failure = run(name + "-witness", [lean, "Witness.lean"], mutant, False)
            if not re.fullmatch(r"Witness\.lean:3:\d+: error: Tactic `decide` proved that the proposition\n(?:  [^\n]*\n)+is false\n", failure):
                raise ValueError("Unexpected false-witness diagnostic: " + failure)
            controls[name] = "typechecked; unchanged correspondence and direct semantic witness rejected"
        shared = work / "shared-leading-boundary"
        (shared / "CssSemantics").mkdir(parents=True)
        for module in MODULES[:2]:
            for suffix in [".lean", ".olean"]:
                (shared / (module + suffix)).write_bytes((work / (module + suffix)).read_bytes())
        boundary = "abbrev Leading (u : CodeUnit) : Prop := 0xd800 ≤ u.val"
        if original.count(boundary) != 1:
            raise ValueError("Shared boundary mutation anchor changed")
        (shared / "DomString.lean").write_text(original.replace(boundary, boundary.replace("≤", "<")))
        (shared / "Correctness.lean").write_bytes((ROOT / "Correctness.lean").read_bytes())
        run("shared-boundary-typecheck", [lean, "-o", "DomString.olean", "DomString.lean"], shared)
        run("shared-boundary-correspondence", [lean, "Correctness.lean"], shared)
        (shared / "Witness.lean").write_text("import DomString\nopen CssSemantics.DomString\nexample : decodeValues [0xd800, 0xdc00] = some [0x10000] := by decide\n")
        failure = run("shared-boundary-witness", [lean, "Witness.lean"], shared, False)
        if not re.fullmatch(r"Witness\.lean:3:\d+: error: Tactic `decide` proved that the proposition\n(?:  [^\n]*\n)+is false\n", failure):
            raise ValueError("Unexpected shared-boundary witness rejection")
        controls["shared-leading-boundary"] = "correspondence still proves against shared wrong classification; independent minimum-pair witness rejects"
        (work / "Domain.lean").write_text("import DomString\nopen CssSemantics.DomString\ndef invalid : CodeUnit := ⟨0x10000, by decide⟩\n")
        failure = run("outside-unit-domain", [lean, "Domain.lean"], work, False)
        if not re.fullmatch(r"Domain\.lean:3:\d+: error: Tactic `decide` proved that the proposition\n(?:  [^\n]*\n)+is false\n", failure):
            raise ValueError("Unexpected domain rejection")
        controls["outside-unit-domain"] = "invalid Fin bound rejected"
        drift = work / "drift"
        (drift / "inputs").mkdir(parents=True)
        (drift / "SOURCES.json").write_bytes((ROOT / "SOURCES.json").read_bytes())
        sources = json.loads((ROOT / "SOURCES.json").read_text())["sources"]
        for source in sources.values():
            (drift / source["file"]).write_bytes((ROOT / source["file"]).read_bytes())
        for key, source in sources.items():
            p = drift / source["file"]
            raw = p.read_bytes()
            p.write_bytes(raw + b"\nchanged\n")
            extract.ROOT = drift
            try:
                extract.extract()
            except ValueError as error:
                if str(error) != "Source drift: " + key:
                    raise
                controls["source-drift-" + key] = str(error)
            else:
                raise ValueError("Source drift accepted")
            finally:
                p.write_bytes(raw)
                extract.ROOT = ROOT
    if hashes() != before:
        raise ValueError("Source changed during verification")
    report = {"status": "pass", "toolchain": version, "modules": MODULES,
              "audits": audits, "theorem_count": len(names),
              "new_theorem_count": len([n for n in names if not n.startswith("CssSemantics.CodePointInput.")]),
              "examples": expected, "controls": controls, "commands": commands,
              "source_hashes": before, "clause_count": len(extract.extract()["clauses"]),
              "temporary_builds_removed": True, "mechanical_prose_translation": False,
              "cssom_or_browser_refinement": False}
    (out / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(f"PASS: {len(names)} theorem audits; {len(expected)} observations; {len(controls)} controls")


if __name__ == "__main__":
    main()
