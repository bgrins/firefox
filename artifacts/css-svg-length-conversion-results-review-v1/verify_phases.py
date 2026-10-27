import collections
import hashlib
import json
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RUN = ROOT / 'artifacts/css-svg-length-conversion-comparison-runtime-v1'
def read(p):
    return json.loads(p.read_text())
def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()
def auth(p, base):
    for name, digest in read(p).items():
        assert sha(base / name) == digest, name

assert sha(RUN / 'DRAFT-FILES.json') == '69173e7a3758ab8acbe3343cc4862394d2a23db4db6c7fdbedb278d09354fcf9'
auth(RUN / 'DRAFT-FILES.json', RUN)
auth(RUN / 'REFERENCES.json', ROOT)
draft = ROOT / 'artifacts/css-svg-length-conversion-comparison-v1'
assert sha(draft / 'DRAFT-FILES.json') == '80bc9ca0f9a88a3aa557b883ab59ea9ea56e39f46573c8003e42c9777fe1791b'
auth(draft / 'DRAFT-FILES.json', draft)
c, disabled = read(RUN / 'CONFIG.json'), read(draft / 'CONFIG.json')
assert c == {**disabled, 'ready_for_execution': True}
for name in read(draft / 'DRAFT-FILES.json'):
    if name != 'CONFIG.json':
        assert (RUN / name).read_bytes() == (draft / name).read_bytes(), name
state, before = read(RUN / 'STATE.json'), read(RUN / 'BEFORE.json')
resources = read(RUN / 'RESOURCES.json')
assert len(resources) == 312 and len(c['head_pins']) == 52
assert len(c['sources']) == 29 and len(c['modified_native_paths']) == 27
for name, digest in c['head_pins'].items():
    body = subprocess.check_output(['git', '-c', 'core.fsmonitor=false', 'show', c['head'] + ':' + name], cwd=ROOT)
    assert hashlib.sha256(body).hexdigest() == digest, name
for name, path in c['candidate_sources'].items():
    assert sha(ROOT / path) == c['candidate_pins'][name]
result, maps = {}, {}
for phase in ('baseline', 'candidate'):
    directory = RUN / ('wpt-' + phase)
    retained = read(directory / 'RUN.json')
    events = [json.loads(line) for line in (directory / 'raw.json').read_text().splitlines()]
    rows = [e for e in events if e.get('action') == 'test_status']
    starts = [e for e in events if e.get('action') == 'test_start']
    ends = [e for e in events if e.get('action') == 'test_end']
    assert rows == retained['rows'] and starts == retained['starts'] and ends == retained['ends']
    names = {(test, name) for test, roster in c['expected_subtests'].items() for name in roster}
    assert len(rows) == len(names) == len({(r['test'], r['subtest']) for r in rows}) == 27
    assert {(r['test'], r['subtest']) for r in rows} == names
    assert len(starts) == len(ends) == 4
    assert {r['test'] for r in starts} == {r['test'] for r in ends} == set(c['expected_subtests'])
    assert all(r['status'] == 'OK' for r in ends)
    assert all(r['status'] in ('PASS', 'FAIL') for r in rows)
    assert sum(e.get('action') == 'suite_start' for e in events) == 1
    assert sum(e.get('action') == 'suite_end' for e in events) == 1
    for event in events:
        action = event.get('action')
        assert action not in ('crash', 'suite_abort', 'test_abort')
        if action == 'log':
            assert event.get('level', '').upper() not in ('ERROR', 'CRITICAL')
        if action == 'process_exit':
            assert event.get('exitcode', event.get('returncode', 0)) == 0
        if action == 'assertion_count':
            assert event.get('min_expected', 0) <= event['count'] <= event.get('max_expected', 0)
        if action in ('log', 'process_output'):
            message = event.get('message', '') + event.get('data', '')
            assert not any(x in message for x in ('PROCESS-CRASH', 'TEST-UNEXPECTED-ERROR', 'TEST-UNEXPECTED-TIMEOUT'))
    assert retained['complete'] and retained['infrastructure_faults'] == []
    assert read(directory / 'CLEANUP.json') == {'owned_group_absent': True, 'errors': []}
    s = state['phases'][phase]
    assert s['build_exit'] == read(RUN / (phase + '-build.json'))['exit'] == 0
    snapshot = s['source_before_build']
    assert snapshot == s['source_after_build']
    assert all(snapshot[k] == before[k] for k in ('head', 'index_diff_sha256', 'index_entries_sha256'))
    sources = dict(c['head_pins'])
    if phase == 'candidate':
        sources.update(c['candidate_pins'])
    else:
        assert snapshot['native_diff_sha256'] == hashlib.sha256(b'').hexdigest()
    assert snapshot['sources'] == sources
    pins = {**resources, **sources, **s['binary_pins'], **{name: sha(RUN / path) for name, path in c['install'].items()}}
    assert retained['before'] == retained['after'] == pins
    counts = dict(collections.Counter(r['status'] for r in rows))
    assert counts == ({'PASS': 23, 'FAIL': 4} if phase == 'baseline' else {'PASS': 27})
    assert retained['exit'] == (1 if phase == 'baseline' else 0)
    maps[phase] = {(r['test'], r['subtest']): r for r in rows}
    result[phase] = {'counts': counts, 'files_ok': 4, 'source_guards': len(sources), 'role_pins': len(pins),
                     'binary_pins': s['binary_pins'], 'raw_sha256': sha(directory / 'raw.json'),
                     'run_sha256': sha(directory / 'RUN.json'), 'cleanup': True}
old, new = maps['baseline'], maps['candidate']
repaired = [key for key in old if old[key]['status'] == 'FAIL' and new[key]['status'] == 'PASS']
expected = {(c['main_tests'][0], kind + ': ' + direction + ' after viewport resize')
            for kind in ('scalar', 'list') for direction in ('percentage to px', 'px to percentage')}
assert set(repaired) == expected
for key in repaired:
    value = '200 but got 100' if ': percentage to px ' in key[1] else '25 but got 50'
    assert old[key]['message'] == 'assert_equals: conversion immediately after viewport resize expected ' + value
assert read(RUN / 'COMPARISON.json') == {'regressions': [], 'changed_failures': [], 'repaired': [list(k) for k in repaired], 'native_acceptance': False}
result.update(repaired=[list(k) for k in repaired], controls_preserved=23, pending_native_overlays_absent_in_both_phases=True,
              restored_epoch_verified=False, acceptance_recommendation='PENDING_TERMINAL_RESTORATION')
(HERE / 'PHASE-REVIEW.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
