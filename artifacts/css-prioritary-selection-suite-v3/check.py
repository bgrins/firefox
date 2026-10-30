import copy
import difflib
import hashlib
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OLD = ROOT / 'artifacts/css-prioritary-selection-suite-v2'
MATCHED = ROOT / 'artifacts/css-prioritary-forced-color-matched-probe-v1'
PAGE = '/forced-colors-mode/registered-prioritary-forced-color-selection.tentative.html'
read = lambda p: json.loads(p.read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
pin = lambda p: {'path': str(p.relative_to(ROOT)), 'sha256': sha(p)}


def authenticate(directory, digest):
    assert sha(directory / 'FILES.json') == digest
    for name, record in read(directory / 'FILES.json').items():
        assert not Path(name).is_absolute() and '..' not in Path(name).parts
        path = directory / name
        assert not path.is_symlink() and path.stat().st_size == record['bytes']
        assert sha(path) == record['sha256'], name


def expected():
    authenticate(OLD, 'aea98dd5d55c3c5c2498950e69f30ed53ad0755be8c06b3c8850f380666e75bb')
    authenticate(MATCHED, '1d737d900c41bf53bb7414e62511f77c50f8161c19210681ea3e0471a3394a79')
    authenticate(ROOT / 'artifacts/css-prioritary-zoom-capture-v1', 'ed0ed2222d90e2e04437dc033bbcd4a62f6264f89a1135b82a10051e99da0de2')
    for record in read(HERE / 'REFERENCES.json'):
        assert sha(ROOT / record['path']) == record['sha256']
    old = read(OLD / 'INPUTS.json')
    matched = read(MATCHED / 'INPUTS.json')
    assert old['resources'][PAGE]['sha256'] == matched['replacement']['old']['sha256'] == '4814b1ca5a70de9cf158b20fae9509eb06782a6f6dbf6f2103111904c1f91c7d'
    assert matched['replacement']['new']['sha256'] == '43cb6d4e4beca7e463a9d0c40daf39cdbfc78a33834b6144cd33786707bd9ede'
    result = copy.deepcopy(old)
    result['packages'].update(predecessor77=str(OLD.relative_to(ROOT)), matched_forced=str(MATCHED.relative_to(ROOT)))
    record = pin(HERE / 'tests' / PAGE[1:])
    assert record['sha256'] == matched['replacement']['new']['sha256']
    result['resources'][PAGE] = record
    result['copy_resources'][PAGE] = record
    result['source_resources'][PAGE] = matched['replacement']['new']
    result['forced_color_replacement'] = {
        'url': PAGE, 'old': old['resources'][PAGE], 'new': record,
        'source': matched['replacement']['new'], 'callback_names_unchanged': True,
        'fresh_original_required': True, 'old_observations_not_identical_inputs': True,
    }
    manifest = read(OLD / 'MANIFEST.json')
    leaf = PAGE.rsplit('/', 1)[1]
    manifest['items']['testharness']['forced-colors-mode'][leaf] = read(MATCHED / 'MANIFEST.json')['items']['testharness']['forced-colors-mode'][leaf]
    return result, manifest


def leaves(node, prefix=()):
    for key, value in node.items():
        if isinstance(value, dict):
            yield from leaves(value, prefix + (key,))
        else:
            yield '/'.join(prefix + (key,)), value


def verify(inputs, manifest):
    expected_inputs, expected_manifest = expected()
    assert inputs == expected_inputs and manifest == expected_manifest
    for name in ['LANES.json', 'ROSTER.json', 'MOZILLA-MANIFEST.json', 'METADATA.json', 'METADATA-ADMISSION.json', 'METADATA-OVERLAYS.json']:
        assert (HERE / name).read_bytes() == (OLD / name).read_bytes(), name
    for tree in ['tests', 'meta', 'mozilla/tests', 'mozilla/meta']:
        assert {p.relative_to(HERE / tree) for p in (HERE / tree).rglob('*') if p.is_file()} == {
            p.relative_to(OLD / tree) for p in (OLD / tree).rglob('*') if p.is_file()
        }
        for original in (OLD / tree).rglob('*'):
            if original.is_file():
                rel = original.relative_to(OLD)
                target = HERE / rel
                source = ROOT / inputs['source_resources'][PAGE]['path'] if str(rel) == 'tests' + PAGE else original
                assert target.read_bytes() == source.read_bytes(), str(rel)
    for group in ['resources', 'source_resources']:
        for record in inputs[group].values():
            assert sha(ROOT / record['path']) == record['sha256']
    for lane in inputs['metadata'].values():
        for record in lane.values():
            if record['sha256'] is not None:
                assert sha(ROOT / record['path']) == record['sha256']
    urls = {'/' + str(p.relative_to(HERE / 'tests')) for p in (HERE / 'tests').rglob('*') if p.is_file()}
    urls |= {'/_mozilla/' + str(p.relative_to(HERE / 'mozilla/tests')) for p in (HERE / 'mozilla/tests').rglob('*') if p.is_file()}
    assert urls == set(inputs['resources']) and len(urls) == inputs['sealed_resource_count'] == 16
    assert set(inputs['copy_resources']) | set(inputs['install_managed_resources']) == urls
    assert not set(inputs['copy_resources']) & set(inputs['install_managed_resources'])
    assert len(inputs['copy_resources']) == 14 and len(inputs['install_managed_resources']) == 2
    roster = read(HERE / 'ROSTER.json')
    assert len(roster) == inputs['pages'] == 12
    assert sum(map(len, roster.values())) == inputs['callbacks'] == 77
    assert inputs['signatures'] == inputs['callbacks'] + inputs['pages'] == 89
    for page, names in read(MATCHED / 'ROSTER.json').items():
        assert roster[page] == names
    lanes = read(HERE / 'LANES.json')
    assert [(lanes[k]['callbacks'], lanes[k]['pages']) for k in ['ordinary', 'forced_colors', 'mozilla_appearance']] == [(68, 8), (3, 2), (6, 2)]
    manifest_urls = set()
    for body, directory in [(manifest, HERE / 'tests'), (read(HERE / 'MOZILLA-MANIFEST.json'), HERE / 'mozilla/tests')]:
        for kind, entries in body['items'].items():
            assert kind in ('testharness', 'support')
            for relative, record in leaves(entries):
                content = (directory / relative).read_bytes()
                assert hashlib.sha1(b'blob ' + str(len(content)).encode() + b'\0' + content).hexdigest() == record[0]
                manifest_urls.add(body['url_base'] + relative)
    assert manifest_urls == urls
    assert inputs['current_binding'] is None and inputs['execution'] is None and inputs['expected_statuses'] is None
    for name in ['INPUTS.json', 'MANIFEST.json']:
        delta = ''.join(difflib.unified_diff((OLD / name).read_text().splitlines(True), (HERE / name).read_text().splitlines(True), fromfile='suite-v2/' + name, tofile='suite-v3/' + name))
        assert (HERE / name.replace('.json', '-DELTA.patch')).read_text() == delta


if __name__ == '__main__':
    assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
    inputs, manifest = read(HERE / 'INPUTS.json'), read(HERE / 'MANIFEST.json')
    verify(inputs, manifest)
    mutations = [
        lambda i, m: i.update(callbacks=74),
        lambda i, m: i['resources'][PAGE].update(sha256='4814b1ca5a70de9cf158b20fae9509eb06782a6f6dbf6f2103111904c1f91c7d'),
        lambda i, m: i['forced_color_replacement'].update(fresh_original_required=False),
        lambda i, m: i['metadata']['portable']['forced-colors-mode/forced-colors-mode-51.html.ini'].update(sha256='wrong'),
        lambda i, m: i['capture_helper'].update(sha256='wrong'),
        lambda i, m: m['items']['testharness']['forced-colors-mode'][PAGE.rsplit('/', 1)[1]].__setitem__(0, 'wrong'),
    ]
    for mutate in mutations:
        changed, changed_manifest = copy.deepcopy(inputs), copy.deepcopy(manifest)
        mutate(changed, changed_manifest)
        try:
            verify(changed, changed_manifest)
        except (AssertionError, KeyError):
            pass
        else:
            raise AssertionError('invalid replacement accepted')
    print(json.dumps({'callbacks': 77, 'pages': 12, 'signatures': 89, 'resources': 16,
                      'sole_served_body_replacement': PAGE, 'negative_controls': len(mutations),
                      'fresh_original_required': True, 'live_operations': False}))
