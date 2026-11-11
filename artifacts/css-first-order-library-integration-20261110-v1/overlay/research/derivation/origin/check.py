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
OWN = ["Schema", "Reader", "SchemaLaws", "Encoder", "EncoderLaws", "TypedSchemaLaws",
       "Document", "Fixture", "Cases", "Runner", "RoundtripRunner", "ReferenceRunner", "ParserBoundary"]


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
        if re.search(r"\bsorry\b|\badmit\b|\bnative_decide\b|^axiom |^unsafe |^partial ", path.read_text(), re.M):
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
    with tempfile.TemporaryDirectory(prefix="json-schema-check-", dir=out) as directory:
        base = Path(directory)
        work = base / "positive"
        work.mkdir()
        for module in modules:
            destination = work / (module + ".lean")
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / (module + ".lean"), destination)
            run("build-" + module.replace("/", "-"), [lean, "-o", module + ".olean", module + ".lean"], work)
        (work / "Audit.lean").write_text("import Cases\n" + "".join(
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
        for runner in ["Runner", "RoundtripRunner", "ReferenceRunner"]:
            output = run(runner, [lean, "--run", runner + ".lean", ROOT / "escape.json"] +
                         [row["input"] for row in expected], work)
            if [json.loads(line) for line in output.splitlines()] != expected:
                raise ValueError("Unexpected execution: " + runner)
        parser_expected = json.loads((ROOT / "PARSER-EXPECTED.json").read_text())
        output = run("parser-boundary", [lean, "--run", "ParserBoundary.lean"] +
                     [row["text"] for row in parser_expected], work)
        if [json.loads(line) for line in output.splitlines()] != [row["value"] for row in parser_expected]:
            raise ValueError("Unexpected JSON parser observation")
        refusal_cases = {}
        fixture = json.loads((ROOT / "escape.json").read_text())
        for label in ["extra-document-field", "extra-ast-field", "alias-cycle", "alias-tail-capture"]:
            bad = json.loads(json.dumps(fixture))
            if label == "extra-document-field":
                bad["code"] = "extra"
            elif label == "extra-ast-field":
                bad["program"]["code"] = "extra"
            elif label == "alias-cycle":
                bad["definitions"]["hexExpr"] = {"op": "use", "args": ["hexExpr"]}
            else:
                bad["definitions"]["hexExpr"] = {"op": "eqChar", "args": [
                    {"op": "var", "args": [1]}, {"op": "scalar", "args": [0]}]}
            path = work / (label + ".json")
            path.write_text(json.dumps(bad))
            result = subprocess.run([str(lean), "--run", "Runner.lean", str(path)], cwd=work,
                                    env=dict(os.environ, LEAN_PATH=str(work)), capture_output=True, text=True)
            output = result.stdout + result.stderr
            (out / (label + ".log")).write_text(output)
            if result.returncode != 1 or output.strip() != "uncaught exception: document refused":
                raise ValueError("Unexpected malformed-document result: " + label + "\n" + output)
            refusal_cases[label] = {"exit": result.returncode, "output_sha256": sha(output.encode())}
        mutations = [
            ("encoder-opcode", "Encoder", "EncoderLaws", [],
             [('| .sub a b => nodeJson "sub" [encodeExprJson a, encodeExprJson b]',
               '| .sub a b => nodeJson "add" [encodeExprJson a, encodeExprJson b]')], "Encoder",
             "((checkExprJson [] [] .nat (encodeExprJson (.sub (.nat 7) (.nat 2) : Expr [] .nat))).map (fun e => eval e .nil)) = some 5"),
            ("encoder-child-order", "Encoder", "EncoderLaws", [],
             [('| .sub a b => nodeJson "sub" [encodeExprJson a, encodeExprJson b]',
               '| .sub a b => nodeJson "sub" [encodeExprJson b, encodeExprJson a]')], "Encoder",
             "((checkExprJson [] [] .nat (encodeExprJson (.sub (.nat 7) (.nat 2) : Expr [] .nat))).map (fun e => eval e .nil)) = some 5"),
            ("encoder-scan-budget", "Encoder", "EncoderLaws", [],
             [('| .scan n e p => nodeJson "scan" [natJson n, encodeExprJson e, encodeStmtJson p]',
               '| .scan n e p => nodeJson "scan" [natJson (n + 1), encodeExprJson e, encodeStmtJson p]')], "Encoder",
             "((checkStmtJson [] [] .chars (encodeStmtJson (.scan 1 (.bool true) (.ret (.var .here)) : Stmt [] .chars))).map (fun p => (interpret p .nil ⟨['a','b'],false⟩).1)) = some ['a']"),
            ("reader-unit-omission", "Reader", "SchemaLaws", ["Encoder"],
             [('| "unit", [] => some ⟨.unit, .unit⟩',
               '| "unit", [] => if true then none else some ⟨.unit, .unit⟩')], "Encoder",
             '(readExprData [] (nodeJson "unit" [])).isSome = true'),
            ("reader-raw-layout-omission", "Reader", "SchemaLaws", ["Encoder"],
             [('some ⟨e, .node (.rightOp outer inner op args) proof⟩',
               'if true then none else some ⟨e, .node (.rightOp outer inner op args) proof⟩')], "Encoder",
             '(readExprData [] (rightObject 0 999 "op" (.str "nat") "args" (.arr #[7]))).isSome = true'),
            ("document-alias-selection", "Document", "Fixture", [],
             [('let hex ← readDefinition definitions "hexExpr" .scalar .bool',
               'let hex ← readDefinition definitions "whitespaceExpr" .scalar .bool')], "Document\nimport FixtureJson",
             "((readDocument TypedCodec.fixture).map (fun p => (FirstOrder.execute p ['4','1','!']).value.toNat)) = some 65"),
        ]
        for name, module, proof_module, downstream, edits, witness_import, witness in mutations:
            witness_source = ("import " + witness_import +
                "\nopen CssDerivation CssDerivation.FirstOrder CssDerivation.JsonSchema Lean\nset_option cbv.warning false\nset_option maxRecDepth 30000\nset_option maxHeartbeats 4000000\nexample : " + witness + " := by\n  conv => lhs; cbv\n  all_goals decide\n")
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
            if not re.fullmatch(r"Witness\.lean:\d+:\d+: error: Tactic `decide` proved that the proposition\n(?:  [^\n]*\n)+is false\n", failure):
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
            ("quotation-drift", "FixtureJson.lean", "Preserved source changed: FixtureJson.lean"),
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
              "malformed_documents": refusal_cases,
              "commands": commands, "sources": before, "temporary_builds_removed": True,
              "canonical_json_value_roundtrip_proved": True, "json_schema_sound_and_complete_proved": True,
              "concrete_json_fixture_correspondence_proved": True,
              "alias_free_json_typed_correspondence_proved": True,
              "universal_document_orchestration_proved": False,
              "json_text_parser_proved": False, "mechanical_prose_derivation": False}
    (out / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(f"PASS: {len(audits)} audits ({len(own_names)} new), {len(report['kernel_cases'])} kernel cases, "
          f"{len(expected)} execution rows per runner, {len(parser_expected)} parser observations, {len(refusal_cases)} document refusals, {len(controls)} controls")


if __name__ == "__main__":
    main()
