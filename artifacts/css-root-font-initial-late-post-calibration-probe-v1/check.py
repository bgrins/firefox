from pathlib import Path
import hashlib
import json
import re
import subprocess
import tempfile

here = Path(__file__).resolve().parent
root = here.parents[1]
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
relative = "tests/web-animations/animation-model/keyframe-effects/initial-root-font-child-keyframes.html"
parent = root / "artifacts/css-root-font-final-animation-wpt-v1" / relative
old = parent.read_text()
new = (here / relative).read_text()
assert sha(parent) == "d46be24b9e0e089fd12e20d868af6fe5ee35da895eb6a353edfe51dcdf67e582"
added = '    const afterCalibration = win.getComputedStyle(target).fontSize;\n'
assert new.count(added) == 1
assert new.replace(added, "").replace(
    "      mode, first, settled, rootSize, plainSize, precondition, afterCalibration,",
    "      mode, first, settled, rootSize, plainSize, precondition,",
) == old
assert new.index("const plainSize =") < new.index(added) < new.index("const rootAnimations =")
refs = json.loads((here / "REFERENCES.json").read_bytes())
for name, digest in refs.items():
    assert sha(root / name) == digest, name
inputs = json.loads((here / "INPUTS.json").read_bytes())
for record in inputs["resources"].values():
    assert sha(root / record["path"]) == record["sha256"]
scripts = re.findall(r"<script>([\s\S]*?)</script>", new)
assert len(scripts) == 1
with tempfile.TemporaryDirectory(prefix="post-calibration-syntax-", dir="/private/tmp") as tmp:
    script = Path(tmp) / "fixture.js"
    script.write_text(scripts[0])
    subprocess.run(["node", "--check", str(script)], check=True)
    code = "const fs=require('fs'),vm=require('vm'),names=[];vm.runInNewContext(fs.readFileSync(process.argv[1],'utf8'),{window:{},promise_test:(_,n)=>names.push(n)});if(names.length!==3)throw Error('roster');console.log(JSON.stringify(names));"
    names = json.loads(subprocess.check_output(["node", "-e", code, str(script)], text=True))
assert not Path(tmp).exists()
print(json.dumps({"success": True, "callbacks": names, "references": len(refs),
                  "exact_parent_erasure": True, "extra_target_reads": 1,
                  "scratch_removed": True, "scratch_path": tmp,
                  "browser_executed": False,
                  "tested": {name: sha(here / name) for name in
                             [relative, "check.py", "REFERENCES.json", "INPUTS.json"]}}, indent=2))
