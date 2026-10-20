import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise SystemExit("requires isolated, no-site, nonoptimized Python")
sys.dont_write_bytecode = True
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import subprocess

ROOT = Path(__file__).resolve().parent

def digest(data):
    return hashlib.sha256(data).hexdigest()

def authenticate(expected):
    data = (ROOT / "FILES.json").read_bytes()
    if digest(data) != expected:
        raise SystemExit("external manifest mismatch")
    files = json.loads(data)
    dirs = {"."}
    for name in files:
        p = Path(name)
        if p.is_absolute() or ".." in p.parts or str(p) != name:
            raise SystemExit("unsafe path")
        dirs.update(str(x) for x in p.parents)
    seen = set()
    for current, subdirs, names in os.walk(ROOT, followlinks=False):
        base = Path(current)
        for name in subdirs + names:
            p = base / name
            rel = str(p.relative_to(ROOT))
            mode = p.lstat().st_mode
            if stat.S_ISDIR(mode):
                if rel not in dirs:
                    raise SystemExit("unexpected directory: " + rel)
            elif stat.S_ISREG(mode):
                if rel in {"FILES.json", "FREEZE.json"}:
                    continue
                if rel not in files or digest(p.read_bytes()) != files[rel]:
                    raise SystemExit("unlisted or changed file: " + rel)
                seen.add(rel)
            else:
                raise SystemExit("nonregular input: " + rel)
    if seen != set(files):
        raise SystemExit("missing inputs")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--files-sha256", required=True)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    authenticate(args.files_sha256)
    out = args.output.resolve()
    if out.exists() or out == ROOT or ROOT in out.parents:
        raise SystemExit("fresh external output required")
    tool = json.loads((ROOT / "TOOLCHAIN.json").read_text())
    lean = Path(tool["lean"])
    if digest(lean.read_bytes()) != tool["sha256"]:
        raise SystemExit("Lean executable mismatch")
    modules = ["PrimaryBit", "Publication", "InitialDispatch", "Witnesses", "MutationWitnesses", "Audit"]
    names = json.loads((ROOT / "AUDIT-NAMES.json").read_text())
    actual = []
    for m in modules[:-1]:
        text = (ROOT / "lean" / (m + ".lean")).read_text()
        if re.search(r"\b(?:sorry|admit|axiom|native_decide)\b", text):
            raise SystemExit("unsupported proof token")
        ns = re.search(r"^namespace (\S+)", text, re.M)[1]
        actual += [ns + "." + n for n in re.findall(r"^theorem (\w+)", text, re.M)]
    if actual != names:
        raise SystemExit("audit inventory differs")
    out.mkdir(parents=True)
    env = os.environ.copy()
    env["LEAN_PATH"] = str(out)
    commands = []

    def run(label, argv, success=True):
        result = subprocess.run(argv, cwd=ROOT, env=env, capture_output=True, text=True)
        (out / (label + ".stdout")).write_text(result.stdout)
        (out / (label + ".stderr")).write_text(result.stderr)
        commands.append({"label": label, "argv": argv, "cwd": str(ROOT), "returncode": result.returncode})
        (out / "COMMANDS.json").write_text(json.dumps(commands, indent=2) + "\n")
        if success and (result.returncode != 0 or result.stderr):
            raise SystemExit("command failed: " + label)
        if not success and (result.returncode == 0 or "is false" not in result.stdout):
            raise SystemExit("falseclaim did not fail semantically: " + label)
        return result

    run("bindings", [sys.executable, "-I", "-S", str(ROOT / "bindings.py")])
    for module in modules:
        run(module, [str(lean), "-o", str(out / (module + ".olean")),
            str(ROOT / "lean" / (module + ".lean"))])
    audit = (out / "Audit.stdout").read_text()
    reports = re.findall(r"'([^']+)' (?:does not depend on any axioms|depends on axioms: \[([^\]]*)\])", audit)
    if [n for n, _ in reports] != names:
        raise SystemExit("axiom report roster differs")
    allowed = {"propext", "Classical.choice", "Quot.sound"}
    if any(set(filter(None, (x.strip() for x in axioms.split(",")))) - allowed for _, axioms in reports):
        raise SystemExit("unexpected axiom")
    for name in ["OmittedClear", "MissingAreaGuard", "OmittedPublish"]:
        run(name, [str(lean), str(ROOT / "falseclaims" / (name + ".lean"))], False)
    authenticate(args.files_sha256)
    (out / "RESULT.json").write_text(json.dumps({"status": "PASS", "audits": len(names),
        "source_bindings": 26, "model_mutants": 3,
        "source_translation": "manual correspondence, not mechanically established",
        "full_native_projection": "OPEN"}, indent=2) + "\n")

if __name__ == "__main__":
    main()
