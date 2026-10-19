import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from controls import MUTATIONS
from diagnostics import errors
from expectations import EXPECTED_AXIOMS, EXPECTED_ERRORS

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[1]
LEAN = ROOT / "artifacts/stylo-bloom-tools/lean-4.35.0-rc4-darwin_aarch64/bin/lean"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate(name, source, path, code, stdout, stderr):
    if stderr:
        raise ValueError("Compiler stderr")
    inventory = errors(source, path, stdout)
    if name == "positive":
        if code != 0 or stdout != EXPECTED_AXIOMS or inventory:
            raise ValueError("Positive proof/axiom audit mismatch")
    elif code != 1 or inventory != EXPECTED_ERRORS[name]:
        raise ValueError("Mutation proof inventory mismatch: " + name)
    return inventory


def guards(positive, negative):
    name, source, path, code, stdout, stderr = positive
    n, s, p, c, out, err = negative
    tests = {
        "positive-nonzero": (name, source, path, 1, stdout, stderr),
        "positive-stderr": (name, source, path, code, stdout, "unexpected"),
        "missing-audit": (name, source, path, code, "\n".join(stdout.splitlines()[1:]) + "\n", stderr),
        "extra-audit": (name, source, path, code, stdout + "unreviewed\n", stderr),
        "unchecked-axiom": (name, source, path, code, stdout.replace("Quot.sound", "sorryAx", 1), stderr),
        "mutation-success": (n, s, p, 0, out, err),
        "mutation-no-error": (n, s, p, c, "", err),
        "mutation-stderr": (n, s, p, c, out, "unexpected"),
        "foreign-path": (n, s, p, c, out.replace(str(p), "/foreign/Clamp.lean"), err),
        "unlocated-error": (n, s, p, c, out + "error: unlocated\n", err),
        "outside-proof-error": (n, s, p, c, out + f"{p}:1:1: error: injected\n", err),
        "unexpected-error-text": (n, s, p, c, out.replace("Tactic `rfl` failed", "unrecognized diagnostic"), err),
    }
    accepted = []
    for label, args in tests.items():
        try:
            validate(*args)
        except (ValueError, KeyError):
            accepted.append(label)
        else:
            raise ValueError("Record guard accepted poison: " + label)
    return accepted


def main():
    if sys.flags.optimize or len(sys.argv) != 2:
        raise ValueError("Usage: python3 check.py NEW_OUTPUT_DIRECTORY; normal Python required")
    out = Path(sys.argv[1]).resolve()
    out.mkdir()
    model = (BASE / "Clamp.lean").read_text()
    if re.search(r"\b(sorry|admit|axiom|unsafe|native_decide)\b", model.replace("#print axioms", "")):
        raise ValueError("Unchecked model construct")
    manifest = json.loads((BASE / "SOURCE-v1.json").read_text())
    for name, expected in manifest["companion_hashes"].items():
        if sha(BASE / name) != expected:
            raise ValueError("Frozen companion mismatch: " + name)
    pins = [BASE / name for name in manifest["companion_hashes"]] + [BASE / "SOURCE-v1.json", LEAN]
    before = {str(path): sha(path) for path in pins}
    calls = []
    inputs = {}
    for name, change in {"positive": None, **MUTATIONS}.items():
        source = model
        if change:
            old, new = change
            if source.count(old) != 1:
                raise ValueError("Mutation target count: " + name)
            source = source.replace(old, new)
        folder = out / name
        folder.mkdir()
        path = folder / "Clamp.lean"
        path.write_text(source)
        env = os.environ.copy()
        env["LEAN_PATH"] = str(folder)
        env.pop("LEAN_SRC_PATH", None)
        command = [str(LEAN), "-DwarningAsError=true", "-Dlinter.unusedVariables=false",
                   "-Dlinter.unusedSimpArgs=false", str(path)]
        result = subprocess.run(command, capture_output=True, text=True, env=env)
        (folder / "stdout.log").write_text(result.stdout)
        (folder / "stderr.log").write_text(result.stderr)
        args = (name, source, path, result.returncode, result.stdout, result.stderr)
        inventory = validate(*args)
        inputs[name] = args
        calls.append({"name": name, "command": command, "exit_code": result.returncode,
                      "errors": inventory, "stdout_sha256": sha(folder / "stdout.log"),
                      "stderr_sha256": sha(folder / "stderr.log"), "source_sha256": sha(path)})
    rejected = guards(inputs["positive"], inputs["DropUnknownUpper"])
    after = {str(path): sha(path) for path in pins}
    if before != after:
        raise ValueError("Inputs changed during proof run")
    report = {"status": "pass", "live_native_verified": False, "inputs": before,
              "inputs_after": after, "calls": calls,
              "axiom_audits": len(EXPECTED_AXIOMS.splitlines()), "compiled_mutations": len(MUTATIONS),
              "record_guards": rejected, "native_bridge": "deferred; no native conformance claim",
              "limits": manifest["limits"]}
    (out / "report.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: v for k, v in report.items() if k not in {"inputs", "inputs_after", "calls"}}, sort_keys=True))


if __name__ == "__main__":
    main()
