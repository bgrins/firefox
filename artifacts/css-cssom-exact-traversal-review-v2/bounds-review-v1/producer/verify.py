import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise SystemExit("requires isolated nonoptimized no-site Python")
sys.dont_write_bytecode = True
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess

HERE = Path(__file__).resolve().parent

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def authenticate(pin):
    if sha(HERE / "FILES.json") != pin:
        raise SystemExit("manifest mismatch")
    manifest = json.loads((HERE / "FILES.json").read_text())
    actual = set()
    for p in HERE.rglob("*"):
        if p.is_symlink():
            raise SystemExit("symlink input")
        if p.is_file():
            actual.add(str(p.relative_to(HERE)))
    if actual != set(manifest) | {"FILES.json", "FREEZE.json"}:
        raise SystemExit("file roster mismatch")
    for n, h in manifest.items():
        p = Path(n)
        if p.is_absolute() or ".." in p.parts or sha(HERE / p) != h:
            raise SystemExit("input mismatch: " + n)

def audits(text):
    expected = json.loads((HERE / "AUDITS.json").read_text())
    rows = re.findall(r"'([^']+)' (?:does not depend on any axioms|depends on axioms: \[([^\]]*)\])", text)
    if [n for n, _ in rows] != expected or len(rows) != 9:
        raise SystemExit("audit roster mismatch")
    allowed = {"propext", "Classical.choice", "Quot.sound"}
    if any(set(filter(None, (a.strip() for a in ax.split(",")))) - allowed for _, ax in rows):
        raise SystemExit("unexpected axiom")
    if "warning:" in text or "error:" in text:
        raise SystemExit("compiler diagnostic")

parser = argparse.ArgumentParser()
parser.add_argument("--files-sha256", required=True)
parser.add_argument("--output", type=Path)
args = parser.parse_args()
authenticate(args.files_sha256)
audits((HERE / "compile.stdout").read_text())
if (HERE / "compile.stderr").read_text():
    raise SystemExit("retained compiler stderr")
if args.output:
    out = args.output.resolve()
    if out.exists() or HERE == out or HERE in out.parents:
        raise SystemExit("fresh external output required")
    tool = json.loads((HERE / "TOOLCHAIN.json").read_text())
    if sha(Path(tool["lean"])) != tool["sha256"]:
        raise SystemExit("toolchain mismatch")
    out.mkdir(parents=True)
    argv = [tool["lean"], "-o", str(out / "ExactTraversalBounds.olean"), str(HERE / "ExactTraversalBounds.lean")]
    result = subprocess.run(argv, cwd=out, env={**os.environ, "LEAN_PATH": str(out)}, capture_output=True, text=True)
    (out / "compile.stdout").write_text(result.stdout)
    (out / "compile.stderr").write_text(result.stderr)
    (out / "COMMAND.json").write_text(json.dumps({"argv": argv, "cwd": str(out), "exit": result.returncode}, indent=2) + "\n")
    if result.returncode or result.stderr:
        raise SystemExit("compilation failed")
    audits(result.stdout)
    authenticate(args.files_sha256)
    (out / "RESULT.json").write_text(json.dumps({"status": "PASS", "audits": 9, "native_projection": "OPEN"}, indent=2) + "\n")
print(json.dumps({"status": "PASS", "audits": 9, "fresh_replay": bool(args.output), "native_projection": "OPEN"}))
