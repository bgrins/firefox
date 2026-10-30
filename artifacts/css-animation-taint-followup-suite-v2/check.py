import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
read = lambda path: json.loads(path.read_bytes())
sha = lambda body: hashlib.sha256(body).hexdigest()


def flatten(node, prefix=""):
    result = {}
    for name, value in node.items():
        path = prefix + name
        if isinstance(value, dict):
            result.update(flatten(value, path + "/"))
        else:
            result[path] = value
    return result


def manifest_check(manifest, roster, resources):
    assert manifest["version"] == 9 and manifest["url_base"] == "/"
    tests = flatten(manifest["items"]["testharness"])
    support = flatten(manifest["items"]["support"])
    assert {"/" + name for name in tests} == set(roster)
    assert set(tests).isdisjoint(support)
    assert set(tests) | set(support) == {name for name in resources if not name.endswith(".headers")}
    for name, entry in {**tests, **support}.items():
        pin = resources[name]
        body = (ROOT / pin["path"]).read_bytes()
        assert sha(body) == pin["sha256"]
        assert hashlib.sha1(b"blob " + str(len(body)).encode() + b"\0" + body).hexdigest() == entry[0]
        assert entry[1:] == ([[None, {}]] if name in tests else [[]])


def main():
    for name, expected in read(HERE / "REFERENCES.json").items():
        assert sha((ROOT / name).read_bytes()) == expected, name
    source_names = ["css-animation-taint-followup-suite-v1",
                    "css-animation-taint-registered-scope-v2",
                    "css-animation-taint-active-value-original-v1"]
    for name in source_names:
        directory = ROOT / "artifacts" / name
        for name, pin in read(directory / "FILES.json").items():
            assert sha((directory / name).read_bytes()) == (pin["sha256"] if isinstance(pin, dict) else pin)
    inputs = read(HERE / "INPUTS.json")
    roster = read(HERE / "ROSTER.json")
    assert inputs["roster"] == roster and set(inputs["pages"]) == set(roster)
    assert (sum(map(len, roster.values())), len(roster), inputs["signatures"], len(inputs["resources"])) == (14, 4, 18, 6)
    for name, paths in read(HERE / "RESOURCE-SOURCES.json").items():
        body = (HERE / "tests" / name).read_bytes()
        assert all((ROOT / path).read_bytes() == body for path in paths)
    manifest_check(read(HERE / "MANIFEST.json"), roster, inputs["resources"])
    prior = ROOT / "artifacts/css-animation-taint-followup-suite-v1"
    registered = ROOT / "artifacts/css-animation-taint-registered-scope-v2"
    assert roster == {**read(prior / "ROSTER.json"), **read(registered / "ROSTER.json")}
    for source in [prior, registered]:
        source_manifest = read(source / "MANIFEST.json")
        for kind in ["support", "testharness"]:
            entries = flatten(source_manifest["items"][kind])
            merged = flatten(read(HERE / "MANIFEST.json")["items"][kind])
            assert all(merged[name] == entry for name, entry in entries.items())
    assert inputs["baseline_execution"] is None

    old = ROOT / "artifacts/css-animation-taint-active-value-original-v1"
    old_roster = read(old / "ROSTER.json")
    policy = read(old / "POLICY.json")["wpt"]
    union = read(HERE / "UNION.json")
    union_roster = read(HERE / "UNION-ROSTER.json")
    assert not set(old_roster) & set(roster)
    assert union_roster == {**old_roster, **roster}
    assert (sum(map(len, union_roster.values())), len(union_roster), union["signatures"], len(union["resources"])) == (120, 16, 136, 20)
    assert all(union["resources"][name] == pin for name, pin in policy["resources"].items())
    assert union["metadata_for_future_local_owner"] == policy["metadata"]
    assert union["expected_statuses"] is None and union["execution"] is None
    assert inputs["current_state_binding"] is None and union["current_state_binding"] is None
    manifest_check(read(HERE / "UNION-MANIFEST.json"), union_roster, union["resources"])
    for names in union_roster.values():
        assert len(names) == len(set(names))
    print(json.dumps({"followup": [14, 4, 18, 6], "union": [120, 16, 136, 20],
                      "references": len(read(HERE / "REFERENCES.json")),
                      "prior_statuses_reinterpreted": False, "executed": False}))


if __name__ == "__main__":
    main()
