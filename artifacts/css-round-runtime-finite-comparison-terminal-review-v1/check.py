import ast
from collections import Counter
import hashlib
import json
from pathlib import Path
import stat
import struct
import sys

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
A = ROOT / 'artifacts'
R = A / 'css-round-runtime-finite-comparison-runtime-v1'
D = A / 'css-round-runtime-finite-comparison-data-v1'
N = A / 'css-round-numerical-baseline-runtime-v1'
I = A / 'css-counter-additive-install-runtime-v1'


def body(p):
    assert p.is_relative_to(A) and stat.S_ISREG(p.lstat().st_mode)
    return p.read_bytes()


sha = lambda p: hashlib.sha256(body(p)).hexdigest()
read = lambda p: json.loads(body(p))
refs = dict(read(R / 'INPUTS.json')['references'])
refs.update({
    'artifacts/css-round-runtime-finite-comparison-runtime-v1/FILES.json': 'a934f55cf45b3c7aa9cab4d44a556591370d58b895097539849f49a4019c983d',
    'artifacts/css-round-runtime-finite-comparison-runtime-v1/ROOT-FINAL-CHECK.json': 'e977d381edbcbc7314909cf20fa3e76ed9dfbea18e49a5dfe0997c57e9cd7ea6',
    'artifacts/css-round-numerical-baseline-runtime-v1/FILES.json': '6488e9596b36cae63c72478be7d533b57812bdd2d680507807160b1d168cbd53',
    'artifacts/css-counter-additive-install-runtime-v1/FILES.json': 'dfe49f900d2ba34410520beabc165b0cb40639ca06fcc19ebe8dab1316b51bb5',
    'artifacts/css-accepted-119-121-122-install-runtime-v1/tests.py': '647ef06b5129e91cbace778a7231874c7a0468df1deb6f785ebdde6ad33566c5',
    'artifacts/css-round-runtime-finite-standalone-dependency-review-v1/FILES.json': 'b0617950c4ce68ddd579d64aff2448b295e79c3026f7f09e456cd45a01aa07b9',
})
for name, expected in refs.items():
    path = ROOT / name
    assert sha(path) == expected, name
    if path.name == 'FILES.json':
        for member, digest in read(path).items():
            assert not Path(member).is_absolute() and '..' not in Path(member).parts
            assert sha(path.parent / member) == digest, member
assert sha(R / 'compare.py') == read(R / 'INPUTS.json')['compare_sha256'] == '73bb0d38fa150eee1552665f3eeca1a47350e481535af7adc094ea6c01e637f1'
assert read(R / 'EXECUTION.json') == {'session': 27331, 'exit': 0,
    'command': 'python3 -I -S artifacts/css-round-runtime-finite-comparison-runtime-v1/compare.py'}
roster = read(D / 'ROSTER.json')
config = read(R / 'CONFIG.json')
expected_config = read(I / 'CONFIG.json')
expected_config.update(tests=['testing/web-platform/tests' + t for t in roster['tests']],
                       expected_subtests=roster['expected_subtests'], reftests=roster['reftests'],
                       expected_total=1484, files_expected_count=43)
assert config == expected_config
before = read(R / 'BEFORE.json')
assert before == read(N / 'FINAL.json')
restoration = read(D / 'RESTORATION-PINS.json')
assert restoration == read(N / 'FINAL-PINS.json') and len(restoration) == 605
assert read(R / 'PRE-FLIGHT.json') == {'preservation': before, 'pins': restoration}
maps = read(D / 'SOURCE-MAPS.json')['source_maps']
assert maps['baseline'] == before['snapshot']['sources'] and len(maps['baseline']) == 72
assert len(config['modified_native_paths']) == 42
index = config['index_expectations']
assert len(index['staged_paths']) == len(index['staged_payload_sha256']) == 925
assert set(index['staged_paths']) == set(index['staged_payload_sha256'])
assert all(before['snapshot'][k] == index[k] for k in ('head', 'index_entries_sha256', 'index_diff_sha256'))
owned = read(R / 'OWNED-TESTS.json')
ownership = read(D / 'OWNERSHIP.json')
assert set(owned) == set(ownership['temporary_fixtures']) and len(owned) == 6
assert before['installed_tests'] == ownership['installed_identities'] and len(before['installed_tests']) == 21
assert len({tuple(v['identity']) for v in owned.values()}) == 6
assert not {tuple(v['identity']) for v in owned.values()} & {tuple(v['identity']) for v in before['installed_tests'].values()}
for name, value in owned.items():
    plan = ownership['temporary_fixtures'][name]
    assert restoration[name] is None and value['sha256'] == plan['sha256'] == sha(ROOT / plan['source'])
helper = ast.parse(body(A / 'css-accepted-119-121-122-install-runtime-v1/tests.py'))
scope = {}
exec(compile(ast.Module(body=[n for n in helper.body if isinstance(n, ast.FunctionDef)
                             and n.name in ('lifecycle', 'infrastructure_faults', 'exit_matches_results')],
                        type_ignores=[]), '<pure lifecycle>', 'exec'), scope)
tree = ast.parse(body(R / 'compare.py'))
node = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'outcomes')
scope['config'] = config
exec(compile(ast.Module(body=[node], type_ignores=[]), '<pure outcomes>', 'exec'), scope)
archived = {(r['test'], r['subtest']): r for r in read(D / 'ARCHIVED-OUTCOMES.json')}
mandatory = read(D / 'MANDATORY.json')
phases = ['baseline_capture', 'runtime_nan_only', 'finite_zero_only', 'combined', 'restored']
observations, results = {}, {}
binary_names = set(read(I / 'BUILT-BINARIES.json'))
for phase in phases:
    source_phase = 'baseline' if phase in ('baseline_capture', 'restored') else phase
    binaries = ({n: restoration[n] for n in binary_names} if phase == 'baseline_capture'
                else read(R / (phase + '-BINARIES.json')))
    assert set(binaries) == binary_names and all(binaries.values())
    if phase != 'baseline_capture':
        assert read(R / (phase + '-build.json')) == {'command': ['./mach', 'build', 'binaries'], 'exit': 0}
        log = body(R / (phase + '-build.log')).decode()
        assert 'Your build was successful!' in log
        architecture = read(R / (phase + '-ARCHITECTURE.json'))
        assert architecture['status'] == 'SUPPORTED_64_BIT_PHASE_BINARIES' and architecture['binary_pins'] == binaries
        assert set(architecture['binaries']) == binary_names
        for name, record in architecture['binaries'].items():
            header = struct.unpack('<8I', bytes.fromhex(record['header_hex']))
            assert record['bits'] == 64 and record['sha256'] == binaries[name]
            assert header[0] == 0xFEEDFACF and header[1] == record['cpu_type'] == 16777228
    active = {**restoration, **maps[source_phase], **binaries,
              **{n: v['sha256'] for n, v in owned.items()}}
    run = read(R / ('wpt-' + phase) / 'RUN.json')
    events = [json.loads(line) for line in body(R / ('wpt-' + phase) / 'raw.json').splitlines()]
    assert run['complete'] is True and run['exit'] == 1
    assert run['before'] == run['after'] == active and len(active) == 605
    assert run['command'] == ['./mach', 'wpt', '--headless', '--processes=1',
                              '--log-raw=' + str(R / ('wpt-' + phase) / 'raw.json'), *config['tests']]
    for key, action in [('rows', 'test_status'), ('starts', 'test_start'), ('ends', 'test_end')]:
        assert run[key] == [e for e in events if e.get('action') == action]
    assert len(run['rows']) == 1484 and len(run['starts']) == len(run['ends']) == 43
    assert len({(r['test'], r['subtest']) for r in run['rows']}) == 1484
    assert {r['test'] for r in run['starts']} == set(roster['tests'])
    assert all([r['subtest'] for r in run['rows'] if r['test'] == test] == names
               for test, names in roster['expected_subtests'].items())
    assert Counter(r['status'] for r in run['ends']) == {'OK': 35, 'PASS': 8}
    assert scope['lifecycle'](events, config)
    assert scope['infrastructure_faults'](events) == run['infrastructure_faults'] == []
    assert scope['exit_matches_results'](run['exit'], run['rows'] + run['ends'])
    assert read(R / ('wpt-' + phase) / 'CLEANUP.json') == {'owned_group_absent': True, 'errors': []}
    actual = scope['outcomes'](run)
    assert set(actual) == set(archived) and len(actual) == 1492
    repairs = set()
    if source_phase != 'baseline':
        rules = mandatory['candidate_families']['combined_optional' if phase == 'combined' else phase]
        repairs = {(r['test'], r['subtest']) for r in rules['required_repairs']}
        assert all(actual[test, name]['status'] == 'PASS' for test, names in rules['required_pass'].items() for name in names)
    changed = {key for key in actual if actual[key] != archived[key]}
    assert changed == repairs
    assert all(archived[k]['status'] == 'FAIL' and actual[k]['status'] == 'PASS'
               and actual[k]['effective_expected'] == 'PASS' and actual[k]['known_intermittent'] == [] for k in repairs)
    differences = [{'baseline': archived[k], 'actual': v} for k, v in actual.items() if v != archived[k]]
    assert read(R / (phase + '-DIFFERENCES.json')) == differences
    assert all(actual[t, n]['status'] == 'PASS' for t, names in mandatory['installed_mandatory']['subtests'].items() for n in names)
    assert all(actual[t, None]['status'] == 'PASS' for t in config['reftests'])
    if phase == 'combined':
        for single in ('runtime_nan_only', 'finite_zero_only'):
            own = {(r['test'], r['subtest']) for r in mandatory['candidate_families'][single]['required_repairs']}
            assert {k for k in actual if actual[k] != observations[single][k]} == repairs - own
    summary = {'status': 'PHASE_COMPARISON_PASS', 'subtests': 1484, 'harnesses_ok': 35,
               'reference_passes': 8, 'required_repairs': len(repairs),
               'counts': dict(Counter(r['status'] for r in run['rows'])),
               'all_other_outcomes_exact': True, 'wpt_exit': 1}
    assert summary == read(R / (phase + '-SUMMARY.json'))
    observations[phase] = actual
    results[phase] = {'raw_records': len(events), **summary}
assert observations['restored'] == observations['baseline_capture'] == archived
assert read(R / 'CLEANUP.json') == {'removed': list(owned), 'errors': [], 'comparison_error': None}
final = read(R / 'FINAL.json')
assert final['snapshot'] == before['snapshot'] and final['installed_tests'] == before['installed_tests']
assert final['pins'] == read(R / 'FINAL-PINS.json') == {**restoration, **read(R / 'restored-BINARIES.json')}
assert all(final['pins'][n] is None for n in owned)
assert read(R / 'RESULT.json') == {'completed_phases': phases, 'comparison_error': None,
                                  'recovery_errors': [], 'native_acceptance': False}
assert read(R / 'ROOT-FINAL-CHECK.json') == {'status': 'ORIGINAL_STACK_RESTORED_VERIFIED',
    'full_roles': 605, 'source_count': 72, 'installed_identities': 21, 'staged_paths': 925,
    'native_paths': 42, 'completed_phases': phases, 'comparison_error': None, 'recovery_errors': [],
    'final_pins_sha256': sha(R / 'FINAL-PINS.json'), 'new_acceptance': False}
refs['artifacts/css-round-runtime-finite-comparison-runtime-v1/EXECUTION.json'] = sha(R / 'EXECUTION.json')
check = {'status': 'ROUND_RUNTIME_FINITE_TERMINAL_REVIEW_GO', 'session': 27331, 'exit': 0,
         'phases': results, 'sources': 72, 'roles': 605, 'installed_identities': 21,
         'staged_payloads': 925, 'native_paths_restored': 42, 'temporary_fixtures_removed': 6,
         'all_other_outcomes_exact': True, 'restored_original_outcomes_exact': True,
         'native_acceptance': False, 'live_inputs_read': False, 'live_actions': False}
for name, value in [('CHECK.json', check), ('REFERENCES.json', refs)]:
    with (HERE / name).open('x') as f:
        f.write(json.dumps(value, indent=2) + '\n')
print(json.dumps(check, indent=2))
