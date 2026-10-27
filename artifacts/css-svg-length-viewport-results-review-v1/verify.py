import collections
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RUNTIME = ROOT / 'artifacts/css-svg-length-viewport-runtime-v1'
read = lambda p: json.loads(p.read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(RUNTIME / 'FILES.json') == '943184c625972474a25dda97eb698f1275f52d6efdb43a506d47d712a638b12a'
manifest = read(RUNTIME / 'FILES.json')
for name, digest in manifest.items():
    assert sha(RUNTIME / name) == digest, name
c, state, receipt = [read(RUNTIME / f) for f in ('CONFIG.json', 'STATE.json', 'ROOT-FINAL-CHECK.json')]
assert receipt['status'] == 'REPRODUCED_AND_PRESERVED' and receipt['exit'] == 0
assert receipt['state_sha256'] == sha(RUNTIME / 'STATE.json')
assert receipt['final_sha256'] == sha(RUNTIME / 'FINAL.json')
assert state['status'] == 'terminal' and state['complete'] and state['preserved']
assert not state['native_changes'] and 'failure' not in state and 'preservation_failure' not in state
before, final = read(RUNTIME / 'BEFORE.json'), read(RUNTIME / 'FINAL.json')
assert before == final
epoch = ROOT / c['epoch']
assert sha(epoch / 'FILES.json') == c['epoch_manifest_sha256']
prior = read(epoch / 'FINAL.json')
assert final['snapshot'] == prior
assert all(final['pins'][name] == digest for name, digest in read(epoch / 'FINAL-PINS.json').items())
assert len(final['snapshot']['sources']) == receipt['source_count'] == 53
assert len(final['pins']) == receipt['pin_count'] == 387
assert receipt['native_modified_paths'] == 30 and receipt['staged_paths'] == 925
old_receipt = read(epoch / 'ROOT-FINAL-CHECK.json')
assert receipt['installed_tests'] == old_receipt['installed_tests'] and len(receipt['installed_tests']) == 7
assert receipt['installed_binary_pins'] == old_receipt['installed_binary_pins']
assert all(final['pins'][name] == digest for name, digest in receipt['installed_binary_pins'].items())
assert all(final['pins'][name] == item['sha256'] for name, item in receipt['installed_tests'].items())
assert final['pins'][c['owned_metadata']] is None
assert (RUNTIME / 'fixture.html').read_bytes() == (ROOT / c['proposal'] / 'probe.html').read_bytes()
directory = RUNTIME / 'wpt-viewport'
run, summary = read(directory / 'RUN.json'), read(RUNTIME / 'SUMMARY.json')
events = [json.loads(line) for line in (directory / 'raw.json').read_text().splitlines()]
rows = [e for e in events if e.get('action') == 'test_status']
assert rows == run['rows'] == summary['rows']
assert len(rows) == len({r['subtest'] for r in rows}) == 10
assert {r['subtest'] for r in rows} == set(c['names'])
assert all(r['test'] == c['test_id'] for r in rows)
assert collections.Counter(r['status'] for r in rows) == {'PASS': 2, 'FAIL': 8}
for row in rows:
    unit = row['subtest'].split(':')[0]
    if unit == 'px':
        assert row['status'] == 'PASS'
    else:
        old, current = (20, 40) if unit in ('vw', 'vmax') else (10, 30)
        assert row['status'] == 'FAIL'
        assert row['message'] == f'assert_approx_equals: first value after iframe resize expected {current} +/- 0.001 but got {old}'
starts = [e for e in events if e.get('action') == 'test_start']
ends = [e for e in events if e.get('action') == 'test_end']
assert starts == run['starts'] and ends == run['ends']
assert len(starts) == len(ends) == 1 and starts[0]['test'] == ends[0]['test'] == c['test_id']
assert ends[0]['status'] == 'OK'
assert sum(e.get('action') == 'suite_start' for e in events) == 1
assert sum(e.get('action') == 'suite_end' for e in events) == 1
spec = importlib.util.spec_from_file_location('tests', ROOT / c['tests_helper'])
tests = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tests)
assert not tests.infrastructure_faults(events) and not run['infrastructure_faults']
assert run['complete'] and run['exit'] == 1 and run['before'] == run['after']
assert run['before'] == {**final['pins'], c['owned_test']: sha(RUNTIME / 'fixture.html')}
assert read(directory / 'CLEANUP.json') == {'owned_group_absent': True, 'errors': []}
assert summary['calibrated'] == state['calibrated'] == receipt['calibrated'] == 10
result = {'runtime_files_sha256': sha(RUNTIME / 'FILES.json'), 'authenticated_payloads': len(manifest),
          'root_receipt_sha256': sha(RUNTIME / 'ROOT-FINAL-CHECK.json'),
          'calibrated': 10, 'PASS': 2, 'FAIL': 8, 'harness_ok': 1,
          'persistent_pins': 387, 'phase_pins': len(run['before']), 'sources': 53,
          'installed_test_identities': 7, 'native_paths': 30, 'staged_paths': 925,
          'subsequent_failed_case_assertions': 'NOT_REACHED', 'accepted_bug': False,
          'scope': 'first-read observed values; no native branch trace or conversion-persistence observation'}
(HERE / 'CHECK.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
