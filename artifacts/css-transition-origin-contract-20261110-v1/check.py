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
MODULES = ["Model", "Laws", "Fixtures", "Cases", "Runner"]
ALLOWED = {"propext", "Quot.sound", "Classical.choice"}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def audits(text, expected):
    rows = re.findall(r"'([^']+)' (?:depends on axioms: \[([^\]]*)\]|does not depend on any axioms)", text)
    assert [name for name, _ in rows] == expected, (rows, expected)
    for name, values in rows:
        assert {v.strip() for v in values.split(",") if v.strip()} <= ALLOWED, (name, values)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--lean", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    lean = args.lean.resolve()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    provenance = json.loads((ROOT / "PROVENANCE.json").read_text())
    assert sha(lean) == provenance["lean_sha256"]
    for row in provenance["copied_evidence"]:
        assert sha(ROOT / row["copy"]) == row["sha256"]
    for name in ["native-excerpts.json", "spec-excerpts.json"]:
        for row in json.loads((ROOT / "inputs" / name).read_text()):
            assert hashlib.sha256(row["text"].encode()).hexdigest() == row["text_sha256"]
    if (ROOT / "SOURCE-ONLY.json").exists():
        for name, expected in json.loads((ROOT / "SOURCE-ONLY.json").read_text()).items():
            assert sha(ROOT / name) == expected, name
    roster = []
    for module in MODULES:
        text = (ROOT / (module + ".lean")).read_text()
        assert not re.search(r"\b(sorry|admit|axiom|unsafe|partial|native_decide)\b", text)
        prefix = "TransitionOrigin.Cases." if module == "Cases" else "TransitionOrigin."
        roster += [prefix + name for name in re.findall(r"^theorem (\w+)", text, re.M)]
    records = []

    def run(label, command, work, expected=0):
        env = dict(os.environ, LEAN_PATH=str(work))
        result = subprocess.run(command, cwd=work, env=env, capture_output=True, text=True, timeout=90)
        stdout = out / (label + ".stdout")
        stderr = out / (label + ".stderr")
        stdout.write_text(result.stdout)
        stderr.write_text(result.stderr)
        records.append({"label": label, "command": command, "cwd": str(work), "exit": result.returncode,
                        "stdout_sha256": sha(stdout), "stderr_sha256": sha(stderr)})
        (out / "COMMANDS.json").write_text(json.dumps(records, indent=2) + "\n")
        assert result.returncode == expected, (label, result.stdout, result.stderr)
        if expected == 0:
            assert "warning:" not in result.stdout and "error:" not in result.stdout
        return result.stdout

    mutants = [
        {"name": "registered-origin-mask", "old": "fun effect => effect.inEffect", "new": "fun _ => true",
         "target": "off_excluded", "witness": "style inEffectPolicy [transition, delayed] = .important"},
        {"name": "filtered-compositor-guard",
         "old": "hasClass registeredPolicy property .animation effects",
         "new": "hasClass inEffectPolicy property .animation effects", "target": "compositorGuardMask_spec",
         "witness": "compositorGuardMask .opacity [transition, delayed] = false ∧ delayed.registered = true ∧ delayed.current = true"},
        {"name": "transition-loses-priority", "old": "| some (.transition, value) => value",
         "new": "| some (.transition, value) => important.getD value", "target": "transition_over_important",
         "witness": "style registeredPolicy [transition] = .important"},
    ]
    with tempfile.TemporaryDirectory(prefix="css-transition-origin-") as temporary:
        work = Path(temporary)
        for module in MODULES:
            shutil.copyfile(ROOT / (module + ".lean"), work / (module + ".lean"))
            run("compile-" + module, [str(lean), "-o", module + ".olean", module + ".lean"], work)
        (work / "Audit.lean").write_text("import Cases\n" + "\n".join("#print axioms " + name for name in roster) + "\n")
        audit = run("audit", [str(lean), "Audit.lean"], work)
        audits(audit, roster)
        output = run("runner", [str(lean), "--run", "Runner.lean"], work)
        labels = re.findall(r'^  \("([^"]+)"', (ROOT / "Cases.lean").read_text(), re.M)
        assert output.splitlines() == [label + "\tpass" for label in labels]
        for mutant in mutants:
            directory = work / mutant["name"]
            directory.mkdir()
            original = (ROOT / "Model.lean").read_text()
            assert original.count(mutant["old"]) == 1
            altered = original.replace(mutant["old"], mutant["new"])
            (directory / "Model.lean").write_text(altered)
            for module in ["Laws", "Fixtures"]:
                shutil.copyfile(ROOT / (module + ".lean"), directory / (module + ".lean"))
            for module in ["Model", "Fixtures"]:
                run(mutant["name"] + "-compile-" + module,
                    [str(lean), "-o", module + ".olean", module + ".lean"], directory)
            failure = run(mutant["name"] + "-unchanged-laws", [str(lean), "Laws.lean"], directory, 1)
            first_error = re.search(r"Laws\.lean:(\d+):\d+: error:", failure)
            assert first_error and "unknown identifier" not in failure and "unexpected token" not in failure
            laws = (ROOT / "Laws.lean").read_text()
            a = laws.index("theorem " + mutant["target"])
            b = laws.find("\ntheorem ", a + 1)
            if b < 0:
                b = len(laws)
            assert laws[:a].count("\n") + 1 <= int(first_error.group(1)) <= laws[:b].count("\n") + 1
            witness = "import Fixtures\nopen TransitionOrigin TransitionOrigin.Cases\n" + \
                "theorem witness : " + mutant["witness"] + " := by decide\n#print axioms witness\n"
            (directory / "Witness.lean").write_text(witness)
            audits(run(mutant["name"] + "-witness", [str(lean), "Witness.lean"], directory), ["witness"])
            mutant["altered_model_sha256"] = hashlib.sha256(altered.encode()).hexdigest()
            mutant["witness_source"] = witness
    (out / "MUTANTS.json").write_text(json.dumps(mutants, indent=2) + "\n")
    (out / "AUDITS.json").write_text(json.dumps(roster, indent=2) + "\n")
    report = {"status": "PASS", "modules": len(MODULES), "theorem_audits": len(roster),
              "executable_rows": len(labels), "compiling_semantic_mutants": len(mutants),
              "mutant_witness_audits": len(mutants), "temporary_build_removed": not work.exists(),
              "native_refinement": False, "spec_membership_proved": False, "new_bug_discovery": False}
    (out / "REPORT.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
