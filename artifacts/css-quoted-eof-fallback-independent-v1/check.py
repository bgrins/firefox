#!/usr/bin/env python3
import hashlib
import json
from pathlib import Path

r = Path(__file__).resolve().parent
h = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
f = json.loads((r / 'FREEZE.json').read_text())
assert h(r / 'MANIFEST.json') == f['manifest_sha256']
m = json.loads((r / 'MANIFEST.json').read_text())
for name, digest in m.items():
    p = r / name
    assert p.is_file() and not p.is_symlink() and h(p) == digest, name
for name in ['evidence', 'evidence/semantics']:
    d = r / name
    receipt = json.loads((d / 'browser-result.json').read_text())
    assert h(d / 'browser-raw.jsonl') == receipt['raw_sha256']
    assert h(d / 'browser-console.log') == receipt['console_sha256']
    assert receipt['stable_pins']
rows = json.loads((r / 'evidence/semantics/browser-result.json').read_text())['rows']
assert sum(x.get('status') == 'FAIL' for x in rows) == 8
assert sum(x.get('status') == 'PASS' for x in rows) == 14
assert 'byte index 25 is out of bounds' in (r / 'evidence/browser-console.log').read_text()
print(json.dumps({'authenticated': len(m), 'root_crash': True, 'semantic_failures': 8, 'semantic_controls': 14, 'review_scope': 'independent source/oracle adjudication; no native patch acceptance'}))
