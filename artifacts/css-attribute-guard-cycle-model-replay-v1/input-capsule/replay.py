import sys

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
sys.dont_write_bytecode = True

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()


def decisive(code, log):
    return code == 1 and re.fullmatch(
        r"False\.lean:\d+:\d+: error: Tactic `decide` proved that the proposition\n[\s\S]+\nis false\n?", log
    ) is not None and log.count("error:") == 1 and not any(
        word in log for word in ("warning:", "failed to reduce", "Reduction got stuck", "sorry", "failed to synthesize"))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest-sha256", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    assert sha(HERE / "FILES.json") == args.manifest_sha256
    for name, digest in json.loads((HERE / "FILES.json").read_text()).items():
        relative = Path(name)
        assert not relative.is_absolute() and ".." not in relative.parts
        assert not (HERE / name).is_symlink() and sha(HERE / name) == digest
    output = args.output
    assert output.is_absolute() and not output.exists() and not output.is_symlink()
    assert HERE not in output.parents and output not in HERE.parents
    inputs = json.loads((HERE / "INPUTS.json").read_text())
    compiler = ROOT / inputs["compiler"]
    assert sha(compiler) == inputs["compiler_sha256"]
    for name, digest in inputs["sources"].items():
        assert sha(HERE / name) == digest
        assert not re.search(r"\b(sorry|axiom|native_decide)\b", (HERE / name).read_text())
    for name, digest in inputs["imports"].items():
        assert sha(ROOT / name) == digest
    references = json.loads((HERE / "REFERENCES.json").read_text())
    for name, digest in references.items():
        assert sha(ROOT / name) == digest
    output.mkdir()
    records = []
    with tempfile.TemporaryDirectory(prefix="css-attribute-guard-", dir="/private/tmp") as temporary:
        scratch = Path(temporary)
        for name in inputs["sources"]:
            shutil.copyfile(HERE / name, scratch / name)
        env = dict(os.environ, LEAN_PATH=temporary, LEAN_NUM_THREADS="1")

        def run(name, command, negative=False):
            result = subprocess.run([str(compiler), "-j1", *command], cwd=scratch, env=env,
                                    capture_output=True, text=True, timeout=45)
            log = result.stdout + result.stderr
            (output / (name + ".log")).write_text(log)
            records.append({"name": name, "command": [str(compiler), "-j1", *command],
                            "exit": result.returncode, "log_sha256": sha(output / (name + ".log"))})
            assert decisive(result.returncode, log) if negative else (
                result.returncode == 0 and "warning:" not in log and "sorryAx" not in log), log
            return log

        version = run("version", ["--version"]).strip()
        for name in ("GuardCycle", "Examples"):
            run(name, ["-o", name + ".olean", name + ".lean"])
        audit = run("audit", ["Audit.lean"])
        axioms = {}
        for line in audit.splitlines():
            match = re.fullmatch(r"'([^']+)' (?:depends on axioms: \[([^]]*)\]|does not depend on any axioms)", line)
            assert match and match[1] not in axioms, line
            axioms[match[1]] = match[2].split(", ") if match[2] else []
            assert set(axioms[match[1]]) <= {"propext", "Quot.sound", "Classical.choice"}
        assert set(axioms) == set(inputs["audited_names"])
        claims = json.loads((HERE / "NEGATIVE-CONTROLS.json").read_text())
        for name, claim in claims.items():
            source = "import Examples\nopen AttributeGuard AttributeGuard.Examples\nexample : " + claim + " := by\n  decide +kernel\n"
            (scratch / "False.lean").write_text(source)
            (output / (name + ".lean")).write_text(source)
            run(name, ["False.lean"], True)
        good = (output / "missing-self-rescue.log").read_text()
        assert not decisive(0, good)
        assert not decisive(1, good + "False.lean:1:1: error: unrelated\n")
        assert not decisive(1, "False.lean:1:1: error: Tactic `decide` failed to reduce\n")
        assert not decisive(1, "False.lean:1:1: error: Unknown identifier `false`\n")
        assert not decisive(1, good.replace("is false", "failed to synthesize"))
    assert not scratch.exists()
    for name, digest in references.items():
        assert sha(ROOT / name) == digest
    assert sha(HERE / "FILES.json") == args.manifest_sha256
    check = {
        "status": "ATTRIBUTE_GUARD_CYCLE_MODEL_PASS", "compiler": version, "threads": 1,
        "model_manifest_sha256": args.manifest_sha256,
        "audited_declarations": len(axioms), "generic_laws": inputs["generic_laws"],
        "closed_kernel_examples": inputs["closed_examples"], "decisive_false_controls": len(claims),
        "diagnostic_gate_negatives": 5, "axioms": axioms, "records": records,
        "owned_scratch_removed": True, "native_refinement": False,
        "canonical_integration": False, "normative_coverage_credit": 0, "accepted_bug_credit": 0,
        "fuel_note": "Fuel exhaustion is distinct from invalid; closed examples use explicit fuel 64, not an unbounded termination proof",
    }
    (output / "CHECK.json").write_text(json.dumps(check, indent=2) + "\n")
    print(json.dumps(check))


if __name__ == "__main__":
    main()
