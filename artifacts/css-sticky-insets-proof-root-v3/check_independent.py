import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise RuntimeError("Use Python -I -S without optimization")
sys.dont_write_bytecode = True
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / "css-sticky-insets-proof-v3"
parser = argparse.ArgumentParser()
parser.add_argument("--manifest-sha", required=True)
parser.add_argument("--replay", required=True)
parser.add_argument("--output", required=True)
args = parser.parse_args()
replay = Path(args.replay).resolve()
out = Path(args.output).resolve()


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(name, value):
    (out / name).write_text(json.dumps(value, indent=2) + "\n")


assert sha(SOURCE / "FILES.json") == args.manifest_sha
manifest = json.loads((SOURCE / "FILES.json").read_text())["files"]
assert {str(p.relative_to(SOURCE)) for p in SOURCE.rglob("*") if p.is_file()} == set(manifest) | {"FILES.json", "FREEZE.json"}
assert all(not (SOURCE / n).is_symlink() and sha(SOURCE / n) == digest for n, digest in manifest.items())
assert json.loads((SOURCE / "FREEZE.json").read_text())["manifest_sha256"] == args.manifest_sha
receipt = json.loads((replay / "AUTHENTICATION.json").read_text())
assert receipt["status"] == "pass" and receipt["manifest_sha256"] == args.manifest_sha
result = json.loads((replay / "RESULT.json").read_text())
assert result["status"] == "pass" and result["audits"] == 191
tools = json.loads((SOURCE / "TOOLCHAIN.json").read_text())
for row in tools.values():
    assert sha(Path(row["path"]).resolve()) == row["sha256"]
out.mkdir(parents=True, exist_ok=False)
commands = []


def run(command, name, *, env=None, success=True):
    process = subprocess.run(command, capture_output=True, text=True, env=env)
    (out / (name + ".log")).write_text(process.stdout + process.stderr)
    commands.append({"name": name, "command": command, "exit": process.returncode})
    write("COMMANDS.json", commands)
    if success:
        assert process.returncode == 0, name
    return process


lean_source = HERE / "Independent.lean"
olean = out / "Independent.olean"
lean_env = {"PATH": "/usr/bin:/bin", "LEAN_PATH": str(out) + os.pathsep + str(replay / "lean")}
run([tools["lean"]["path"], "-o", str(olean), str(lean_source)], "independent-compile", env=lean_env)
names = re.findall(r"^theorem (\w+)", lean_source.read_text(), re.M)
assert len(names) == 9
audit = out / "Audit.lean"
audit.write_text("import Independent\n" + "\n".join("#print axioms Independent." + name for name in names) + "\n")
process = run([tools["lean"]["path"], str(audit)], "independent-axioms", env=lean_env)
audited = {}
for line in process.stdout.splitlines():
    match = re.fullmatch(r"'([^']+)' depends on axioms: \[([^]]*)\]", line)
    if match:
        name, axioms = match[1], match[2].split(", ") if match[2] else []
    else:
        match = re.fullmatch(r"'([^']+)' does not depend on any axioms", line)
        assert match, line
        name, axioms = match[1], []
    assert name not in audited and set(axioms) <= {"propext", "Quot.sound", "Classical.choice"}
    audited[name] = axioms
assert list(audited) == ["Independent." + name for name in names]
write("AUDITS.json", audited)

spec = importlib.util.spec_from_file_location("independent_generator", SOURCE / "native/generate.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
generated = module.generate("combined", "full_entry_driver.cpp")
old_driver = (SOURCE / "native/full_entry_driver.cpp").read_text()
assert generated.endswith(old_driver)
cpp = out / "Continuation.cpp"
cpp.write_text(generated[:-len(old_driver)] + (HERE / "continuation_driver.cpp").read_text())
expected = [
    [60, 40, 450, -50, 40, 500, 500],
    [0, 40, 450, -50, 40, 500, 500],
    [60, 50, 440, -40, 50, 50, 490],
    None,
    None,
]
native = []
for label, flag in [("debug", "-O0"), ("optimized", "-O2")]:
    binary = out / ("continuation-" + label)
    run([tools["clang"]["path"], "-std=c++20", flag, "-fsanitize=undefined", "-fno-sanitize-recover=all",
         str(cpp), "-o", str(binary)], label + "-compile")
    for mode in range(6):
        process = run([str(binary), str(mode)], label + "-" + str(mode), success=mode != 5)
        if mode == 5:
            assert process.returncode != 0 and "signed integer overflow" in process.stderr
            assert "2147483647 - -1" in process.stderr
            native.append({"mode": mode, "configuration": label, "predicted_overflow": True})
            continue
        assert not process.stderr
        actual = json.loads(process.stdout)
        trace = [907, 407] if mode >= 3 else [907, 407, 407, 207, 1170, 1121, 1172, 700, 302]
        assert actual == {"value": expected[mode], "trace": trace}, (label, mode, actual)
        native.append({"mode": mode, "configuration": label, "actual": actual})
write("NATIVE.json", native)
assert all(sha(SOURCE / n) == digest for n, digest in manifest.items())
write("RESULT.json", {"complete": True, "manifest_sha256": args.manifest_sha,
      "audits": len(audited), "native_runs": len(native), "admitted_native_runs": 10,
      "predicted_overflows": 2, "independent_source": sha(lean_source), "driver": sha(HERE / "continuation_driver.cpp"),
      "scope": "Conditional full-frame caller model and extracted-native provider calibration; no browser reachability claim."})
print(json.dumps({"complete": True, "audits": len(audited), "native_runs": len(native)}))
