import hashlib
import json
from pathlib import Path

base=Path(__file__).resolve().parent
old=json.loads((base/'SOURCE-v1.json').read_text())
names=list(old['companion_hashes'])+['SOURCE-v1.json','Candidate.lean','Scaling.lean','Instances.lean',
    'check_v2.py','controls_v2.py','expectations_v2.py','materialize_v2.py','source_check_v2.py',
    'NATIVE-v2.json','mod-rem-before.rs','mod-rem-after.rs','clamp-before.rs','clamp-after-v2.rs',
    'README-v2.md','REVIEW-v2.md','SOURCE-COMMIT-v2.md','freeze_v2.py']
names=list(dict.fromkeys(names))
for name,expected in old['companion_hashes'].items():
    if hashlib.sha256((base/name).read_bytes()).hexdigest()!=expected:
        raise ValueError('Preserved preparation changed: '+name)
paths=[str((base/name).relative_to(base.parents[1])) for name in names+['SOURCE-v2.json','tooling-paths-v2.txt']]
(base/'tooling-paths-v2.txt').write_text('\n'.join(paths)+'\n')
names+=['tooling-paths-v2.txt']
manifest={'status':'complete candidate semantic model with explicit manual native bridge',
    'companion_hashes':{name:hashlib.sha256((base/name).read_bytes()).hexdigest() for name in names},
    'limits':'Arbitrary-tree control-flow preservation conditional on native conversion/type/comparison certificates; fully proved canonical/common-unit/fallback model instances; rational finite nonnegative basis semantics; no Rust extraction, IEEE rounding/overflow, general leaf conversion or CSS conformance proof'}
(base/'SOURCE-v2.json').write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n')
