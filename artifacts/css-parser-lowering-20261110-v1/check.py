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
OWN = ["ExtendedBackend", "ParserLowering", "LoweredProgram", "LoweringLaws", "LoweredNumber", "LoweringCases"]


def sha(data):
    return hashlib.sha256(data).hexdigest()


def authenticate(root):
    preserved = json.loads((root / "PRESERVED.json").read_text())
    for name, digest in preserved["sha256"].items():
        if sha((root / name).read_bytes()) != digest:
            raise ValueError("Preserved source changed: " + name)
    original = source_map.ROOT
    source_map.ROOT = root
    try:
        clauses = source_map.extract()
    finally:
        source_map.ROOT = original
    if clauses != json.loads((root / "CLAUSES.json").read_text()):
        raise ValueError("Reviewed clause map changed")


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
                raise ValueError("Unexpected namespace")
            scopes.pop()
        elif theorem:
            result.append(".".join(scopes + [theorem[1]]))
    if scopes:
        raise ValueError("Unclosed namespace")
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--lean", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    lean, out = args.lean.resolve(), args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    authenticate(ROOT)
    preserved = json.loads((ROOT / "PRESERVED.json").read_text())
    modules = [name.replace(".", "/") for name in preserved["modules"]] + OWN
    files = [module + ".lean" for module in modules] + [
        "check.py", "source_map.py", "EXPECTED.json", "SOURCE.json", "CLAUSES.json",
        "PRESERVED.json", "LIBRARY.json", "PROTOCOL.json", "PRIOR-REFUSAL.json",
        "MAPPING.md", "inputs/css-syntax-3.bs"]
    before = {name: sha((ROOT / name).read_bytes()) for name in files}
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
        raise ValueError("Duplicate theorem declaration")
    commands = {}

    def run(name, argv, work, reject=False):
        process = subprocess.run([str(x) for x in argv], cwd=work,
                                 env=dict(os.environ, LEAN_PATH=str(work)), capture_output=True, text=True)
        output = process.stdout + process.stderr
        (out / (name + ".log")).write_text(output)
        commands[name] = {"exit": process.returncode, "output_sha256": sha(output.encode())}
        if reject:
            if process.returncode != 1 or "error:" not in output:
                raise ValueError("Unexpected rejection: " + name)
        elif process.returncode or (re.search(r"(?m)^(?:[^\n]*:\d+:\d+: )?(?:warning:|error:|error\()", output) or re.search(r"\bsorry\b", output)):
            raise ValueError("Unexpected diagnostic: " + name + "\n" + output)
        return output

    version = run("version", [lean, "--version"], out).strip()
    if "version 4.35.0-rc4," not in version:
        raise ValueError("Unexpected Lean version")
    controls = {}
    with tempfile.TemporaryDirectory(prefix="parser-lowering-check-", dir=out) as directory:
        base = Path(directory)
        work = base / "positive"
        work.mkdir()
        for module in modules:
            destination = work / (module + ".lean")
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / (module + ".lean"), destination)
            run("build-" + module.replace("/", "-"), [lean, "-o", module + ".olean", module + ".lean"], work)
        (work / "Audit.lean").write_text("import LoweredNumber\n" + "".join(
            "#print axioms " + name + "\n" for name in names))
        output = run("axioms", [lean, "Audit.lean"], work)
        audits = {}
        for line in re.sub(r",\n\s*", ", ", output).splitlines():
            match = re.fullmatch(r"'([^']+)' (does not depend on any axioms|depends on axioms: \[(.*)\])", line)
            if not match:
                raise ValueError("Unexpected axiom record: " + line)
            axioms = set(match[3].split(", ")) if match[3] else set()
            if not axioms <= {"propext", "Classical.choice", "Quot.sound"}:
                raise ValueError("Unapproved axiom: " + line)
            if match[1] in audits:
                raise ValueError("Duplicate axiom record")
            audits[match[1]] = sorted(axioms)
        if set(audits) != set(names):
            raise ValueError("Incomplete axiom audit")
        (work / "Run.lean").write_text('import LoweringCases\ndef main : IO Unit := do\n  for (name, ok) in CssParserLowering.Cases.checks do\n    IO.println s!"{name}: {ok}"\n')
        observations = run("examples", [lean, "--run", "Run.lean"], work).splitlines()
        expected = json.loads((ROOT / "EXPECTED.json").read_text())
        if observations != [name + ": true" for name in expected]:
            raise ValueError("Unexpected examples")
        mutations = [
            ("rollback-keeps-raised-error", "ExtendedBackend", "LoweringLaws",
             ".putState before", ".bind .getState fun after => .putState { before with error := after.error }",
             "run (lower errorThenEmpty) ⟨['x'], false⟩ = (none, ⟨['x'], false⟩)"),
            ("pair-failure-not-atomic", "ParserLowering", "LoweringLaws",
             "  | .pair left right =>\n    transaction (.bind (lower left) fun first =>\n      match first with\n      | none => pure none\n      | some a => .bind (lower right) fun second => pure (second.map fun b => (a, b)))",
             "  | .pair left right =>\n    .bind (lower left) fun first =>\n      match first with\n      | none => pure none\n      | some a => .bind (lower right) fun second => pure (second.map fun b => (a, b))",
             'run (lower pairAB) ⟨"ax".toList, true⟩ = (none, ⟨"ax".toList, true⟩)'),
            ("capped-maximal-scan", "ParserLowering", "LoweringLaws",
             ".scan before.input.length", ".scan (min before.input.length 2)",
             'executeNumber ⟨"12345px".toList, false⟩ = some (⟨12345, 0, false, none⟩, ⟨"px".toList, false⟩)'),
            ("lost-legacy-error", "ExtendedBackend", "LoweringLaws",
             "| .legacy program, state => CssDerivation.run program state",
             "| .legacy program, state => CssDerivation.run program { state with error := false }",
             "run (lower (.legacy (.ret (.scalar '!')))) ⟨['x'], true⟩ = (some '!', ⟨['x'], true⟩)"),
            ("optional-failure-is-fatal", "ParserLowering", "LoweringLaws",
             "fun result => pure (some result)", "fun result => pure (result.map some)",
             'executeNumber ⟨"123px".toList, false⟩ = some (⟨123, 0, false, none⟩, ⟨"px".toList, false⟩)'),
            ("inverted-take", "ParserLowering", "LoweringLaws",
             "if accepts predicate c then pure (some c) else pure none",
             "if accepts predicate c then pure none else pure (some c)",
             'run (lower (character \'a\')) ⟨"ab".toList, false⟩ = (some \'a\', ⟨[\'b\'], false⟩)'),
        ]
        for name, module, proof_module, old, new, witness in mutations:
            mutant = base / name
            shutil.copytree(work, mutant)
            text = (ROOT / (module + ".lean")).read_text()
            if text.count(old) != 1:
                raise ValueError("Mutation anchor changed: " + name)
            (mutant / (module + ".lean")).write_text(text.replace(old, new))
            run(name + "-typecheck", [lean, "-o", module + ".olean", module + ".lean"], mutant)
            runtime_modules = ["LoweredProgram"]
            if module == "ExtendedBackend":
                runtime_modules.insert(0, "ParserLowering")
            for runtime in runtime_modules:
                run(name + "-" + runtime, [lean, "-o", runtime + ".olean", runtime + ".lean"], mutant)
            run(name + "-laws", [lean, proof_module + ".lean"], mutant, reject=True)
            run(name + "-cases", [lean, "-o", "LoweringCases.olean", "LoweringCases.lean"], mutant)
            (mutant / "Witness.lean").write_text("import LoweringCases\nopen CssParserLowering CssParserLowering.Cases\nexample : " + witness + " := by decide\n")
            failure = run(name + "-witness", [lean, "Witness.lean"], mutant, reject=True)
            if not re.fullmatch(r"Witness\.lean:3:\d+: error: Tactic `decide` proved that the proposition\n(?:  [^\n]*\n)+is false\n", failure):
                raise ValueError("Unexpected semantic witness rejection: " + name + "\n" + failure)
            controls[name] = "type-correct runtime mutant; unchanged proof and exact false witness rejected"
        drift = base / "drift"
        drift.mkdir()
        for name in files:
            destination = drift / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, destination)
        drift_targets = [
            ("old-backend-drift", "StatefulIR.lean", "Preserved source changed: StatefulIR.lean"),
            ("parser-source-drift", "ParserIR.lean", "Preserved source changed: ParserIR.lean"),
            ("css-source-drift", "inputs/css-syntax-3.bs", "Pinned CSS source drift"),
        ]
        for name, file, diagnostic in drift_targets:
            original = (drift / file).read_bytes()
            (drift / file).write_bytes(original + b"changed")
            try:
                authenticate(drift)
            except ValueError as error:
                if str(error) != diagnostic:
                    raise
                controls[name] = diagnostic
            else:
                raise ValueError("Changed input accepted")
            (drift / file).write_bytes(original)
    if before != {name: sha((ROOT / name).read_bytes()) for name in files}:
        raise ValueError("Inputs changed during verification")
    report = {"status": "pass", "toolchain": version, "audits": audits,
              "new_declarations": own_names, "examples": expected, "controls": controls,
              "commands": commands, "sources": before, "temporary_builds_removed": True,
              "generic_parser_lowering_proved": True, "whole_state_atomic_failure_proved": True,
              "number_instance_proved": True, "json_codec_proved": False,
              "numeric_projection_lowered": False, "native_refinement_proved": False,
              "mechanical_prose_derivation": False}

    (out / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(f"PASS: {len(audits)} audits ({len(own_names)} new), {len(expected)} observations, {len(controls)} controls")


if __name__ == "__main__":
    main()
