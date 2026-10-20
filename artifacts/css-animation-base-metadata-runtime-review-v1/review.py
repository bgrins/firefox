from pathlib import Path
import hashlib
import json

here = Path(__file__).resolve().parent
repo = here.parents[1]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
for name, digest in json.loads((here / 'INPUTS.json').read_text()).items():
    assert sha(repo / name) == digest, name
base = repo / 'artifacts/css-animation-base-metadata-root-v1'
audit = repo / 'artifacts/css-animation-base-metadata-audit-v1'
manifest = json.loads((audit / 'MANIFEST.json').read_text())
assert sha(audit / 'MANIFEST.json') == json.loads((audit / 'FREEZE.json').read_text())['manifest_sha256']
for name, digest in manifest.items():
    assert sha(audit / name) == digest, name
run = json.loads((base / 'RUN.json').read_text())
raw = [json.loads(x) for x in (base / 'raw.json').read_text().splitlines()]
rows = [x for x in raw if x.get('action') == 'test_status']
ends = [x for x in raw if x.get('action') == 'test_end']
expected = []
for direction in ['clean to tainted', 'tainted to clean']:
    expected.extend([(f'Neutral start {direction}, same payload', 'FAIL'),
                     (f'Neutral start {direction}, different payload', 'PASS'),
                     (f'Neutral end {direction}, same payload', 'FAIL'),
                     (f'Explicit replacement ignores base {direction}', 'PASS')])
assert [(x['subtest'], x['status']) for x in rows] == expected
assert len({(x['test'], x['subtest']) for x in rows}) == 8
assert all(x['test'] == '/css/css-values/animation-base-equal-payload-taint.html' for x in rows)
assert rows == run['rows'] and ends == run['harness']
assert len(ends) == 1 and ends[0]['status'] == 'OK'
assert sum(x.get('action') == 'suite_end' for x in raw) == 1
assert not any(x.get('action') == 'crash' for x in raw)
assert run['stable_after'] and run['exit'] == 1
for row in rows:
    if row['status'] == 'FAIL':
        assert row['message'].startswith('assert_equals: Immediate effect URL taint expected ')
        assert 'runCase@' in row['stack'] and '.html:66:8' in row['stack']
pair_path = repo / 'artifacts/css-animation-endpoint-paired-root-v1/PAIR.json'
pair = json.loads(pair_path.read_text())
transfer = json.loads((repo / 'artifacts/css-animation-endpoint-final-root-v1/FORMAT-TRANSFER.json').read_text())
assert sha(pair_path) == run['pair_sha256']
assert pair['complete'] and pair['build']['exit'] == 0
assert pair['build']['sources_stable'] and pair['sources_stable_after'] and pair['binaries_stable_after']
pins = dict(pair['candidate_pins'])
assert pins[transfer['path']] == transfer['before_sha256']
pins[transfer['path']] = transfer['after_sha256']
pins['testing/web-platform/tests/css/css-values/animation-base-equal-payload-taint.html'] = sha(audit / 'probe.html')
pins.update({'objdir-full.noindex/dist/Nightly.app/Contents/MacOS/' + n: h for n, h in pair['candidate_binaries'].items()})
assert pins == run['pins']
source = (audit / 'source' / transfer['path']).read_bytes()
assert hashlib.sha256(source).hexdigest() == transfer['before_sha256']
assert source.count(transfer['old'].encode()) == 1
assert hashlib.sha256(source.replace(transfer['old'].encode(), transfer['new'].encode())).hexdigest() == transfer['after_sha256']
result = {'status': 'PASS', 'source_inputs_authenticated': len(manifest), 'raw_identities': expected,
          'failure_assertion': 'Immediate effect URL taint', 'harness': 'OK', 'stable_receipt_pins': len(pins),
          'pair_build_exit': pair['build']['exit'], 'format_transfer': 'exact one whitespace replacement',
          'claim': 'retained runtime and provenance reconstruction; no browser execution or candidate repair acceptance'}
print(json.dumps(result, indent=2))
