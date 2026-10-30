import hashlib
import json
from pathlib import Path
import sys

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
read = lambda p: json.loads(p.read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()

def leaves(tree, prefix=''):
    for name, value in tree.items():
        path = prefix + name
        if isinstance(value, dict):
            yield from leaves(value, path + '/')
        else:
            yield path, value

inputs = read(HERE / 'INPUTS.json')
for name, claim in read(HERE / 'REFERENCES.json').items():
    path = ROOT / name
    assert path.stat().st_size == claim['bytes'] and sha(path) == claim['sha256']
for url, target in inputs['resources'].items():
    source = inputs['source_resources'][url]
    assert sha(ROOT / source['path']) == source['sha256'] == target['sha256'] == sha(ROOT / target['path'])
    assert (ROOT / source['path']).read_bytes() == (ROOT / target['path']).read_bytes()
urls, pages = set(), set()
for kind, folder, name in [('portable', 'tests', 'MANIFEST.json'), ('mozilla', 'mozilla/tests', 'MOZILLA-MANIFEST.json')]:
    manifest = read(HERE / name)
    assert sha(HERE / name) == inputs['manifests'][kind]['sha256']
    manifest_paths = set()
    for item_type, tree in manifest['items'].items():
        assert item_type in ('testharness', 'support')
        for relative, row in leaves(tree):
            body = (HERE / folder / relative).read_bytes()
            assert hashlib.sha1(b'blob ' + str(len(body)).encode() + b'\0' + body).hexdigest() == row[0]
            url = manifest['url_base'] + relative
            urls.add(url)
            manifest_paths.add(relative)
            if item_type == 'testharness':
                assert len(row) == 2 and row[1][0] is None
                pages.add(url)
    assert manifest_paths == {str(p.relative_to(HERE / folder)) for p in (HERE / folder).rglob('*') if p.is_file()}
assert urls == set(inputs['resources']) and len(urls) == 8
roster, lanes = read(HERE / 'ROSTER.json'), read(HERE / 'LANES.json')
assert pages == set(roster) and len(pages) == 6
assert sum(map(len, roster.values())) == 28
old_roster = read(ROOT / 'artifacts/css-prioritary-selection-suite-v3/ROSTER.json')
for page, names in roster.items():
    if 'overridden-line-height' in page:
        assert names == ['Registered line-height dependency: ' + n for n in ['no-loser', 'literal', 'overridden', 'active-cycle']]
    else:
        assert names == [n for n in old_roster[page] if n != 'Prioritary selection preservation: zoom-observation']
assert [(lanes[n]['callbacks'], lanes[n]['pages']) for n in ['ordinary', 'forced_colors', 'mozilla_appearance']] == [(20, 3), (2, 1), (6, 2)]
assert {p:names for lane in lanes.values() for p,names in lane['roster'].items()} == roster
for kind, folder in [('portable', 'meta'), ('mozilla', 'mozilla/meta')]:
    present = set()
    for name, claim in inputs['metadata'][kind].items():
        path = HERE / folder / name
        if claim['sha256'] is None:
            assert not path.exists() and not path.is_symlink()
        else:
            assert sha(path) == claim['sha256'] and 'expected:' not in path.read_text()
            present.add(name)
    assert present == {str(p.relative_to(HERE / folder)) for p in (HERE / folder).rglob('*') if p.is_file()}
assert inputs['execution'] is inputs['current_binding'] is inputs['baseline_outcomes'] is inputs['expected_statuses'] is None
assert inputs['fresh_original_required'] and inputs['capture_helper'] is None
assert not inputs['install_managed_resources'] and inputs['copy_resources'] == inputs['resources']
lint = read(HERE / 'LINT.json')
assert not lint['portable'] and len(lint['mozilla']) == 4
assert all(row[0] == 'SPECIALPOWERS API' for row in lint['mozilla'])
print(json.dumps({'callbacks': 28, 'pages': 6, 'signatures': 34, 'resources': 8, 'exact_source_copies': True, 'genuine_manifests': True, 'portable_lint_errors': 0, 'mozilla_only_privileged_API_findings': 4, 'baseline_outcomes': None, 'browser_run': False}))
