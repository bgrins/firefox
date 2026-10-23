import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise RuntimeError("Require python3 -I -S without optimization")
sys.dont_write_bytecode = True
import ast
import copy
import importlib.util
import json
from pathlib import Path
import subprocess

here = Path(__file__).resolve().parent
for name in ("run.py", "validate.py", "self_check.py"):
    ast.parse((here / name).read_text(), filename=name)
subprocess.run(["node", "--check", str(here / "benchmark.js")], check=True)
spec = importlib.util.spec_from_file_location("validator", here / "validate.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
c = json.loads((here / "CONFIG.json").read_text())
configs = [(k, s, n) for k in c["kinds"] for s in c["states"] for n in c["sizes"]]
rows = []
for r in range(c["measured_rounds"]):
    for slot in range(len(configs)):
        ordinal = (slot + r + c["warmup_rounds"]) % len(configs)
        kind, state, count = configs[ordinal]
        n = min(count, c["query_limit"])
        indices = [0] if n == 1 else [i * (count - 1) // (n - 1) for i in range(n)]
        sizes = [[8, 8] for _ in range(n * c["iterations"])]
        rows.append(dict(round=r, slot=slot, ordinal=ordinal, kind=kind, state=state, count=count,
                         indices=indices, observedSizes=sizes,
                         outerChecksum=sum((168 if i % 2 == 0 else 160) + 64 for i in range(c["iterations"])),
                         queryChecksum=sum((ordinal + 1) * (i + 1) * (j + 1) for i in range(c["iterations"]) for j in indices),
                         geometryChecksum=len(sizes) * 384, mismatches=0, **{key: 0 for key in module.TIMERS}))
observation = dict(complete=True, label="synthetic", config=c, rows=rows, elapsedMs=0)
summary = module.validate(observation, c, "synthetic")
if (summary["measuredRows"], summary["queryReads"], summary["mutationFlushes"], summary["recoveryPreparations"]) != (84, 4032, 1344, 1344):
    raise RuntimeError("Unexpected workload counts")
mutations = {
    "missing row": lambda x: x["rows"].pop(),
    "wrong order": lambda x: x["rows"].reverse(),
    "work checksum": lambda x: x["rows"][0].update(queryChecksum=0),
    "geometry checksum": lambda x: x["rows"][0].update(geometryChecksum=0),
    "invalid timer": lambda x: x["rows"][0].update(mutationFlushMs=float("nan")),
    "wrong selection": lambda x: x["rows"][0].update(indices=[0]),
    "incomplete": lambda x: x.update(complete=False),
}
rejections = []
for name, mutate in mutations.items():
    changed = copy.deepcopy(observation)
    mutate(changed)
    try:
        module.validate(changed, c, "synthetic")
    except (ValueError, KeyError):
        rejections.append(name)
    else:
        raise RuntimeError("Accepted corruption: " + name)
changed = copy.deepcopy(observation)
changed["rows"][0]["observedSizes"][0] = [0, 0]
changed["rows"][0]["geometryChecksum"] -= 384
changed["rows"][0]["mismatches"] = 1
if module.validate(changed, c, "synthetic")["geometryMismatches"] != 1:
    raise RuntimeError("Geometry failure must remain descriptive data")
print(json.dumps({"kind": "source and synthetic checks only; no browser timings", "syntax": "PASS", "measuredRows": 84, "queryReads": 4032, "rejected": rejections, "zeroTimersRetained": True, "geometryMismatchRetained": True}, indent=2))
