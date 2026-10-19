from pathlib import Path
import hashlib
import json
import difflib

ROOT=Path(__file__).resolve().parent
for name,digest in json.loads((ROOT/'MANIFEST.json').read_text()).items():
    assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest,name
original=(ROOT/'original.rs').read_text()
proposed=(ROOT/'proposed.rs').read_text()
formatted=(ROOT/'formatted.rs').read_text()
before='''                    *removed_backslash = missing_closing_characters.is_empty()
                        && token_slice.ends_with("\\\\");'''
after='''                    *removed_backslash =
                        missing_closing_characters.is_empty() && token_slice.ends_with("\\\\");'''
assert proposed.count(before)==1
assert proposed.replace(before,after)==formatted
expected=''.join(difflib.unified_diff(original.splitlines(True),formatted.splitlines(True),fromfile='a/servo/components/style/custom_properties.rs',tofile='b/servo/components/style/custom_properties.rs'))
assert expected==(ROOT/'native.patch').read_text()
print(json.dumps({'status':'PASS','binding':'one exact whitespace-only wrapping replacement outside strings/comments','formatted_sha256':hashlib.sha256(formatted.encode()).hexdigest(),'parent_candidate_sha256':hashlib.sha256(proposed.encode()).hexdigest()}))
