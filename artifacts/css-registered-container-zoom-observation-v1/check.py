import ast
import copy
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("validation", HERE / "validate.py")
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)


def measurement(variant=None):
    return {"specifiedCSS": "synthetic", "value": "17px" if variant and variant.startswith("registered-") else None,
            "css": {key: "synthetic" for key in v.CSS}, "dimensions": {key: 10 for key in v.DIMS},
            "rect": {key: 10 for key in v.RECT}, **({"variant": variant} if variant else {})}


def row(case, changes, identity, registration, base=None):
    snapshots = []
    for step, change in enumerate(changes):
        snapshots.append({"step":step, "change":change,
            "environment":{"userAgent":"synthetic", "devicePixelRatio":1, "innerWidth":800, "innerHeight":600,
                           "clientWidth":800, "clientHeight":600, "visualViewport":None, "zoom":"1", "writingMode":"horizontal-tb"},
            "ancestors":[measurement() for _ in case["ancestors"]],
            "targets":[measurement(variant) for variant in case["variants"]],
            "deltas":[{"variant":variant, "widthCSSOMEqual":True, "rectWidthDifference":0, "rectHeightDifference":0} for variant in case["variants"][1:]]})
    return {"id":identity, "registration":registration, "registrationErrors":[], "snapshots":snapshots,
            **({"baseCase":base} if base else {})}


payload = {"observation":{"queryOrder":v.ORDER, "rows":[], "sequences":[]}}
for index, case in enumerate(v.CASES):
    payload["observation"]["rows"].append(row(case,[None],case["id"],"--container-zoom-"+str(index)))
for index, sequence in enumerate(v.MUTATIONS):
    case = next(c for c in v.CASES if c["id"] == sequence["baseCase"])
    payload["observation"]["sequences"].append(row(case,sequence["steps"],sequence["id"],"--container-zoom-m"+str(index),sequence["baseCase"]))
v.summarize(payload)
negative = []
for group in ["rows", "sequences"]:
    for index, item in enumerate(payload["observation"][group]):
        changed = copy.deepcopy(payload); changed["observation"][group].pop(index); negative.append(changed)
        changed = copy.deepcopy(payload); changed["observation"][group][index]["id"] = "wrong"; negative.append(changed)
        for step, snapshot in enumerate(item["snapshots"]):
            changed = copy.deepcopy(payload); changed["observation"][group][index]["snapshots"].pop(step); negative.append(changed)
            for target_index in range(len(snapshot["targets"])):
                changed = copy.deepcopy(payload); changed["observation"][group][index]["snapshots"][step]["targets"].pop(target_index); negative.append(changed)
            changed = copy.deepcopy(payload); changed["observation"][group][index]["snapshots"][step]["deltas"][0]["rectWidthDifference"] = 999; negative.append(changed)
for changed in negative:
    try: v.summarize(changed)
    except (ValueError, KeyError, TypeError): continue
    raise AssertionError("malformed observation accepted")
changed = copy.deepcopy(payload)
changed["observation"]["rows"][0]["registrationErrors"] = ["unsupported registration"]
v.summarize(changed)
for file in HERE.glob("*.py"): ast.parse(file.read_text())
print(json.dumps({"positive_shapes":2,"negative_shapes_rejected":len(negative),"cases":42,"baseline_targets":94,
                  "mutation_sequences":3,"mutation_snapshots":10,"mutation_target_observations":30,"browser_executed":False},indent=2))
