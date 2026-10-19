import sys
assert sys.flags.isolated and sys.flags.no_site
import argparse, hashlib, json, tomllib
from pathlib import Path, PurePosixPath
R = Path(__file__).resolve().parent
p = argparse.ArgumentParser()
p.add_argument('--live', action='store_true')
a = p.parse_args()
def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()
records = json.loads((R / 'MANIFEST.json').read_text())
seen = set()
for row in records:
    rel = PurePosixPath(row['path'])
    assert not rel.is_absolute() and '..' not in rel.parts and str(rel) == row['path']
    assert row['path'] not in seen
    seen.add(row['path'])
    target = R / rel
    assert target.is_file() and not target.is_symlink()
    for parent in target.parents:
        if parent == R:
            break
        assert not parent.is_symlink()
    assert sha(target) == row['sha256'], row['path']
actual = {str(p.relative_to(R)) for p in R.rglob('*') if p.is_file()}
assert actual - {'MANIFEST.json', 'FREEZE.json'} == seen
assert not any(p.is_symlink() for p in R.rglob('*'))
e = R / 'evidence'
source = e / 'source'
source_pins = json.loads((e / 'SOURCE-PINS.json').read_text())
for path, digest in source_pins.items():
    assert sha(source / path) == digest
    if a.live:
        assert sha(R.parents[1] / path) == digest, path
for row in json.loads((e / 'RETRIEVAL.json').read_text()):
    assert sha(e / row['path']) == row['sha256'] and row['url'].startswith('https://')
assert json.loads((e / 'issue5741.json').read_text())['state'] == 'open'
pr = json.loads((e / 'pr2516.json').read_text())
assert pr['merged_at'] == '2018-04-11T13:12:17Z' and '1898' in pr['body']
comments = json.loads((e / 'issue1898-comments.json').read_text())
assert any(x['id'] == 342556321 and 'Make it so that setters' in x['body'] for x in comments)
assert 'id="dom-cssstyledeclaration-setproperty"' in (e / 'cssom.html').read_text()
assert 'id="all-shorthand"' in (e / 'css-cascade-5.html').read_text()
props = source / 'servo/components/style/properties'
longhands = tomllib.loads((props / 'longhands.toml').read_text())
shorthands = tomllib.loads((props / 'shorthands.toml').read_text())
assert len(shorthands) == 94
for name, data in shorthands.items():
    subs = data.get('sub_properties', []) + data.get('extra_gecko_sub_properties', [])
    assert len(subs) == len(set(subs)), name
    groups = {}
    for sub in subs:
        prop = longhands[sub]
        group = prop.get('logical_group')
        if group:
            groups.setdefault(group, set()).add(prop.get('logical', False))
    assert all(len(kinds) == 1 for kinds in groups.values()), name
generator = (props / 'data.py').read_text()
assert 'logical_longhands + other_longhands' in generator
assert 'if p.name in ["direction", "unicode-bidi"]:' in generator
browser = e / 'root-browser'
before = json.loads((browser / 'baseline-before.json').read_text())
assert before == json.loads((browser / 'baseline-after.json').read_text()) == json.loads((browser / 'baseline-input.json').read_text())
for path, digest in source_pins.items():
    if path in before['fixed']:
        assert digest == before['fixed'][path], path
test_path = 'testing/web-platform/tests/css/cssom/setproperty-all-logical-order.html'
assert before['fixed'][test_path] == sha(browser / 'setproperty-all-logical-order.html')
result = json.loads((browser / 'baseline-result.json').read_text())
assert result['stable_pins'] and result['exit_code'] == 1
assert result['raw_sha256'] == sha(browser / 'baseline-raw.jsonl')
assert result['console_sha256'] == sha(browser / 'baseline-console.log')
raw = [json.loads(line) for line in (browser / 'baseline-raw.jsonl').read_text().splitlines()]
rows = [x for x in raw if x['action'] == 'test_status']
assert len(rows) == len({x['subtest'] for x in rows}) == 24
for row in rows:
    assert row['status'] == ('FAIL' if row['subtest'].startswith('all expansion order:') else 'PASS')
    retained = [x for x in result['rows'] if x.get('subtest') == row['subtest']]
    assert len(retained) == 1 and retained[0]['status'] == row['status']
assert sum(x['status'] == 'FAIL' for x in rows) == 8
assert [x['status'] for x in raw if x['action'] == 'test_end'] == ['OK']
print(json.dumps({'authenticated_files': len(records), 'metadata_shorthands': 94, 'metadata_unique_and_group_uniform': True, 'browser_fail': 8, 'browser_pass': 16, 'live_checked': a.live, 'verdict': 'relational ordering discrepancy; independent normative adjudication required'}))
