import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise SystemExit("requires python3 -I -S without optimization")
sys.dont_write_bytecode = True
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parent
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    out = args.output.resolve()
    if out.exists() or out == ROOT or ROOT in out.parents:
        raise SystemExit("fresh external output required")
    tool = json.loads((ROOT / "capsule/TOOLS.json").read_text())[
        "artifacts/stylo-bloom-tools/lean-4.35.0-rc4-darwin_aarch64/bin/lean"]
    if hashlib.sha256(Path(tool["path"]).read_bytes()).hexdigest() != tool["sha256"]:
        raise SystemExit("Lean mismatch")
    out.mkdir(parents=True)
    env = os.environ.copy()
    env["LEAN_PATH"] = str(out)
    commands = []
    for name, argv in [
        ("Edges", [tool["path"], "-o", str(out / "Edges.olean"), str(ROOT / "capsule/lean/Edges.lean")]),
        ("Challenges", [tool["path"], str(ROOT / "Challenges.lean")]),
    ]:
        r = subprocess.run(argv, env=env, text=True, capture_output=True)
        (out / (name + ".stdout")).write_text(r.stdout)
        (out / (name + ".stderr")).write_text(r.stderr)
        commands.append({"argv": argv, "returncode": r.returncode})
        (out / "COMMANDS.json").write_text(json.dumps(commands, indent=2) + "\n")
        if r.returncode or r.stderr:
            raise SystemExit("compilation failed")
    names = re.findall(r"^theorem (\w+)", (ROOT / "Challenges.lean").read_text(), re.M)
    reports = re.findall(r"'RectangleIndependent\.(\w+)' (?:does not depend on any axioms|depends on axioms: \[([^\]]*)\])",
        (out / "Challenges.stdout").read_text())
    if [n for n, _ in reports] != names:
        raise SystemExit("audit roster mismatch")
    if any(set(filter(None, (s.strip() for s in ax.split(",")))) -
        {"propext", "Classical.choice", "Quot.sound"} for _, ax in reports):
        raise SystemExit("unexpected axiom")
    (out / "RESULT.json").write_text(json.dumps({"status": "PASS", "audits": len(names),
        "axioms": dict(reports)}, indent=2) + "\n")

if __name__ == "__main__":
    main()
