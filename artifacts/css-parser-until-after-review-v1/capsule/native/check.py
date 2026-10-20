import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise RuntimeError("Require python3 -I -S without optimization")
from pathlib import Path
import argparse, hashlib, json, os, subprocess
ROOT = Path(__file__).resolve().parents[1]
def require(ok, message):
    if not ok: raise RuntimeError(message)
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
config = json.loads((ROOT / "TOOLCHAIN.json").read_text())
for tool in ("lean", "rustc"):
    require(sha(Path(config[tool])) == config[tool + "_sha256"], "toolchain mismatch")
cases = json.loads((ROOT / "native/CASES.json").read_text())
require(len({c["name"] for c in cases}) == len(cases), "duplicate case")
for case in cases:
    require(set(case) == {"name", "input", "ops"}, "case fields")
    case["input"].encode("utf-8")
    saved = False
    for op in case["ops"]:
        fields = op.split(":")
        if op in {"enable", "query", "next", "save", "reset"}:
            if op == "save": saved = True
            if op == "reset": require(saved, "unsaved reset")
        elif fields[0] in {"outer", "depth", "limit"}:
            require(len(fields) == 2 and fields[1].isdigit(), "control grammar")
            value = int(fields[1]); require(0 <= value < 256, "u8 control")
            if fields[0] == "outer": require(value & ~254 == 0, "outer mask")
        elif fields[0] == "after":
            require(len(fields) == 5 and all(x.isdigit() for x in fields[1:]), "after grammar")
            require(int(fields[1]) & ~30 == 0 and fields[2] in {"0", "1"} and fields[3] in {"0", "1"} and fields[4] in {"0", "1"}, "after admission")
        else: raise RuntimeError("unadmitted operation")
expected_cases = "namespace AfterCases\ndef cases : List (List (Fin 256) × List String) := [\n" + ",\n".join("([" + ",".join(map(str, c["input"].encode())) + "],[" + ",".join(json.dumps(x) for x in c["ops"]) + "])" for c in cases) + "\n]\nend AfterCases\n"
require((ROOT / "lean/AfterCases.lean").read_text() == expected_cases, "case transfer mismatch")
for binding in json.loads((ROOT / "native/BINDINGS.json").read_text()):
    source = ROOT / binding["source"]
    require(sha(source) == binding["source_sha256"], "binding full source")
    body = source.read_bytes()[binding["start_byte"]:binding["end_byte"]]
    require(body == (ROOT / binding["retained"]).read_bytes() and hashlib.sha256(body).hexdigest() == binding["sha256"], "binding body")
p = argparse.ArgumentParser(); p.add_argument("--output", required=True, type=Path); a = p.parse_args(); out = a.output.resolve()
require(out != ROOT and ROOT not in out.parents, "output must be external")
out.mkdir(parents=True, exist_ok=False)
env = {k: v for k, v in os.environ.items() if not k.startswith(("LEAN_", "PYTHON"))}
commands = []
def run(command, extra=None):
    result = subprocess.run(command, cwd=out, env=extra or env, text=True, capture_output=True)
    commands.append(dict(command=command, exit=result.returncode, stdout=result.stdout, stderr=result.stderr))
    (out / "COMMANDS.json").write_text(json.dumps(commands, indent=2) + "\n")
    require(result.returncode == 0, "command failure: " + result.stderr + result.stdout)
    return result
run([sys.executable, "-I", "-S", str(ROOT / "compile.py"), "--output", str(out / "lean"), "AfterDriver"])
lean_env = {**env, "LEAN_PATH": str(out / "lean")}
model_run = run([config["lean"], "--root=" + str(ROOT / "lean"), "--run", str(ROOT / "lean/AfterDriver.lean")], lean_env)
require(not model_run.stderr and "PANIC" not in model_run.stdout, "model diagnostics / unsupported provider")
model = model_run.stdout
(out / "model.txt").write_text(model)
identity = [(i, j, op) for i, c in enumerate(cases) for j, op in enumerate(["init"] + c["ops"])]
def rows(raw):
    lines = raw.splitlines(); require(len(lines) == len(identity), "snapshot roster")
    for line, (case, step, op) in zip(lines, identity):
        f = line.split("|"); require(len(f) == 13, "snapshot arity")
        require(f[:3] == [str(case), str(step), op], "snapshot identity")
    return lines
expected = rows(model)
for mode, flags in [("debug", []), ("release", ["--release"])]:
    target = out / ("native-" + mode)
    run([sys.executable, "-I", "-S", str(ROOT / "native/build.py"), "--output", str(target)] + flags)
    raw = (target / "raw.txt").read_text(); rows(raw); require(raw == model, "native/model difference: " + mode)
mutants = {}
for mutation in json.loads((ROOT / "native/MUTATIONS.json").read_text()):
    target = out / ("native-" + mutation["id"])
    run([sys.executable, "-I", "-S", str(ROOT / "native/build.py"), "--release", "--output", str(target), "--mutation", mutation["id"]])
    actual = rows((target / "raw.txt").read_text())
    differences = [dict(row=i, expected=x, actual=y) for i, (x, y) in enumerate(zip(expected, actual)) if x != y]
    require(differences, "undetected native mutant")
    mutants[mutation["id"]] = differences
(out / "MUTANT-DIFFERENCES.json").write_text(json.dumps(mutants, indent=2) + "\n")
unsupported = []
for family in ("numeric", "string", "hash", "atKeyword"):
    source = out / ("Unsupported_" + family + ".lean")
    source.write_text('import AfterDriver\n#eval provider .'+family+' [49]\n')
    result = run([config["lean"], str(source)], lean_env)
    require("unadmitted provider" in result.stdout + result.stderr, "provider did not fail closed")
    unsupported.append(family)
result = dict(cases=len(cases), snapshots=len(expected), native_modes=["debug", "release"], native_mutants={k:len(v) for k,v in mutants.items()}, rejected_provider_families=unsupported, source_bindings=len(json.loads((ROOT / "native/BINDINGS.json").read_text())), scope="finite complete-source native agreement with explicitly projected state and restricted callbacks; no universal provider/callback proof")
(out / "RESULT.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result))
