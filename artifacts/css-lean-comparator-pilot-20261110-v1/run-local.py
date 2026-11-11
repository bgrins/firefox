import argparse
import gzip
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import time


ROOT = Path(__file__).resolve().parent
AXIOMS = ["propext", "Quot.sound", "Classical.choice"]
PRIMITIVES = [
    "Nat.add", "Nat.sub", "Nat.mul", "Nat.pow", "Nat.gcd", "Nat.div", "Nat.mod",
    "Nat.beq", "Nat.ble", "Nat.land", "Nat.lor", "Nat.xor", "Nat.shiftLeft",
    "Nat.shiftRight", "String.ofList", "Char.ofNat", "List", "eagerReduce",
    "Nat", "String", "String.mk", "Char", "optParam", "autoParam",
    "semiOutParam", "outParam",
]
TARGET = "NumericDigits.scan_reference"
TARGETS = ["Quot", "Quot.mk", "Quot.lift", "Quot.ind", TARGET, *AXIOMS, *PRIMITIVES]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--toolchain", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    tool = args.toolchain.resolve()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    pins = json.loads((ROOT / "PINS.json").read_text())
    assert sha(ROOT / "preserved/NumericDigits.lean") == pins["canonical_input"]["sha256"]
    for name, expected in pins["libraries"].items():
        assert sha(tool / name) == expected, name
    for name, expected in pins["tools"].items():
        assert sha(tool / "bin" / name) == expected, name
    for row in pins["tool_sources"]:
        assert sha(ROOT / row["copy"]) == row["sha256"]
    source = (ROOT / "preserved/NumericDigits.lean").read_text()
    challenge = source.split("\ntheorem cover ")[0] + "\nend NumericDigits\n"
    assert (ROOT / "project/Challenge.lean").read_text() == challenge
    assert (ROOT / "variants/good.lean").read_text() == challenge
    official = (ROOT / "tool-source/lake/Lake/CLI/Check.lean").read_text()
    primitive_body = official.split("def primitiveTargets")[1].split("def builtinTargets")[0]
    primitive_body = "\n".join(s.split("--")[0] for s in primitive_body.splitlines())
    assert re.findall(r"``([A-Za-z0-9_.]+)", primitive_body) == PRIMITIVES
    adapter = (ROOT / "Diagnostic.lean").read_text().split("def primitiveNames")[1].split("def main")[0]
    assert re.findall(r"``([A-Za-z0-9_.]+)", adapter) == PRIMITIVES
    if (ROOT / "SOURCE-ONLY.json").exists():
        for name, expected in json.loads((ROOT / "SOURCE-ONLY.json").read_text()).items():
            assert sha(ROOT / name) == expected, name
    env = dict(os.environ, PATH=str(tool / "bin") + os.pathsep + os.environ["PATH"])
    records = []

    def run(label, command, cwd, expected=0):
        begin = time.monotonic()
        result = subprocess.run(command, cwd=cwd, env=env, capture_output=True, timeout=120)
        stdout = out / (label + ".stdout")
        stderr = out / (label + ".stderr")
        stdout.write_bytes(result.stdout)
        stderr.write_bytes(result.stderr)
        records.append({"label": label, "command": command, "cwd": str(cwd),
                        "exit": result.returncode, "seconds": time.monotonic() - begin,
                        "stdout_sha256": sha(stdout), "stderr_sha256": sha(stderr)})
        (out / "COMMANDS.json").write_text(json.dumps(records, indent=2) + "\n")
        assert result.returncode == expected, (label, result.returncode, result.stderr[-2000:])
        return result.stdout.decode(), result.stderr.decode()

    exports = {}
    observations = {}
    with tempfile.TemporaryDirectory(prefix="css-comparator-pilot-") as temporary:
        scratch = Path(temporary)
        env["LEAN_PATH"] = str(scratch)
        for name in ["check", "comparator"]:
            run("help-" + name, [str(tool / "bin/lake"), "help", name], scratch)
        run("lean-version", [str(tool / "bin/lean"), "--version"], scratch)
        shutil.copy(ROOT / "project/Challenge.lean", scratch / "Challenge.lean")
        run("compile-challenge", [str(tool / "bin/lean"), "-o", "Challenge.olean", "Challenge.lean"], scratch)
        audit, _ = run("canonical-proof-audit", [str(tool / "bin/lean"), str(ROOT / "Audit.lean")], scratch)
        assert "depends on axioms" in audit
        used = audit.split("depends on axioms:", 1)[1].strip().strip("[]")
        assert all(a.strip() in AXIOMS for a in used.split(",") if a.strip())
        dependencies, _ = run("direct-module-dependencies", [str(tool / "bin/lean"), "--deps", "Challenge.lean"], scratch)
        module_pins = {p: sha(Path(p)) for p in dependencies.splitlines()}
        (out / "DIRECT-MODULES.json").write_text(json.dumps(module_pins, indent=2) + "\n")

        def export(label, module):
            text, _ = run("export-" + label, [str(tool / "bin/leanexport"), module, "--", *TARGETS], scratch)
            path = scratch / (label + ".ndjson")
            path.write_text(text)
            exports[label] = {"sha256": sha(path), "bytes": path.stat().st_size,
                              "records": len(text.splitlines()), "roots": TARGETS}
            if label == "challenge":
                with gzip.GzipFile(filename="", mode="wb", fileobj=(out / "challenge.ndjson.gz").open("wb"), mtime=0) as zipped:
                    zipped.write(path.read_bytes())
            (out / "EXPORTS.json").write_text(json.dumps(exports, indent=2) + "\n")
            (out / ("export-" + label + ".stdout")).unlink()
            records[-1]["stdout_retention"] = "export hash/size/roots; challenge additionally retained compressed"
            (out / "COMMANDS.json").write_text(json.dumps(records, indent=2) + "\n")
            return path

        challenge_export = export("challenge", "Challenge")
        if os.uname().sysname == "Darwin":
            for name, options in [
                ("check", ["--from-export", str(challenge_export)]),
                ("comparator", ["--config", str(ROOT / "project/comparator.json"),
                                "--challenge-from-export", str(challenge_export),
                                "--solution-from-export", str(challenge_export)]),
            ]:
                _, error = run("official-" + name, [str(tool / "bin/lake"), name, *options], scratch, 2)
                assert "needs Linux namespaces" in error
        for label in ["good", "changed-predicate", "extra-premise", "forbidden-axiom"]:
            shutil.copy(ROOT / "variants" / (label + ".lean"), scratch / "Solution.lean")
            run("compile-" + label, [str(tool / "bin/lean"), "-o", "Solution.olean", "Solution.lean"], scratch)
            solution_export = export(label, "Solution")
            text, _ = run("diagnostic-" + label, [str(tool / "bin/lean"), "--run", str(ROOT / "Diagnostic.lean"),
                                                  str(challenge_export), str(solution_export)], scratch)
            lines = text.splitlines()
            if label == "good":
                assert lines[:2] == ["comparison: match", "axioms: permitted"]
            elif label == "changed-predicate":
                assert "Const does not match between challenge and target" in lines[0]
                assert lines[1] == "axioms: permitted"
            elif label == "extra-premise":
                assert "theorem statement do not match" in lines[0]
                assert lines[1] == "axioms: permitted"
            else:
                assert lines[:2] == ["comparison: match", "axioms: Illegal axiom detected: 'NumericDigits.forbidden'"]
            observations[label] = lines
            checkers = [("leanchecker", ["--from-export"])]
            if label == "good":
                checkers += [("leanchecker-paranoid", ["--from-export"]),
                             ("lean4lean", ["--import"]), ("con-leche", ["--jobs=2"]),
                             ("con-ron", ["--jobs=2"])]
            for checker, options in checkers:
                run(label + "-" + checker, [str(tool / "bin" / checker), *options, str(solution_export)], scratch)
            configuration = {"use_stdin": False, "export_file_path": str(solution_export),
                             "permitted_axioms": AXIOMS, "unpermitted_axiom_hard_error": False,
                             "num_threads": 2, "nat_extension": True, "string_extension": True}
            nanoda_config = scratch / "nanoda.json"
            nanoda_config.write_text(json.dumps(configuration))
            (out / (label + "-nanoda-config.json")).write_text(json.dumps(configuration, indent=2) + "\n")
            _, nanoda_error = run(label + "-nanoda", [str(tool / "bin/nanoda_bin"), str(nanoda_config)], scratch,
                                  expected=101 if label == "forbidden-axiom" else 0)
            if label == "forbidden-axiom":
                assert "declaration not found in infer_const, NumericDigits.forbidden" in nanoda_error
        project = scratch / "project"
        shutil.copytree(ROOT / "project", project)
        env.pop("LEAN_PATH")
        run("manifest-materialization", [str(tool / "bin/lake"), "build"], project)
        shutil.copy(project / "lake-manifest.json", out / "lake-manifest.json")
    report = {"status": "DIAGNOSTIC PASS; isolated comparator acceptance pending Linux",
              "protected_acceptance": False, "observations": observations,
              "good_external_checkers": 6, "variants": 4, "commands": len(records),
              "temporary_compiled_output_removed": not scratch.exists()}
    (out / "REPORT.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
