import argparse
import hashlib
import importlib.util
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
    parser.add_argument("--lean", required=True)
    args = parser.parse_args()
    lean = str(Path(args.lean).resolve())
    build = HERE / "build"
    logs = HERE / "logs"
    build.mkdir(exist_ok=True)
    logs.mkdir(exist_ok=True)
    (build / "CssSemantics").mkdir(exist_ok=True)
    env = dict(os.environ, LEAN_PATH=str(build), PYTHONDONTWRITEBYTECODE="1")
    results = []

    def run(name, command, expected=0, environment=env):
        result = subprocess.run(command, cwd=HERE, env=environment, capture_output=True, text=True, timeout=90, check=False)
        (logs / (name + ".log")).write_text(result.stdout + result.stderr)
        results.append({"name": name, "command": command, "returncode": result.returncode, "log_sha256": sha(logs / (name + ".log"))})
        if result.returncode != expected:
            raise RuntimeError(name + " returned " + str(result.returncode))
        return result.stdout + result.stderr

    (HERE / "RESULT.json").unlink(missing_ok=True)
    run("extraction", [sys.executable, "-I", "-B", str(HERE / "extract.py")])
    library = json.loads((HERE / "LIBRARY.json").read_text())
    for name, expected in library["files"].items():
        if sha(HERE / name) != expected:
            raise ValueError("Changed library snapshot: " + name)
    version = run("lean-version", [lean, "--version"])
    if "4.35.0-rc4" not in version:
        raise ValueError("Use the existing library's Lean 4.35.0-rc4 toolchain")
    for module in ["CssInput", "CssEscape"]:
        run(module, [lean, "-R", str(HERE / "library"), "-o", str(build / "CssSemantics" / (module + ".olean")), str(HERE / "library/CssSemantics" / (module + ".lean"))])
    run("generated", [lean, "-R", str(HERE), "-o", str(build / "Generated.olean"), str(HERE / "Generated.lean")])
    proof_log = run("bridge", [lean, "-R", str(HERE), str(HERE / "Bridge.lean")])
    expected_audits = [
        "'CssDerivation.afterBackslash' depends on axioms: [propext, Quot.sound]",
        "'CssDerivation.afterBackslash_spec' depends on axioms: [propext, Quot.sound]",
    ]
    if proof_log.strip().splitlines() != expected_audits:
        raise ValueError("Unexpected bridge audit output")

    spec = importlib.util.spec_from_file_location("derivation_extract", HERE / "extract.py")
    extractor = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(extractor)
    source = (HERE / "inputs/css-syntax-3.bs").read_text()
    controls = []
    for name, replacement in [
        ("unsupported-operator", "Only if the first <a>code point</a> is not"),
        ("additional-paragraph", "If the first <a>code point</a> is not"),
    ]:
        mutated = source.replace("If the first <a>code point</a> is not", replacement, 1)
        if name == "additional-paragraph":
            mutated = mutated.replace("Otherwise, return true.\n", "Otherwise, return true.\n\n\tPerform an additional operation.\n", 1)
        try:
            extractor.extract(mutated)
        except ValueError as error:
            controls.append({"name": name, "result": "rejected", "reason": str(error)})
        else:
            raise ValueError("Unrecognized prose was silently accepted: " + name)

    ir = json.loads((HERE / "algorithm.json").read_text())
    ir["branches"][1]["return"] = True
    mutant = build / "mutant"
    mutant.mkdir(exist_ok=True)
    (mutant / "Generated.lean").write_text(extractor.generate(ir))
    mutation_env = dict(env, LEAN_PATH=str(mutant) + os.pathsep + str(build))
    run("mutant-generated", [lean, "-R", str(mutant), "-o", str(mutant / "Generated.olean"), str(mutant / "Generated.lean")], environment=mutation_env)
    failure = run("mutant-bridge", [lean, "-R", str(HERE), str(HERE / "Bridge.lean")], expected=1, environment=mutation_env)
    if "Tactic `rfl` failed" not in failure or "Tactic `decide` proved that the proposition" not in failure:
        raise ValueError("Mutant failed for an unexpected reason")
    controls.append({"name": "accept-newline", "result": "well-typed generated algorithm; correspondence proof and newline example rejected"})

    manifest = json.loads((HERE / "SOURCE.json").read_text())
    changed = build / "source-drift"
    (changed / "inputs").mkdir(parents=True, exist_ok=True)
    shutil.copyfile(HERE / "extract.py", changed / "extract.py")
    shutil.copyfile(HERE / "SOURCE.json", changed / "SOURCE.json")
    (changed / manifest["file"]).write_bytes((HERE / manifest["file"]).read_bytes() + b"\n")
    drift_log = run("source-drift", [sys.executable, "-I", "-B", str(changed / "extract.py")], expected=1)
    if "Pinned source changed" not in drift_log:
        raise ValueError("Source drift failed for an unexpected reason")
    controls.append({"name": "source-drift", "result": "actual extractor rejects altered source before generation"})
    result = {
        "passed": True,
        "claim": "Generated predicate equals the pinned library's after-backslash predicate for every List Char; prose correspondence remains manually interpreted.",
        "source_sha256": manifest["sha256"],
        "library_revision": library["revision"],
        "lean_version": version.strip(),
        "controls": controls,
        "commands": results,
        "files": {name: sha(HERE / name) for name in ["extract.py", "check.py", "Bridge.lean", "Generated.lean", "algorithm.json", "LIBRARY.json", "SOURCE.json"]},
        "native_browser_run": False,
        "prose_refinement_proved": False,
    }
    (HERE / "RESULT.json").write_text(json.dumps(result, indent=2) + "\n")
    shutil.rmtree(build)
    print(json.dumps({"passed": True, "controls": controls, "temporary_build_removed": True}, indent=2))


if __name__ == "__main__":
    main()
