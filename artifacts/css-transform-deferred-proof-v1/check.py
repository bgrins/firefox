import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from controls import MUTATIONS
from expectations import EXPECTED_AXIOMS, EXPECTED_ERRORS
import source_check

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[1]
LEAN = ROOT / "artifacts/stylo-bloom-tools/lean-4.35.0-rc4-darwin_aarch64/bin/lean"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def errors(source, path, output):
    lines = source.splitlines()
    declarations = [(i, line) for i, line in enumerate(lines, 1)
                    if re.match(r"^(theorem|def|structure|inductive|end|#print) ", line)]
    found = []
    headers = re.findall(r"^(.+):(\d+):\d+: error(?:\([^\n)]*\))?: (.*)$", output, re.M)
    if len(re.findall(r"\berror(?:\([^\n)]*\))?:", output)) != len(headers):
        raise ValueError("Unlocated compiler diagnostic")
    for filename, line, message in headers:
        if filename != str(path):
            raise ValueError("Foreign diagnostic")
        owner = max(i for i, (start, _) in enumerate(declarations) if start <= int(line))
        start, text = declarations[owner]
        if not text.startswith("theorem "):
            raise ValueError("Diagnostic outside theorem")
        end = declarations[owner + 1][0]
        body = [i for i in range(start, end) if ":= by" in lines[i - 1]]
        if not body or int(line) < body[0]:
            raise ValueError("Diagnostic outside proof body")
        found.append([text.split()[1], message])
    return found


def main():
    if sys.flags.optimize:
        raise ValueError("Normal Python required")
    if len(sys.argv) not in (2, 3) or (len(sys.argv) == 3 and sys.argv[2] != "--snapshots-only"):
        raise ValueError("Usage: check.py NEW_OUTPUT_DIRECTORY [--snapshots-only]")
    out = Path(sys.argv[1]).resolve()
    out.mkdir()
    live = len(sys.argv) == 2
    binding, pins = source_check.run(live)
    model = (BASE / "Deferred.lean").read_text()
    if re.search(r"\b(sorry|admit|axiom|unsafe|native_decide)\b", model.replace("#print axioms", "")):
        raise ValueError("Unchecked model construct")
    companions = [line.strip() for line in (BASE / "tooling-paths.txt").read_text().splitlines() if line.strip()]
    pins += [ROOT / name for name in companions] + [BASE / "tooling-paths.txt", LEAN]
    pins = list(dict.fromkeys(pins))
    before = {str(path): sha(path) for path in pins}
    (out / "source-binding.json").write_text(json.dumps(binding, indent=2) + "\n")
    calls = []
    for name, change in {"positive": None, **MUTATIONS}.items():
        source = model
        if change:
            old, new = change
            expected_count = 2 if name == "DropPercentageDependency" else 1
            if source.count(old) != expected_count:
                raise ValueError("Mutation target count: " + name)
            source = source.replace(old, new, 1)
        folder = out / name
        folder.mkdir()
        path = folder / "Deferred.lean"
        path.write_text(source)
        env = os.environ.copy()
        env["LEAN_PATH"] = str(folder)
        env.pop("LEAN_SRC_PATH", None)
        command = [str(LEAN), "-DwarningAsError=true", "-Dlinter.unusedVariables=false",
                   "-Dlinter.unusedSimpArgs=false", str(path)]
        result = subprocess.run(command, capture_output=True, text=True, env=env)
        (folder / "stdout.log").write_text(result.stdout)
        (folder / "stderr.log").write_text(result.stderr)
        if result.stderr:
            raise ValueError("Compiler stderr: " + name)
        inventory = errors(source, path, result.stdout)
        if name == "positive":
            if result.returncode != 0 or result.stdout != EXPECTED_AXIOMS or inventory:
                raise ValueError("Positive proof/axiom audit mismatch")
        elif result.returncode != 1 or inventory != EXPECTED_ERRORS[name]:
            raise ValueError("Mutation proof inventory mismatch: " + name + repr(inventory))
        calls.append({"name": name, "command": command, "exit_code": result.returncode,
                      "errors": inventory, "stdout_sha256": sha(folder / "stdout.log"),
                      "stderr_sha256": sha(folder / "stderr.log"), "source_sha256": sha(path)})
    after = {str(path): sha(path) for path in pins}
    if before != after:
        raise ValueError("Inputs changed during proof run")
    report = {"status": "pass", "live_native_verified": live, "inputs": before,
              "inputs_after": after, "calls": calls,
              "axiom_audits": len(EXPECTED_AXIOMS.splitlines()), "compiled_mutations": len(MUTATIONS),
              "source_controls": len(binding["source_controls"]),
              "limits": "Conditional manually bridged model; no Rust extraction, floating point, singular fallback, or compositor proof"}
    (out / "report.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: v for k, v in report.items() if k not in {"inputs", "inputs_after", "calls"}}, sort_keys=True))


if __name__ == "__main__":
    main()
