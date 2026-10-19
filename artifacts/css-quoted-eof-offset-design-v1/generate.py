from pathlib import Path
import difflib
import hashlib
import json

ROOT = Path(__file__).resolve().parent
source = (ROOT / 'source/custom_properties.rs').read_text()
candidate = source

def replace(old, new, count=1):
    global candidate
    assert candidate.count(old) == count, (old, candidate.count(old))
    candidate = candidate.replace(old, new)

replace('        let mut missing_closing_characters = String::new();',
        '        let mut missing_closing_characters = String::new();\n        let mut removed_backslash = false;')
replace('            &mut missing_closing_characters,\n',
        '            &mut missing_closing_characters,\n            &mut removed_backslash,\n')
replace('''            if css.ends_with("\\\\")
                && matches!(missing_closing_characters.as_bytes()[0], b'"' | b'\\'')
            {''', '''            if removed_backslash {''')
replace('    missing_closing_characters: &mut String,\n',
        '    missing_closing_characters: &mut String,\n    removed_backslash: &mut bool,\n', 2)
import re
candidate, count = re.subn(r'(?m)^( +)missing_closing_characters,\n',
    r'\1missing_closing_characters,\n\1removed_backslash,\n', candidate)
assert count == 4, count
replace('''                        + missing_closing_characters.len();''',
        '''                        + missing_closing_characters.len()
                        - usize::from(*removed_backslash);''')
replace('''                    missing_closing_characters.push_str(quote)''',
        '''                    *removed_backslash = missing_closing_characters.is_empty()
                        && token_slice.ends_with("\\\\");
                    missing_closing_characters.push_str(quote)''')
(ROOT / 'candidate/custom_properties.rs').write_text(candidate)
patch = ''.join(difflib.unified_diff(source.splitlines(True), candidate.splitlines(True),
    fromfile='a/servo/components/style/custom_properties.rs',
    tofile='b/servo/components/style/custom_properties.rs'))
(ROOT / 'native.patch').write_text(patch)
(ROOT / 'evidence/SOURCE-IDENTITY.json').write_text(json.dumps({
    'original': hashlib.sha256(source.encode()).hexdigest(),
    'candidate': hashlib.sha256(candidate.encode()).hexdigest(),
    'patch': hashlib.sha256(patch.encode()).hexdigest(),
}, indent=2)+'\n')
