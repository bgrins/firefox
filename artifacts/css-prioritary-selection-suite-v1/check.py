import copy
import hashlib
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PACKAGES = {
    'original45': 'artifacts/css-registered-selected-color-suite-v3',
    'overridden9': 'artifacts/css-registered-overridden-color-scheme-probe-v1',
    'supplement20': 'artifacts/css-prioritary-selection-preservation-probe-v1',
    'capture': 'artifacts/css-prioritary-zoom-capture-v1',
}
PAGE = '/css/css-properties-values-api/registered-prioritary-selection.tentative.html'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pin(path):
    return {'path': str(path.relative_to(ROOT)), 'sha256': sha(path)}


def read(path):
    return json.loads(path.read_bytes())


def write(name, value):
    (HERE / name).write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')


def authenticate():
    references = read(HERE / 'REFERENCES.json')
    for entry in references:
        assert sha(ROOT / entry['path']) == entry['sha256']
    for folder in PACKAGES.values():
        directory = ROOT / folder
        for name, entry in read(directory / 'FILES.json').items():
            assert sha(directory / name) == entry['sha256']
    return references


def assemble():
    references = authenticate()
    old = read(ROOT / PACKAGES['original45'] / 'INPUTS.json')
    nine = read(ROOT / PACKAGES['overridden9'] / 'INPUTS.json')
    supplement = read(ROOT / PACKAGES['supplement20'] / 'INPUTS.json')
    sources = {'/' + k: v for k, v in old['resources'].items()}
    for values in [nine['resources'], supplement['resources']]:
        for url, value in values.items():
            if url in sources:
                assert value['sha256'] == sources[url]['sha256']
            else:
                sources[url] = value
    original_page = copy.deepcopy(sources[PAGE])
    sources[PAGE] = pin(ROOT / PACKAGES['capture'] / 'candidate.html')
    for name in ['record.js', 'receive.py']:
        sources['/__research__/zoom/' + name] = pin(ROOT / PACKAGES['capture'] / name)
    assert len(sources) == 15
    resources = {}
    for url, source in sources.items():
        assert sha(ROOT / source['path']) == source['sha256']
        target = HERE / ('mozilla/tests/' + url[len('/_mozilla/'):] if url.startswith('/_mozilla/') else 'tests/' + url[1:])
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists():
            assert target.read_bytes() == (ROOT / source['path']).read_bytes()
        else:
            target.write_bytes((ROOT / source['path']).read_bytes())
        resources[url] = pin(target)
    actual_urls = {'/' + str(q.relative_to(HERE / 'tests')) for q in (HERE / 'tests').rglob('*') if q.is_file()}
    actual_urls |= {'/_mozilla/' + str(q.relative_to(HERE / 'mozilla/tests')) for q in (HERE / 'mozilla/tests').rglob('*') if q.is_file()}
    assert actual_urls == set(resources)
    assert '/__research__/zoom/CONFIG.json' not in actual_urls
    roster = copy.deepcopy(old['roster'])
    for folder in ['overridden9', 'supplement20']:
        entries = read(ROOT / PACKAGES[folder] / 'ROSTER.json')
        assert not set(roster) & set(entries)
        roster.update(entries)
    assert len(roster) == 11 and sum(map(len, roster.values())) == 74
    lanes = {}
    for lane in ['ordinary', 'forced_colors', 'mozilla_appearance']:
        selected = {page: names for page, names in roster.items()
                    if ('mozilla_appearance' if page.startswith('/_mozilla/') else
                        'forced_colors' if page.startswith('/forced-colors-mode/') else 'ordinary') == lane}
        lanes[lane] = {'roster': selected, 'callbacks': sum(map(len, selected.values())), 'pages': len(selected)}
    assert [(v['callbacks'], v['pages']) for v in lanes.values()] == [(68, 8), (3, 2), (3, 1)]
    metadata = {'portable': copy.deepcopy(old['metadata']), 'mozilla': {}}
    for name, entry in old['metadata_captures'].items():
        assert sha(ROOT / entry['path']) == metadata['portable'][name]['sha256']
    admission = {v['path']: {'sha256': v['sha256'], 'source': 'historical original45 descriptor'}
                 for v in old['metadata'].values() if v['sha256'] is None}
    admission[nine['metadata_absence_requires_future_owner_check']] = {'sha256': None, 'source': 'historical overridden9 descriptor'}
    captured = ROOT / 'artifacts/css-priority-suite-metadata-source-v1'
    for entry in read(captured / 'SOURCE.json')['paths']:
        original = entry['path']
        lane = 'mozilla' if '/mozilla/meta/' in original else 'portable'
        name = original.split('/meta/', 1)[1]
        admission[original] = dict(entry, source='root 1d7680/0 saved current/HEAD capture')
        if entry['absent']:
            assert entry['sha256'] is None and entry['absent_at_head']
            value = {'path': original, 'sha256': None}
        else:
            assert entry['committed_bytes_match'] and sha(captured / original) == entry['sha256']
            value = pin(captured / original)
        if name in metadata[lane]:
            assert metadata[lane][name]['sha256'] == value['sha256']
        metadata[lane][name] = value
    overlays = {}
    for source in supplement['metadata']:
        relative = source['path'].split('/meta/', 1)[1]
        lane = 'mozilla' if '/mozilla/meta/' in source['path'] else 'portable'
        if relative in metadata[lane] and metadata[lane][relative]['sha256'] != source['sha256']:
            assert lane == 'mozilla' and relative == 'css/css-cascade/prioritary-appearance-selection.html.ini'
            assert metadata[lane][relative]['sha256'] is None
            overlays[lane + '/' + relative] = {'captured_absent': metadata[lane][relative], 'runtime_overlay': source}
        metadata[lane][relative] = source
    for lane, entries in metadata.items():
        for name, entry in entries.items():
            if entry['sha256'] is None:
                continue
            assert sha(ROOT / entry['path']) == entry['sha256']
            target = HERE / ('mozilla/meta' if lane == 'mozilla' else 'meta') / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes((ROOT / entry['path']).read_bytes())
            entries[name] = pin(target)
    write('METADATA.json', metadata)
    write('METADATA-ADMISSION.json', admission)
    write('METADATA-OVERLAYS.json', overlays)
    write('ROSTER.json', roster)
    write('LANES.json', lanes)
    inputs = {'packages': PACKAGES, 'callbacks': 74, 'pages': 11, 'signatures': 85,
              'sealed_resource_count': 15, 'resources': resources, 'source_resources': sources,
              'copy_resources': {k:v for k,v in resources.items() if not k.startswith('/__research__/zoom/')},
              'install_managed_resource_pins': {k:v for k,v in resources.items() if k.startswith('/__research__/zoom/')},
              'metadata': metadata, 'original45_metadata': old['metadata'],
              'metadata_admission': admission, 'metadata_overlays': overlays,
              'sole_page_replacement': {'page': PAGE, 'before': original_page, 'after': sources[PAGE]},
              'install_managed_resources': ['/__research__/zoom/record.js', '/__research__/zoom/receive.py'],
              'runtime_generated_not_presealed': ['/__research__/zoom/CONFIG.json', '/__research__/zoom/REQUEST.json', '/__research__/zoom/ERRORS.jsonl'],
              'capture_helper': pin(ROOT / PACKAGES['capture'] / 'capture.py'),
              'current_binding': None, 'expected_statuses': None, 'execution': None}
    write('INPUTS.json', inputs)
    return inputs, roster, references


def manifests(roster):
    wpt = ROOT / 'testing/web-platform/tests'
    sys.path[:0] = [str(p) for p in (wpt / 'tools/third_party').iterdir() if p.is_dir()] + [str(wpt / 'tools'), str(wpt)]
    from manifest.manifest import Manifest
    for folder, url, output in [('tests', '/', 'MANIFEST.json'), ('mozilla/tests', '/_mozilla/', 'MOZILLA-MANIFEST.json')]:
        tests = HERE / folder
        manifest = Manifest(str(tests), url)
        manifest.update([(str(p.relative_to(tests)), None, True) for p in tests.rglob('*') if p.is_file()], parallel=False)
        body = manifest.to_json()
        write(output, body)
        count = 0
        for page in roster:
            if page.startswith('/_mozilla/') != (url == '/_mozilla/'):
                continue
            node = body['items']['testharness']
            relative = page[len(url):]
            for part in relative.split('/'):
                node = node[part]
            assert node[0] == hashlib.sha1(b'blob ' + str((tests / relative).stat().st_size).encode() + b'\0' + (tests / relative).read_bytes()).hexdigest()
            count += 1
        assert count == (1 if url == '/_mozilla/' else 10)


if __name__ == '__main__':
    inputs, roster, refs = assemble()
    manifests(roster)
    write('CHECK.json', {'references': len(refs), 'source_closures_authenticated': 4,
                        'callbacks': 74, 'pages': 11, 'signatures': 85, 'sealed_resources': 15,
                        'genuine_manifests': 2, 'original45_unchanged': True,
                        'overridden9_unchanged': True, 'supplement20_sole_zoom_page_replacement': True,
                        'runtime_CONFIG_presealed': False, 'browser_execution': False})
    print(json.dumps(read(HERE / 'CHECK.json')))
