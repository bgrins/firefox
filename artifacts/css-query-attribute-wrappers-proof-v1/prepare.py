import hashlib
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[1]
NAMES = ['Query.lean', 'bridge.py', 'bridge-prefix.rs', 'bridge-suffix.rs', 'check.py',
         'condition-before.rs', 'condition-candidate.rs', 'TOOLCHAIN-v1.json', 'README.md',
         'prepare.py', 'tooling-paths-v1.txt']
paths = [BASE / name for name in NAMES]
sources = sorted(str(p.relative_to(ROOT)) for p in paths + [BASE / 'SOURCE-v1.json'])
(BASE / 'tooling-paths-v1.txt').write_text('\n'.join(sources) + '\n')
paths.append(ROOT / 'servo/components/style/queries/condition.rs')
manifest = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
(BASE / 'SOURCE-v1.json').write_text(json.dumps(manifest, indent=2) + '\n')
print('Prepared source identities; run check.py into a fresh output directory.')
