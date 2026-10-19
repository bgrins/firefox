#!/usr/bin/env python3
import difflib
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


freeze = json.loads((ROOT / 'FREEZE.json').read_text())
assert sha(ROOT / 'MANIFEST.json') == freeze['manifest_sha256']
manifest = json.loads((ROOT / 'MANIFEST.json').read_text())
for name, expected in manifest.items():
    assert sha(ROOT / name) == expected, name
assert sha(ROOT / 'proposal.rs') == 'd38d0831d0e4acc68e0a7064f03674de81e0e6e6f35e0243ab349305015dd794'
assert sha(ROOT / 'formatted.rs') == '71a507cba6ed20b40e690c29555844514870530a5bccc74e41459aa12e46d5bc'
original = (ROOT / 'proposal.rs').read_text()
candidate = original
for owner in ['substitution', 'self']:
    lines = [
        '            let mut value = ComputedRegisteredValue::universal(Arc::new(VariableValue::new_resolved(',
        f'                {owner}.css.into_owned(),',
        '                url_data,',
        f'                {owner}.first_token_type,',
        f'                {owner}.last_token_type,',
        '            )));',
    ]
    before = '\n'.join(lines)
    after = '\n'.join(['            let mut value =',
                        '                ComputedRegisteredValue::universal(Arc::new(VariableValue::new_resolved(',
                        *['    ' + line for line in lines[1:]]])
    assert candidate.count(before) == 1
    candidate = candidate.replace(before, after)
assert candidate == (ROOT / 'formatted.rs').read_text()
patch = ''.join(difflib.unified_diff(original.splitlines(True), candidate.splitlines(True),
                                    fromfile='proposal/custom_properties.rs',
                                    tofile='formatted/custom_properties.rs'))
assert patch == (ROOT / 'format-only-v2.patch').read_text()
print(json.dumps({'authenticated_files': len(manifest), 'exact_expression_wraps': 2,
                  'all_other_bytes_unchanged': True, 'native_execution': False}))
