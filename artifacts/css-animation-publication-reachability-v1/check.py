import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parent
manifest = json.loads((root / 'FILES.json').read_text())
actual = {p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file()}
assert actual == set(manifest) | {'FILES.json'}
assert not any(p.is_symlink() for p in root.rglob('*'))
for name, expected in manifest.items():
    assert hashlib.sha256((root / name).read_bytes()).hexdigest() == expected, name
for inventory in ['SOURCE-PINS.json', 'UPSTREAM-PINS.json']:
    for row in json.loads((root / inventory).read_text()):
        assert hashlib.sha256((root / row['snapshot']).read_bytes()).hexdigest() == row['sha256']
for row in json.loads((root / 'SPEC-PINS.json').read_text()):
    assert hashlib.sha256((root / row['path']).read_bytes()).hexdigest() == row['sha256']
    assert all(row['anchors'].values())

receipt = json.loads((root / 'runtime/RUN.json').read_text())
assert receipt['phase'] == 'done' and receipt['exit'] == 1 and receipt['stable'] is True
events = [json.loads(line) for line in (root / 'runtime/raw.json').read_text().splitlines()]
rows = [row for row in events if row.get('action') == 'test_status']
kinds = ['constant inherit', 'inherit first', 'inherit last', 'neutral first',
         'neutral last', 'initial control', 'valid parent control',
         'unresolved declaration control']
expected = [(f'{kind}; inherits={inherits}', 'FAIL' if i < 5 else 'PASS')
            for inherits in ['false', 'true'] for i, kind in enumerate(kinds)]
assert [(row['subtest'], row['status']) for row in rows] == expected
for row in rows:
    if row['status'] == 'FAIL':
        assert 'sampled value, fallback alias and width' in row['message']
        assert 'expected array ["", "61px", "61px"] got ["20px", "20px", "20px"]' in row['message']
assert [row['status'] for row in events if row.get('action') == 'test_end'] == ['OK']
probe_hash = hashlib.sha256((root / 'probe.html').read_bytes()).hexdigest()
assert probe_hash in receipt['pins'].values()
assert (root / 'probe-v2.html').read_text() == (root / 'probe.html').read_text().replace(
    'element.style.setProperty(name, "inherit");',
    'element.style.setProperty(name, validParent ? "33px" : "var(--publication-missing)");'
).replace('"direct inherit reference"', '"direct guaranteed-invalid or valid reference"')
print(json.dumps({'integrity': 'PASS', 'baseline': {'FAIL': 10, 'PASS': 6, 'harness': 'OK'},
                  'v2': 'source-only revised diagnostic; separate root runtime gate',
                  'scope': 'retained evidence verification, not native or formal replay'}, indent=2))
