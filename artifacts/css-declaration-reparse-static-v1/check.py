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
src = (e / 'source/servo/components/style/properties/mod.rs').read_text()
start = src.index('fn parse_non_custom_property_declaration_value_into(')
end = src.index('\nimpl PropertyDeclaration', start)
helper = (e / 'helper.rs').read_text()
assert helper == src[start:end]
remote = json.loads((e / 'searchfox-properties.json').read_text())['output']
start = remote.index('fn parse_non_custom_property_declaration_value_into(')
end = remote.index('\nimpl PropertyDeclaration', start)
assert remote[start:end] == helper
assert (e / 'vendor/cssparser/src/parser.rs').read_bytes() == (e / 'source/third_party/rust/cssparser/src/parser.rs').read_bytes()
for row in json.loads((e / 'vendor-live-comparison.json').read_text()):
    assert row['matches_live']
    assert sha(e / 'vendor' / row['path'].removeprefix('third_party/rust/')) == row['sha256']
b = e / 'root-browser'
before = json.loads((b / 'baseline-before.json').read_text())
after = json.loads((b / 'baseline-after.json').read_text())
assert before == after == json.loads((b / 'baseline-input.json').read_text())
for name in ['servo/components/style/properties/mod.rs', 'third_party/rust/cssparser/src/parser.rs', 'servo/components/style/custom_properties.rs']:
    assert before['fixed'][name] == sha(e / 'source' / name)
test_path = 'testing/web-platform/tests/css/css-syntax/declaration-curly-fallback.html'
assert before['fixed'][test_path] == sha(R / 'declaration-curly-fallback.html')
result = json.loads((b / 'baseline-result.json').read_text())
assert result['stable_pins'] and result['exit_code'] == 1
assert result['raw_sha256'] == sha(b / 'baseline-raw.jsonl')
raw = [json.loads(line) for line in (b / 'baseline-raw.jsonl').read_text().splitlines()]
rows = [x for x in raw if x['action'] == 'test_status']
assert len(rows) == 48 and len({x['subtest'] for x in rows}) == 48
bad = {'serif {var(--x)}', 'serif, {var(--x)}', '{var(--x)} serif', 'serif {} var(--x)', 'serif {env(x)}', 'serif {attr(x)}'}
for row in rows:
    expected_failure = any(row['subtest'].endswith('font-family: ' + x) for x in bad)
    assert row['status'] == ('FAIL' if expected_failure else 'PASS')
    matches = [x for x in result['rows'] if x.get('subtest') == row['subtest']]
    assert len(matches) == 1 and matches[0]['status'] == row['status']
assert sum(x['status'] == 'FAIL' for x in rows) == 24
assert [x['status'] for x in raw if x['action'] == 'test_end'] == ['OK']
if a.output:
    out = a.output.resolve()
    assert not out.is_relative_to(R) and not out.exists()
    subprocess.run([sys.executable, '-I', '-S', str(R / 'replay.py'), '--output', str(out)], check=True)
print(json.dumps(dict(authenticated_files=len(records), browser_fail=24, browser_pass=24, complete_helper_binding=True)))
