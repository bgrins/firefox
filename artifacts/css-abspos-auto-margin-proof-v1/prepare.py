import hashlib
import json
from pathlib import Path

BASE=Path(__file__).resolve().parent
ROOT=BASE.parents[1]
NAMES=['Margins.lean','bridge.py','fixtures.py','bridge-prefix.cpp','bridge-suffix.cpp','check.py',
       'native-before.cpp','native-candidate.cpp','header-before.h','header-candidate.h','ReflowInput.cpp',
       'LayoutConstants.h','nsStyleStruct.h','spec-css-position-3.html','issue-11478.json',
       'issue-11478-comments.json','independent-design.md','SPEC-v1.json','TOOLCHAIN-v1.json',
       'README.md','prepare.py','tooling-paths-v1.txt']
live={'native-candidate.cpp':'layout/generic/AbsoluteContainingBlock.cpp',
      'header-candidate.h':'layout/generic/AbsoluteContainingBlock.h',
      'ReflowInput.cpp':'layout/generic/ReflowInput.cpp','LayoutConstants.h':'layout/base/LayoutConstants.h',
      'nsStyleStruct.h':'layout/style/nsStyleStruct.h'}
for archived,current in live.items():
    if (BASE/archived).read_bytes()!=(ROOT/current).read_bytes(): raise ValueError('live input mismatch '+current)
paths=[BASE/name for name in NAMES]
(BASE/'tooling-paths-v1.txt').write_text('\n'.join(sorted(str(p.relative_to(ROOT)) for p in paths+[BASE/'SOURCE-v1.json']))+'\n')
paths += [ROOT/name for name in live.values()]
manifest={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
(BASE/'SOURCE-v1.json').write_text(json.dumps(manifest,indent=2)+'\n')
print('Prepared source identities; replay check.py in a fresh output directory.')
