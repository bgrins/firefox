import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
RUNTIME = ROOT / 'artifacts/css-font-metric-demand-native-original-runtime-1/original-wpt-ordinary'
OWNER = RUNTIME.parent
RELEASE = ROOT / 'artifacts/css-font-metric-demand-installed-release-runtime-3'
STAGE = RUNTIME
FIXTURE = ROOT / 'artifacts/css-registered-font-metric-demand-probe-v2'
read = lambda p: json.loads(p.read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
result = read(RUNTIME / 'RESULT.json')
assert result['success'] and result['exit'] == 1 and result['execution_error'] is None
outcomes = read(OWNER / 'original-OUTCOMES.json')
events = [json.loads(line) for line in (RUNTIME / 'raw.jsonl').read_text().splitlines()]
rows = [r for r in events if r.get('action') == 'test_status']
ends = [r for r in events if r.get('action') == 'test_end']
assert rows == outcomes['rows'] and ends == outcomes['endings']
assert sha(RUNTIME / 'raw.jsonl') == outcomes['lanes']['ordinary']['raw_sha256']
roster = read(FIXTURE / 'ROSTER.json')
assert len(rows) == 13 and {(r['test'], r['subtest']) for r in rows} == {(p, n) for p, names in roster.items() for n in names}
assert len(ends) == 1 and ends[0]['status'] == 'OK'
assert sum(r['status'] == 'PASS' for r in rows) == 3
assert sum(r['status'] == 'FAIL' for r in rows) == 10
build = read(OWNER / 'original-build/RESULT.json')
assert build['command_success'] and build['browser_build_performed'] and build['error'] is None
assert read(OWNER / 'original-build/build-RESULT.json')['exit'] == 0
app = read(RUNTIME / 'APPLICATION-METADATA.json')
assert app == build['application_metadata'] == read(RUNTIME / 'APPLICATION-METADATA-POST.json')
assert build['binaries'] == read(RUNTIME / 'BINARY-PINS.json')
assert app['build_revision'] == app['harness_revision'] == 'a1e0ffba3651cf27853c33d22bb7b1b5368f658f'
assert app['source_role'] == 'original' and app['browser_build_id'] == '20261030123747'
roles = read(ROOT / 'artifacts/css-font-metric-demand-native-original-v1/SOURCE-ROLES.json')
assert build['native_sources'] == {p: v['base_sha256'] for p,v in roles.items()}
starts = [r for r in events if r.get('action') == 'suite_start']
assert len(starts) == 1
assert starts[0]['run_info']['browser_build_id'] == app['browser_build_id']
assert starts[0]['run_info']['revision'] == app['harness_revision']
for name, digest in read(STAGE / 'STAGED-RESOURCES.json').items():
    assert sha(STAGE / name) == digest
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
    assert len(mismatches) == 2
    failures.append({'name': item['subtest'], **payload, 'mismatches': mismatches,
                     'assertion_suffix': message[start + end:]})
assert sum(len(f['mismatches']) for f in failures) == 20
old = [json.loads(line) for line in (RELEASE / 'raw.jsonl').read_text().splitlines()]
oldrows = {r['subtest']: r for r in old if r.get('action') == 'test_status'}
assert len(oldrows) == 13 and set(oldrows) == {r['subtest'] for r in rows}
signature = lambda r: {k:r.get(k) for k in ('test','subtest','status','message')}
changed = [r['subtest'] for r in rows if signature(r) != signature(oldrows[r['subtest']])]
assert changed == ['Registered metric: weight / ch / attr']
attr = next(f for f in failures if f['input'] == 'attr')
assert [r['first'] for r in attr['observations']] == ['20px','20px','30px','30px']
terminal = read(OWNER / 'ROOT-OWNER-TERMINAL.json')
owner_result = read(OWNER / 'RESULT.json')
assert terminal == {'session':80766,'launch':'c53f82','terminal':'a2c1fe','exit':0,
                    'result_sha256':sha(OWNER / 'RESULT.json')}
assert owner_result['success'] and owner_result['restoration_verified']
assert owner_result['runtime_controls_unchanged'] and owner_result['empty_staging_preserved']
assert owner_result['error'] is None and owner_result['native_fix_acceptance'] is False
output = {'pass':3,'fail':10,'harness_ok':1,'rechecked_failure_rows':40,'metric_mismatches':20,
          'unchanged_release_callback_signatures':12,'changed_release_callbacks':changed,
          'failures':failures,'build_metadata':app,'native_sources':build['native_sources'],
          'owner_terminal':terminal,'owner_result':owner_result,
          'pass_phase_values_archived':False,'matching_effective_preferences_proven':False,
          'native_fix_acceptance':False,'independent_live_restoration_check':False}
(HERE / 'OBSERVATIONS.json').write_text(json.dumps(output,indent=2)+'\n')
paths = [RUNTIME / n for n in ['raw.jsonl','RESULT.json','APPLICATION-METADATA.json','APPLICATION-METADATA-POST.json','BINARY-PINS.json','STAGED-RESOURCES.json','COMMAND.json']]
paths += [OWNER / n for n in ['original-build/RESULT.json','original-build/build-RESULT.json','original-OUTCOMES.json','ROOT-OWNER-TERMINAL.json','RESULT.json']]
paths += [RELEASE / 'raw.jsonl',RELEASE / 'RESULT.json',FIXTURE / 'ROSTER.json',FIXTURE / 'INPUTS.json',FIXTURE / 'FILES.json',ROOT / 'artifacts/css-font-metric-demand-native-original-v1/SOURCE-ROLES.json']
paths += [STAGE / n for n in read(STAGE / 'STAGED-RESOURCES.json')]
refs = {str(p.relative_to(ROOT)):sha(p) for p in paths}
(HERE / 'REFERENCES.json').write_text(json.dumps(refs,indent=2,sort_keys=True)+'\n')
print(json.dumps({k:v for k,v in output.items() if k not in ['failures','build_metadata','native_sources','owner_terminal','owner_result']}))
