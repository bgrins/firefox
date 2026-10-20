import hashlib
import json
from pathlib import Path
import sys


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text())


def hunks(path):
    result = {}
    name = None
    old = new = None
    for line in path.read_text().splitlines(keepends=True):
        if line.startswith('--- '):
            name = line[4:].strip().removeprefix('a/')
        elif line.startswith('+++ '):
            name = line[4:].strip().removeprefix('b/')
            result.setdefault(name, [])
        elif line.startswith('@@ '):
            old, new = [], []
            result[name].append((old, new))
        elif old is not None and line[:1] in (' ', '-', '+'):
            if line[0] != '+': old.append(line[1:])
            if line[0] != '-': new.append(line[1:])
        elif line.startswith('diff --git '):
            old = new = None
    return {name: [(''.join(old), ''.join(new)) for old, new in pairs] for name, pairs in result.items()}


def run(repo, out):
    review = repo / 'artifacts/css-animation-invalid-publication-review-v1'
    final = repo / 'artifacts/css-animation-invalid-publication-final-v1'
    controls = repo / 'artifacts/css-animation-invalid-publication-controls-v1'
    source = repo / 'artifacts/css-animation-publication-reachability-v1'
    fix = repo / 'artifacts/css-animation-invalid-publication-fix-v1'
    test = 'testing/web-platform/tests/css/css-properties-values-api/animation-invalid-inherit-publication.html'
    receipt = read(controls / 'RUN.json')
    raw = [json.loads(line) for line in (controls / 'raw.json').read_text().splitlines()]
    assert receipt['complete'] and receipt['stable'] and receipt['exit'] == 0
    rows = [row for row in raw if row.get('action') == 'test_status']
    assert rows == receipt['rows'] and len(rows) == 22 and all(row['status'] == 'PASS' for row in rows)
    harness = [row for row in raw if row.get('action') == 'test_end']
    assert harness == receipt['harness'] and len(harness) == 1 and harness[0]['status'] == 'OK'
    assert len({(row['test'], row['subtest']) for row in rows}) == 22
    old_rows = read(repo / 'artifacts/css-animation-publication-runtime-v2/RUN.json')['rows']
    assert [(row['test'],row['subtest']) for row in rows[:16]] == [(row['test'],row['subtest']) for row in old_rows]
    landing = read(fix / 'LANDING-PINS.json')
    assert all(receipt['pins'][name] == pin for name, pin in landing.items())
    fixture_pin = sha(review / 'proposed-final-wpt.html')
    assert receipt['pins'][test] == fixture_pin == sha(final / 'landing.html')
    packaging = read(final / 'PACKAGING.json')
    native = hunks(final / 'native.patch')
    assert set(native) == set(landing)
    assert sha(final / 'native.patch') == sha(fix / 'native-only.patch')
    for label in ['head','standalone']:
        section = packaging[label]
        patch = repo / section['patch']
        assert sha(patch) == section['patch_sha256']
        packaged = hunks(patch)
        assert set(packaged) == set(native) | {test} == set(section['paths'])
        assert {name:packaged[name] for name in native} == native
        assert packaged[test] == [('', (final / 'landing.html').read_text())]
        for name,pin in section['pins'].items():
            target = final / 'landing.html' if name == test else final / label / Path(name).relative_to('servo/components/style')
            assert sha(target) == pin
    upstream_pins = {item['source']:item for item in read(source / 'UPSTREAM-PINS.json')}
    for name, pairs in native.items():
        item = upstream_pins[name]
        path = source / item['snapshot']
        assert sha(path) == item['sha256']
        text = path.read_text()
        for old,new in pairs:
            assert text.count(old) == 1
            text = text.replace(old,new,1)
        expected = final / 'standalone' / Path(name).relative_to('servo/components/style')
        assert text == expected.read_text()
    result = {'status':'PASS','final_fixture_sha256':fixture_pin,'final_runtime':{'PASS':22,'harness_OK':1},'original_paired_rows':16,'added_candidate_only_rows':6,'landing_native_pins':landing,'packaging_receipt_sha256':sha(final/'PACKAGING.json'),'controls_receipt_sha256':sha(controls/'RUN.json'),'controls_raw_sha256':sha(controls/'raw.json'),'standalone_exact_native_application_to_retained_upstream':True,'both_packaged_native_hunks_equal_reviewed_native_patch':True,'both_packages_exactly_three_native_plus_identical_WPT':True,'limits':['No isolated HEAD/upstream browser or build performed.','Six additional controls have candidate observations only.','HEAD/index preservation and reverse-apply are producer receipts, not independently executed Git operations.']}
    out.write_text(json.dumps(result,indent=2)+'\n')


if __name__ == '__main__':
    run(Path(sys.argv[1]).resolve(),Path(sys.argv[2]).resolve())
