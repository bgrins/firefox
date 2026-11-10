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
MODULES = ["Model", "Laws", "Cases"]


def sha(data):
    return hashlib.sha256(data).hexdigest()


def source_check(root):
    source = json.loads((root / "SOURCE.json").read_text())
    data = (root / source["file"]).read_bytes()
    if sha(data) != source["sha256"]:
        raise ValueError("Specification snapshot changed")
    for record in source["excerpts"]:
        excerpt = data[record["start_byte"]:record["end_byte"]]
        if sha(excerpt) != record["sha256"] or excerpt != (root / record["file"]).read_bytes():
            raise ValueError("Specification excerpt changed: " + record["id"])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--lean", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    lean, out = args.lean.resolve(), args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    source_check(ROOT)
    names = re.findall(r"^theorem (\w+)", (ROOT / "Laws.lean").read_text(), re.M)
    files = [module + ".lean" for module in MODULES] + [
        "check.py", "EXPECTED.json", "SOURCE.json", "MAPPING.md", "variables.html",
        "replacement.html", "acquisition-boundary.html", "infectious.html"]
    before = {name: sha((ROOT / name).read_bytes()) for name in files}
    for module in MODULES:
        if re.search(r"\bsorry\b|\badmit\b|^axiom |^unsafe ", (ROOT / (module + ".lean")).read_text(), re.M):
            raise ValueError("Unapproved proof escape")
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
    with tempfile.TemporaryDirectory(prefix="taint-check-", dir=out) as directory:
        base = Path(directory)
        work = base / "positive"
        work.mkdir()
        for module in MODULES:
            shutil.copyfile(ROOT / (module + ".lean"), work / (module + ".lean"))
            run("build-" + module, [lean, "-o", module + ".olean", module + ".lean"], work)
        (work / "Audit.lean").write_text("import Laws\n" + "".join(
            "#print axioms CssAnimationTaint." + name + "\n" for name in names))
        output = run("axioms", [lean, "Audit.lean"], work)
        audits = {}
        for line in re.sub(r",\n\s*", ", ", output).splitlines():
            match = re.fullmatch(r"'CssAnimationTaint\.(\w+)' (does not depend on any axioms|depends on axioms: \[(.*)\])", line)
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
        (work / "Run.lean").write_text('import Cases\ndef main : IO Unit := do\n  for (name, ok) in CssAnimationTaint.Cases.checks do\n    IO.println s!"{name}: {ok}"\n')
        observations = run("examples", [lean, "--run", "Run.lean"], work).splitlines()
        expected = json.loads((ROOT / "EXPECTED.json").read_text())
        if observations != [name + ": true" for name in expected]:
            raise ValueError("Unexpected examples")
        mutations = [
            ("missing-animation-gate",
             "if binding.animationTainted && destination == .nonanimatable then none",
             "if binding.animationTainted && destination == .nonanimatable then binding.value",
             "evaluate environment .nonanimatable (.reference 1 (some (.literal fallback))) = ⟨some fallback, [1]⟩"),
            ("overbroad-animation-gate",
             "binding.animationTainted && destination == .nonanimatable",
             "binding.animationTainted && (destination == .nonanimatable || destination == .animatable)",
             "evaluate environment .animatable (.reference 1 none) = ⟨some plain, [1]⟩"),
            ("conflated-attribute-gate",
             "binding.animationTainted && destination",
             "(binding.animationTainted || binding.value.any (·.attributeTainted)) && destination",
             "evaluate environment .nonanimatable (.reference 2 none) = ⟨some attr, [2]⟩"),
            ("eager-unused-fallback",
             "| some value => ⟨some value, [name]⟩",
             "| some value =>\n      match fallback with\n      | none => ⟨some value, [name]⟩\n      | some expression =>\n        let other := evaluate environment destination expression\n        ⟨some value, name :: other.reads⟩",
             "evaluate environment .nonanimatable (.reference 3 (some (.reference 1 none))) = ⟨some plain, [3]⟩"),
            ("lost-attribute-payload",
             "| some value => ⟨some value, [name]⟩",
             "| some value => ⟨some { value with attributeTainted := false }, [name]⟩",
             "evaluate environment .nonanimatable (.reference 2 none) = ⟨some attr, [2]⟩"),
            ("discarded-fallback",
             "⟨result.value, name :: result.reads⟩",
             "⟨none, name :: result.reads⟩",
             "evaluate environment .nonanimatable (.reference 1 (some (.literal fallback))) = ⟨some fallback, [1]⟩"),
        ]
        for name, old, new, witness in mutations:
            mutant = base / name
            shutil.copytree(work, mutant)
            text = (ROOT / "Model.lean").read_text()
            runtime, relation = text.split("\ndef Allowed", 1)
            if runtime.count(old) != 1:
                raise ValueError("Mutation anchor changed: " + name)
            (mutant / "Model.lean").write_text(runtime.replace(old, new) + "\ndef Allowed" + relation)
            run(name + "-typecheck", [lean, "-o", "Model.olean", "Model.lean"], mutant)
            run(name + "-laws", [lean, "Laws.lean"], mutant, reject=True)
            run(name + "-cases", [lean, "-o", "Cases.olean", "Cases.lean"], mutant)
            (mutant / "Witness.lean").write_text("import Cases\nopen CssAnimationTaint CssAnimationTaint.Cases\nexample : " + witness + " := by decide\n")
            failure = run(name + "-witness", [lean, "Witness.lean"], mutant, reject=True)
            if not re.fullmatch(r"Witness\.lean:3:\d+: error: Tactic `decide` proved that the proposition\n(?:  [^\n]*\n)+is false\n", failure):
                raise ValueError("Unexpected semantic witness rejection: " + name + "\n" + failure)
            controls[name] = "type-correct runtime mutant; unchanged laws and exact false witness rejected"
        drift = base / "drift"
        drift.mkdir()
        for name in ["SOURCE.json", "variables.html", "replacement.html", "acquisition-boundary.html", "infectious.html"]:
            shutil.copyfile(ROOT / name, drift / name)
        (drift / "variables.html").write_bytes((drift / "variables.html").read_bytes() + b"changed")
        try:
            source_check(drift)
        except ValueError as error:
            if str(error) != "Specification snapshot changed":
                raise
            controls["source-drift"] = str(error)
        else:
            raise ValueError("Changed specification accepted")
    if before != {name: sha((ROOT / name).read_bytes()) for name in files}:
        raise ValueError("Inputs changed during verification")
    report = {"status": "pass", "toolchain": version, "audits": audits,
              "examples": expected, "controls": controls, "commands": commands,
              "sources": before, "temporary_builds_removed": True,
              "acquisition_policy_proved": False, "native_refinement_proved": False,
              "selected_branch_only_infection_proved": False}
    (out / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(f"PASS: {len(audits)} theorem audits, {len(expected)} observations, {len(controls)} controls")


if __name__ == "__main__":
    main()
