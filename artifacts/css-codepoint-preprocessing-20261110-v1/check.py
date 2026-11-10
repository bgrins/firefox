import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys


HERE = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--lean", type=Path, required=True)
    args = parser.parse_args()
    lean = str(args.lean.resolve())
    (HERE / "RESULT.json").unlink(missing_ok=True)
    sources = json.loads((HERE / "SOURCES.json").read_text())["sources"]
    library = json.loads((HERE / "LIBRARY.json").read_text())
    for name, expected in library["files"].items():
        if sha(HERE / name) != expected:
            raise ValueError("Reference source changed: " + name)
    build = HERE / "build"
    if build.exists():
        shutil.rmtree(build)
    (build / "CssSemantics").mkdir(parents=True)
    (HERE / "logs").mkdir(exist_ok=True)
    env = dict(os.environ, LEAN_PATH=str(build))
    commands, controls = [], []

    def run(name, argv, expected=0, environment=None):
        process = subprocess.run(argv, env=environment or env, capture_output=True, text=True)
        output = process.stdout + process.stderr
        log = HERE / "logs" / (name + ".log")
        log.write_text(output)
        commands.append({"name": name, "argv": argv, "returncode": process.returncode, "log_sha256": sha(log)})
        if process.returncode != expected:
            raise ValueError(f"Unexpected exit for {name}: {process.returncode}; see {log}")
        return output

    def compile(name, module, root, output_root, environment=None):
        return run(name, [lean, "-R", str(root), "-o", str(output_root / (module + ".olean")), str(root / (module + ".lean"))], environment=environment)

    version = run("lean-version", [lean, "--version"]).strip()
    if "version 4.35.0-rc4," not in version:
        raise ValueError("Review toolchain change explicitly")
    run("source-links", [sys.executable, "-I", "-B", str(HERE / "source_links.py")])
    compile("model", "CodePointInput", HERE, build)
    expected_correctness = [f"'CssSemantics.CodePointInput.{name}' depends on axioms: [propext, Classical.choice, Quot.sound]" for name in
        ["preprocess_iff", "preprocess_normalized", "preprocess_length_le"]]
    expected_correctness.extend([
        "'CssSemantics.CodePointInput.surrogate_cons' depends on axioms: [propext, Quot.sound]",
        "'CssSemantics.CodePointInput.ofNat?_none_iff' depends on axioms: [propext]",
    ])
    if compile("correctness", "Correctness", HERE, build).strip().splitlines() != expected_correctness:
        raise ValueError("Unexpected correctness audit; no sorry/custom axioms or warnings admitted")
    compile("reference", "CssSemantics/CssInput", HERE / "library", build)
    expected_refinement = [f"'CssSemantics.CodePointInput.{name}' depends on axioms: [propext, Classical.choice, Quot.sound]" for name in
        ["scalar_refinement", "normalized_iff_fixed", "preprocess_idempotent", "preserve_ordinary"]]
    if compile("refinement", "Refinement", HERE, build).strip().splitlines() != expected_refinement:
        raise ValueError("Unexpected refinement audit")
    if compile("examples", "Examples", HERE, build).strip():
        raise ValueError("Unexpected example diagnostics")

    original = (HERE / "CodePointInput.lean").read_text()
    point_start, point_end = original.index("def point "), original.index("inductive Point ")
    preprocess_start, preprocess_end = original.index("def preprocess "), original.index("def filterValues ")
    point = original[point_start:point_end]
    preprocess = original[preprocess_start:preprocess_end]
    mutations = [
        ("crlf-not-collapsed", "preprocess", "p.val = 0x0d ∧ q.val = 0x0a", "False", "[0x0d, 0x0a]", "some ['\\n']"),
        ("spurious-pair", "preprocess", "p.val = 0x0d ∧ q.val = 0x0a", "p.val = 0x0d ∨ q.val = 0x0a", "[0x41, 0x0a]", "some ['A', '\\n']"),
        ("cr-not-converted", "point", "p.val = 0x0d ∨ p.val = 0x0c", "p.val = 0x0c", "[0x0d]", "some ['\\n']"),
        ("ff-not-converted", "point", "p.val = 0x0d ∨ p.val = 0x0c", "p.val = 0x0d", "[0x0c]", "some ['\\n']"),
        ("nul-not-replaced", "point", "p.val = 0 ∨ Surrogate p", "Surrogate p", "[0]", "some ['�']"),
        ("surrogate-endpoints-excluded", "point", "Surrogate p", "(0xd800 < p.val ∧ p.val < 0xdfff)", "[0xd800, 0xdfff]", "some ['�', '�']"),
        ("noncharacter-replaced", "point", "p.val = 0 ∨ Surrogate p", "p.val = 0 ∨ Surrogate p ∨ p.val = 0x10ffff", "[0x10ffff]", "some [Char.ofNat 0x10ffff]"),
        ("codepoints-treated-as-utf16", "preprocess", "if p.val = 0x0d ∧ q.val = 0x0a then", "if p.val = 0xd83d ∧ q.val = 0xde00 then Char.ofNat 0x1f600 :: preprocess rest\n      else if p.val = 0x0d ∧ q.val = 0x0a then", "[0xd83d, 0xde00]", "some ['�', '�']"),
    ]
    for name, region, old, new, input_term, output_term in mutations:
        text, begin, end = (point, point_start, point_end) if region == "point" else (preprocess, preprocess_start, preprocess_end)
        if text.count(old) != 1:
            raise ValueError("Ambiguous executable-only mutation " + name)
        folder = build / name
        folder.mkdir()
        mutant_env = dict(env, LEAN_PATH=str(folder) + os.pathsep + str(build))
        (folder / "CodePointInput.lean").write_text(original[:begin] + text.replace(old, new) + original[end:])
        compile(name + "-model", "CodePointInput", folder, folder, mutant_env)
        failure = run(name + "-proof", [lean, str(HERE / "Correctness.lean")], expected=1, environment=mutant_env)
        if "error:" not in failure:
            raise ValueError("No relational correctness failure for " + name)
        witness = "import CodePointInput\nopen CssSemantics.CodePointInput\nexample : filterValues " + input_term + " = " + output_term + " := by decide\n"
        (folder / "Witness.lean").write_text(witness)
        failure = run(name + "-witness", [lean, str(folder / "Witness.lean")], expected=1, environment=mutant_env)
        if "Tactic `decide` proved that the proposition" not in failure or "is false" not in failure:
            raise ValueError("No concrete counterexample for " + name)
        controls.append({"name": name, "result": "executable mutant typechecks; unchanged relational proof and concrete witness fail"})

    impossible = build / "OutsideDomain.lean"
    impossible.write_text("import CodePointInput\nopen CssSemantics.CodePointInput\ndef outside : CodePoint := ⟨0x110000, by decide⟩\n")
    failure = run("outside-domain", [lean, str(impossible)], expected=1)
    if "Tactic `decide` proved that the proposition" not in failure:
        raise ValueError("Unexpected out-of-domain result")
    controls.append({"name": "outside-domain", "result": "code point above U+10FFFF cannot satisfy the domain bound"})
    for changed, record in sources.items():
        folder = build / (changed + "-drift")
        (folder / "inputs").mkdir(parents=True)
        for name in ["source_links.py", "SOURCES.json", *(r["file"] for r in sources.values())]:
            shutil.copyfile(HERE / name, folder / name)
        target = folder / record["file"]
        target.write_bytes(target.read_bytes() + b"\n")
        failure = run(changed + "-drift", [sys.executable, "-I", "-B", str(folder / "source_links.py")], expected=1)
        if "Pinned source changed" not in failure:
            raise ValueError("Unexpected source-drift failure")
        controls.append({"name": changed + "-drift", "result": "changed specification bytes rejected"})
    names = ["CodePointInput.lean", "Correctness.lean", "Refinement.lean", "Examples.lean", "check.py", "source_links.py", "SOURCES.json", "LIBRARY.json", "CLAUSES.json"]
    result = {"passed": True, "lean_version": version, "examples": 21,
        "domain": "All Unicode code points U+0000 through U+10FFFF, including surrogate code points; output is Unicode scalars",
        "relation_correspondence": True, "scalar_refinement": True, "idempotence_after_embedding": True,
        "prose_refinement_proved": False, "byte_or_utf16_decoding_modeled": False, "native_browser_run": False,
        "controls": controls, "commands": commands, "files": {name: sha(HERE / name) for name in names}}
    (HERE / "RESULT.json").write_text(json.dumps(result, indent=2) + "\n")
    shutil.rmtree(build)
    print(json.dumps({"passed": True, "examples": 21, "controls": controls, "temporary_build_removed": True}, indent=2))


if __name__ == "__main__":
    main()
