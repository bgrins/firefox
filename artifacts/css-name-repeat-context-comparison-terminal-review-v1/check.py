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
R = A / 'css-name-repeat-context-comparison-runtime-v1'
D = A / 'css-name-repeat-context-comparison-data-v1/data'
S = A / 'css-name-repeat-context-comparison-controller-review-v1'
B = A / 'css-name-repeat-context-baseline-runtime-v1'


def body(path):
    assert path.is_relative_to(A) and stat.S_ISREG(path.lstat().st_mode)
    return path.read_bytes()


def unique(pairs):
    assert len(dict(pairs)) == len(pairs)
    return dict(pairs)


def constant(value):
    raise ValueError(value)


loads = lambda text: json.loads(text, object_pairs_hook=unique, parse_constant=constant)
read = lambda path: loads(body(path))
sha = lambda path: hashlib.sha256(body(path)).hexdigest()
refs = {
    str((R / 'FILES.json').relative_to(ROOT)): '190b81b9b4296dd94646a42527c53c34e78a595dd34dd747b0f90e164bd04105',
    str((S / 'FILES.json').relative_to(ROOT)): '6cd41d2c2b27283354dae83c0398cb31f77b35fc86af294440438e3126270d90',
}
for name, digest in refs.items():
    path = ROOT / name
    assert sha(path) == digest
    for member, expected in read(path).items():
        assert not Path(member).is_absolute() and '..' not in Path(member).parts
        assert sha(path.parent / member) == expected
inputs = read(R / 'INPUTS.json')
disabled = read(S / 'REVIEWED-INPUTS.json')
assert read(R / 'INPUTS.disabled.json') == disabled
assert inputs == dict(disabled, ready_for_execution=True,
    controller_review={'path': str(S.relative_to(ROOT)), 'manifest_sha256': refs[str((S / 'FILES.json').relative_to(ROOT))]})
assert sha(R / 'compare.py') == inputs['compare_sha256'] == '303e3bd29f5e4acbd033d616ee83e8a33fa46b9bfe6dc1c2759afc230d61617d'
for name, digest in inputs['manifests'].items():
    path = ROOT / name / 'FILES.json'
    assert sha(path) == digest
    refs[str(path.relative_to(ROOT))] = digest
    for member, expected in read(path).items():
        assert not Path(member).is_absolute() and '..' not in Path(member).parts
        assert sha(path.parent / member) == expected
for name, digest in inputs['helper_pins'].items():
    assert sha(ROOT / name) == digest
assert read(R / 'ROOT-REVIEW-BINDING.json') == {'status': 'NAME_REPEAT_COMPARISON_ROOT_BINDING_GO',
    'inputs_sha256': sha(R / 'INPUTS.json'), 'compare_sha256': sha(R / 'compare.py'),
    'controller_review_manifest_sha256': refs[str((S / 'FILES.json').relative_to(ROOT))]}
assert read(R / 'ROOT-COMPLETION.json') == {'session': 92179, 'exit': 0,
    'terminal_tool_chunk': '86e078', 'status': 'CANDIDATE_AND_RESTORATION_COMPLETE',
    'candidate_installed': False, 'native_acceptance': False}
assert read(R / 'ROOT-EXECUTION.json') == {'session': 92179, 'status': 'RUNNING',
    'command': 'python3 -I -S artifacts/css-name-repeat-context-comparison-runtime-v1/compare.py',
    'native_acceptance': False}
before = read(R / 'BEFORE.json')
assert before == read(B / 'FINAL.json') == read(R / 'PRE-FLIGHT.json')
assert before['pins'] == read(D / 'RESTORATION-PINS.json') and len(before['pins']) == 611
maps = read(D / 'SOURCE-MAPS.json')
assert maps['baseline'] == maps['restored'] == before['snapshot']['sources']
assert len(maps['baseline']) == 72 and len(before['installed_tests']) == 23
roster = read(D / 'ROSTER.json')
config = read(B / 'CONFIG.json')
config.update({k: roster[k] for k in ('tests', 'expected_subtests', 'reftests')})
config['tests'] = ['testing/web-platform/tests' + name for name in roster['tests']]
config.update(expected_total=1532, files_expected_count=46, source_pins=maps['baseline'],
              guard_sources=sorted(maps['baseline']), resource_guard_paths=sorted(read(D / 'RESOURCES.json')), install={})
config['modified_native_paths'] = sorted(set(config['modified_native_paths']) | {'servo/components/style/values/generics/calc.rs'})
assert config == read(R / 'CONFIG.json') and len(config['modified_native_paths']) == 43
assert len(config['index_expectations']['staged_paths']) == len(config['index_expectations']['staged_payload_sha256']) == 925
owned = read(R / 'OWNED-TESTS.json')
planned = read(D / 'OWNERSHIP.json')
assert set(owned) == set(planned['temporary_fixtures']) and len(owned) == 7
assert len({tuple(v['identity']) for v in owned.values()}) == 7
assert not {tuple(v['identity']) for v in owned.values()} & {tuple(v['identity']) for v in before['installed_tests'].values()}
for name, value in owned.items():
    assert set(value) == {'identity', 'sha256'} and len(value['identity']) == 2
    assert all(type(v) is int for v in value['identity']) and before['pins'][name] is None
    assert value['sha256'] == planned['temporary_fixtures'][name]['sha256']
    assert sha(ROOT / planned['temporary_fixtures'][name]['source']) == value['sha256']
helper = A / 'css-accepted-119-121-122-install-runtime-v1/tests.py'
assert sha(helper) == '647ef06b5129e91cbace778a7231874c7a0468df1deb6f785ebdde6ad33566c5'
nodes = [n for n in ast.parse(body(helper)).body if isinstance(n, ast.FunctionDef)
         and n.name in ('infrastructure_faults', 'lifecycle', 'exit_matches_results')]
api = {}
assert len(nodes) == 3
exec(compile(ast.Module(body=nodes, type_ignores=[]), '<pure lifecycle functions>', 'exec'), api)
archived = {(r['test'], r['subtest']): r for r in read(D / 'ARCHIVED-OUTCOMES.json')}
policy = read(D / 'EXPERIMENT-POLICY.json')
repairs = {(r['test'], r['subtest']) for r in policy['observed_repair_witnesses']}
landing = {(r['test'], r['subtest']) for r in policy['candidate_required_PASS']}
assert len(archived) == 1540 and len(repairs) == 8 and len(landing) == 10
phase_records = {}


def normalize(row, subtest):
    return {'test': row['test'], 'subtest': subtest, 'status': row['status'],
            'message': row.get('message'), 'expected': row.get('expected'),
            'effective_expected': row.get('expected', row['status']),
            'known_intermittent': row.get('known_intermittent', [])}


for phase, counts in [('candidate', {'PASS': 1454, 'FAIL': 78}), ('restored', {'PASS': 1446, 'FAIL': 86})]:
    binaries = read(R / (phase + '-BINARIES.json'))
    assert set(binaries) == set(read(D / 'EPOCH.json')['baseline_binary_pins'])
    build = read(R / (phase + '-BUILD-SOURCES.json'))
    assert build == {'before': maps[phase], 'after': maps[phase], 'binaries': binaries, 'exit': 0}
    assert read(R / (phase + '-build.json')) == {'command': ['./mach', 'build', 'binaries'], 'exit': 0}
    architecture = read(R / (phase + '-ARCHITECTURE.json'))
    assert architecture['status'] == 'SUPPORTED_64_BIT_PHASE_BINARIES' and architecture['binary_pins'] == binaries
    assert set(architecture['binaries']) == set(binaries)
    for name, value in architecture['binaries'].items():
        assert value['bits'] == 64 and value['sha256'] == binaries[name]
        header = struct.unpack('<8I', bytes.fromhex(value['header_hex']))
        assert header[0] == 0xFEEDFACF and header[1] == value['cpu_type'] == 16777228
    pins = {**before['pins'], **maps[phase], **binaries, **{n: v['sha256'] for n, v in owned.items()}}
    assert len(pins) == 611
    pre = read(R / (phase + '-PRE-CAPTURE.json'))
    assert pre['pins'] == pins and pre['installed_tests'] == before['installed_tests']
    assert pre['snapshot']['sources'] == maps[phase]
    assert all(pre['snapshot'][k] == before['snapshot'][k] for k in ('head', 'index_diff_sha256', 'index_entries_sha256'))
    if phase == 'restored':
        assert pre['snapshot'] == before['snapshot']
    directory = R / ('wpt-' + phase)
    events = [loads(line) for line in body(directory / 'raw.json').splitlines()]
    run = read(directory / 'RUN.json')
    assert run['command'] == ['./mach', 'wpt', '--headless', '--processes=1',
                             '--log-raw=' + str(directory / 'raw.json'), *config['tests']]
    assert run['complete'] is True and run['before'] == run['after'] == pins
    assert not api['infrastructure_faults'](events) and run['infrastructure_faults'] == []
    assert api['lifecycle'](events, config) and api['exit_matches_results'](run['exit'], run['rows'] + run['ends'])
    assert run['exit'] == 1
    assert sum(e.get('action') == 'suite_start' for e in events) == sum(e.get('action') == 'suite_end' for e in events) == 1
    for key, action in [('rows', 'test_status'), ('starts', 'test_start'), ('ends', 'test_end')]:
        assert run[key] == [e for e in events if e.get('action') == action]
    assert len(run['rows']) == 1532 and Counter(r['status'] for r in run['rows']) == counts
    assert len(run['starts']) == len(run['ends']) == 46 and Counter(e['status'] for e in run['ends']) == {'OK': 38, 'PASS': 8}
    assert all([r['subtest'] for r in run['rows'] if r['test'] == name] == names for name, names in config['expected_subtests'].items())
    rows = [normalize(r, r['subtest']) for r in run['rows']]
    rows += [normalize(r, None) for r in run['ends'] if r['test'] in config['reftests']]
    values = {(r['test'], r['subtest']): r for r in rows}
    assert len(values) == len(rows) == 1540 and set(values) == set(archived)
    changed = {key for key in archived if values[key] != archived[key]}
    assert changed == (repairs if phase == 'candidate' else set())
    if phase == 'candidate':
        assert all(values[key]['status'] == 'PASS' and values[key]['effective_expected'] == 'PASS'
                   and values[key]['known_intermittent'] == [] for key in landing)
    differences = [{'baseline': archived[k], 'actual': v} for k, v in values.items() if v != archived[k]]
    improvements = [{'baseline': value, 'actual': values[key], 'required_landing': key in repairs}
                    for key, value in archived.items() if value['status'] == 'FAIL' and values[key]['status'] == 'PASS']
    assert read(R / (phase + '-DIFFERENCES.json')) == differences
    assert read(R / (phase + '-IMPROVEMENTS.json')) == improvements
    assert read(R / (phase + '-SUMMARY.json')) == {'status': 'PHASE_PRESERVATION_PASS_PENDING_REVIEW',
        'subtests': 1532, 'harnesses_ok': 38, 'reference_passes': 8, 'counts': counts,
        'required_repairs': 8 if phase == 'candidate' else 0, 'additional_improvements': 0,
        'errors': [], 'wpt_exit': 1, 'native_acceptance': False}
    assert read(directory / 'CLEANUP.json') == {'owned_group_absent': True, 'errors': []}
    phase_records[phase] = {'raw_records': len(events), 'counts': counts, 'harnesses_ok': 38,
                            'reftests_PASS': 8, 'changed_outcomes': len(changed), 'build_exit': 0, 'wpt_exit': 1}
transitions = []
for recovery, from_phase, to_phase in [(False, 'baseline', 'candidate'), (True, 'candidate', 'baseline')]:
    for name in maps['bodies']:
        value = {'path': name, 'from': maps[from_phase][name], 'to': maps[to_phase][name], 'recovery': recovery}
        transitions.append(value)
        assert read(R / ('source-write-' + str(len(transitions)) + '.json')) == value
assert read(R / 'RESULT.json') == {'completed_phases': ['candidate', 'restored'],
    'captured_phases': ['candidate', 'restored'], 'comparison_error': None, 'recovery_errors': [],
    'source_transitions': transitions, 'mutation_started': True, 'native_acceptance': False}
assert read(R / 'CLEANUP.json') == {'removed': list(owned), 'errors': [], 'comparison_error': None}
final_pins = {**before['pins'], **read(R / 'restored-BINARIES.json')}
assert read(R / 'FINAL-PINS.json') == final_pins
assert read(R / 'FINAL.json') == dict(before, pins=final_pins)
assert all(final_pins[name] is None for name in owned)
assert read(R / 'ROOT-FINAL-CHECK.json') == {'status': 'ORIGINAL_STACK_RESTORED_VERIFIED',
    'full_roles': 611, 'source_count': 72, 'installed_identities': 23, 'staged_paths': 925,
    'native_paths': 43, 'completed_phases': ['candidate', 'restored'], 'captured_phases': ['candidate', 'restored'],
    'comparison_error': None, 'recovery_errors': [], 'final_pins_sha256': sha(R / 'FINAL-PINS.json'), 'native_acceptance': False}
refs[str((R / 'ROOT-FINAL-CHECK.json').relative_to(ROOT))] = sha(R / 'ROOT-FINAL-CHECK.json')
check = {'status': 'NAME_REPEAT_COMPARISON_TERMINAL_REVIEW_GO', 'session': 92179,
    'exit': 0, 'terminal_tool_chunk': '86e078', 'phases': phase_records,
    'new_cases_PASS': 10, 'exact_repairs': 8, 'extra_improvements': 0, 'changed_retained_FAILURES': 0,
    'roles': 611, 'sources': 72, 'installed_identities': 23, 'staged_payloads': 925,
    'native_paths': 43, 'temporary_fixtures_removed': 7, 'sources_restored': True,
    'restored_capture_exact': True, 'candidate_installed': False,
    'native_acceptance': False, 'live_inputs_read': False, 'live_actions': False}
for name, value in [('CHECK.json', check), ('REFERENCES.json', refs)]:
    with (HERE / name).open('x') as stream:
        stream.write(json.dumps(value, indent=2) + '\n')
print(json.dumps(check, indent=2))
