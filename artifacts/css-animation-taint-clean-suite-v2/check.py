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
    for name, digest in read(HERE / "REFERENCES.json").items():
        assert sha((ROOT / name).read_bytes()) == digest, name
    inputs = read(HERE / "INPUTS.json")
    for key in ("previous_suite", "new_fixture"):
        binding = inputs[key]
        directory = ROOT / binding["directory"]
        assert sha((directory / "FILES.json").read_bytes()) == binding["manifest_sha256"]
        for name, pin in read(directory / "FILES.json").items():
            assert sha((directory / name).read_bytes()) == (pin["sha256"] if isinstance(pin, dict) else pin)
    old_directory = ROOT / inputs["previous_suite"]["directory"]
    old = read(old_directory / "INPUTS.json")
    new = ROOT / inputs["new_fixture"]["directory"]
    added = read(new / "ROSTER.json")
    roster = read(HERE / "ROSTER.json")
    assert not set(old["roster"]) & set(added)
    assert roster == inputs["roster"] == {**old["roster"], **added}
    assert (sum(map(len, roster.values())), len(roster), inputs["signatures"], len(inputs["resources"])) == (125, 18, 143, 22)
    assert inputs["callbacks"] == 125 and inputs["page_endings"] == 18
    assert all(inputs["resources"][k] == v for k, v in old["resources"].items())
    assert all(inputs["metadata"][k] == v for k, v in old["metadata"].items())
    new_name = next(iter(added)).lstrip("/")
    assert set(inputs["resources"]) - set(old["resources"]) == {new_name}
    assert set(inputs["metadata"]) - set(old["metadata"]) == {new_name + ".ini"}
    assert inputs["metadata"][new_name + ".ini"]["sha256"] is None
    assert inputs["new_metadata_absence"] == "testing/web-platform/meta/" + new_name + ".ini"
    assert (ROOT / inputs["resources"][new_name]["path"]).read_bytes() == (new / "tests" / new_name).read_bytes()
    for name, record in read(new / "INPUTS.json")["resources"].items():
        assert sha((ROOT / record["path"]).read_bytes()) == inputs["resources"][name]["sha256"]
    manifest = read(HERE / "MANIFEST.json")
    manifest_check(manifest, roster, inputs["resources"])
    for source in (read(old_directory / "MANIFEST.json"), read(new / "MANIFEST.json")):
        for kind in ("support", "testharness"):
            merged = flatten(manifest["items"][kind])
            assert all(merged[k] == v for k, v in flatten(source["items"][kind]).items())
    assert inputs["expected_statuses"] is inputs["execution"] is inputs["current_state_binding"] is None
    print(json.dumps({"callbacks": 125, "pages": 18, "signatures": 143, "resources": 22, "original123_exact_subset": True, "genuine_manifest_entries_preserved": True, "live_reads": False}))


if __name__ == "__main__":
    main()
