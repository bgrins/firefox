import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
RUNTIME = ROOT / 'artifacts/css-font-metric-demand-installed-release-runtime-3'
STAGE = ROOT / 'artifacts/css-font-metric-demand-installed-stage-v2'
FIXTURE = ROOT / 'artifacts/css-registered-font-metric-demand-probe-v2'
read = lambda p: json.loads(p.read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
result = read(RUNTIME / 'RESULT.json')
assert result['complete'] and result['exit'] == 1 and result['error'] is None
assert result['app_and_staged_inputs_preserved'] and result['cleanup']['owned_group_absent']
assert result['cleanup']['temporary_root_removed']
events = [json.loads(line) for line in (RUNTIME / 'raw.jsonl').read_text().splitlines()]
rows = [r for r in events if r.get('action') == 'test_status']
ends = [r for r in events if r.get('action') == 'test_end']
assert rows == result['rows'] and ends == result['endings']
assert sha(RUNTIME / 'raw.jsonl') == result['raw_sha256']
roster = read(FIXTURE / 'ROSTER.json')
assert len(rows) == 13 and {(r['test'], r['subtest']) for r in rows} == {(p, n) for p, names in roster.items() for n in names}
assert len(ends) == 1 and ends[0]['status'] == 'OK'
assert sum(r['status'] == 'PASS' for r in rows) == 3
assert sum(r['status'] == 'FAIL' for r in rows) == 10
assert read(RUNTIME / 'APP-PRE.json') == read(RUNTIME / 'APP-POST.json')
app = read(RUNTIME / 'APP-PRE.json')
assert app['version'] == '158.0'
assert result['run_info'][0]['browser_build_id'] == app['application']['buildid']
assert all(sha(STAGE / name) == digest for name, digest in read(STAGE / 'STAGED-RESOURCES.json').items())
for url, record in read(FIXTURE / 'INPUTS.json')['resources'].items():
    assert sha(ROOT / record['path']) == sha(STAGE / 'tests' / url[1:]) == record['sha256']
failures = []
for item in rows:
    if item['status'] != 'FAIL':
        continue
    message = item['message']
    assert message.startswith('assert_approx_equals: ')
    start = message.index('{')
    payload, end = json.JSONDecoder().raw_decode(message[start:])
    observations = payload['observations']
    assert len(observations) == 4
    for row in observations:
        assert row['fontSize'] == str(row['size']) + 'px'
        assert row['fontFamily'] == row['family'] and row['fontWeight'] == str(row['weight'])
        assert row['fontStyle'] == row['style'] and row['fontStretch'] == row['stretch']
        assert row['fontSizeAdjust'] == row['adjust']
        assert row['computedWritingMode'] == row['writingMode'] and row['textOrientation'] == row['orientation']
        assert abs(float(row['em'][:-2]) - row['size']) <= 0.02
        assert row['first'].endswith('px') and row['reference'].endswith('px')
        assert float(row['ch'][:-2]) > 0
    for size in [20, 30]:
        pair = [r for r in observations if r['size'] == size]
        assert len(pair) == 2 and abs(float(pair[0]['ch'][:-2]) - float(pair[1]['ch'][:-2])) > 1
    mismatches = [r for r in observations if abs(float(r['first'][:-2]) - float(r['reference'][:-2])) > 0.02]
    assert len(mismatches) == (4 if payload['input'] == 'attr' else 2)
    failures.append({'name': item['subtest'], **payload, 'mismatches': mismatches,
                     'assertion_suffix': message[start + end:]})
assert sum(len(f['mismatches']) for f in failures) == 22
output = {'pass': 3, 'fail': 10, 'harness_ok': 1, 'rechecked_failure_rows': 40,
          'metric_mismatches': 22, 'failures': failures, 'native_baseline_tested': False,
          'native_fix_acceptance': False, 'release_browser': app['application'],
          'pass_phase_values_archived': False, 'saved_cleanup_verified': True}
(HERE / 'OBSERVATIONS.json').write_text(json.dumps(output, indent=2) + '\n')
references = {str(p.relative_to(ROOT)): sha(p) for p in [RUNTIME / 'RESULT.json', RUNTIME / 'ROOT-TERMINAL.json',
    RUNTIME / 'raw.jsonl', RUNTIME / 'APP-PRE.json', RUNTIME / 'APP-POST.json', STAGE / 'STAGED-RESOURCES.json',
    FIXTURE / 'INPUTS.json', FIXTURE / 'ROSTER.json', FIXTURE / 'FILES.json']}
(HERE / 'REFERENCES.json').write_text(json.dumps(references, indent=2) + '\n')
print(json.dumps({k: v for k, v in output.items() if k not in ('failures', 'release_browser')}))
