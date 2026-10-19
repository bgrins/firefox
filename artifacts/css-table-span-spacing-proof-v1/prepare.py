import hashlib
import json
from pathlib import Path

import bridge

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[1]
FILES = ['SpanSpacing.lean', 'bridge.py', 'bridge-prefix.cpp', 'bridge-suffix.cpp',
         'candidate.inc', 'original.inc', 'allocation.inc', 'accumulation.inc',
         'check.py', 'prepare.py', 'README.md', 'BINDING-v1.json', 'TOOLCHAIN-v1.json',
         'css22-tables.html', 'SPEC-v1.json', 'tooling-paths-v1.txt']
bridge.validate((ROOT / bridge.BINDING['native_path']).read_text())
paths = [BASE / name for name in FILES]
(BASE / 'tooling-paths-v1.txt').write_text('\n'.join(sorted(
    str(p.relative_to(ROOT)) for p in paths + [BASE / 'SOURCE-v1.json'])) + '\n')
paths += [ROOT / bridge.BINDING[key] for key in ['native_path', 'nscoord_path']]
manifest = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
(BASE / 'SOURCE-v1.json').write_text(json.dumps(manifest, indent=2) + '\n')
print('Prepared. Replay check.py into a new directory; do not prepare a frozen package again.')
