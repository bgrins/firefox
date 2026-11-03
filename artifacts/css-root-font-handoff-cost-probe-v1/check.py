import hashlib
import json
from pathlib import Path
import subprocess

here = Path(__file__).resolve().parent
root = here.parents[1]
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
source = (here / "probe.js").read_text()
subprocess.run(["node", "--check", str(here / "probe.js")], check=True)
subprocess.run(["node", "-e", "const fs=require('fs'),vm=require('vm');const f=vm.runInNewContext(fs.readFileSync(process.argv[1],'utf8'));if(typeof f!=='function'||f.constructor.name!=='AsyncFunction'||f.length!==0)throw Error('not the expected inert function');", str(here / "probe.js")], check=True)
timed = source.split("        const start = win.performance.now();\n", 1)[1].split("        row.samples.push", 1)[0]
assert timed == """        rootAnimation.currentTime = currentTime;
        const value = win.getComputedStyle(target).fontSize;
        const elapsedMs = win.performance.now() - start;
"""
loop = source.split("      for (let index = 0;", 1)[1].split("      row.post =", 1)[0]
assert "await " not in loop and loop.count("getComputedStyle(") == 1
assert "getComputedStyle(root)" not in loop and "getAnimations" not in loop
roster = json.loads((here / "ROSTER.json").read_bytes())
assert roster["leaf_counts"] == [0, 1000, 5000]
assert roster["all_samples"] == 3 * (4 + 12) == 48
assert roster["measured_samples"] == 3 * 12 == 36
assert "const counts = [0, 1000, 5000];" in source
assert "const warmups = 4;" in source and "const repetitions = 12;" in source
assert "index % 2 === 0 ? 1000 : 0" in loop
assert "currentTime === 1000 ? 64 : 32" in loop
refs = json.loads((here / "REFERENCES.json").read_bytes())
for name, digest in refs.items():
    assert sha(root / name) == digest, name
print(json.dumps({"success": True, "syntax_and_inert_function": True,
                  "exact_timed_region": True, "samples": 48, "measured": 36,
                  "references": len(refs), "browser_executed": False,
                  "tested": {name: sha(here / name) for name in
                             ["probe.js", "ROSTER.json", "REFERENCES.json", "check.py"]}}, indent=2))
