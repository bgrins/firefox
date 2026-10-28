import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise SystemExit("Require python3 -I -S without optimization")
sys.dont_write_bytecode = True
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
def need(ok, reason):
    if not ok:
        raise RuntimeError(reason)
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
def read(path):
    return json.loads(path.read_text())
def authenticate(base, pins):
    for name, digest in pins.items():
        need(not Path(name).is_absolute() and ".." not in Path(name).parts, "unsafe input")
        source = base / name
        need(stat.S_ISREG(source.lstat().st_mode) and sha(source) == digest, "changed input " + name)

parser = argparse.ArgumentParser()
parser.add_argument("--manifest-sha", required=True)
parser.add_argument("--library", type=Path, required=True)
parser.add_argument("--lean", type=Path, required=True)
parser.add_argument("--lean-sha", required=True)
parser.add_argument("--output", type=Path, required=True)
args = parser.parse_args()
library, lean, output = args.library.resolve(), args.lean.resolve(), args.output.resolve()
need(not output.exists() and output != library and library not in output.parents, "fresh output outside library")
need(sha(HERE / "INPUT-FILES.json") == args.manifest_sha, "input manifest identity")
authenticate(HERE, read(HERE / "INPUT-FILES.json"))
pins = read(HERE / "LIBRARY-INPUTS.json")
need(set(pins) == {"CssSemantics/TransitionMachine.lean", "CssSemantics/ProviderObservation.lean"}, "import roster")
authenticate(library, pins)
need(sha(lean) == args.lean_sha, "compiler identity")
names = read(HERE / "AUDITS.json")
declared = ["CssSemantics.ProviderObservation." + n for n in re.findall(r"^theorem (\w+)",
    (library / "CssSemantics/ProviderObservation.lean").read_text(), re.M)]
need(names == declared == re.findall(r"#print axioms ([\w.]+)", (HERE / "ImportAudit.lean").read_text()),
     "complete direct-import audit roster")
output.mkdir(parents=True)
commands = []
summary = {"status": "INCOMPLETE", "new_CSS_specification_coverage": False}

def run(label, argv, work, env):
    result = subprocess.run([str(lean), *argv], cwd=work, env=env,
        capture_output=True, text=True, timeout=60)
    (output / (label + ".stdout")).write_text(result.stdout)
    (output / (label + ".stderr")).write_text(result.stderr)
    commands.append({"label": label, "argv": [str(lean), *argv], "exit": result.returncode})
    need(result.returncode == 0 and not result.stderr, "Lean failure " + label)
    return result.stdout

try:
    with tempfile.TemporaryDirectory(prefix="provider-observation-", dir=output) as directory:
        work = Path(directory)
        env = dict(os.environ, LEAN_PATH=str(work))
        version = run("version", ["--version"], work, env)
        need(version.startswith("Lean (version 4.35.0-rc4,"), "unsupported Lean version")
        for name in pins:
            target = work / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes((library / name).read_bytes())
        (work / "ImportAudit.lean").write_bytes((HERE / "ImportAudit.lean").read_bytes())
        for name in ["CssSemantics/TransitionMachine", "CssSemantics/ProviderObservation"]:
            need(not run(Path(name).name, ["-o", name + ".olean", name + ".lean"], work, env),
                 "unexpected compilation diagnostics")
        audit = run("ImportAudit", ["ImportAudit.lean"], work, env)
        need(re.findall(r"^'([\w.]+)'", audit, re.M) == names, "audit output roster")
        for line in audit.splitlines():
            match = re.fullmatch(r"'([\w.]+)' depends on axioms: \[(.*?)\]", line)
            need(match is not None and set(match[2].split(", ")) <= {"propext", "Quot.sound"},
                 "unexpected audit axiom or output")
        authenticate(library, pins)
        summary.update(status="PASS_PORTABLE_PROVIDER_OBSERVATION_IMPORT", audited_names=names,
            library_inputs=pins, lean_sha256=args.lean_sha, lean_version=version.strip(),
            Gecko_adapter_imported=False, native_correctness_proved=False)
except BaseException as error:
    summary["failure"] = repr(error)
    raise
finally:
    summary["temporary_products_removed"] = not any(p.is_dir() for p in output.iterdir())
    (output / "COMMANDS.json").write_text(json.dumps(commands, indent=2) + "\n")
    (output / "SUMMARY.json").write_text(json.dumps(summary, indent=2) + "\n")
print(json.dumps(summary))
