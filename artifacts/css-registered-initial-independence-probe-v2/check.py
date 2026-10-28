import hashlib
import json
from pathlib import Path
import re
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
BASE = HERE.parent / "css-registered-initial-independence-probe-v1"
original = "registered-initial-computational-independence.html"
expanded = "registered-initial-selected-independence.html"
assert (HERE / original).read_bytes() == (BASE / original).read_bytes()
cases = json.loads((HERE / "CASES.json").read_text())
assert len(cases) == 46 and len({c["id"] for c in cases}) == 46
assert len([c for c in cases if c["family"] == "selected-alternative"]) == 6
assert len([c for c in cases if c["family"] == "container-dependence"]) == 30
assert len([c for c in cases if c["family"] == "independent-control"]) == 10
rosters = {}
with tempfile.TemporaryDirectory(prefix="css-initial-probe-check-", dir="/private/tmp") as scratch:
    for filename in [original, expanded, "initial-independence-observations.html"]:
        body = (HERE / filename).read_text()
        scripts = re.findall(r"<script>([\s\S]*?)</script>", body)
        assert len(scripts) == 1
        script = Path(scratch) / (filename + ".js")
        script.write_text(scripts[0])
        subprocess.run(["node", "--check", str(script)], check=True)
        if filename == "initial-independence-observations.html":
            continue
        wrapper = Path(scratch) / "enumerate.js"
        wrapper.write_text("const fs=require('fs'),vm=require('vm'); const names=[]; vm.runInNewContext(fs.readFileSync(process.argv[2],'utf8'),{test:(_callback,name)=>names.push(name)}); process.stdout.write(JSON.stringify(names));")
        names = json.loads(subprocess.check_output(["node", str(wrapper), str(script)]))
        assert len(names) == (21 if filename == original else 46)
        assert len(names) == len(set(names))
        rosters["/css/css-properties-values-api/" + filename] = names
assert sum(map(len, rosters.values())) == 67
assert len(json.loads((HERE / "OBSERVATION-CASES.json").read_text())) == 5
for name, anchors in json.loads((HERE / "ANCHORS.json").read_text()).items():
    text = (HERE / (name + ".html")).read_text()
    assert all('id="' + anchor + '"' in text for anchor in anchors)
(HERE / "TARGET-SUBTESTS.json").write_text(json.dumps(rosters, indent=2) + "\n")
result = {"original21_byte_identical": True, "original_sha256": hashlib.sha256((HERE / original).read_bytes()).hexdigest(), "normative_assertions": 67, "new_assertions": 46, "report_only_observations": 5, "node_syntax": True, "callbacks_executed": False, "browser_executed": False, "scratch_removed": True}
(HERE / "STATIC.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result))
