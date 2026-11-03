from copy import deepcopy
import json
from pathlib import Path
import runpy

module = runpy.run_path(str(Path(__file__).with_name("assess.py")))
assess, cases, phases = (module[k] for k in ["assess", "CASES", "PHASES"])
data = {"schema": "numeric-font-settings-parent-metrics-v1", "cleanup": True,
        "errors": [], "samples": []}
for prop, tag, form in cases:
    for phase, (parent, child) in phases.items():
        for timing in ["first", "settled"]:
            value = parent if form == "em-ratio" else parent / 2 if form == "ch-ratio" else 20
            data["samples"].append({
                "property": prop, "tag": tag, "form": form,
                "phase": {"name": phase, "parent": parent, "child": child}, "timing": timing,
                "compatMode": "CSS1Compat", "parentFontSize": f"{parent}px", "childFontSize": f"{child}px",
                "metrics": {"parentEm": parent, "childEm": child, "parentCh": parent / 2, "childCh": child / 2},
                "supports": True, "declaration": "synthetic-admitted", "admitted": True,
                "computed": f'"{tag}" {value:g}', "value": value})
assert assess(data)["observations"] == 66
child = deepcopy(data)
for row in child["samples"]:
    if row["form"] == "em-ratio":
        row["value"] = row["phase"]["child"]
        row["computed"] = f'"{row["tag"]}" {row["value"]}'
assert all(x["status"] == "matches-child" for x in assess(child)["outcomes"] if x["form"] == "em-ratio")
unsupported = deepcopy(data)
for row in unsupported["samples"]:
    if row["form"] != "literal":
        row.update(supports=False, declaration="", admitted=False, computed="normal", value=None)
assert all(x["status"] == "not-admitted" for x in assess(unsupported)["outcomes"] if x["form"] != "literal")
unstable = deepcopy(data)
row = next(r for r in unstable["samples"] if r["form"] == "em-ratio")
row.update(value=99, computed='"wdth" 99')
assert any(x["status"] == "unstable" for x in assess(unstable)["outcomes"])
mutations = [
    lambda d: d.update(cleanup=False),
    lambda d: d["samples"].pop(),
    lambda d: d["samples"].append(deepcopy(d["samples"][0])),
    lambda d: d["samples"][0].update(compatMode="BackCompat"),
    lambda d: d["samples"][0].update(parentFontSize="19px"),
    lambda d: d["samples"][0]["metrics"].update(childEm=39),
    lambda d: d["samples"][0].update(value=21, computed='"wdth" 21'),
    lambda d: d["samples"][6].update(value=21, computed='"wdth" 21'),
    lambda d: d["samples"][0]["metrics"].update(parentCh=float("nan")),
]
for mutate in mutations:
    changed = deepcopy(data)
    mutate(changed)
    try:
        assess(changed)
    except AssertionError:
        continue
    raise AssertionError("Invalid synthetic observation was accepted")
print(json.dumps({"synthetic_positive_paths": 4, "rejected_corruptions": len(mutations),
                  "browser_observations": 0}))
