import hashlib
import importlib.util
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
OWNER = ROOT / 'artifacts/css-explicit-taint-combined-native-candidate-browser-v1'
RUNTIME = ROOT / 'artifacts/css-explicit-taint-combined-native-candidate-browser-runtime-v1'
read = lambda p: json.loads(p.read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


assert sha(OWNER / 'FILES.json') == 'e84f0d66f97085c5cff65b5ac54f370149fd60b62cf91051872ad940fda01273'
for name, record in read(OWNER / 'FILES.json').items():
    assert sha(OWNER / name) == record['sha256']
    assert (OWNER / name).stat().st_size == record['bytes']
policy = read(OWNER / 'POLICY.json')
assessor = load('combined_assessor', OWNER / 'assess.py')
checks = load('combined_checks', ROOT / policy['wpt']['checks_helper'])
baseline = read(OWNER / 'BASELINE82.json')
build = read(RUNTIME / 'candidate-build/RESULT.json')
command = read(RUNTIME / 'candidate-build/COMMAND.json')
assert build['browser_build_performed'] and build['command_success'] and build['preservation_verified']
assert build['error'] is None
assert command['owner_manifest'] == sha(OWNER / 'FILES.json')
expected_sources = {name: role['candidate_sha256'] for name, role in read(OWNER / 'SOURCE-ROLES.json').items()}
assert command['source_sha256'] == build['native_sources'] == expected_sources
assert build['application_metadata']['source_role'] == 'candidate'
rows, ends, lanes = [], [], {}
for lane in policy['lane_order']:
    phase = RUNTIME / ('candidate-wpt-' + lane)
    result = read(phase / 'RESULT.json')
    assert result['success'] and result['preservation_verified'] and result['execution_error'] is None
    metadata = read(phase / 'APPLICATION-METADATA.json')
    assert metadata == read(phase / 'APPLICATION-METADATA-POST.json') == build['application_metadata']
    assert read(phase / 'BINARY-PINS.json') == build['binaries']
    for name, pin in read(phase / 'STAGED-RESOURCES.json').items():
        assert sha(phase / name) == pin
    for url, record in policy['wpt_lanes'][lane]['resources'].items():
        resource = phase / 'mozilla-tests' / url[len('/_mozilla/'):] if url.startswith('/_mozilla/') else phase / 'tests' / url[1:]
        assert sha(resource) == record['sha256']
    events = [json.loads(line) for line in (phase / 'raw.jsonl').read_text().splitlines()]
    actual = assessor.assess(events, result['exit'], read(phase / 'ASSESSMENT-POLICY.json'), checks, run_binding=metadata)
    assert actual == read(phase / 'ASSESSMENT.json') and actual['complete']
    rows.extend(assessor.signature(row) for row in actual['rows'])
    ends.extend(assessor.signature(row) for row in actual['ends'])
    lanes[lane] = {'raw_sha256': sha(phase / 'raw.jsonl'), 'assessment_sha256': sha(phase / 'ASSESSMENT.json'), 'statuses': dict(Counter(row['status'] for row in actual['rows']))}
key = lambda row: (row['test'], row['kind'], row.get('subtest') or '')
old = {key(row): row for row in baseline['rows'] + baseline['ends']}
new = {key(row): row for row in rows + ends}
assert len(rows) == len(baseline['rows']) == 82
assert len(ends) == len(baseline['ends']) == 7
assert len(old) == len(new) == 89 and set(old) == set(new)
assert all(row['status'] == 'PASS' for row in rows)
assert all(row['status'] == 'OK' for row in ends)
preserved = [identity for identity, row in old.items() if row['status'] == 'PASS' or row['kind'] == 'test_end']
assert len(preserved) == 76 and all(old[identity] == new[identity] for identity in preserved)
differences = [{'identity': identity, 'original': old[identity], 'candidate': new[identity]} for identity in sorted(old) if old[identity] != new[identity]]
assert len(differences) == 13
assert all(row['original']['status'] == 'FAIL' and row['candidate']['status'] == 'PASS' for row in differences)
assert Counter(row['candidate']['test'] for row in differences) == Counter({
    '/css/css-values/attr-fallback-taint.html': 11,
    '/css/css-values/attr-fallback-taint-registration-transition.html': 2,
})
report = {'comparison_passed': True, 'candidate_pass': 82, 'preserved_pass_signatures': 69,
          'preserved_ending_signatures': 7, 'fail_to_pass': 13, 'differences': differences,
          'baseline_source': baseline['source_sha256'], 'candidate_sources': expected_sources,
          'build_sha256': sha(RUNTIME / 'candidate-build/RESULT.json'),
          'baseline_sha256': sha(OWNER / 'BASELINE82.json'), 'lanes': lanes,
          'native_acceptance': False, 'independent_restoration_audit_required': True}
with (HERE / 'RESULT.json').open('x') as stream:
    json.dump(report, stream, indent=2)
    stream.write('\n')
print('82 PASS; 69 prior PASS and seven endings unchanged; exactly 13 FAIL-to-PASS improvements')
