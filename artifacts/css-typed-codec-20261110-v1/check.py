import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parent
OWN = ["Codec", "Laws", "JsonCodec", "JsonLaws", "FixtureJson", "Fixture", "Cases",
       "Runner", "RuntimeCheck", "ParserBoundary"]


def sha(data):
    return hashlib.sha256(data).hexdigest()


def authenticate(root):
    preserved = json.loads((root / "PRESERVED.json").read_text())
    for name, digest in preserved["sha256"].items():
        if sha((root / name).read_bytes()) != digest:
            raise ValueError("Preserved source changed: " + name)
    quoted = ('import JsonCodec\n\nnamespace CssDerivation.TypedCodec\n\ndef fixture : Lean.Json := json% '
              + (root / "escape.json").read_text() + '\nend CssDerivation.TypedCodec\n')
    if (root / "FixtureJson.lean").read_text() != quoted:
        raise ValueError("Quoted fixture is not the exact JSON source")


def declarations(path):
    scopes, result = [], []
    for raw in path.read_text().splitlines():
        line = raw.strip()
        opening = re.fullmatch(r"namespace (\S+)", line)
        ending = re.fullmatch(r"end(?: (\S+))?", line)
        theorem = re.match(r"(?:@\[[^]]+\] )?theorem (\S+)", line)
        if opening:
            scopes.append(opening[1])
        elif ending and ending[1] is not None:
            if not scopes or ending[1] != scopes[-1]:
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
        "check.py", "replay.py", "EXPECTED.json", "PARSER-EXPECTED.json", "PRESERVED.json",
        "escape.json", "CLAUSES.json", "MAPPING.md"]
    before = {name: sha((ROOT / name).read_bytes()) for name in files}
    names, own_names = [], []
    for module in modules:
        path = ROOT / (module + ".lean")
        if re.search(r"\bsorry\b|\badmit\b|^axiom |^unsafe |^partial ", path.read_text(), re.M):
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
                raise ValueError("Unexpected rejection: " + name + "\n" + output)
        elif process.returncode or (re.search(r"(?m)^(?:[^\n]*:\d+:\d+: )?(?:warning:|error:|error\()", output) or re.search(r"\bsorry\b", output)):
            raise ValueError("Unexpected diagnostic: " + name + "\n" + output)
        return output

    version = run("version", [lean, "--version"], out).strip()
    if "version 4.35.0-rc4," not in version:
        raise ValueError("Unexpected Lean version")
    controls = {}
    with tempfile.TemporaryDirectory(prefix="typed-codec-check-", dir=out) as directory:
        base = Path(directory)
        work = base / "positive"
        work.mkdir()
        for module in modules:
            destination = work / (module + ".lean")
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / (module + ".lean"), destination)
            run("build-" + module.replace("/", "-"), [lean, "-o", module + ".olean", module + ".lean"], work)
        (work / "Audit.lean").write_text("import Cases\nimport JsonLaws\n" + "".join(
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
        expected = json.loads((ROOT / "EXPECTED.json").read_text())
        for runner in ["Runner", "RuntimeCheck"]:
            output = run(runner, [lean, "--run", runner + ".lean", ROOT / "escape.json"] +
                         [row["input"] for row in expected], work)
            if [json.loads(line) for line in output.splitlines()] != expected:
                raise ValueError("Unexpected execution: " + runner)
        parser_expected = json.loads((ROOT / "PARSER-EXPECTED.json").read_text())
        output = run("parser-boundary", [lean, "--run", "ParserBoundary.lean"] +
                     [row["text"] for row in parser_expected], work)
        if [json.loads(line) for line in output.splitlines()] != [row["value"] for row in parser_expected]:
            raise ValueError("Unexpected JSON parser observation")
        sub_old = "pure ⟨.nat, .sub a b⟩"
        sub_new = "pure ⟨.nat, .add a b⟩"
        mutations = [
            ("same-type-index", "Codec", "Laws", [],
             [("| .there v => encodeVar v + 1", "| .there v => encodeVar v")], "Codec",
             "((decodeVar [.nat, .nat] .nat (encodeVar (Var.there Var.here : Var [.nat, .nat] .nat))).map (fun v => lookup v (.cons 3 (.cons 7 .nil)))) = some 7"),
            ("same-type-opcode", "Codec", "Laws", [], [(sub_old, sub_new)], "Codec",
             "((decodeExpr [] .nat (.sub (.nat 7) (.nat 2))).map (fun e => eval e .nil)) = some 5"),
            ("scan-budget", "Codec", "Laws", [],
             [("pure (.scan budget p next)", "pure (.scan (budget + 1) p next)")], "Codec",
             "((decodeStmt [] .chars (.scan 1 (.bool true) (.ret (.var 0)))).map (fun p => (interpret p .nil ⟨['a','b'],false⟩).1)) = some ['a']"),
            ("guard-bypassed", "Codec", "Laws", [],
             [(sub_old, sub_new), ("if encodeExpr e = normalizeExpr data then some e else none", "some e")], "Codec",
             "((checkExpr [] .nat (.sub (.nat 7) (.nat 2))).map encodeExpr) = some (.sub (.nat 7) (.nat 2))"),
            ("scope-check-lost", "Codec", "Laws", [],
             [("if Γ.head? = some head then inferExpr Γ e else none", "if Γ.head? = some head then inferExpr Γ e else inferExpr Γ e")], "Codec",
             "(inferExpr [.bool] (.scope .nat (.bool true))).isNone = true"),
            ("json-opcode", "JsonCodec", "Fixture", ["FixtureJson"],
             [("some (.sub a b)", "some (.add a b)")], "FixtureJson",
             "((decodeDocument fixture).map (fun p => (FirstOrder.execute p ['4','1','!']).value.toNat)) = some 65"),
            ("extra-field-admitted", "JsonCodec", "JsonLaws", [],
             [("if !exactFields [\"op\", \"args\"] fields then none else do", "if false then none else do")], "JsonCodec",
             '(foldJson [] (json% {"op":"nat","args":[1],"code":"extra"})).atom.expression.isNone = true'),
        ]
        for name, module, proof_module, downstream, edits, witness_import, witness in mutations:
            witness_source = ("import " + witness_import +
                "\nopen CssDerivation CssDerivation.FirstOrder CssDerivation.TypedCodec Lean\nexample : " + witness + " := by decide\n")
            (work / "Witness.lean").write_text(witness_source)
            run(name + "-witness-positive", [lean, "Witness.lean"], work)
            mutant = base / name
            shutil.copytree(work, mutant)
            text = (ROOT / (module + ".lean")).read_text()
            for old, new in edits:
                if text.count(old) != 1:
                    raise ValueError("Mutation anchor changed: " + name)
                text = text.replace(old, new)
            (mutant / (module + ".lean")).write_text(text)
            run(name + "-typecheck", [lean, "-o", module + ".olean", module + ".lean"], mutant)
            for runtime in downstream:
                run(name + "-" + runtime, [lean, "-o", runtime + ".olean", runtime + ".lean"], mutant)
            run(name + "-laws", [lean, proof_module + ".lean"], mutant, reject=True)
            (mutant / "Witness.lean").write_text(witness_source)
            failure = run(name + "-witness", [lean, "Witness.lean"], mutant, reject=True)
            if not re.fullmatch(r"Witness\.lean:3:\d+: error: Tactic `decide` proved that the proposition\n(?:  [^\n]*\n)+is false\n", failure):
                raise ValueError("Unexpected semantic witness rejection: " + name + "\n" + failure)
            controls[name] = "type-correct implementation; unchanged proof and exact false witness rejected"
        drift = base / "drift"
        drift.mkdir()
        for name in files:
            destination = drift / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, destination)
        for name, file, diagnostic in [
            ("typed-ir-drift", "FirstOrder.lean", "Preserved source changed: FirstOrder.lean"),
            ("source-excerpt-drift", "CLAUSES.json", "Preserved source changed: CLAUSES.json"),
            ("quotation-drift", "FixtureJson.lean", "Quoted fixture is not the exact JSON source"),
        ]:
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
              "new_declarations": own_names, "kernel_cases": declarations(ROOT / "Cases.lean"),
              "execution_rows": expected, "parser_observations": parser_expected, "controls": controls,
              "commands": commands, "sources": before, "temporary_builds_removed": True,
              "typed_data_codec_roundtrip_proved": True, "accepted_data_erasure_proved": True,
              "concrete_json_fixture_correspondence_proved": True,
              "universal_json_schema_correspondence_proved": False,
              "json_text_parser_proved": False, "mechanical_prose_derivation": False}
    (out / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(f"PASS: {len(audits)} audits ({len(own_names)} new), {len(report['kernel_cases'])} kernel cases, "
          f"{len(expected)} execution rows per runner, {len(parser_expected)} parser observations, {len(controls)} controls")


if __name__ == "__main__":
    main()
