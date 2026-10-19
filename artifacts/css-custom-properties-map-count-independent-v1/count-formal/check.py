from pathlib import Path
import hashlib
import json
import sys

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
r = Path(__file__).resolve().parent
f = json.loads((r / 'FREEZE.json').read_text())
assert hashlib.sha256((r / 'MANIFEST.json').read_bytes()).hexdigest() == f['manifest_sha256']
m = json.loads((r / 'MANIFEST.json').read_text())
assert {str(p.relative_to(r)) for p in r.rglob('*') if p.is_file()} == set(m) | {'FREEZE.json','MANIFEST.json'}
for name, h in m.items():
    p = r / name
    assert not p.is_symlink() and hashlib.sha256(p.read_bytes()).hexdigest() == h, name
receipt = json.loads((r / 'receipts/RESULT.json').read_text())
assert receipt['audited_theorems'] == 55 and receipt['source_bindings'] == 48
assert len(receipt['mutations']) == 4
assert all(x['definition_compiled'] and x['semantic_rejection'] for x in receipt['mutations'])
print('PASS', len(m), 'inputs; retained independent 55-audit/4-mutant replay')
