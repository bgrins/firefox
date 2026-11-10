import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
import source_map

ROOT = Path(__file__).resolve().parent
OWN = ["ParserIR", "NumberTree", "NumberBridge", "NumberExamples"]
OLD = ["StatefulIR", "FirstOrder", "Lowering", "GeneratedEscape", "Bridge",
       "GeneratedFirstOrder", "FOBridge", "PreservedExamples"]


def sha(data):
    return hashlib.sha256(data).hexdigest()


def preserved(root):
    for name, metadata in json.loads((root / "PRESERVED.json").read_text()).items():
        if sha((root / name).read_bytes()) != metadata["sha256"]:
            raise ValueError("Preserved escape/IR source drift: " + name)
    for name, expected in json.loads((root / "LIBRARY.json").read_text())["sha256"].items():
        if sha((root / name).read_bytes()) != expected:
            raise ValueError("Reference source drift: " + name)


def declarations(path):
    scopes, result = [], []
    for raw in path.read_text().splitlines():
        line = raw.strip()
        opening = re.fullmatch(r"namespace (\S+)", line)
        ending = re.fullmatch(r"end(?: (\S+))?", line)
        theorem = re.match(r"theorem (\S+)", line)
        if opening:
            scopes.append(opening[1])
        elif ending:
            if not scopes or ending[1] not in [None, scopes[-1]]:
                raise ValueError("Unexpected namespace in " + str(path))
            scopes.pop()
        elif theorem:
            result.append(".".join(scopes + [theorem[1]]))
    if scopes:
        raise ValueError("Unclosed namespace")
    return result


def audit_records(output):
    result = {}
    for line in re.sub(r",\n\s*", ", ", output).splitlines():
        match = re.fullmatch(r"'([^']+)' (does not depend on any axioms|depends on axioms: \[(.*)\])", line)
        if not match:
            raise ValueError("Unexpected axiom output: " + line)
        axioms = set(match[3].split(", ")) if match[3] else set()
        if not axioms <= {"propext", "Classical.choice", "Quot.sound"} or match[1] in result:
            raise ValueError("Unexpected axiom set or duplicate declaration")
        result[match[1]] = sorted(axioms)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--lean", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    lean, out = args.lean.resolve(), args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    library = json.loads((ROOT / "LIBRARY.json").read_text())
    modules = [m.replace(".", "/") for m in library["modules_in_build_order"]] + OLD + OWN
    files = [m + ".lean" for m in modules] + [
        "check.py", "source_map.py", "EXPECTED.json", "SOURCE.json", "CLAUSES.json",
        "PRESERVED.json", "LIBRARY.json", "PRIOR-REFUSAL.json", "PROTOCOL.json", "MAPPING.md",
        "inputs/css-syntax-3.bs"]

    def hashes():
        return {name: sha((ROOT / name).read_bytes()) for name in files}

    before = hashes()
    preserved(ROOT)
    if source_map.extract() != json.loads((ROOT / "CLAUSES.json").read_text()):
        raise ValueError("Reviewed source mapping changed")
    expected = json.loads((ROOT / "EXPECTED.json").read_text())
    commands, controls = {}, {}

    def run(name, argv, work, success=True):
        result = subprocess.run([str(x) for x in argv], cwd=work,
                                env=dict(os.environ, LEAN_PATH=str(work)), capture_output=True, text=True)
        text = result.stdout + result.stderr
        (out / (name + ".log")).write_text(text)
        commands[name] = {"argv": [str(x) for x in argv], "exit": result.returncode, "log_sha256": sha(text.encode())}
        if success:
            if result.returncode or re.search(r"(?m)^(?:[^\n]*:\d+:\d+: )?(?:warning:|error:|error\()", text) or re.search(r"\bsorry\b", text):
                raise ValueError("Unexpected build diagnostic: " + name + "\n" + text)
        elif result.returncode != 1 or "error:" not in text:
            raise ValueError("Unexpected rejection: " + name + "\n" + text)
        return text

    version = run("toolchain", [lean, "--version"], out).strip()
    if "version 4.35.0-rc4," not in version:
        raise ValueError("Unexpected Lean version")
    names, own_names = [], []
    for module in modules:
        path = ROOT / (module + ".lean")
        if re.search(r"\bsorry\b|\badmit\b|^axiom |^unsafe ", path.read_text(), re.M):
            raise ValueError("Unapproved proof escape")
        found = declarations(path)
        names += found
        if module in OWN:
            own_names += found
    if len(names) != len(set(names)):
        raise ValueError("Duplicate theorem name")
    with tempfile.TemporaryDirectory(prefix="number-check-", dir=out) as directory:
        base = Path(directory)
        work = base / "positive"
        work.mkdir()
        for module in modules:
            dest = work / (module + ".lean")
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes((ROOT / (module + ".lean")).read_bytes())
            run("build-" + module.replace("/", "-"), [lean, "-o", module + ".olean", module + ".lean"], work)
        (work / "Audit.lean").write_text("import NumberExamples\n" + "".join("#print axioms " + n + "\n" for n in names))
        audits = audit_records(run("axioms", [lean, "Audit.lean"], work))
        if set(audits) != set(names):
            raise ValueError("Axiom inventory mismatch")
        (work / "Run.lean").write_text('import NumberExamples\ndef main : IO Unit := do\n  for (name, ok) in CssDerivation.NumberTransferExamples.checks do\n    IO.println s!"PASS {name}: {ok}"\n')
        text = run("examples", [lean, "--run", "Run.lean"], work)
        if text.splitlines() != ["PASS " + n + ": true" for n in expected]:
            raise ValueError("Executable vector changed")
        mutations = [
            ("fraction-lookahead", "NumberTree", ".right (.take dotPredicate) nonemptyDigitsTree", ".right (.take dotPredicate) digitsTree",
             'NumberTransfer.execute ⟨"1.".toList, false⟩ = some (⟨1, 0, false, none⟩, ⟨[\'.\'], false⟩)'),
            ("exponent-lookahead", "NumberTree", ".pair signTree nonemptyDigitsTree", ".pair signTree digitsTree",
             'NumberTransfer.execute ⟨"1e+".toList, false⟩ = some (⟨1, 0, false, none⟩, ⟨"e+".toList, false⟩)'),
            ("bounded-scan", "ParserIR", "let scanned := scanWhile predicate state.input", "let scanned := FirstOrder.scanData predicate .nil 2 state.input",
             'NumberTransfer.execute ⟨"1234px".toList, false⟩ = some (⟨1234, 0, false, none⟩, ⟨"px".toList, false⟩)'),
            ("rollback-error", "ParserIR", "| none => some (none, state)", "| none => some (none, { state with error := false })",
             'NumberTransfer.execute ⟨"1e+".toList, true⟩ = some (⟨1, 0, false, none⟩, ⟨"e+".toList, true⟩)'),
            ("wrong-scale", "NumberTree", "exponent - fraction.length", "exponent + fraction.length",
             'NumberTransfer.execute ⟨"1.5e2".toList, false⟩ = some (⟨15, 1, true, none⟩, ⟨[], false⟩)'),
            ("wrong-type-flag", "NumberTree", "parts.2.2.1.isSome || parts.2.2.2.isSome", "parts.2.2.1.isSome && parts.2.2.2.isSome",
             'NumberTransfer.execute ⟨"1.5".toList, false⟩ = some (⟨15, -1, true, none⟩, ⟨[], false⟩)'),
        ]
        for name, module, old, new, witness in mutations:
            mutant = base / name
            shutil.copytree(work, mutant)
            text = (ROOT / (module + ".lean")).read_text()
            if text.count(old) != 1:
                raise ValueError("Mutation anchor changed: " + name)
            text = text.replace(old, new)
            if module == "ParserIR":
                # Runtime definitions compile independently of the deliberately rejected laws.
                text = text[:text.index("theorem Scanned.result")] + "end CssDerivation.ParserIR\n"
            (mutant / (module + ".lean")).write_text(text)
            run(name + "-typecheck", [lean, "-o", module + ".olean", module + ".lean"], mutant)
            if module == "ParserIR":
                run(name + "-tree", [lean, "-o", "NumberTree.olean", "NumberTree.lean"], mutant)
            run(name + "-bridge", [lean, "NumberBridge.lean"], mutant, False)
            (mutant / "Witness.lean").write_text("import NumberTree\nopen CssDerivation\nexample : " + witness + " := by decide\n")
            failure = run(name + "-witness", [lean, "Witness.lean"], mutant, False)
            if not re.fullmatch(r"Witness\.lean:3:\d+: error: Tactic `decide` proved that the proposition\n(?:  [^\n]*\n)+is false\n", failure):
                raise ValueError("Unexpected semantic witness diagnostic: " + failure)
            controls[name] = "type-correct changed runtime; unchanged reference bridge and exact semantic witness reject"
        (work / "WrongShape.lean").write_text("import NumberTree\nopen CssDerivation CssDerivation.ParserIR CssDerivation.NumberTransfer\ndef wrong : Parser NumberShape := .legacy (.ret (.scalar 'x'))\n")
        failure = run("wrong-result-shape", [lean, "WrongShape.lean"], work, False)
        if "Type mismatch" not in failure or "NumberShape" not in failure or "warning:" in failure:
            raise ValueError("Unexpected shape control diagnostic")
        controls["wrong-result-shape"] = "scalar result rejected at compound result type"
        (work / "WrongCaller.lean").write_text('import NumberBridge\nexample : CssSemantics.CssNumberParts.startsNumber "+".toList = true := by decide\n')
        failure = run("wrong-caller", [lean, "WrongCaller.lean"], work, False)
        if not re.fullmatch(r"WrongCaller\.lean:2:\d+: error: Tactic `decide` proved that the proposition\n(?:  [^\n]*\n)+is false\n", failure):
            raise ValueError("Unexpected caller rejection")
        controls["wrong-caller"] = "sign-only input does not satisfy caller start predicate"
        drift = base / "source-drift"
        (drift / "inputs").mkdir(parents=True)
        (drift / "SOURCE.json").write_bytes((ROOT / "SOURCE.json").read_bytes())
        (drift / "inputs/css-syntax-3.bs").write_bytes((ROOT / "inputs/css-syntax-3.bs").read_bytes() + b"\nchanged\n")
        source_map.ROOT = drift
        try:
            source_map.extract()
        except ValueError as error:
            if str(error) != "Pinned CSS source drift":
                raise
            controls["source-drift"] = str(error)
        else:
            raise ValueError("Source drift accepted")
        finally:
            source_map.ROOT = ROOT
        shutil.copyfile(ROOT / "PRESERVED.json", work / "PRESERVED.json")
        shutil.copyfile(ROOT / "LIBRARY.json", work / "LIBRARY.json")
        (work / "FirstOrder.lean").write_bytes((ROOT / "FirstOrder.lean").read_bytes() + b"\nchanged\n")
        try:
            preserved(work)
        except ValueError as error:
            if str(error) != "Preserved escape/IR source drift: FirstOrder.lean":
                raise
            controls["old-ir-drift"] = str(error)
        else:
            raise ValueError("Old IR drift accepted")
    if hashes() != before:
        raise ValueError("Inputs changed during verification")
    report = {"status": "pass", "toolchain": version, "modules": modules, "audits": audits,
              "new_declarations": own_names, "examples": expected, "ready_cases": 23,
              "off_domain_cases": 4, "generic_cases": 6, "preserved_escape_examples": 9,
              "controls": controls, "commands": commands, "source_hashes": before,
              "temporary_builds_removed": True, "number_is_held_out": False,
              "mechanical_prose_translation": False, "browser_float_refinement": False}
    (out / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(f"PASS: {len(audits)} audits ({len(own_names)} new); {len(expected)} observations; {len(controls)} controls")


if __name__ == "__main__":
    main()
