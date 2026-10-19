#!/usr/bin/env python3
import hashlib
import json
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

for name, expected in json.loads((HERE / 'INPUTS.json').read_text()).items():
    assert sha(HERE / name) == expected, name
pins = json.loads((HERE / 'source/PINS.json').read_text())
for phase in ('original', 'candidate'):
    for name, expected in pins[phase].items():
        assert sha(HERE / 'source' / phase / name) == expected
assert sha(HERE / 'native-wpt-v1.patch') == '08027345b7f8a23aba216b6244d5c48ec7cc9ba459a4536fc9bf291f4a5159e2'
paths = re.findall(r'^\+\+\+ (.*)$', (HERE / 'native-wpt-v1.patch').read_text(), re.M)
assert paths == ['b/servo/components/style/properties/cascade.rs', 'b/testing/web-platform/tests/css/css-values/attr-fallback-preparation.html']
for file, phase in [('baseline-v3-receipt.json', 'original'), ('candidate-v3-receipt.json', 'candidate')]:
    row = json.loads((HERE / file).read_text())
    assert row['all_inputs_unchanged'] and row['suite_end_count'] == 1
    assert row['pins_before']['servo/components/style/properties/cascade.rs'] == pins[phase]['cascade.rs']
    assert row['pins_before']['servo/components/style/custom_properties.rs'] == pins[phase]['custom_properties.rs']
print(json.dumps({'integrity_source_binding': 'PASS', 'scope': 'bounded preparation source review'}))
