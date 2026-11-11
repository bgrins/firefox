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
OWN = ["ByteAdapter", "PartsBridge", "Observation", "LexicalBridge", "EntryBridge",
       "DocumentBridge", "TokenBridge", "RuntimeSupport", "Cases", "Runner", "ReferenceRunner"]


MUTANTS = [
    ("sign-presence-lost", "    parts.1.isSome,", "    false,",
     "(observeDocument numberFixture ⟨['+', '0', 'x'], false⟩).map Observation.hasSign = some true"),
    ("exponent-type-lost", "parts.2.2.1.isNone && parts.2.2.2.isNone", "parts.2.2.1.isNone",
     "(observeDocument numberFixture ⟨['1', 'e', '0'], false⟩).map Observation.isInteger = some false"),
    ("prefix-one-too-long", "source.length - rest.length", "source.length - rest.length + 1",
     "(observeDocument numberFixture ⟨['1', 'x'], false⟩).map Observation.consumed = some [49]"),
]


def sha(data):
    return hashlib.sha256(data).hexdigest()


def authenticate(root):
    for record in json.loads((root / "PRESERVED.json").read_text())["records"]:
        name = record["installed"]
        if sha((root / name).read_bytes()) != record["sha256"]:
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
    for name, old, _, _ in MUTANTS:
        if (ROOT / "Observation.lean").read_text().count(old) != 1:
            raise ValueError("Mutation anchor changed: " + name)
    quoted = ROOT / "CssDerivation/Examples/NumberDocument.lean"
    literal = re.search(r"^def numberFixture : Json := json% (.+)$", quoted.read_text(), re.M)
    if not literal or literal[1] + "\n" != (ROOT / "number.json").read_text():
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
    known_diagnostics = json.loads((ROOT / "LEGACY-DIAGNOSTICS.json").read_text())

    def run(label, argv, work, reject=False):
        result = subprocess.run([str(x) for x in argv], cwd=work,
            env=dict(os.environ, LEAN_PATH=str(work)), capture_output=True, text=True)
        output = result.stdout + result.stderr
        (out / (label + ".log")).write_text(output)
        commands[label] = {"argv": [str(x) for x in argv], "exit": result.returncode, "output_sha256": sha(output.encode())}
        if reject:
            if result.returncode != 1 or "error:" not in output:
                raise ValueError("Unexpected rejection: " + label + "\n" + output)
        elif label in known_diagnostics:
            if result.returncode or sha(output.encode()) != known_diagnostics[label]:
                raise ValueError("Changed legacy diagnostic: " + label + "\n" + output)
        elif result.returncode or re.search(r"(?m)^(?:[^\n]*:\d+:\d+: )?(?:warning:|error:|error\()", output):
            raise ValueError("Unexpected result: " + label + "\n" + output)
        return output

    with tempfile.TemporaryDirectory(prefix="number-lexical-", dir=out) as directory:
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
        for label, command, expected in [
            ("actual-file", ["Runner.lean", ROOT / "number.json", ROOT / "corpus.json"], "expected.json"),
            ("reference", ["ReferenceRunner.lean", ROOT / "corpus.json"], "expected.json"),
            ("changed-valid", ["Runner.lean", ROOT / "changed-number.json", ROOT / "changed-corpus.json"], "changed-expected.json")]:
            output = run(label, [lean, "--run", *command], work)
            rows = [json.loads(line) for line in output.splitlines()]
            if rows != json.loads((ROOT / expected).read_text()):
                raise ValueError("Runtime mismatch: " + label)
            runtime[label] = rows
        fixed_pair = [row for row in runtime["actual-file"] if row[0] == "1+2"]
        if fixed_pair == runtime["changed-valid"]:
            raise ValueError("Changed valid input program had no effect")
        malformed = {}
        original = json.loads((ROOT / "number.json").read_text())
        for label in ["unknown-tag", "wrong-version", "wrong-arity", "parser-alias", "wrong-shape"]:
            bad = json.loads(json.dumps(original))
            if label == "unknown-tag": bad["program"]["op"] = "unknown"
            elif label == "wrong-version": bad["schema"] = "css-parser-ir-v2"
            elif label == "wrong-arity": bad["program"]["args"].append(None)
            elif label == "parser-alias": bad["program"] = {"op": "use", "args": ["number"]}
            else: bad["program"] = {"op": "scan", "args": [{"op": "bool", "args": [True]}]}
            path = work / (label + ".json")
            path.write_text(json.dumps(bad))
            result = subprocess.run([str(lean), "--run", "Runner.lean", str(path), str(ROOT / "corpus.json")], cwd=work,
                env=dict(os.environ, LEAN_PATH=str(work)), capture_output=True, text=True)
            output = result.stdout + result.stderr
            (out / (label + ".log")).write_text(output)
            if result.returncode != 1 or output.strip() != "uncaught exception: document rejected":
                raise ValueError("Wrong actual-file rejection: " + label + "\n" + output)
            malformed[label] = {"exit": result.returncode, "output_sha256": sha(output.encode()), "input": bad}
        for name, old, new, proposition in MUTANTS:
            witness = ("import Observation\nimport CssDerivation.Examples.NumberDocument\n"
                "open CssNumberLexicalBridge CssDerivation.ParserJson CssDerivation.NumberTransfer\n"
                "set_option cbv.warning false\nset_option maxRecDepth 30000\nset_option maxHeartbeats 4000000\n"
                "example : " + proposition + " := by\n  conv => lhs; cbv\n  all_goals decide\n")
            (work / "Witness.lean").write_text(witness)
            run(name + "-positive", [lean, "Witness.lean"], work)
            mutant = base / name
            shutil.copytree(work, mutant)
            source = (ROOT / "Observation.lean").read_text()
            if source.count(old) != 1:
                raise ValueError("Mutation anchor changed: " + name)
            (mutant / "Observation.lean").write_text(source.replace(old, new))
            run(name + "-compiles", [lean, "-o", "Observation.olean", "Observation.lean"], mutant)
            failure = run(name + "-laws", [lean, "LexicalBridge.lean"], mutant, reject=True)
            if "unsolved goals" not in failure or any(x in failure for x in ["unknown identifier", "Unknown module", "failed to synthesize"]):
                raise ValueError("Wrong law failure: " + name)
            failure = run(name + "-witness", [lean, "Witness.lean"], mutant, reject=True)
            if not re.fullmatch(r"Witness\.lean:\d+:\d+: error: Tactic `decide` proved that the proposition\n(?:  [^\n]*\n)+is false\n", failure):
                raise ValueError("Not an exact semantic false witness: " + name + "\n" + failure)
            controls[name] = "adapter compiles; unchanged law and exact false witness reject"
        drift = base / "drift"
        drift.mkdir()
        for name in ["PRESERVED.json"] + sorted({r["installed"] for r in preserved["records"]}):
            path = drift / name
            path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, path)
        for name in ["NumericLexical.lean", "CssDerivation/Examples/NumberTree.lean", "number.json"]:
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
        "legacy_diagnostics_exact_hashes": known_diagnostics,
        "normalized_ascii_caller_bridge": True, "fixed_json_full_state_lowering_composed": True,
        "numeric_core_distinct_from_full_token": True, "native_rust_refinement": False,
        "native_error_mapping": False, "json_text_parser_proved": False,
        "float_conversion_proved": False, "mechanical_prose_derivation": False}
    (out / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(f"PASS: {len(audits)} audits ({len(new_names)} new), {len(report['kernel_cases'])} cases, "
          f"{sum(map(len, runtime.values()))} runtime rows, {len(malformed)} refusals, {len(controls)} controls")


if __name__ == "__main__":
    main()
