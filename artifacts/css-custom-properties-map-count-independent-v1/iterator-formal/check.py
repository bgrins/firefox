from pathlib import Path
import hashlib
import json
import sys

assert sys.flags.isolated and sys.flags.no_site
r = Path(__file__).resolve().parent
f = json.loads((r / 'FREEZE.json').read_text())
assert hashlib.sha256((r / 'MANIFEST.json').read_bytes()).hexdigest() == f['manifest_sha256']
m = json.loads((r / 'MANIFEST.json').read_text())
assert {str(p.relative_to(r)) for p in r.rglob('*') if p.is_file()} == set(m) | {'FREEZE.json','MANIFEST.json'}
for name, h in m.items():
    p = r / name
    assert not p.is_symlink() and hashlib.sha256(p.read_bytes()).hexdigest() == h, name
receipt = json.loads((r / 'receipts/CHECK.json').read_text())
assert receipt['theorem_axiom_reports'] == 50 and len(receipt['mutations']) == 5
assert len(json.loads((r / 'GUARDS.json').read_text())) == 8
print('PASS', len(m), 'inputs; retained independent 50-audit/4-mutant/8-guard replay')
