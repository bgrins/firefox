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
OWN = ["DocumentModel", "KeyLaws", "DefinitionLaws", "DocumentLaws", "AliasBridge",
       "Fixture", "Examples", "Cases", "Runner"]


def sha(data):
    return hashlib.sha256(data).hexdigest()


def authenticate(root):
    preserved = json.loads((root / "PRESERVED.json").read_text())
    for category in ["canonical_sha256", "prototype_sha256", "fixture_sha256"]:
        for name, digest in preserved[category].items():
            if sha((root / name).read_bytes()) != digest:
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
    for name, expected in sources.items():
        if sha((ROOT / name).read_bytes()) != expected:
            raise ValueError("Source changed: " + name)
    authenticate(ROOT)
    preserved = json.loads((ROOT / "PRESERVED.json").read_text())
    modules = preserved["canonical_modules"] + ["Model.lean", "Prototype.lean"] + [n + ".lean" for n in OWN]
    names, new_names = [], []
    for module in modules:
        p = ROOT / module
        if re.search(r"\bsorry\b|\badmit\b|\bnative_decide\b|^axiom |^partial |^unsafe ", p.read_text(), re.M):
            raise ValueError("Unapproved proof escape")
        found = declarations(p)
        names += found
        if module[:-5] in OWN:
            new_names += found
    if len(names) != len(set(names)):
        raise ValueError("Duplicate theorem")
    commands = {}

    def run(label, argv, work, reject=False):
        p = subprocess.run([str(x) for x in argv], cwd=work,
                           env=dict(os.environ, LEAN_PATH=str(work)), capture_output=True, text=True)
        output = p.stdout + p.stderr
        (out / (label + ".log")).write_text(output)
        commands[label] = {"exit": p.returncode, "output_sha256": sha(output.encode())}
        if reject:
            if p.returncode != 1 or "error:" not in output:
                raise ValueError("Unexpected rejection: " + label + "\n" + output)
        elif p.returncode or re.search(r"(?m)^(?:[^\n]*:\d+:\d+: )?(?:warning:|error:|error\()", output):
            raise ValueError("Unexpected result: " + label + "\n" + output)
        return output

    controls = {}
    with tempfile.TemporaryDirectory(prefix="document-schema-", dir=out) as directory:
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
        profiles = json.loads((ROOT / "PROFILE-EXPECTED.json").read_text())
        profiles["escape"] = {"profile": "escape", "rows": json.loads((ROOT / "EXPECTED.json").read_text())}
        for name, fixture in profiles.items():
            rows = fixture["rows"]
            output = run("runtime-" + name, [lean, "--run", "Runner.lean", fixture["profile"],
                         ROOT / (name + ".json")] + [row["input"] for row in rows], work)
            if [json.loads(line) for line in output.splitlines()] != rows:
                raise ValueError("Runtime result mismatch: " + name)
        malformed = {}
        original = json.loads((ROOT / "next.json").read_text())
        for label in ["extra-field", "wrong-version", "missing-definition", "extra-definition",
                      "wrong-result", "tail-capture", "self-use", "nonobject-source-map"]:
            bad = json.loads(json.dumps(original))
            if label == "extra-field":
                bad["extra"] = 0
            elif label == "wrong-version":
                bad["schema"] = 2
            elif label == "missing-definition":
                bad["definitions"] = {}
            elif label == "extra-definition":
                bad["definitions"]["extra"] = bad["definitions"]["next"]
            elif label == "wrong-result":
                bad["definitions"]["next"] = {"op": "nat", "args": [0]}
            elif label == "tail-capture":
                bad["definitions"]["next"] = {"op": "scalarOf", "args": [{"op": "var", "args": [1]}]}
            elif label == "self-use":
                bad["definitions"]["next"] = {"op": "use", "args": ["next"]}
            else:
                bad["source_map"] = None
            path = work / (label + ".json")
            path.write_text(json.dumps(bad))
            p = subprocess.run([str(lean), "--run", "Runner.lean", "next", str(path)], cwd=work,
                               env=dict(os.environ, LEAN_PATH=str(work)), capture_output=True, text=True)
            output = p.stdout + p.stderr
            (out / (label + ".log")).write_text(output)
            if p.returncode != 1 or output.strip() != "uncaught exception: document refused":
                raise ValueError("Wrong actual-file rejection " + label + "\n" + output)
            malformed[label] = {"exit": p.returncode, "output_sha256": sha(output.encode())}
        mutants = [
            ("duplicate-signature-guard", "DefinitionLaws", ["KeyLaws"],
             "if (signatures.map Signature.name).Nodup then\n"
             "    if fieldsExactly definitions (signatures.map Signature.name) then\n"
             "      readDefinitionList signatures definitions\n    else none\n  else none",
             "if fieldsExactly definitions (signatures.map Signature.name) then\n"
             "    readDefinitionList signatures definitions\n  else none",
             "(readDefinitions duplicateProfile duplicateExploit).isNone = true"),
            ("declared-result-ignored", "DefinitionLaws", ["KeyLaws"],
             "readDefinition definitions signature.name signature.head signature.result",
             "readDefinition definitions signature.name signature.head .scalar",
             "(readDefinitions wrongResultProfile nextDefinitions).isNone = true"),
            ("definition-name-swapped", "DefinitionLaws", ["KeyLaws"],
             "readDefinition definitions signature.name signature.head signature.result",
             'readDefinition definitions "next" signature.head signature.result',
             '((readDefinitions [nextSignature, ⟨"second", .nat, .scalar⟩] '
             '(.mkObj [("second", nextBody), ("next", nextBody)])).map (fun aliases => aliases.map Prod.fst)) '
             '= some ["next", "second"]'),
            ("source-map-executed", "DocumentLaws", ["KeyLaws", "DefinitionLaws"],
             'let program ← field j "program"', 'let program ← field j "source_map"',
             'valueOf [] (document (.mkObj []) (nodeJson "ret" [nodeJson "scalar" [65]]) '
             '(nodeJson "ret" [nodeJson "scalar" [66]])) = some 65'),
        ]
        for name, law, downstream, old, new, proposition in mutants:
            witness = ("import Examples\nopen Lean CssDerivation CssDerivation.FirstOrder "
                       "CssDerivation.JsonSchema CssDerivation.DocumentSchema CssDerivation.DocumentSchema.Examples\n"
                       "set_option cbv.warning false\nset_option maxRecDepth 30000\nset_option maxHeartbeats 4000000\n"
                       "example : " + proposition + " := by\n  conv => lhs; cbv\n  all_goals decide\n")
            (work / "Witness.lean").write_text(witness)
            run(name + "-positive", [lean, "Witness.lean"], work)
            mutant = base / name
            shutil.copytree(work, mutant)
            source = (ROOT / "DocumentModel.lean").read_text()
            if source.count(old) != 1:
                raise ValueError("Mutation anchor changed " + name)
            (mutant / "DocumentModel.lean").write_text(source.replace(old, new))
            run(name + "-compiles", [lean, "-o", "DocumentModel.olean", "DocumentModel.lean"], mutant)
            for module in downstream + ["Examples"]:
                run(name + "-rebuild-" + module, [lean, "-o", module + ".olean", module + ".lean"], mutant)
            run(name + "-laws", [lean, law + ".lean"], mutant, reject=True)
            failure = run(name + "-witness", [lean, "Witness.lean"], mutant, reject=True)
            if not re.fullmatch(r"Witness\.lean:\d+:\d+: error: Tactic `decide` proved that the proposition\n(?:  [^\n]*\n)+is false\n", failure):
                raise ValueError("Not the exact semantic false witness: " + name + "\n" + failure)
            controls[name] = "implementation compiles; unchanged theorem and concrete false witness reject"
        drift = base / "drift"
        drift.mkdir()
        for name in ["PRESERVED.json"] + list(preserved["canonical_sha256"]) + list(preserved["prototype_sha256"]) + list(preserved["fixture_sha256"]):
            path = drift / name
            path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, path)
        for name in ["CssDerivation/Codec/Json/Reader.lean", "Prototype.lean", "escape.json"]:
            original = (drift / name).read_bytes()
            (drift / name).write_bytes(original + b"changed")
            try:
                authenticate(drift)
            except ValueError as error:
                if str(error) != "Preserved source changed: " + name:
                    raise
                controls["drift:" + name] = str(error)
            else:
                raise ValueError("Drift was not rejected")
            (drift / name).write_bytes(original)
    if sources != {name: sha((ROOT / name).read_bytes()) for name in sources}:
        raise ValueError("Sources changed during validation")
    report = {"status": "pass", "audits": audits, "new_declarations": new_names,
              "kernel_cases": declarations(ROOT / "Cases.lean"), "runtime_profiles": profiles,
              "malformed_documents": malformed, "controls": controls, "commands": commands,
              "source_sha256": sources, "temporary_builds_removed": True,
              "definition_list_sound_and_complete": True, "document_sound": True,
              "escape_wrapper_all_json_equivalent": True, "selected_alias_noncapture": True,
              "arbitrary_alias_document_converse": False, "json_text_parser_proved": False,
              "mechanical_prose_derivation": False}
    (out / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(f"PASS: {len(audits)} audits ({len(new_names)} new), {len(report['kernel_cases'])} cases, "
          f"{sum(len(p['rows']) for p in profiles.values())} runtime rows, {len(malformed)} refusals, {len(controls)} controls")


if __name__ == "__main__":
    main()
