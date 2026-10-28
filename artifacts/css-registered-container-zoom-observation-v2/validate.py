import copy
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
CASES = json.loads((HERE / "CASES.json").read_text())
MUTATIONS = json.loads((HERE / "PROTOCOL.json").read_text())["mutations"]
ORDER = "viewport, ancestors outer-to-inner, targets in declared variant order; custom value then computed properties then dimensions then rect"
CSS = {"width", "height", "zoom", "fontSize", "lineHeight", "writingMode", "inlineSize", "blockSize", "containerType"}
DIMS = {"clientWidth", "clientHeight", "offsetWidth", "offsetHeight"}
RECT = {"x", "y", "width", "height", "top", "right", "bottom", "left"}


def need(value, message):
    if not value:
        raise ValueError(message)


def numeric(value):
    return type(value) in (int, float) and math.isfinite(value)


def measure(value, registered, target):
    need(set(value) == {"specifiedCSS", "value", "css", "dimensions", "rect"} | ({"variant"} if target else set()), "measurement fields")
    need(isinstance(value["specifiedCSS"], str) and value["specifiedCSS"], "specified CSS")
    need(isinstance(value["value"], str) if registered else value["value"] is None, "registered value shape")
    need(set(value["css"]) == CSS and all(isinstance(x, str) and x for x in value["css"].values()), "computed CSS")
    need(set(value["dimensions"]) == DIMS and all(numeric(x) for x in value["dimensions"].values()), "dimensions")
    need(set(value["rect"]) == RECT and all(numeric(x) for x in value["rect"].values()), "rect")


def snapshots(row, case, changes):
    need(len(row["snapshots"]) == len(changes), "snapshot count")
    for step, (snapshot, change) in enumerate(zip(row["snapshots"], changes)):
        need(set(snapshot) == {"step", "change", "environment", "ancestors", "targets", "deltas"}, "snapshot fields")
        need(type(snapshot["step"]) is int and snapshot["step"] == step and snapshot["change"] == change, "mutation identity")
        environment = snapshot["environment"]
        need(set(environment) == {"userAgent", "devicePixelRatio", "innerWidth", "innerHeight", "clientWidth", "clientHeight", "visualViewport", "zoom", "writingMode"}, "environment fields")
        need(all(isinstance(environment[k], str) and environment[k] for k in ["userAgent", "zoom", "writingMode"]), "environment strings")
        need(all(numeric(environment[k]) and environment[k] > 0 for k in ["devicePixelRatio", "innerWidth", "innerHeight", "clientWidth", "clientHeight"]), "viewport dimensions")
        visual = environment["visualViewport"]
        need(visual is None or set(visual) == {"width", "height", "scale"} and all(numeric(x) and x > 0 for x in visual.values()), "visual viewport")
        need(len(snapshot["ancestors"]) == len(case["ancestors"]), "ancestor count")
        for ancestor in snapshot["ancestors"]:
            measure(ancestor, False, False)
        need([x["variant"] for x in snapshot["targets"]] == case["variants"], "variant identities")
        for target in snapshot["targets"]:
            measure(target, target["variant"].startswith("registered-"), True)
        ordinary = snapshot["targets"][0]
        expected = [{"variant": target["variant"], "widthCSSOMEqual": target["css"]["width"] == ordinary["css"]["width"],
                     "rectWidthDifference": target["rect"]["width"] - ordinary["rect"]["width"],
                     "rectHeightDifference": target["rect"]["height"] - ordinary["rect"]["height"]}
                    for target in snapshot["targets"][1:]]
        need(len(snapshot["deltas"]) == len(expected), "delta count")
        for delta in snapshot["deltas"]:
            need(set(delta) == {"variant", "widthCSSOMEqual", "rectWidthDifference", "rectHeightDifference"}, "delta fields")
            need(type(delta["widthCSSOMEqual"]) is bool and numeric(delta["rectWidthDifference"]) and numeric(delta["rectHeightDifference"]), "delta types")
        need(snapshot["deltas"] == expected, "derived deltas")


def summarize(payload):
    need(isinstance(payload, dict) and set(payload) == {"observation"}, "payload")
    observation = payload["observation"]
    need(set(observation) == {"queryOrder", "rows", "sequences"} and observation["queryOrder"] == ORDER, "observation fields/order")
    need(len(observation["rows"]) == len(CASES) and len(observation["sequences"]) == len(MUTATIONS), "case counts")
    names = []
    for rows, configs, sequence in [(observation["rows"], CASES, False), (observation["sequences"], MUTATIONS, True)]:
        for row, config in zip(rows, configs):
            need(set(row) == {"id", "registration", "registrationErrors", "snapshots"} | ({"baseCase"} if sequence else set()), "row fields")
            need(row["id"] == config["id"], "case identity")
            need(isinstance(row["registration"], str) and row["registration"].startswith("--container-zoom-"), "registration name")
            names.append(row["registration"])
            need(isinstance(row["registrationErrors"], list) and all(isinstance(x, str) for x in row["registrationErrors"]), "registration errors")
            case = next(c for c in CASES if c["id"] == config["baseCase"]) if sequence else config
            if sequence:
                need(row["baseCase"] == config["baseCase"], "mutation base")
            snapshots(row, case, config["steps"] if sequence else [None])
    need(len(names) == len(set(names)), "registration uniqueness")
    return copy.deepcopy(observation)
