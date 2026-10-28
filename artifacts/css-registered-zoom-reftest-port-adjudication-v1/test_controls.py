import copy
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("adjudication", HERE / "replay.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
root = HERE.parents[1]
cap = root / "artifacts/css-registered-zoom-standalone-wpt-v2"
experiment = m.read(cap / "EXPERIMENT.json")
declared = m.references(m.read(cap / "SUBSET-MANIFEST.json"), experiment)
original = m.read(root / "artifacts/css-registered-zoom-standalone-wpt-runtime-original-1/ASSESSMENT.json")
candidate = m.read(root / "artifacts/css-registered-zoom-standalone-wpt-runtime-candidate-1/ASSESSMENT.json")
left, right, records = m.normalize_pair(original, candidate, declared)
assert original != left and candidate != right and len(records) == 6
for old, new in ((original, left), (candidate, right)):
    expected = copy.deepcopy(old)
    for event in expected["ends"]:
        if event["test"] in declared:
            event["message"] = m.canonical_message(event, declared)[0]
    assert new == expected
rejected = []
for test in declared:
    event = next(e for e in candidate["ends"] if e["test"] == test)
    mutations = {
        "wrong test URL": lambda e:e.update(message=e["message"].replace(test, test+"extra", 1)),
        "wrong reference path": lambda e:e.update(message=e["message"].replace(declared[test][0]+"\n", declared[test][0]+"extra\n")),
        "wrong host": lambda e:e.update(message=e["message"].replace("web-platform.test", "other.test", 1)),
        "wrong operator": lambda e:e.update(message=e["message"].replace(" == ", " != ")),
        "wrong scheme": lambda e:e.update(message=e["message"].replace("http:", "https:", 1)),
        "port zero": lambda e:e.update(message=e["message"].replace(":62607", ":0")),
        "port overflow": lambda e:e.update(message=e["message"].replace(":62607", ":65536")),
        "ports differ": lambda e:e.update(message=e["message"].replace(":62607", ":62608", 1)),
        "extra text": lambda e:e.update(message=e["message"]+"ignored"),
        "missing newline": lambda e:e.update(message=e["message"].rstrip("\n")),
        "FAIL status": lambda e:e.update(status="FAIL"),
        "wrong action": lambda e:e.update(action="test_status"),
        "subtest field": lambda e:e.update(subtest="ignored"),
        "expected addition": lambda e:e.update(expected="PASS"),
        "intermittent drift": lambda e:e.update(known_intermittent=["FAIL"]),
        "unknown identity": lambda e:e.update(test="/unknown.html"),
    }
    for name, mutate in mutations.items():
        bad = copy.deepcopy(event)
        mutate(bad)
        try:
            m.canonical_message(bad, declared)
        except ValueError:
            rejected.append(test+": "+name)
        else:
            raise AssertionError(name)
    for name in ("missing completion", "duplicate completion"):
        bad = copy.deepcopy(candidate)
        if name.startswith("missing"):
            bad["ends"] = [e for e in bad["ends"] if e["test"] != test]
        else:
            bad["ends"].append(copy.deepcopy(event))
        try:
            m.normalize_pair(original, bad, declared)
        except ValueError:
            rejected.append(test+": "+name)
        else:
            raise AssertionError(name)
print(json.dumps({"positive_controls":["six actual port pairs accepted", "exactly six message fields change per copy"],
                  "negative_controls":rejected,"rejected_count":len(rejected),
                  "browser_executed":False,"runtime_edited":False}, indent=2))
