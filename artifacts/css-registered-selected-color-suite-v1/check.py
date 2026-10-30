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
    for name, digest in read(HERE / 'REFERENCES.json').items():
        assert sha((ROOT / name).read_bytes()) == digest
    inputs = read(HERE / 'INPUTS.json')
    merged_resources, merged_roster = {}, {}
    manifests = []
    for binding in inputs['fixtures']:
        directory = ROOT / binding['directory']
        assert sha((directory / 'FILES.json').read_bytes()) == binding['manifest_sha256']
        for name, pin in read(directory / 'FILES.json').items():
            assert sha((directory / name).read_bytes()) == (pin['sha256'] if isinstance(pin, dict) else pin)
        roster = read(directory / 'ROSTER.json')
        assert not set(merged_roster) & set(roster)
        merged_roster.update(roster)
        manifest = read(directory / 'MANIFEST.json')
        manifests.append(manifest)
        for name in {**flatten(manifest['items']['testharness']), **flatten(manifest['items']['support'])}:
            path = directory / 'tests' / name
            pin = {'path': str(path.relative_to(ROOT)), 'sha256': sha(path.read_bytes())}
            if name in merged_resources:
                assert merged_resources[name]['sha256'] == pin['sha256']
            else:
                merged_resources[name] = pin
    assert inputs['roster'] == read(HERE / 'ROSTER.json') == merged_roster
    assert inputs['resources'] == merged_resources
    assert (sum(map(len, merged_roster.values())), len(merged_roster), len(merged_resources)) == (28,2,4)
    assert (inputs['callbacks'],inputs['page_endings'],inputs['signatures']) == (28,2,30)
    assert [len(read(ROOT / b['directory'] / 'ROSTER.json')[next(iter(read(ROOT / b['directory'] / 'ROSTER.json')))]) for b in inputs['fixtures']] == [5,23]
    manifest = read(HERE / 'MANIFEST.json')
    manifest_check(manifest, merged_roster, merged_resources)
    for source in manifests:
        for kind in ('support','testharness'):
            actual = flatten(manifest['items'][kind])
            assert all(actual[k] == v for k,v in flatten(source['items'][kind]).items())
    assert inputs['new_metadata_absences'] == ['testing/web-platform/meta'+page+'.ini' for page in merged_roster]
    for page in merged_roster:
        pin = inputs['metadata'][page.lstrip('/')+'.ini']
        assert pin == {'path':'testing/web-platform/meta'+page+'.ini','sha256':None}
    for name,pin in inputs['metadata'].items():
        if pin['sha256'] is not None:
            capture = inputs['metadata_captures'][name]
            assert sha((ROOT / capture['path']).read_bytes()) == capture['sha256'] == pin['sha256']
            old = read(ROOT / 'artifacts/css-animation-taint-clean-original-v4/POLICY.json')
            assert old['wpt']['metadata'][name] == pin
    assert inputs['expected_statuses'] is inputs['execution'] is inputs['current_state_binding'] is None
    print(json.dumps({'callbacks':28,'pages':2,'signatures':30,'resources':4,'exact_original5_preserved':True,'genuine_manifest_entries':True,'live_reads':False}))


if __name__ == '__main__':
    main()
