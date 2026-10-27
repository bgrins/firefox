import ast
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
P = ROOT / 'artifacts/css-name-repeat-context-install-runtime-v2'
D = ROOT / 'artifacts/css-name-repeat-context-comparison-data-v1/data'
OLD = ROOT / 'artifacts/css-name-repeat-context-comparison-runtime-v1'

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def unique(pairs):
    d = {}
    for k, v in pairs:
        assert k not in d, k
        d[k] = v
    return d

def read(p):
    return json.loads(p.read_text(), object_pairs_hook=unique)

def auth(p, digest):
    assert sha(p / 'FILES.json') == digest
    m = read(p / 'FILES.json')
    for n, h in m.items():
        assert not Path(n).is_absolute() and '..' not in Path(n).parts
        assert sha(p / n) == h, n
    return m

manifest = auth(P, 'a1a4b7a98bfb4799acc9046e85f2d23e39bca814eb7d9cdb94119f84da45c41b')
assert len(manifest) == 40
inputs = read(P / 'INPUTS.json')
for n, h in inputs['manifests'].items():
    auth(ROOT / n, h)
for n, h in inputs['helper_pins'].items():
    assert sha(ROOT / n) == h
review = inputs['controller_review']
auth(ROOT / review['path'], review['manifest_sha256'])
assert sha(P / 'install.py') == inputs['install_sha256'] == '9bf9ca8cce3534eeaff2e0af0ada388baafc7a41c89e544ba57937abfac8ead0'
assert sha(P / 'DRAFT-FILES.json') == '6bb675d2bf1ce4d22824c10f57b2079f00337456c66e532b920df3dce3d35ac7'
for n, h in read(P / 'DRAFT-FILES.json').items():
    assert sha(P / ('INPUTS.disabled.json' if n == 'INPUTS.json' else n)) == h
old_inputs = read(P / 'INPUTS.disabled.json')
assert {k for k in inputs if inputs[k] != old_inputs[k]} == {'ready_for_execution', 'controller_review'}
assert inputs['ready_for_execution'] is True and inputs['actual_session'] is None and inputs['actual_exit'] is None
assert read(P / 'ROOT-REVIEW-BINDING.json') == {'status': 'NAME_REPEAT_INSTALL_ROOT_BINDING_GO', 'inputs_sha256': sha(P / 'INPUTS.json'), 'install_sha256': sha(P / 'install.py'), 'controller_review_manifest_sha256': review['manifest_sha256']}

before, final = read(P / 'BEFORE.json'), read(P / 'FINAL.json')
assert before == read(OLD / 'FINAL.json') == read(P / 'PRE-FLIGHT.json')
assert before['pins'] == read(OLD / 'FINAL-PINS.json')
assert final == read(P / 'candidate-PRE-CAPTURE.json')
assert final['pins'] == read(P / 'FINAL-PINS.json')
maps = read(D / 'SOURCE-MAPS.json')
assert before['snapshot']['sources'] == maps['baseline'] == maps['restored']
assert final['snapshot'] == read(OLD / 'candidate-PRE-CAPTURE.json')['snapshot']
assert final['snapshot']['sources'] == maps['candidate'] and len(maps['candidate']) == 72
for k in ('head', 'index_entries_sha256', 'index_diff_sha256'):
    assert before['snapshot'][k] == final['snapshot'][k]
changed = {k for k in maps['baseline'] if maps['baseline'][k] != maps['candidate'][k]}
assert changed == set(maps['bodies']) and len(changed) == 2
owned = read(P / 'OWNED-TESTS.json')
assert len(owned) == 1
landing = next(iter(owned)); url = '/' + landing.removeprefix('testing/web-platform/tests/')
assert final['installed_tests'] == {**before['installed_tests'], **owned}
assert len(before['installed_tests']) == 23 and len(final['installed_tests']) == 24
ownership = read(D / 'OWNERSHIP.json')
assert before['installed_tests'] == ownership['installed_identities']
assert before['pins'][landing] is None
assert owned[landing]['sha256'] == ownership['temporary_fixtures'][landing]['sha256']
assert owned[landing]['sha256'] == sha(ROOT / ownership['temporary_fixtures'][landing]['source'])
assert len(owned[landing]['identity']) == 2 and all(type(x) is int for x in owned[landing]['identity'])
bins = read(P / 'candidate-BINARIES.json')
expected_pins = {**before['pins'], **maps['candidate'], **bins, landing: owned[landing]['sha256']}
assert final['pins'] == expected_pins and len(expected_pins) == 611
for n in set(ownership['temporary_fixtures']) - {landing}:
    assert final['pins'][n] is None
for n in ownership['permanent_absences']:
    assert final['pins'][n] is None
build = read(P / 'candidate-BUILD-SOURCES.json')
assert build == {'before': maps['candidate'], 'after': maps['candidate'], 'binaries': bins, 'exit': 0}
assert read(P / 'candidate-build.json') == {'command': ['./mach', 'build', 'binaries'], 'exit': 0}
arch = read(P / 'candidate-ARCHITECTURE.json')
assert arch['binary_pins'] == bins
assert set(arch['binaries']) == set(bins)
for n, h in bins.items():
    assert arch['binaries'][n]['sha256'] == h and arch['binaries'][n]['bits'] == 64

config = read(P / 'CONFIG.json')
roster = read(D / 'ROSTER.json')
expected_config = read(OLD / 'CONFIG.json')
expected_config.update(tests=[landing], expected_subtests={url: roster['expected_subtests'][url]}, reftests=[], expected_total=10, files_expected_count=1, source_pins=maps['baseline'], guard_sources=sorted(maps['baseline']), resource_guard_paths=sorted(read(D / 'RESOURCES.json')), install={})
assert config == expected_config
assert len(config['modified_native_paths']) == 43 and set(config['modified_native_paths']) <= set(maps['baseline'])
assert len(config['index_expectations']['staged_payload_sha256']) == 925
run = read(P / 'wpt-candidate/RUN.json')
raw = [json.loads(l, object_pairs_hook=unique) for l in (P / 'wpt-candidate/raw.json').read_text().splitlines()]
for key, action in [('rows', 'test_status'), ('starts', 'test_start'), ('ends', 'test_end')]:
    assert run[key] == [e for e in raw if e.get('action') == action]
assert len(run['rows']) == 10 and len(run['starts']) == len(run['ends']) == 1
assert [r['subtest'] for r in run['rows']] == config['expected_subtests'][url]
assert all(r['status'] == 'PASS' and r.get('expected', 'PASS') == 'PASS' and not r.get('known_intermittent') for r in run['rows'])
assert run['ends'][0]['status'] == 'OK' and not run['ends'][0].get('known_intermittent')
assert run['before'] == run['after'] == final['pins'] and run['exit'] == 0 and run['complete'] is True and run['infrastructure_faults'] == []
assert run['command'] == ['./mach', 'wpt', '--headless', '--processes=1', '--log-raw=' + str(P / 'wpt-candidate/raw.json'), landing]
s = (ROOT / 'artifacts/css-accepted-119-121-122-install-runtime-v1/tests.py').read_text()
functions = [n for n in ast.parse(s).body if isinstance(n, ast.FunctionDef) and n.name in {'lifecycle', 'infrastructure_faults', 'exit_matches_results'}]
ns = {}; exec(compile(ast.Module(body=functions, type_ignores=[]), '<archived pure lifecycle functions>', 'exec'), ns)
assert ns['lifecycle'](raw, config) and not ns['infrastructure_faults'](raw)
assert ns['exit_matches_results'](0, run['rows'] + run['ends'])
assert read(P / 'wpt-candidate/CLEANUP.json') == {'owned_group_absent': True, 'errors': []}

def normalize(r):
    return {'test': r['test'], 'subtest': r['subtest'], 'status': r['status'], 'message': r.get('message'), 'expected': r.get('expected'), 'effective_expected': r.get('expected', r['status']), 'known_intermittent': r.get('known_intermittent', [])}
actual = {(r['test'], r['subtest']): normalize(r) for r in run['rows']}
archived = {(r['test'], r['subtest']): r for r in read(D / 'ARCHIVED-OUTCOMES.json') if r['test'] == url}
assert set(actual) == set(archived)
diffs = [{'baseline': archived[k], 'actual': v} for k, v in actual.items() if v != archived[k]]
assert diffs == read(P / 'candidate-DIFFERENCES.json') and len(diffs) == 8
assert read(P / 'candidate-IMPROVEMENTS.json') == [{**x, 'required_landing': True} for x in diffs]
assert all(x['baseline']['status'] == 'FAIL' and x['actual']['status'] == 'PASS' for x in diffs)
old_run = read(OLD / 'wpt-candidate/RUN.json')
assert [normalize(r) for r in old_run['rows'] if r['test'] == url] == list(actual.values())
summary = read(P / 'candidate-SUMMARY.json')
assert summary == {'status': 'LANDING_VALIDATION_PASS', 'subtests': 10, 'harnesses_ok': 1, 'reference_passes': 0, 'counts': {'PASS': 10, 'FAIL': 0}, 'required_repairs': 8, 'additional_improvements': 0, 'errors': [], 'wpt_exit': 0, 'native_acceptance': False}
result = read(P / 'RESULT.json')
transitions = [read(P / ('source-write-' + str(i) + '.json')) for i in (1, 2)]
assert {t['path'] for t in transitions} == changed
for t in transitions:
    assert t == {'path': t['path'], 'from': maps['baseline'][t['path']], 'to': maps['candidate'][t['path']], 'recovery': False}
assert result == {'status': 'ACCEPTED_FIX_INSTALLED', 'fix': 127, 'installed': True, 'restored': False, 'candidate_ready': True, 'completed_phases': ['candidate'], 'captured_phases': ['candidate'], 'installation_error': None, 'recovery_errors': [], 'source_transitions': transitions, 'mutation_started': True, 'new_native_acceptance': False}
assert read(P / 'CLEANUP.json') == {'removed': [], 'retained': [landing], 'errors': [], 'installation_error': None}
assert not any(n.startswith('RECOVERY-') for n in manifest) and not (P / 'RECOVERY-RESULT.json').exists()
assert sha(P / 'FINAL.json') == '90d47fefc000595e353ccaff6175ceb8c032d219fff1cdf82d63a4cfd88d54b1'
assert sha(P / 'ROOT-FINAL-CHECK.json') == '288f7e84f72dc69e6a578fbf2ccf04416c2de6f45947e91a1faa5d7e1aa0ce66'
root = read(P / 'ROOT-FINAL-CHECK.json'); completion = read(P / 'ROOT-COMPLETION.json')
assert root['installation_session'] == completion['installation_session'] == 63017
assert root['installation_exit'] == completion['installation_exit'] == 0
assert root['installation_terminal_chunk'] == completion['installation_terminal_chunk'] == 'dc3d7d'
assert completion['root_preservation_session'] == 78872 and completion['root_preservation_exit'] == 0
assert root['final_pins_sha256'] == sha(P / 'FINAL-PINS.json')
assert [root[k] for k in ['roles', 'sources', 'installed_identities', 'staged_payloads', 'working_staged_payloads', 'native_paths', 'landing_cases_pass']] == [611, 72, 24, 925, 925, 43, 10]
assert root['recovery_result_absent'] is True and root['new_native_acceptance'] is False
check = {'status': 'NAME_REPEAT_INSTALL_TERMINAL_REVIEW_GO', 'runtime_manifest': sha(P / 'FILES.json'), 'root_receipt': sha(P / 'ROOT-FINAL-CHECK.json'), 'actual_installation_session': 63017, 'actual_installation_exit': 0, 'root_preservation_session': 78872, 'root_preservation_exit': 0, 'raw_events': len(raw), 'landing_passes': 10, 'harness_ok': 1, 'repairs_matching_prior_full_comparison': 8, 'roles': 611, 'source_guards': 72, 'installed_identities': 24, 'staged_payloads': 925, 'native_paths': 43, 'prior_temporary_absences': 6, 'new_acceptance': False, 'live_inputs_read': False, 'scope': 'Archive joins and raw lifecycle; root live preservation observations are authenticated, not rerun.'}
(HERE / 'CHECK.json').write_text(json.dumps(check, indent=2) + '\n')
print(json.dumps(check, indent=2))
