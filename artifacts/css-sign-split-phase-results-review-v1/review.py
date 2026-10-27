import collections
import hashlib
import importlib.util
import json
import math
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
S = HERE / 'snapshot'
read = lambda p: json.loads(p.read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
c = read(S / 'CONFIG.json')
states = read(S / 'COMPLETED-PHASES.json')
before = read(S / 'BEFORE.json')
resources = read(S / 'RESOURCES.json')
policy = read(S / 'SEMANTIC-FAILURES.json')
roster = c['expected_subtests']
assert roster == read(S / 'ROSTER.json')
assert len(roster) == 13 and sum(map(len, roster.values())) == 1037
assert resources == c['resource_pins'] and len(resources) == 427
assert before == c['execution_snapshot']
fixtures = {p: sha(S / f) for p, f in c['install'].items()}
assert len(fixtures) == 2
assert resources['testing/web-platform/tests/css/css-values/sign-zero-font-basis.html'] is None
assert read(S / 'fixture-lint.json') == {
    'command': ['./mach', 'lint', '--linter', 'wpt', *c['install']], 'exit': 0}

fields = ('status', 'message', 'expected', 'known_intermittent')
maps = {}
reports = {}
raw_events = {}
for phase in ('baseline', 'raw_only', 'raw_plus_sign'):
    record = states[phase]
    source_map = dict(c['head_pins'])
    source_map.update({p: c['candidate_pins'][p] for p in c['phase_candidate_paths'][phase]})
    assert len(source_map) == 67 and set(source_map) == set(c['guard_sources'])
    assert record['source_before_build'] == record['source_after_build']
    assert record['source_before_build']['sources'] == source_map
    for key in ('head', 'index_diff_sha256', 'index_entries_sha256'):
        assert record['source_before_build'][key] == before[key]
    assert record['build_exit'] == 0
    assert read(S / (phase + '-build.json')) == {
        'command': ['./mach', 'build', 'binaries'], 'exit': 0}
    binaries = record['binary_pins']
    assert set(binaries) == set(read(S / 'ORIGINAL-BINARIES.json'))
    assert len(binaries) == 2 and all(re.fullmatch('[0-9a-f]{64}', h) for h in binaries.values())
    expected_pins = {**resources, **source_map, **fixtures, **binaries}
    run = read(S / f'wpt-{phase}/RUN.json')
    assert run['before'] == run['after'] == expected_pins
    raw_path = ROOT / 'artifacts/css-sign-zero-font-split-comparison-runtime-v1' / f'wpt-{phase}/raw.json'
    assert run['command'] == ['./mach', 'wpt', '--headless', '--processes=1',
                              '--log-raw=' + str(raw_path), *c['tests']]
    assert read(S / f'wpt-{phase}/CLEANUP.json') == {'owned_group_absent': True, 'errors': []}
    events = [json.loads(line) for line in (S / f'wpt-{phase}/raw.json').read_text().splitlines()]
    raw_events[phase] = events
    lifecycle = []
    rows, starts, ends = [], [], []
    active = set()
    done = set()
    for e in events:
        action = e.get('action')
        assert action not in ('crash', 'suite_abort', 'test_abort')
        assert not (action == 'log' and e.get('level', '').upper() in ('ERROR', 'CRITICAL'))
        if action == 'process_exit':
            assert e.get('exitcode', e.get('returncode', 0)) == 0
        if action == 'assertion_count':
            assert e.get('min_expected', 0) <= e['count'] <= e.get('max_expected', 0)
        if action in ('log', 'process_output'):
            text = e.get('message', '') + e.get('data', '')
            assert not any(x in text for x in ('PROCESS-CRASH', 'TEST-UNEXPECTED-ERROR', 'TEST-UNEXPECTED-TIMEOUT'))
        if action == 'suite_start':
            assert lifecycle == []
            lifecycle.append('start')
        elif action == 'suite_end':
            assert lifecycle == ['start'] and not active and done == set(roster)
            lifecycle.append('end')
        elif action == 'test_start':
            name = e['test']
            assert lifecycle == ['start'] and name in roster and name not in active | done
            active.add(name)
            starts.append(e)
        elif action == 'test_status':
            assert e['test'] in active and e['status'] in ('PASS', 'FAIL')
            rows.append(e)
        elif action == 'test_end':
            assert e['test'] in active and e['status'] == 'OK'
            active.remove(e['test'])
            done.add(e['test'])
            ends.append(e)
    assert lifecycle == ['start', 'end'] and len(starts) == len(ends) == 13
    assert len(rows) == len({(x['test'], x['subtest']) for x in rows}) == 1037
    for test, names in roster.items():
        assert [x['subtest'] for x in rows if x['test'] == test] == names
    assert run['rows'] == rows and run['starts'] == starts and run['ends'] == ends
    assert run['complete'] is True and run['infrastructure_faults'] == []
    unexpected = [x for x in rows + ends if x['status'] != x.get('expected', x['status'])
                  and x['status'] not in x.get('known_intermittent', [])]
    assert run['exit'] == int(bool(unexpected))
    landing = [x for x in rows if x['test'] in c['landing_tests']]
    assert len(landing) == 19
    failures = [x for x in landing if x['status'] == 'FAIL']
    for row in failures:
        rule = policy[row['subtest']]
        match = re.fullmatch(r'assert_equals: (.+) expected ([+-]?[\d.]+(?:e[+-]?\d+)?) but got ([+-]?[\d.]+(?:e[+-]?\d+)?)', row['message'])
        assert match
        label, expected, actual = match.groups()
        expected, actual = float(expected), float(actual)
        assert label in rule['assertions'] and expected == rule['assertions'][label]
        assert math.isfinite(actual) and actual != expected
        assert rule['actual_range'][0] <= actual <= rule['actual_range'][1]
    counts = dict(collections.Counter(x['status'] for x in rows))
    assert counts == record['subtests']
    landing_record = {'counts': {s: sum(x['status'] == s for x in landing) for s in ('PASS', 'FAIL')},
                      'failures': failures, 'calibration_failure_rejected': False,
                      'required_baseline_failure_count': None,
                      'later_semantic_assertions_after_failure': 'NOT_REACHED'}
    assert landing_record == read(S / (phase + '-LANDING.json'))
    maps[phase] = {(x['test'], x['subtest']): {key: x.get(key) for key in fields} for x in rows}
    reports[phase] = {'counts': counts, 'landing': landing_record['counts'],
                      'harness_OK': len(ends), 'wpt_exit': run['exit'],
                      'phase_pin_count': len(expected_pins), 'sources': source_map,
                      'binary_pins': binaries, 'landing_failures': failures,
                      'control_failures': [x for x in rows if x['test'] not in c['landing_tests'] and x['status'] == 'FAIL']}

comparisons = {}
for phase in ('raw_only', 'raw_plus_sign'):
    base, new = maps['baseline'], maps[phase]
    basis_name = c['phase_repair_basis'][phase]
    basis = maps[basis_name]
    assert base.keys() == new.keys() == basis.keys()
    for old in (base, basis):
        for key in old:
            assert old[key]['status'] != 'PASS' or new[key]['status'] == 'PASS', key
            if old[key]['status'] == new[key]['status'] == 'FAIL':
                assert old[key] == new[key], key
    repaired = [list(k) for k in base if base[k]['status'] == 'FAIL' and new[k]['status'] == 'PASS']
    own = [list(k) for k in basis if basis[k]['status'] == 'FAIL' and new[k]['status'] == 'PASS'
           and k[0] in c['phase_repair_tests'][phase]]
    assert own
    assert all(v['status'] == 'PASS' for k, v in new.items() if k[0] in c['phase_required_tests'][phase])
    comparison = {'status': 'PASSED', 'regressions': [], 'changed_failures': [],
                  'repaired': repaired, 'repair_basis_regressions': [],
                  'repair_basis_changed_failures': [], 'required_landing_failures': [],
                  'own_repaired': own, 'repair_basis': basis_name, 'native_acceptance': False}
    assert comparison == read(S / (phase + '-COMPARISON.json')) == states[phase]['semantic_comparison']
    comparisons[phase] = comparison

spec = importlib.util.spec_from_file_location('reference_parse', ROOT / 'artifacts/css-sign-split-final-checker-v1/parse.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
for phase in maps:
    values, counts, _ = module.phase(raw_events[phase], read(S / f'wpt-{phase}/RUN.json'), c, policy)
    assert values == maps[phase] and counts == reports[phase]['counts']
for phase, result in comparisons.items():
    assert module.compare(maps['baseline'], maps[phase], maps[c['phase_repair_basis'][phase]], c, phase) == result

result = {'status': 'PHASE_ONLY_GO', 'phases': reports, 'comparisons': comparisons,
          'native_acceptance': False, 'final_restoration_assessed': False,
          'live_source_binary_index_reads': False}
(HERE / 'CHECK.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps({'status': result['status'], 'counts': {p: r['counts'] for p, r in reports.items()},
                  'own_repairs': {p: len(r['own_repaired']) for p, r in comparisons.items()}}, indent=2))
