import hashlib
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[1]
NAMES = ['ObjectFit.lean','bridge.py','bridge-prefix.cpp','bridge-suffix.cpp','check.py',
         'native-before.cpp','native-candidate.cpp','renderer.cpp','spec-css-images-3.html',
         'SPEC-v1.json','TOOLCHAIN-v1.json','README.md','prepare.py','tooling-paths-v1.txt']
if (BASE/'native-candidate.cpp').read_bytes() != (ROOT/'layout/base/nsLayoutUtils.cpp').read_bytes():
    raise ValueError('live candidate does not match archived candidate')
if (BASE/'renderer.cpp').read_bytes() != (ROOT/'layout/painting/nsImageRenderer.cpp').read_bytes():
    raise ValueError('live renderer does not match archived helper source')
paths = [BASE/name for name in NAMES]
source_paths = sorted(str(p.relative_to(ROOT)) for p in paths+[BASE/'SOURCE-v1.json'])
(BASE/'tooling-paths-v1.txt').write_text('\n'.join(source_paths)+'\n')
paths += [ROOT/'layout/base/nsLayoutUtils.cpp',ROOT/'layout/painting/nsImageRenderer.cpp']
manifest = {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
(BASE/'SOURCE-v1.json').write_text(json.dumps(manifest,indent=2)+'\n')
print('Prepared source identities; replay check.py in a fresh output directory.')
