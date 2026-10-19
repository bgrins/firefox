#!/usr/bin/env python3
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    seal = json.loads((ROOT / 'FREEZE.json').read_text())
    assert digest(ROOT / 'MANIFEST.json') == seal['manifest_sha256']
    manifest = json.loads((ROOT / 'MANIFEST.json').read_text())
    actual = {str(p.relative_to(ROOT)) for p in ROOT.rglob('*') if p.is_file()}
    assert actual == set(manifest) | {'MANIFEST.json', 'FREEZE.json'}
    for name, expected in manifest.items():
        path = ROOT / name
        assert not path.is_symlink() and path.resolve().is_relative_to(ROOT)
        assert digest(path) == expected, name
    pins = json.loads((ROOT / 'SOURCE-PINS.json').read_text())
    for name, expected in pins.items():
        assert digest(ROOT / 'evidence/source' / name) == expected
    raw = ROOT / 'evidence/source/artifacts/css-animation-taint-probe-v1/registered-values-initial-raw.json'
    rows = []
    for line in raw.read_text().splitlines():
        value = json.loads(line)
        if value.get('action') in ('test_status', 'test_end'):
            rows.append({k: value[k] for k in ('action', 'test', 'subtest', 'status', 'message') if k in value})
    assert rows == json.loads((ROOT / 'OBSERVATIONS.json').read_text())
    assert [r['status'] for r in rows] == ['PASS', 'FAIL', 'FAIL', 'FAIL', 'FAIL', 'PASS', 'OK']
    assert len({r['subtest'] for r in rows if 'subtest' in r}) == 6
    print(json.dumps({'authenticated_inputs': len(manifest), 'source_files': len(pins),
                      'subtests': 6, 'pass': 2, 'fail': 4, 'harness': 'OK',
                      'scope': 'retained source/spec audit and raw reconstruction; no native execution'}))


if __name__ == '__main__':
    main()
