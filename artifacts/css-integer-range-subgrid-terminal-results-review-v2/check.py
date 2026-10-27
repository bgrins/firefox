import collections
import hashlib
import json
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
R = ROOT / 'artifacts/css-integer-range-subgrid-comparison-runtime-v2'
K = ROOT / 'artifacts/css-integer-range-subgrid-final-checker-bound-v2'
read = lambda p: json.loads(p.read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()

def auth(path, digest):
    assert sha(path) == digest
    items = read(path)
    for name, value in items.items():
        assert not Path(name).is_absolute() and '..' not in Path(name).parts
        assert sha(path.parent / name) == value, name
    return len(items)

payloads = auth(R / 'FILES.json', '2524cc5020c3a345648f5b8be02e0c102dd070fb23f446e35742da633fe65891')
checker_payloads = auth(K / 'FILES.json', '25fb1d6ed2eebbfa4d18d23234bf18ce2c04eb58718bd1a0fd4c979ad0dfffdf')
auth(ROOT / 'artifacts/css-integer-range-subgrid-terminal-results-review-v1/FILES.json', '3758160e4e0c7e90b2249b3ba3e06fd77fc23e676c659b583040198b17834dde')
for folder in (R, K):
    for name, digest in read(folder / 'REFERENCES.json').items():
        assert sha(ROOT / name) == digest, name
c, s, receipt = [read(R / n) for n in ('CONFIG.json', 'STATE.json', 'ROOT-FINAL-CHECK.json')]
assert sha(R / 'ROOT-FINAL-CHECK.json') == 'b25951fe40f10c65a55b48b754c3a4b3ccfedb7e5f04d525561807a3641dc3b0'
assert (R / 'ROOT-FINAL-CHECK.json').read_bytes() == (K / 'ROOT-FINAL-CHECK.json').read_bytes()
assert read(K / 'final-check.log') == receipt
b = read(K / 'CONFIG.json')
assert b['session'] == receipt['session'] == 92779 and b['session_exit'] == receipt['exit'] == 0
for field, name in [('runtime_draft_sha256', 'DRAFT-FILES.json'), ('state_sha256', 'STATE.json'), ('final_sha256', 'FINAL.json'), ('final_pins_sha256', 'FINAL-PINS.json')]:
    assert receipt[field] == sha(R / name)
assert b['terminal_state_sha256'] == receipt['state_sha256']
assert b['runtime_config_sha256'] == sha(R / 'CONFIG.json')
assert b['preflight_receipt_sha256'] == c['execution_receipt_sha256'] == sha(ROOT / c['execution_receipt'])
assert receipt['status'] == 'COMPARISON_PASSED_VERIFIED_RESTORED' and receipt['native_acceptance'] is False
assert s['status'] == 'terminal' and s['restored'] is True and s['restore_build_exit'] == 0
assert s['recovery_errors'] == [] and 'failure' not in s and s['campaign_completed'] and s['all_variants_passed']
assert s['accepted_native_repair'] is False and s['lint_exit'] == 0
assert read(R / 'fixture-lint.json') == {'command': ['./mach', 'lint', '--linter', 'wpt', *c['install']], 'exit': 0}
before, final = read(R / 'BEFORE.json'), read(R / 'FINAL.json')
assert before == final == c['execution_snapshot'] and final['sources'] == c['source_pins']
assert len(final['sources']) == 69 and len(c['sources']) == len(s['restored_paths']) == 42
assert set(c['sources']) == set(s['restored_paths'])
for name in c['sources']:
    assert sha(R / 'original' / name) == final['sources'][name]
assert len(c['modified_native_paths']) == len(set(c['modified_native_paths'])) == 36
index = c['index_expectations']
assert len(index['staged_paths']) == len(set(index['staged_paths'])) == 925
for field in ('head', 'index_entries_sha256', 'index_diff_sha256'):
    assert final[field] == index[field]
assert receipt['installed_tests'] == c['installed_tests'] and len(c['installed_tests']) == 11
resources = read(R / 'RESOURCES.json')
assert resources == c['resource_pins'] and len(resources) == 461
binaries = s['restored_binary_pins']
assert binaries == receipt['restored_binary_pins'] and len(binaries) == 2
final_pins = read(R / 'FINAL-PINS.json')
assert final_pins == {**resources, **final['sources'], **binaries} and len(final_pins) == 532
assert all(name in final_pins and final_pins[name] is None for name in c['install'])
for name, item in c['installed_tests'].items():
    assert final_pins[name] == item['sha256'] and len(item['identity']) == 2
assert receipt['phase_errors'] == {} and receipt['failure'] is None and receipt['all_variants_passed']
assert [receipt[k] for k in ('source_count', 'saved_sources', 'resource_count', 'pin_count', 'native_modified_paths', 'staged_paths')] == [69, 42, 461, 532, 36, 925]

roster = read(R / 'ROSTER.json')
assert roster == c['expected_subtests'] and sum(map(len, roster.values())) == 339
refs = set(c['reftests'])
assert len(refs) == 6 and len(roster) == 15 and not refs & set(roster)
expected_names = {(t, n) for t, names in roster.items() for n in names}
fixtures = {n: sha(R / f) for n, f in c['install'].items()}
maps = read(R / 'PHASE-SOURCE-MAPS.json')
values, counts, repairs = {}, {}, {}
fields = ('status', 'message', 'expected', 'known_intermittent')
for phase in ('baseline', 'range_only', 'cache_only', 'combined'):
    d = R / ('wpt-' + phase)
    run = read(d / 'RUN.json')
    events = [json.loads(line) for line in (d / 'raw.json').read_text().splitlines()]
    rows, starts, ends, active, finished = [], [], [], set(), set()
    opened = closed = False
    for e in events:
        a = e.get('action')
        assert a not in ('crash', 'suite_abort', 'test_abort')
        assert not (a == 'log' and e.get('level', '').upper() in ('ERROR', 'CRITICAL'))
        if a == 'process_exit': assert e.get('exitcode', e.get('returncode', 0)) == 0
        if a == 'assertion_count': assert e.get('min_expected', 0) <= e['count'] <= e.get('max_expected', 0)
        if a in ('log', 'process_output'):
            assert not any(x in e.get('message', '') + e.get('data', '') for x in ('PROCESS-CRASH', 'TEST-UNEXPECTED-ERROR', 'TEST-UNEXPECTED-TIMEOUT'))
        if a == 'suite_start':
            assert not opened and not closed
            opened = True
        elif a == 'suite_end':
            assert opened and not active and finished == set(roster) | refs
            opened, closed = False, True
        elif a == 'test_start':
            assert opened and e['test'] in set(roster) | refs and e['test'] not in active | finished
            active.add(e['test']); starts.append(e)
        elif a == 'test_status':
            assert opened and e['test'] in active and e['test'] in roster and e['status'] in ('PASS', 'FAIL')
            rows.append(e)
        elif a == 'test_end':
            assert opened and e['test'] in active and e['status'] == ('PASS' if e['test'] in refs else 'OK')
            active.remove(e['test']); finished.add(e['test']); ends.append(e)
    assert closed and not opened and len(starts) == len(ends) == 21
    assert len(rows) == len({(e['test'], e['subtest']) for e in rows}) == 339
    assert {(e['test'], e['subtest']) for e in rows} == expected_names
    for test, names in roster.items(): assert [e['subtest'] for e in rows if e['test'] == test] == names
    assert run['rows'] == rows and run['starts'] == starts and run['ends'] == ends
    assert run['complete'] is True and run['infrastructure_faults'] == []
    unexpected = any(e['status'] != e.get('expected', e['status']) and e['status'] not in e.get('known_intermittent', []) for e in rows + ends)
    assert run['exit'] == int(unexpected)
    assert read(d / 'CLEANUP.json') == {'owned_group_absent': True, 'errors': []}
    record = s['phases'][phase]
    assert record['build_exit'] == 0 and read(R / (phase + '-build.json')) == {'command': ['./mach', 'build', 'binaries'], 'exit': 0}
    phase_sources = {**c['head_pins'], **{n: c['candidate_pins'][n] for n in c['phase_candidate_paths'][phase]}}
    assert phase_sources == maps[phase] == record['source_before_build']['sources']
    assert record['source_before_build'] == record['source_after_build']
    for field in ('head', 'index_entries_sha256', 'index_diff_sha256'): assert record['source_before_build'][field] == before[field]
    if phase == 'baseline': assert record['source_before_build']['native_diff_sha256'] == hashlib.sha256(b'').hexdigest()
    assert run['before'] == run['after'] == {**resources, **phase_sources, **fixtures, **record['binary_pins']}
    arch = read(R / (phase + '-BINARY-ARCHITECTURE.json'))
    assert sha(R / (phase + '-BINARY-ARCHITECTURE.json')) == record['binary_architecture_sha256']
    assert arch['status'] == 'SUPPORTED_64_BIT_PHASE_BINARIES' and arch['binary_pins'] == record['binary_pins']
    cpus = set()
    for n, row in arch['binaries'].items():
        header = bytes.fromhex(row['header_hex'])
        magic, cpu, _, kind, commands, extent, _, _ = struct.unpack('<8I', header)
        assert magic == 0xfeedfacf and cpu in (0x1000007, 0x100000c) and row['bits'] == 64
        assert kind == (2 if Path(n).name == 'firefox' else 6) and commands > 0 and 8 * commands <= extent <= row['size'] - 32
        assert row['sha256'] == record['binary_pins'][n]
        cpus.add(cpu)
    assert len(cpus) == 1 and len(arch['binaries']) == 2
    count = dict(collections.Counter(e['status'] for e in rows))
    counts[phase] = count
    rr = receipt['phases'][phase]
    assert rr['subtests'] == count == {k: v for k, v in record['subtests'].items() if v}
    assert rr['source_pins'] == phase_sources and rr['binary_pins'] == record['binary_pins']
    assert rr['raw_sha256'] == sha(d / 'raw.json') and rr['run_sha256'] == sha(d / 'RUN.json')
    assert rr['phase_pin_count'] == len(run['before']) == 532 and rr['harness_OK'] == 15
    landing = read(R / (phase + '-LANDING.json'))
    main = [e for e in rows if e['test'] in c['landing_tests']]
    assert len(main) == 31 and landing['failures'] == [e for e in main if e['status'] == 'FAIL']
    assert landing['counts'] == {v: sum(e['status'] == v for e in main) for v in ('PASS', 'FAIL')}
    assert all(e['message'].startswith(('assert_equals: computed count honors its range expected ', 'assert_equals: calculated zero and literal one resolve to the same names expected ', 'assert_equals: large fixed repeat leaves no auto-fill capacity expected ')) for e in landing['failures'])
    values[phase] = {(e['test'], e['subtest']): {k: e.get(k) for k in fields} for e in rows}
    values[phase].update({(e['test'], '<reftest>'): {k: e.get(k) for k in fields} for e in ends if e['test'] in refs})

for phase in ('range_only', 'cache_only', 'combined'):
    old, new = values['baseline'], values[phase]
    assert old.keys() == new.keys()
    comparisons = read(R / (phase + '-COMPARISON.json'))
    assert comparisons == s['phases'][phase]['semantic_comparison'] == receipt['variants'][phase]
    assert comparisons['status'] == 'PASSED' and comparisons['native_acceptance'] is False
    for basis in c['phase_preservation_bases'][phase]:
        for identity, value in values[basis].items():
            if value['status'] == 'PASS': assert new[identity]['status'] == 'PASS'
            elif new[identity]['status'] == 'FAIL': assert new[identity] == value
        assert comparisons['preservation'][basis] == {'regressions': [], 'changed_failures': []}
    repaired = [list(k) for k in old if old[k]['status'] == 'FAIL' and new[k]['status'] == 'PASS']
    assert comparisons['repaired'] == repaired
    own = [k for k in repaired if k[0] in c['phase_repair_tests'][phase]]
    assert own and comparisons['own_repaired'] == own
    assert comparisons['required_landing_failures'] == []
    assert all(v['status'] == 'PASS' for k, v in new.items() if k[0] in c['phase_required_tests'][phase])
    repairs[phase] = repaired
assert {tuple(k) for k in repairs['combined']} == {tuple(k) for k in repairs['range_only'] + repairs['cache_only']}
assert counts == {'baseline': {'PASS': 291, 'FAIL': 48}, 'range_only': {'PASS': 299, 'FAIL': 40}, 'cache_only': {'PASS': 297, 'FAIL': 42}, 'combined': {'PASS': 305, 'FAIL': 34}}
print(json.dumps({'status': 'INTEGER_RANGE_SUBGRID_TERMINAL_RESULTS_GO', 'runtime_payloads_authenticated': payloads, 'checker_payloads_authenticated': checker_payloads, 'counts': counts, 'reftests_pass_each_phase': 6, 'harness_OK_each_phase': 15, 'repairs': repairs, 'restored': True, 'source_count': 69, 'saved_sources': 42, 'resources': 461, 'final_pins': 532, 'native_modified_paths': 36, 'staged_paths': 925, 'installed_identities': 11, 'restored_binary_pins': binaries, 'native_acceptance': False, 'live_checks_repeated': False}, indent=2))
