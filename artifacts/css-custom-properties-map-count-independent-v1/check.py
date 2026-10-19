from pathlib import Path
import hashlib
import json
import subprocess
import sys

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
r = Path(__file__).resolve().parent
f = json.loads((r / 'FREEZE.json').read_text())
assert hashlib.sha256((r / 'MANIFEST.json').read_bytes()).hexdigest() == f['manifest_sha256']
m = json.loads((r / 'MANIFEST.json').read_text())
assert not any(p.is_symlink() for p in r.rglob('*'))
assert {str(p.relative_to(r)) for p in r.rglob('*') if p.is_file()} == set(m) | {'MANIFEST.json', 'FREEZE.json'}
for name, pin in m.items():
    assert hashlib.sha256((r / name).read_bytes()).hexdigest() == pin, name
for script, receipt in [('review_matrix39.py','MATRIX39-REVIEW.json'), ('review_matrix41.py','MATRIX41-REVIEW.json'), ('literal_witness.py','LITERAL-WITNESS.json')]:
    p = subprocess.run([sys.executable, '-I', '-S', str(r / script)], capture_output=True, text=True)
    assert p.returncode == 0, p.stderr
    assert json.loads(p.stdout) == json.loads((r / receipt).read_text()), script
for child in ['iterator-formal', 'count-formal']:
    p = subprocess.run([sys.executable, '-I', '-S', str(r / child / 'check.py')], capture_output=True, text=True)
    assert p.returncode == 0, p.stderr
print('PASS', len(m), 'inputs; native/source review, exact matrices, counterexample and both conditional proof review receipts')
