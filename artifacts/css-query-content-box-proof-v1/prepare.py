import hashlib
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[1]
FILES = ['ContentSize.lean', 'bridge.py', 'bridge-prefix.cpp', 'bridge-suffix.cpp',
         'mask-prefix.rs', 'mask-suffix.rs', 'check.py', 'prepare.py', 'README.md',
         'TOOLCHAIN-v1.json', 'tooling-paths-v1.txt', 'before-nsPresContext.cpp',
         'candidate-nsPresContext.cpp', 'native-GeckoBindings.cpp', 'native-nsStyleStruct.cpp',
         'native-nsStyleStruct.h', 'native-wrapper.rs', 'native-container_rule.rs',
         'native-feature.rs', 'native-box.rs', 'native-nsIFrame.cpp',
         'css-conditional-5.html', 'css-cascade-5.html', 'SPEC-SOURCES-v1.json']
LIVE = {'candidate-nsPresContext.cpp': 'layout/base/nsPresContext.cpp',
        'native-GeckoBindings.cpp': 'layout/style/GeckoBindings.cpp',
        'native-nsStyleStruct.cpp': 'layout/style/nsStyleStruct.cpp',
        'native-nsStyleStruct.h': 'layout/style/nsStyleStruct.h',
        'native-wrapper.rs': 'servo/components/style/gecko/wrapper.rs',
        'native-container_rule.rs': 'servo/components/style/stylesheets/container_rule.rs',
        'native-feature.rs': 'servo/components/style/queries/feature.rs',
        'native-box.rs': 'servo/components/style/values/specified/box.rs',
        'native-nsIFrame.cpp': 'layout/generic/nsIFrame.cpp'}
for archive, live in LIVE.items():
    if (BASE / archive).read_bytes() != (ROOT / live).read_bytes():
        raise ValueError('archived source drift: ' + live)
paths = [BASE / name for name in FILES]
source_paths = sorted(str(p.relative_to(ROOT)) for p in paths + [BASE / 'SOURCE-v1.json'])
(BASE / 'tooling-paths-v1.txt').write_text('\n'.join(source_paths) + '\n')
paths += [ROOT / live for live in LIVE.values()]
manifest = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
(BASE / 'SOURCE-v1.json').write_text(json.dumps(manifest, indent=2) + '\n')
print('Prepared source identities; run check.py into a fresh output directory.')
