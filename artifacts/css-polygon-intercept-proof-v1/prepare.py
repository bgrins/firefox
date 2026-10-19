import hashlib
import json
from pathlib import Path

import bridge

BASE=Path(__file__).resolve().parent
ROOT=BASE.parents[1]
FILES=['Interpolation.lean','bridge.py','prefix.cpp','suffix.cpp','candidate.inc','original.inc',
       'helper.inc','BINDING-v1.json','DOMAIN-SOURCES-v1.json','TOOLCHAIN-v1.json','SPEC-v1.json',
       'css-shapes-1.html','check.py','prepare.py','README.md','tooling-paths-v1.txt']
bridge.validate((ROOT/bridge.BINDING['native_path']).read_text())
paths=[BASE/name for name in FILES]
(BASE/'tooling-paths-v1.txt').write_text('\n'.join(sorted(str(p.relative_to(ROOT))
    for p in paths+[BASE/'SOURCE-v1.json']))+'\n')
domain=json.loads((BASE/'DOMAIN-SOURCES-v1.json').read_text())
for name,expected in domain.items():
    if hashlib.sha256((ROOT/name).read_bytes()).hexdigest()!=expected:
        raise ValueError('domain-source drift: '+name)
paths += [ROOT/name for name in domain]
paths += [ROOT/bridge.BINDING[key] for key in ['native_path','helper_path']]
manifest={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
(BASE/'SOURCE-v1.json').write_text(json.dumps(manifest,indent=2)+'\n')
print('Prepared identities. Run check.py into a fresh directory.')
