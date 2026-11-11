import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import runpy
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parent
OWN = ["ParserSchema", "ParserReader", "ParserCodecLaws", "ParserEncoder", "ParserEncoderLaws",
       "ParserDocument", "ParserDocumentLaws", "NumberDocument", "NumberDocumentLaws",
       "Fixture", "Cases", "Runner", "EmitNumber"]


def sha(data):
    return hashlib.sha256(data).hexdigest()


def authenticate(root):
    preserved = json.loads((root / "PRESERVED.json").read_text())
    for record in preserved["records"]:
        name = record["installed"]
        if sha((root / name).read_bytes()) != record["installed_sha256"]:
            raise ValueError("Preserved source changed: " + name)


def declarations(path):
    scopes, names = [], []
    for raw in path.read_text().splitlines():
        line = raw.strip()
        opening = re.fullmatch(r"namespace (\S+)", line)
        ending = re.fullmatch(r"end(?: (\S+))?", line)
        theorem = re.match(r"(?:@\[[^]]+\] )?theorem (\S+)", line)
        if opening:
            scopes.append(opening[1])
        elif ending and ending[1] is not None:
            if not scopes or scopes[-1] != ending[1]:
                raise ValueError("Unexpected namespace")
            scopes.pop()
        elif theorem:
            names.append(".".join(scopes + [theorem[1]]))
    if scopes:
        raise ValueError("Unclosed namespace")
    return names


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--lean", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    lean, out = args.lean.resolve(), args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    sources = json.loads((ROOT / "SOURCE-ONLY.json").read_text())
    for name, digest in sources.items():
        if sha((ROOT / name).read_bytes()) != digest:
            raise ValueError("Source changed: " + name)
    authenticate(ROOT)
    if runpy.run_path(str(ROOT / "source_map.py"))["extract"]() != json.loads((ROOT / "CLAUSES.json").read_text()):
        raise ValueError("Pinned normative mapping changed")
    for variable, filename in [("numberFixture", "number.json"), ("changedFixture", "changed-number.json")]:
        literal = re.search(r"^def " + variable + r" : Json := json% (.+)$", (ROOT / "Fixture.lean").read_text(), re.M)
        if not literal or literal[1] + "\n" != (ROOT / filename).read_text():
            raise ValueError("Quoted fixture differs from actual file")
    preserved = json.loads((ROOT / "PRESERVED.json").read_text())
    modules = preserved["modules"] + [name + ".lean" for name in OWN]
    names, new_names = [], []
    for module in modules:
        path = ROOT / module
        if re.search(r"\bsorry\b|\badmit\b|\bnative_decide\b|^axiom |^partial |^unsafe ", path.read_text(), re.M):
            raise ValueError("Unapproved proof escape")
        found = declarations(path)
        names += found
        if module[:-5] in OWN:
            new_names += found
    if len(set(names)) != len(names):
        raise ValueError("Duplicate theorem")
    commands, controls = {}, {}

    def run(label, argv, work, reject=False):
        result = subprocess.run([str(x) for x in argv], cwd=work,
            env=dict(os.environ, LEAN_PATH=str(work)), capture_output=True, text=True)
        output = result.stdout + result.stderr
        (out / (label + ".log")).write_text(output)
        commands[label] = {"exit": result.returncode, "output_sha256": sha(output.encode())}
        if reject:
            if result.returncode != 1 or "error:" not in output:
                raise ValueError("Unexpected rejection: " + label + "\n" + output)
        elif result.returncode or re.search(r"(?m)^(?:[^\n]*:\d+:\d+: )?(?:warning:|error:|error\()", output):
            raise ValueError("Unexpected result: " + label + "\n" + output)
        return output

    with tempfile.TemporaryDirectory(prefix="number-document-", dir=out) as directory:
        base = Path(directory)
        work = base / "positive"
        work.mkdir()
        version = run("version", [lean, "--version"], work)
        if "version 4.35.0-rc4," not in version:
            raise ValueError("Wrong toolchain")
        for module in modules:
            path = work / module
            path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / module, path)
            run("build-" + module.replace("/", "-"), [lean, "-o", module[:-5] + ".olean", module], work)
        (work / "Audit.lean").write_text("import Cases\n" + "".join("#print axioms " + n + "\n" for n in names))
        output = run("audits", [lean, "Audit.lean"], work)
        audits = {}
        for line in re.sub(r",\n\s*", ", ", output).splitlines():
            match = re.fullmatch(r"'([^']+)' (does not depend on any axioms|depends on axioms: \[(.*)\])", line)
            if not match:
                raise ValueError("Unexpected axiom record: " + line)
            axioms = set(match[3].split(", ")) if match[3] else set()
            if not axioms <= {"propext", "Classical.choice", "Quot.sound"} or match[1] in audits:
                raise ValueError("Unapproved axiom record")
            audits[match[1]] = sorted(axioms)
        if set(audits) != set(names):
            raise ValueError("Incomplete axiom inventory")
        runtime = {}
        reference = runpy.run_path(str(ROOT / "reference.py"))["rows"]
        for changed, doc, expected in [(False, "number", "expected"), (True, "changed-number", "changed-expected")]:
            expected_rows = json.loads((ROOT / (expected + ".json")).read_text())
            if reference(changed) != expected_rows:
                raise ValueError("Reference observations changed")
            output = run("runtime-" + doc, [lean, "--run", "Runner.lean", ROOT / (doc + ".json")], work)
            if [json.loads(line) for line in output.splitlines()] != expected_rows:
                raise ValueError("Runtime mismatch: " + doc)
            emitted = run("emit-" + doc, [lean, "--run", "EmitNumber.lean"] + (["changed"] if changed else []), work)
            if emitted != (ROOT / (doc + ".json")).read_text():
                raise ValueError("Encoded fixture changed")
            runtime[doc] = expected_rows
        if runtime["number"] == runtime["changed-number"]:
            raise ValueError("Changed valid program had no effect")
        malformed = {}
        original = json.loads((ROOT / "number.json").read_text())
        for label in ["unknown-tag", "wrong-version", "extra-definitions", "extra-profile", "wrong-shape",
                      "wrong-arity", "parser-alias", "predicate-alias", "nonobject-source-map"]:
            bad = json.loads(json.dumps(original))
            if label == "unknown-tag": bad["program"]["op"] = "unknown"
            elif label == "wrong-version": bad["schema"] = "css-parser-ir-v2"
            elif label == "extra-definitions": bad["definitions"] = {}
            elif label == "extra-profile": bad["profile"] = "number"
            elif label == "wrong-shape": bad["program"] = {"op": "scan", "args": [{"op": "bool", "args": [True]}]}
            elif label == "wrong-arity": bad["program"]["args"].append(None)
            elif label == "parser-alias": bad["program"] = {"op": "use", "args": ["number"]}
            elif label == "predicate-alias": bad["program"]["args"][0]["args"][0]["args"][0] = {"op": "use", "args": ["sign"]}
            else: bad["source_map"] = None
            path = work / (label + ".json")
            path.write_text(json.dumps(bad))
            result = subprocess.run([str(lean), "--run", "Runner.lean", str(path)], cwd=work,
                env=dict(os.environ, LEAN_PATH=str(work)), capture_output=True, text=True)
            output = result.stdout + result.stderr
            (out / (label + ".log")).write_text(output)
            if result.returncode != 1 or output.strip() != "uncaught exception: rejected parser document":
                raise ValueError("Wrong actual-file rejection: " + label + "\n" + output)
            malformed[label] = {"exit": result.returncode, "output_sha256": sha(output.encode()), "input": bad}
        mutants = [
            ("optional-overrejection", "ParserReader", "ParserCodecLaws",
             '| "optional", [j] => do\n      let ⟨shape, p, proof⟩ ← readParser j\n      some ⟨.optional shape, .optional p, .optional proof⟩',
             '| "optional", [_] => none',
             '(decodeParser (.optional (.base .chars)) (nodeJson "optional" [nodeJson "scan" [nodeJson "bool" [.bool true]]])).isSome = true'),
            ("right-order-swapped", "ParserEncoder", "ParserEncoderLaws",
             '| _, .right a b => nodeJson "right" [encodeParser a, encodeParser b]',
             '| _, .right a b => nodeJson "right" [encodeParser b, encodeParser a]',
             '(decodeParser (.base .scalar) (encodeParser (.right (.take (.eqChar (.var .here) (.scalar \'a\'))) (.take (.eqChar (.var .here) (.scalar \'b\')))))).map '
             '(fun p => (ParserIR.run p ⟨"ab".toList, false⟩).map (fun x => x.1)) = some (some \'b\')'),
            ("nonempty-erased", "ParserEncoder", "ParserEncoderLaws",
             '| _, .nonempty p => nodeJson "nonempty" [encodeParser p]',
             '| _, .nonempty p => encodeParser p',
             '(decodeParser (.base .chars) (encodeParser (.nonempty (.scan (.bool true))))).map '
             '(fun p => (ParserIR.run p ⟨[], false⟩).isNone) = some true'),
            ("version-guard-removed", "ParserDocument", "ParserDocumentLaws",
             '    if version.getStr?.toOption != some "css-parser-ir-v1" then none else do',
             '    let _ := version\n    do',
             '(readDocument (.base .chars) (Json.mkObj [("schema", .str "css-parser-ir-v2"), '
             '("program", encodeParser (.scan (.bool true))), ("source_map", Json.mkObj [])])).isNone = true'),
        ]
        for name, implementation, laws, old, new, proposition in mutants:
            witness = ("import " + implementation + "\nopen Lean CssDerivation CssDerivation.FirstOrder "
                "CssDerivation.JsonSchema CssDerivation.ParserIR CssDerivation.ParserJson\n"
                "set_option cbv.warning false\nset_option maxRecDepth 30000\nset_option maxHeartbeats 4000000\n"
                "example : " + proposition + " := by\n  conv => lhs; cbv\n  all_goals decide\n")
            (work / "Witness.lean").write_text(witness)
            run(name + "-positive", [lean, "Witness.lean"], work)
            mutant = base / name
            shutil.copytree(work, mutant)
            source = (ROOT / (implementation + ".lean")).read_text()
            if source.count(old) != 1:
                raise ValueError("Mutation anchor changed: " + name)
            (mutant / (implementation + ".lean")).write_text(source.replace(old, new))
            run(name + "-compiles", [lean, "-o", implementation + ".olean", implementation + ".lean"], mutant)
            run(name + "-laws", [lean, laws + ".lean"], mutant, reject=True)
            failure = run(name + "-witness", [lean, "Witness.lean"], mutant, reject=True)
            if not re.fullmatch(r"Witness\.lean:\d+:\d+: error: Tactic `decide` proved that the proposition\n(?:  [^\n]*\n)+is false\n", failure):
                raise ValueError("Not an exact semantic false witness: " + name + "\n" + failure)
            controls[name] = "implementation compiles; unchanged theorem and concrete false witness reject"
        drift = base / "drift"
        drift.mkdir()
        for name in ["PRESERVED.json"] + sorted({r["installed"] for r in preserved["records"]}):
            path = drift / name
            path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, path)
        for name in ["ParserIR.lean", "CssDerivation/Codec/Json/Reader.lean", "inputs/css-syntax-3.bs"]:
            original = (drift / name).read_bytes()
            (drift / name).write_bytes(original + b"changed")
            try:
                authenticate(drift)
            except ValueError as error:
                if str(error) != "Preserved source changed: " + name: raise
                controls["drift:" + name] = str(error)
            else:
                raise ValueError("Drift was not rejected")
            (drift / name).write_bytes(original)
    if sources != {name: sha((ROOT / name).read_bytes()) for name in sources}:
        raise ValueError("Sources changed during validation")
    report = {"status": "pass", "audits": audits, "new_declarations": new_names,
        "kernel_cases": declarations(ROOT / "Cases.lean"), "runtime": runtime,
        "malformed_documents": malformed, "controls": controls, "commands": commands,
        "source_sha256": sources, "temporary_builds_removed": True,
        "parser_schema_sound_and_complete": True, "envelope_sound_and_complete": True,
        "full_state_lowering_composed": True, "number_shape_implies_css_algorithm": False,
        "json_text_parser_proved": False, "mechanical_prose_derivation": False}
    (out / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(f"PASS: {len(audits)} audits ({len(new_names)} new), {len(report['kernel_cases'])} cases, "
          f"{sum(map(len, runtime.values()))} runtime rows, {len(malformed)} refusals, {len(controls)} controls")


if __name__ == "__main__":
    main()
