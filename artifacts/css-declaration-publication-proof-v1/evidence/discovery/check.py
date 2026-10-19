import sys
assert sys.flags.isolated and sys.flags.no_site
import argparse, hashlib, json, subprocess
from pathlib import Path, PurePosixPath
R = Path(__file__).resolve().parent
p = argparse.ArgumentParser()
p.add_argument('--output', type=Path)
a = p.parse_args()
def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()
records = json.loads((R / 'MANIFEST.json').read_text())
seen = set()
for rec in records:
    name = rec['path']
    rel = PurePosixPath(name)
    assert not rel.is_absolute() and '..' not in rel.parts and str(rel) == name
    assert name not in seen
    seen.add(name)
    path = R / name
    assert path.is_file() and not path.is_symlink()
    for parent in path.parents:
        if parent == R:
            break
        assert not parent.is_symlink()
    assert sha(path) == rec['sha256'], name
actual = {str(p.relative_to(R)) for p in R.rglob('*') if p.is_file()}
assert actual - {'MANIFEST.json', 'FREEZE.json'} == seen
assert not any(p.is_symlink() for p in R.rglob('*'))
e = R / 'evidence'
for path, digest in json.loads((e / 'SOURCE-PINS.json').read_text()).items():
    assert sha(e / 'source' / path) == digest
for row in json.loads((e / 'VENDOR-COMPARISON.json').read_text()):
    assert row['matches_current'] and sha(R / row['path']) == row['sha256']
for name in ['param', 'publication', 'helper']:
    assert json.loads((e / ('searchfox-' + name + '.json')).read_text())['exit_code'] == 0
src = (e / 'source/servo/components/style/properties/mod.rs').read_text()
needle = '            ParseError::custom(style_traits::StyleParseErrorKind::UnspecifiedError)'
assert src.count(needle) == 1
candidate = src.replace(needle, '            declarations.clear();\n' + needle)
assert candidate == (e / 'candidate-properties.rs').read_text()
assert sha(e / 'candidate-properties.rs') == '2ef96482f50b06dcf87a18abc4d1a9aa0109a9063aa71cadc53e7737022c094d'
b = e / 'root-browser'
before = json.loads((b / 'baseline-before.json').read_text())
assert before == json.loads((b / 'baseline-after.json').read_text()) == json.loads((b / 'baseline-input.json').read_text())
for name in ['servo/components/style/properties/mod.rs', 'servo/components/style/custom_properties.rs', 'servo/components/style/values/specified/param.rs', 'servo/components/style/properties/declaration_block.rs']:
    assert before['fixed'][name] == sha(e / 'source' / name)
assert before['fixed']['third_party/rust/cssparser/src/parser.rs'] == sha(R / 'vendor/cssparser/src/parser.rs')
assert before['fixed']['testing/web-platform/tests/css/css-link-params/link-parameters-publication.html'] == sha(R / 'link-parameters-publication.html')
result = json.loads((b / 'baseline-result.json').read_text())
assert result['stable_pins'] and result['exit_code'] == 1
assert result['raw_sha256'] == sha(b / 'baseline-raw.jsonl')
assert result['console_sha256'] == sha(b / 'baseline-console.log')
raw = [json.loads(line) for line in (b / 'baseline-raw.jsonl').read_text().splitlines()]
rows = [x for x in raw if x['action'] == 'test_status']
assert len(rows) == 25 and len({x['subtest'] for x in rows}) == 25
bad_values = ['param(--a, var(--x, red))', 'param(--a, env(not-real, red))', 'param(--a, attr(data-x))']
bad = {op + ': ' + v for op in ['new', 'remove'] for v in bad_values}
for row in rows:
    assert row['status'] == ('FAIL' if row['subtest'] in bad else 'PASS')
    matches = [x for x in result['rows'] if x.get('subtest') == row['subtest']]
    assert len(matches) == 1 and matches[0]['status'] == row['status']
assert [x['status'] for x in raw if x['action'] == 'test_end'] == ['OK']
if a.output:
    out = a.output.resolve()
    assert not out.is_relative_to(R) and not out.exists()
    subprocess.run([sys.executable, '-I', '-S', str(R / 'native/build.py'), '--output', str(out)], check=True)
    for variant in ['original', 'clear-candidate']:
        assert (out / (variant + '.jsonl')).read_bytes() == (R / 'receipts' / (variant + '.jsonl')).read_bytes()
        assert (out / (variant + '.rs')).read_bytes() == (R / 'receipts' / (variant + '.rs')).read_bytes()
        assert (out / (variant + '-bindings.json')).read_bytes() == (R / 'receipts' / (variant + '.bindings.json')).read_bytes()
print(json.dumps(dict(authenticated_files=len(records), browser_fail=6, browser_pass=19, native_rows_per_variant=13)))
