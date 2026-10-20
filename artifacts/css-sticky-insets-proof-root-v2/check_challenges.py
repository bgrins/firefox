import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise SystemExit("use python3 -I -S")
sys.dont_write_bytecode = True
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parent / "css-sticky-insets-proof-v2"
EXPECTED = "1e9875b161403f1981e041cfc72cf2ff68cf5468bb3c97efa5ba3746bdfc992e"

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def require(value, message):
    if not value:
        raise SystemExit(message)

require(digest(SOURCE / "FILES.json") == EXPECTED, "producer identity")
manifest = json.loads((SOURCE / "FILES.json").read_text())["files"]
for name, pin in manifest.items():
    require(digest(SOURCE / name) == pin, "producer file: " + name)
tools = json.loads((SOURCE / "TOOLCHAIN.json").read_text())
for name in ["lean", "clang"]:
    require(digest(Path(tools[name]["path"])) == tools[name]["sha256"], "tool: " + name)
authentication = json.loads((ROOT / "replay-v1/AUTHENTICATION.json").read_text())
require(authentication["manifest_sha256"] == EXPECTED, "fresh replay identity")
output = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else ROOT / "challenges-v3"
output.mkdir()
env = dict(os.environ)
env.pop("LEAN_SYSROOT", None)
env.pop("LEAN_SRC_PATH", None)
env["LEAN_PATH"] = str(output / "lean")
(output / "lean").mkdir()
records = []

def run(command, stem):
    log = output / (stem + ".log")
    with log.open("w") as stream:
        result = subprocess.run(command, env=env, stdout=stream, stderr=subprocess.STDOUT)
    record = {"command": command, "exit": result.returncode, "log": log.name}
    records.append(record)
    (output / "COMMANDS.json").write_text(json.dumps(records, indent=2) + "\n")
    return result.returncode, log.read_text()

modules = ["StickyAxis", "StickyPosition", "StickyWritingMode", "StickyGeometry",
           "StickyRanges", "StickyNumeric", "StickyContinuations", "StickyMachineGeometry",
           "StickyConsumers", "StickyPipeline", "StickyChallenges", "StickyAbsolute",
           "StickyEndpoints", "StickyEndpointCaller"]
for name in modules:
    code, text = run([tools["lean"]["path"], "--root=" + str(SOURCE / "lean"),
                      "-o", str(output / "lean" / (name + ".olean")),
                      str(SOURCE / "lean" / (name + ".lean"))], "module-" + name)
    require(code == 0, "fresh module: " + name)
code, text = run([tools["lean"]["path"], str(ROOT / "CrossAxisChallenges.lean")], "lean")
require(code == 0, "kernel challenges")
require(text.count("depends on axioms: [propext]") == 3, "exact three axiom reports")
require("sorryAx" not in text, "sorry rejected")
spec = importlib.util.spec_from_file_location("producer_generate", SOURCE / "native/generate.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
source = output / "CrossAxis.cpp"
source.write_text(module.generate("combined", str(ROOT / "CrossAxisDriver.cpp")))
rows = []
for mode, flag in [("debug", "-O0"), ("optimized", "-O2")]:
    executable = output / ("native-" + mode)
    command = [tools["clang"]["path"], "-std=c++20", flag, "-fsanitize=undefined",
               "-fno-sanitize-recover=all", str(source), "-o", str(executable)]
    code, text = run(command, mode + "-compile")
    require(code == 0, "native compilation")
    for case in range(4):
        code, text = run([str(executable), str(case)], mode + "-" + str(case))
        if case == 0:
            require(code == 0 and text == "10,500\n", "ordinary positive control")
        else:
            require(code != 0 and "signed integer overflow" in text, "opposite-axis overflow witness")
        rows.append({"mode": mode, "case": case, "exit": code, "output": text})
result = {"status": "PASS", "meaning": "three proof-domain counterexamples, not browser reachability",
          "manifest_sha256": EXPECTED, "generated_source_sha256": digest(source), "rows": rows}
(output / "RESULT.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps({"status": "PASS", "kernel_witnesses": 3, "native_runs": len(rows)}))
