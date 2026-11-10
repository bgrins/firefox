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
OWN = ["PairStream", "PairLaws", "Adapters", "AdapterLaws", "Pipeline", "PipelineLaws", "Cases"]


def sha(data):
    return hashlib.sha256(data).hexdigest()


def authenticate(root):
    library = json.loads((root / "LIBRARY.json").read_text())
    for name, digest in library["sha256"].items():
        if sha((root / name).read_bytes()) != digest:
            raise ValueError("Reference library changed: " + name)
    for clause in json.loads((root / "CLAUSES.json").read_text())["clauses"]:
        if sha((root / clause["file"]).read_bytes()) != clause["sha256"]:
            raise ValueError("Specification excerpt changed: " + clause["anchor"])


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
    library = json.loads((ROOT / "LIBRARY.json").read_text())
    modules = ["CssSemantics/" + name for name in library["modules"]] + OWN
    files = [module + ".lean" for module in modules] + [
        "check.py", "EXPECTED.json", "SOURCES.json", "CLAUSES.json", "LIBRARY.json", "MAPPING.md"]
    files += [clause["file"] for clause in json.loads((ROOT / "CLAUSES.json").read_text())["clauses"]]
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
        elif process.returncode or re.search(r"\bwarning:|\berror:|\bsorry\b", output):
            raise ValueError("Unexpected diagnostic: " + name + "\n" + output)
        return output

    version = run("version", [lean, "--version"], out).strip()
    if "version 4.35.0-rc4," not in version:
        raise ValueError("Unexpected Lean version")
    controls = {}
    with tempfile.TemporaryDirectory(prefix="domstring-stream-check-", dir=out) as directory:
        base = Path(directory)
        work = base / "positive"
        work.mkdir()
        for module in modules:
            destination = work / (module + ".lean")
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / (module + ".lean"), destination)
            run("build-" + module.replace("/", "-"), [lean, "-o", module + ".olean", module + ".lean"], work)
        (work / "Audit.lean").write_text("import PipelineLaws\n" + "".join(
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
        (work / "Run.lean").write_text('import Cases\ndef main : IO Unit := do\n  for (name, ok) in CssStreaming.Cases.checks do\n    IO.println s!"{name}: {ok}"\n')
        observations = run("examples", [lean, "--run", "Run.lean"], work).splitlines()
        expected = json.loads((ROOT / "EXPECTED.json").read_text())
        if observations != [name + ": true" for name in expected]:
            raise ValueError("Unexpected examples")
        mutations = [
            ("reset-surrogate-at-chunk", "PairStream", "PairLaws",
             "let first := feed machine pending input", "let first := feed machine none input",
             "decodeValues [[0xd83d], [0xdca9]] = some [0x1f4a9]"),
            ("omit-utf16-eof", "Pipeline", "PipelineLaws",
             "let lastInput := flush first result.inputPending", "let lastInput := (flush first result.inputPending).take 0",
             "prepareValues [[0xd800]] = some [0xfffd]"),
            ("omit-css-eof", "Pipeline", "PipelineLaws",
             "flush second lastOutput.pending", "(flush second lastOutput.pending).take 0",
             "prepareValues [[13]] = some [10]"),
            ("reset-cr-at-chunk", "Pipeline", "PipelineLaws",
             "feed second middlePending decoded.output", "feed second none decoded.output",
             "prepareValues [[13], [0x61]] = some [10, 0x61]"),
            ("early-surrogate-replacement", "Adapters", "AdapterLaws",
             "single := DomString.unitPoint",
             "single := fun unit => if DomString.Leading unit ∨ DomString.Trailing unit then ⟨0xfffd, by decide⟩ else DomString.unitPoint unit",
             "decodeValues [[0xd800]] = some [0xd800]"),
            ("wrong-pair-value", "Adapters", "AdapterLaws",
             "if pair : DomString.Leading first ∧ DomString.Trailing second then\n      some (DomString.pairPoint first second pair.1 pair.2)",
             "if _pair : DomString.Leading first ∧ DomString.Trailing second then\n      some (DomString.unitPoint first)",
             "decodeValues [[0xd800], [0xdc00]] = some [0x10000]"),
        ]
        for name, module, proof_module, old, new, witness in mutations:
            mutant = base / name
            shutil.copytree(work, mutant)
            text = (ROOT / (module + ".lean")).read_text()
            if text.count(old) != 1:
                raise ValueError("Mutation anchor changed: " + name)
            (mutant / (module + ".lean")).write_text(text.replace(old, new))
            run(name + "-typecheck", [lean, "-o", module + ".olean", module + ".lean"], mutant)
            if module == "PairStream":
                for runtime in ["Adapters", "Pipeline"]:
                    run(name + "-" + runtime, [lean, "-o", runtime + ".olean", runtime + ".lean"], mutant)
            run(name + "-laws", [lean, proof_module + ".lean"], mutant, reject=True)
            run(name + "-cases", [lean, "-o", "Cases.olean", "Cases.lean"], mutant)
            (mutant / "Witness.lean").write_text("import Cases\nopen CssStreaming CssStreaming.Cases\nexample : " + witness + " := by decide\n")
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
            ("library-drift", "CssSemantics/CssDomStringInput.lean", "Reference library changed: CssSemantics/CssDomStringInput.lean"),
            ("css-source-drift", "spec/css-input-preprocessing.txt", "Specification excerpt changed: input-preprocessing"),
            ("utf16-source-drift", "spec/ecma-sec-stringtocodepoints.txt", "Specification excerpt changed: sec-stringtocodepoints"),
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
              "utf16_chunk_equivalence_proved": True, "css_chunk_equivalence_proved": True,
              "composed_incremental_equivalence_proved": True,
              "cssom_coercion_proved": False, "byte_decoding_proved": False,
              "mechanical_prose_derivation": False, "native_refinement_proved": False}
    (out / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(f"PASS: {len(audits)} audits ({len(own_names)} new), {len(expected)} observations, {len(controls)} controls")


if __name__ == "__main__":
    main()
