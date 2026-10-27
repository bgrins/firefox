import hashlib
import importlib.util
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
RUNTIME = ROOT / 'artifacts/css-hidden-svg-matrix-comparison-runtime-v1'
read = lambda p: json.loads(p.read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
c = read(RUNTIME / 'CONFIG.json')
state = read(RUNTIME / 'STATE.json')
assert sha(RUNTIME / 'DRAFT-FILES.json') == 'e36ee9f4fee6237d882c7f1c347647708de26a67d4fa6edd2f50c0d866203d0d'
for manifest, base in [('DRAFT-FILES.json', RUNTIME), ('REFERENCES.json', ROOT)]:
    for name, digest in read(RUNTIME / manifest).items():
        assert sha(base / name) == digest, name
spec = importlib.util.spec_from_file_location('availability', RUNTIME / 'validate_availability.py')
availability = importlib.util.module_from_spec(spec)
spec.loader.exec_module(availability)
phases = {}
paired = {}
expected_keys = {(test, name) for test, names in c['expected_subtests'].items() for name in names}
resources = read(RUNTIME / 'RESOURCES.json')
owned = next(iter(c['install']))
for phase in ('baseline', 'candidate'):
    directory = RUNTIME / ('wpt-' + phase)
    events = [json.loads(line) for line in (directory / 'raw.json').read_text().splitlines()]
    run = read(directory / 'RUN.json')
    rows = [event for event in events if event.get('action') == 'test_status']
    starts = [event for event in events if event.get('action') == 'test_start']
    ends = [event for event in events if event.get('action') == 'test_end']
    assert rows == run['rows'] and starts == run['starts'] and ends == run['ends']
    assert len(rows) == len(expected_keys) == 34
    assert {(r['test'], r['subtest']) for r in rows} == expected_keys
    assert len(starts) == len(ends) == 7
    assert {e['test'] for e in starts} == {e['test'] for e in ends} == set(c['expected_subtests'])
    assert all(e['status'] == 'OK' for e in ends)
    assert sum(e.get('action') == 'suite_start' for e in events) == 1
    assert sum(e.get('action') == 'suite_end' for e in events) == 1
    for e in events:
        assert e.get('action') not in ('crash', 'suite_abort', 'test_abort')
        assert not (e.get('action') == 'log' and e.get('level', '').upper() in ('ERROR', 'CRITICAL'))
        if e.get('action') == 'process_exit':
            assert e.get('exitcode', e.get('returncode', 0)) == 0
        if e.get('action') == 'assertion_count':
            assert e.get('min_expected', 0) <= e['count'] <= e.get('max_expected', 0)
        if e.get('action') in ('log', 'process_output'):
            assert not any(x in e.get('message', '') + e.get('data', '') for x in
                           ('PROCESS-CRASH', 'TEST-UNEXPECTED-ERROR', 'TEST-UNEXPECTED-TIMEOUT'))
    assert run['complete'] is True and run['infrastructure_faults'] == []
    record = state['phases'][phase]
    sources = {**c['head_pins'], **(c['candidate_pins'] if phase == 'candidate' else {})}
    assert record['source_before_build'] == record['source_after_build']
    assert record['source_before_build']['sources'] == sources
    before = read(RUNTIME / 'BEFORE.json')
    for key in ('head', 'index_diff_sha256', 'index_entries_sha256'):
        assert record['source_before_build'][key] == before[key]
    if phase == 'baseline':
        assert record['source_before_build']['native_diff_sha256'] == hashlib.sha256(b'').hexdigest()
    assert record['build_exit'] == read(RUNTIME / (phase + '-build.json'))['exit'] == 0
    pins = {**resources, **sources, owned: sha(RUNTIME / 'fixture.html'), **record['binary_pins']}
    assert run['before'] == run['after'] == pins and len(pins) == 356
    assert read(directory / 'CLEANUP.json') == {'owned_group_absent': True, 'errors': []}
    failures = [r for r in rows if r['status'] == 'FAIL']
    assert all(r['status'] in ('PASS', 'FAIL') for r in rows)
    assert run['exit'] == (1 if failures else 0)
    if phase == 'baseline':
        assert {r['subtest'] for r in failures} == {
            'getCTM: viewBox, hidden viewport resize',
            'getScreenCTM: viewBox, hidden viewport resize'}
        assert all('first matrix after viewport resize expected property 0 to be 2 but got 1' in r['message'] for r in failures)
    else:
        assert failures == []
    capdir = RUNTIME / ('availability-' + phase)
    capture, payload = read(capdir / 'RESULT.json'), read(capdir / 'payload.json')
    summary = availability.validate(payload)
    assert summary == read(capdir / 'SUMMARY.json') and summary['stable'] == 8
    assert capture['before'] == capture['after'] == pins
    assert capture['observations'] == [payload]
    assert capture['status'] == 'terminal' and capture['profile_removed'] is True
    assert capture['cleanup_errors'] == []
    assert capture['process_cleanup']['terminal'] and capture['process_cleanup']['noLiveGroup']
    paired[phase] = {(r['test'], r['subtest']): r for r in rows}
    phases[phase] = {'pass': len(rows) - len(failures), 'fail': len(failures),
                     'files_ok': len(ends), 'pins': len(pins), 'build_exit': 0,
                     'raw_sha256': sha(directory / 'raw.json'), 'run_sha256': sha(directory / 'RUN.json'),
                     'binary_pins': record['binary_pins'], 'failures': failures,
                     'availability_sha256': sha(capdir / 'payload.json'), 'availability_stable': 8}
assert (RUNTIME / 'availability-baseline/payload.json').read_bytes() == (RUNTIME / 'availability-candidate/payload.json').read_bytes()
repairs = [list(k) for k in paired['baseline'] if paired['baseline'][k]['status'] == 'FAIL' and paired['candidate'][k]['status'] == 'PASS']
assert len(repairs) == 2
assert read(RUNTIME / 'COMPARISON.json') == {'regressions': [], 'changed_failures': [], 'repaired': repairs, 'native_acceptance': False}
assert state['lint_exit'] == read(RUNTIME / 'fixture-lint.json')['exit'] == 0
result = {'phases': phases, 'repairs': repairs, 'availability_byte_identical': True,
          'independence_from_pending107_for_tested_histories': True,
          'terminal_restoration_reviewed': False}
(HERE / 'PHASE-RESULTS.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps({p: {k: v for k, v in r.items() if k in ('pass', 'fail', 'files_ok', 'pins', 'availability_stable')} for p, r in phases.items()}, indent=2))
