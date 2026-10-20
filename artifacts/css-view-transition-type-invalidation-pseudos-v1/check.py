import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise RuntimeError("Use python3 -I -S without optimization")
from pathlib import Path
import hashlib, json, stat
root = Path(__file__).resolve().parent
def require(ok, why):
    if not ok: raise RuntimeError(why)
def load(n): return json.loads((root/n).read_text())
rows = load("FILES.json")
expected = {r["path"] for r in rows} | {"FILES.json", "FREEZE.json"}
actual = set()
for p in root.rglob("*"):
    mode = p.lstat().st_mode
    require(stat.S_ISDIR(mode) or stat.S_ISREG(mode), "nonregular")
    if stat.S_ISREG(mode): actual.add(p.relative_to(root).as_posix())
require(actual == expected, "roster")
for r in rows:
    data = (root/r["path"]).read_bytes()
    require(len(data) == r["bytes"] and hashlib.sha256(data).hexdigest() == r["sha256"], "input")
require(load("FREEZE.json")["FILES_sha256"] == hashlib.sha256((root/"FILES.json").read_bytes()).hexdigest(), "seal")
receipt = load("runtime-v1/RUN.json")
raw = load("runtime-v1/raw.json")
require(receipt["stable_pins"] and receipt["pins_before"] == receipt["pins_after"] and raw["complete"], "runtime")
ops = ["add", "delete", "clear", "add-existing", "delete-missing", "clear-empty"]
require([r["label"] for r in raw["rows"]] == ["ready/"+x for x in ops], "cases")
for op, row in zip(ops, raw["rows"]):
    require(not row["beforeFailures"] and not row["refreshFailures"], "calibration")
    active = op in ["add", "add-existing"]
    want = {"rootBefore": "0.8" if active else "0.2", "childBefore": "0.75" if active else "0.25", "groupOpacity": "0.7" if active else "0.3"}
    for key, value in want.items():
        require(row["expected"][key] == value and row["refreshed"][key] == value, "oracle")
    failures = ["color", "width", "rootBefore", "childBefore", "groupOpacity"] if op in ops[:3] else []
    require(row["failures"] == failures, "discrepancies")
    require(row["operation"]["activeIdentity"], "owner")
    require(row["actual"]["groupAnimationName"] == "-ua-view-transition-group-anim-root" and row["actual"]["groupAnimationDuration"] == "100s", "animation calibration")
    require(any(a["pseudo"] == "::view-transition-group(root)" and a["state"] == "running" and a["name"] == "-ua-view-transition-group-anim-root" for a in row["operation"]["animations"]), "running group")
print(json.dumps({"status": "PASS", "rows": 6, "discrepancies": 3, "controls": 3}))
