import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parent


def digest(data):
    return hashlib.sha256(data).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--lean", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    lean, out = args.lean.resolve(), args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    sources = {name: (ROOT / name).read_bytes() for name in
               ["GroupOrderModel.lean", "GroupOrder.lean", "check.py"]}
    commands = {}

    def run(label, argv, work, succeeds=True):
        result = subprocess.run([str(x) for x in argv], cwd=work,
                                env=dict(os.environ, LEAN_PATH=str(work)),
                                capture_output=True, text=True)
        text = result.stdout + result.stderr
        (out / (label + ".log")).write_text(text)
        commands[label] = {"exit": result.returncode, "sha256": digest(text.encode())}
        if succeeds:
            if result.returncode or "warning:" in text or "error:" in text:
                raise ValueError(label + "\n" + text)
        elif result.returncode == 0:
            raise ValueError("Invalid claim was accepted: " + label)
        return text

    with tempfile.TemporaryDirectory(prefix="group-order-", dir=out) as name:
        work = Path(name)
        for filename, data in sources.items():
            (work / filename).write_bytes(data)
        run("model", [lean, "-o", "GroupOrderModel.olean", "GroupOrderModel.lean"], work)
        run("laws", [lean, "-o", "GroupOrder.olean", "GroupOrder.lean"], work)
        names = re.findall(r"(?m)^theorem ([A-Za-z_][A-Za-z0-9_]*)", sources["GroupOrder.lean"].decode())
        qualified = ["KeyframeGroupOrder." + n for n in names]
        (work / "Audit.lean").write_text("import GroupOrder\n" +
                                        "".join("#print axioms " + n + "\n" for n in qualified))
        text = run("axioms", [lean, "Audit.lean"], work)
        audits = {}
        for line in re.sub(r",\n\s*", ", ", text).splitlines():
            match = re.fullmatch(r"'([^']+)' (does not depend on any axioms|depends on axioms: \[(.*)\])", line)
            if not match:
                raise ValueError("Unexpected axiom record: " + line)
            axioms = set(match[3].split(", ")) if match[3] else set()
            if match[1] in audits or not axioms <= {"propext", "Classical.choice", "Quot.sound"}:
                raise ValueError("Unexpected theorem axioms: " + line)
            audits[match[1]] = sorted(axioms)
        if set(audits) != set(qualified) or len(names) != len(set(names)):
            raise ValueError("Incomplete theorem audit")
        model = sources["GroupOrderModel.lean"].decode()
        old = "groups.filter (· != key) ++ [key]"
        if model.count(old) != 1:
            raise ValueError("Mutation target changed")
        mutations = {
            "retain-latest-position": "if key ∈ groups then groups else groups ++ [key]",
            "prepend-group": "key :: groups.filter (· != key)",
            "duplicate-group": "groups ++ [key]",
        }
        (work / "Witness.lean").write_text(
            "import GroupOrderModel\nopen KeyframeGroupOrder\n"
            "example : (assembleReverse [0, 1, 2, 1]).reverse = [0, 1, 2] := by decide\n")
        run("positive-witness", [lean, "Witness.lean"], work)
        for label, replacement in mutations.items():
            (work / "GroupOrderModel.lean").write_text(model.replace(old, replacement))
            run(label + "-compile", [lean, "-o", "GroupOrderModel.olean", "GroupOrderModel.lean"], work)
            run(label + "-unchanged-laws", [lean, "GroupOrder.lean"], work, succeeds=False)
            failure = run(label + "-false-witness", [lean, "Witness.lean"], work, succeeds=False)
            expected_failure = (
                "Witness.lean:3:67: error: Tactic `decide` proved that the proposition\n"
                "  (assembleReverse [0, 1, 2, 1]).reverse = [0, 1, 2]\n"
                "is false\n")
            if failure != expected_failure:
                raise ValueError("Expected a false proposition diagnostic: " + label)
    if sources != {name: (ROOT / name).read_bytes() for name in sources}:
        raise ValueError("Sources changed during verification")
    report = {"status": "pass", "sources": {n: digest(b) for n, b in sources.items()},
              "lean_sha256": digest(lean.read_bytes()), "audits": audits,
              "compiling_semantic_mutants": list(mutations), "commands": commands,
              "temporary_builds_removed": True, "native_memory_or_payload_correctness_proved": False}
    (out / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(f"PASS: {len(audits)} theorem audits and {len(mutations)} compiling semantic mutants")


if __name__ == "__main__":
    main()
