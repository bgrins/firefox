import hashlib
import json
from pathlib import Path

base = Path(__file__).resolve().parent
names = ['Clamp.lean', 'check.py', 'controls.py', 'diagnostics.py', 'expectations.py',
         'freeze.py', 'README.md', 'REVIEW.md', 'SPEC-v1.json', 'comparison-functions.html',
         'values4-calc-ieee.txt', 'values4-calc-simplification.txt']
manifest = {
    'status': 'semantic proof preparation; native bridge deferred',
    'companion_hashes': {name: hashlib.sha256((base / name).read_bytes()).hexdigest() for name in names},
    'limits': 'Exact rational exceptional-number model; canonical AST preservation and separate finite nonnegative unit-scaling rewrite; no Rust extraction, IEEE rounding/overflow, mixed-unit certificate derivation, native binding, browser verification, or full CSS proof',
}
(base / 'SOURCE-v1.json').write_text(json.dumps(manifest, indent=2, sort_keys=True) + '\n')
