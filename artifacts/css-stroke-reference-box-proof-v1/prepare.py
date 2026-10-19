import hashlib
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[1]
NAMES = ['ReferenceBox.lean','bridge.py','bridge-prefix.cpp','bridge-suffix.cpp','check.py',
         'native-before.cpp','native-candidate.cpp','native-header.h','spec-css-transforms-1.html',
         'SPEC-v1.json','TOOLCHAIN-v1.json','README.md','prepare.py','tooling-paths-v1.txt']
paths = [BASE/name for name in NAMES]
source_paths = sorted(str(p.relative_to(ROOT)) for p in paths+[BASE/'SOURCE-v1.json'])
(BASE/'tooling-paths-v1.txt').write_text('\n'.join(source_paths)+'\n')
paths += [ROOT/'layout/style/nsStyleTransformMatrix.cpp', ROOT/'layout/style/nsStyleTransformMatrix.h']
manifest = {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
(BASE/'SOURCE-v1.json').write_text(json.dumps(manifest,indent=2)+'\n')
print('Prepared source identities; replay check.py in a fresh output directory.')
