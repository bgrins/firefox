import copy
import json
import subprocess
from corpus import case_for
from native_oracle import encode


def run_invalid(binary, output):
    base = case_for([65, 66], 1)
    base["glyphs"] = [[0x800A0041, []], [0x800A0042, []]]
    base["range"], base["runs"], base["spacing"] = [0, 2], [0], [[0, 0], [0, 0]]
    cases = []
    def add(name, mutate):
        case = copy.deepcopy(base)
        mutate(case)
        cases.append((name, case))
    add("range-overflow", lambda c: c.update(range=[0, 3]))
    add("range-reversed", lambda c: c.update(range=[2, 1]))
    add("invalid-direction", lambda c: c.update(direction=0))
    add("first-run-uncovered", lambda c: c.update(runs=[1]))
    add("duplicate-run-offset", lambda c: c.update(runs=[0, 0]))
    add("missing-font-runs", lambda c: c.update(runs=[]))
    add("latin1-out-of-range", lambda c: c.update(latin=True, text=[256, 65]))
    add("unit-out-of-range", lambda c: c.update(text=[65536, 65]))
    add("simple-with-details", lambda c: c["glyphs"].__setitem__(0, [0x800A0041, [[65, 10, 0, 0]]]))
    add("complex-count-mismatch", lambda c: c["glyphs"].__setitem__(0, [0x00010001, []]))
    add("first-not-cluster-start", lambda c: c["glyphs"].__setitem__(0, [0x00030000, []]))
    add("first-not-ligature-start", lambda c: c["glyphs"].__setitem__(0, [0x00050000, []]))
    add("pair-split-by-cluster", lambda c: c.update(text=[0xD800, 0xDC00]))
    def bad_spacing(c):
        c["glyphs"][1] = [0x00070000, []]
        c["spacing"][1] = [1, 0]
    add("spacing-inside-ligature", bad_spacing)
    results = []
    for name, case in cases:
        result = subprocess.run([str(binary)], input=encode(case), text=True, capture_output=True)
        assert result.returncode == 2, (name, result.returncode, result.stderr)
        assert not result.stderr, name
        results.append({"name": name, "raw_input": case, "status": "diagnostic rejection, not a semantic mutation witness", "exit": result.returncode})
    output.write_text(json.dumps(results, indent=2) + "\n")
    return results
