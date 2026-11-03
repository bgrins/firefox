import json
import math
from pathlib import Path
import re
import sys

PHASES = {"p20-c40": (20, 40), "p30-c40": (30, 40), "p30-c60": (30, 60)}
CASES = [("font-variation-settings", "wdth", form)
         for form in ["literal", "absolute-ratio", "em-ratio"]] + [
    (prop, "XPRB", form)
    for prop in ["font-variation-settings", "font-feature-settings"]
    for form in ["literal", "absolute-ratio", "em-ratio", "ch-ratio"]]


def assess(data):
    assert data["schema"] == "numeric-font-settings-parent-metrics-v1"
    assert data["cleanup"] is True and data["errors"] == []
    expected = {(prop, tag, form, phase, timing) for prop, tag, form in CASES
                for phase in PHASES for timing in ["first", "settled"]}
    rows = {}
    for row in data["samples"]:
        key = (row["property"], row["tag"], row["form"], row["phase"]["name"], row["timing"])
        assert key in expected and key not in rows
        parent, child = PHASES[key[3]]
        assert row["phase"] == {"name": key[3], "parent": parent, "child": child}
        assert row["compatMode"] == "CSS1Compat"
        assert row["parentFontSize"] == f"{parent}px" and row["childFontSize"] == f"{child}px"
        assert row["metrics"]["parentEm"] == parent and row["metrics"]["childEm"] == child
        assert all(math.isfinite(v) and v > 0 for v in row["metrics"].values())
        assert row["admitted"] == (row["supports"] and row["declaration"] != "")
        match = re.fullmatch(r'"([A-Za-z]{4})"\s+([-+]?(?:\d+\.?\d*|\.\d+)(?:e[-+]?\d+)?)',
                             row["computed"], re.I)
        value = float(match[2]) if match and match[1] == key[1] else None
        assert row["value"] == value
        assert value is None or math.isfinite(value)
        if key[2] == "literal":
            assert row["admitted"] and value == 20
        if key[2] == "absolute-ratio" and row["admitted"]:
            assert value == 20
        rows[key] = row
    assert set(rows) == expected
    outcomes = []
    for prop, tag, form in CASES:
        for phase, (parent, child) in PHASES.items():
            row = rows[prop, tag, form, phase, "settled"]
            literal = rows[prop, tag, "literal", phase, "settled"]
            absolute = rows[prop, tag, "absolute-ratio", phase, "settled"]
            assert literal["admitted"] and literal["value"] == 20
            if absolute["admitted"]:
                assert absolute["value"] == 20
            status = "not-admitted"
            parent_value = child_value = None
            if row["admitted"]:
                if form != "literal":
                    assert absolute["admitted"], "Missing admitted absolute-ratio control"
                value = row["value"]
                if value is None:
                    status = "unparsed-computed-value"
                else:
                    if form == "em-ratio":
                        parent_value, child_value = parent, child
                    elif form == "ch-ratio":
                        parent_value = row["metrics"]["parentCh"]
                        child_value = row["metrics"]["childCh"]
                    else:
                        parent_value = child_value = 20
                    boundary = (prop == "font-feature-settings" and form == "ch-ratio" and
                                any(abs(x % 1 - 0.5) < 0.001 for x in [parent_value, child_value]))
                    if prop == "font-feature-settings":
                        parent_value, child_value = int(parent_value + 0.5), int(child_value + 0.5)
                    p = abs(value - parent_value) <= 0.03
                    c = abs(value - child_value) <= 0.03
                    status = ("rounding-boundary" if boundary else "matches-both" if p and c else
                              "matches-parent" if p else "matches-child" if c else "matches-neither")
            first = rows[prop, tag, form, phase, "first"]
            stable = first["computed"] == row["computed"]
            outcomes.append({"property": prop, "tag": tag, "form": form, "phase": phase,
                             "status": status if stable else "unstable", "first": first["computed"],
                             "settled": row["computed"], "stable": stable,
                             "parent_alternative": parent_value, "child_alternative": child_value})
    return {"complete_identity_set": True, "observations": len(rows),
            "controls_validated": True, "outcomes": outcomes,
            "native_source_binding_verified": False, "accepted_bug_or_fix": False}


if __name__ == "__main__":
    print(json.dumps(assess(json.loads(Path(sys.argv[1]).read_text())), indent=2))
