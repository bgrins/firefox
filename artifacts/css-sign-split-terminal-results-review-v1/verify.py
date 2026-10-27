import hashlib
import importlib.util
import json
import pathlib
import sys

sys.dont_write_bytecode = True
ROOT = pathlib.Path(__file__).resolve().parents[2]
HERE = pathlib.Path(__file__).resolve().parent
R = ROOT / 'artifacts/css-sign-zero-font-split-comparison-runtime-v1'
P = ROOT / 'artifacts/css-sign-split-phase-results-review-v1'
B = ROOT / 'artifacts/css-sign-split-final-checker-bound-v1'
D = ROOT / 'artifacts/css-sign-split-final-checker-v1'


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def read(p):
    return json.loads(p.read_text())


def auth(path, expected):
    assert sha(path) == expected, str(path)
    manifest = read(path)
    for name, digest in manifest.items():
        assert sha(path.parent / name) == digest, name
    return len(manifest)


refs = {
    R / 'FILES.json': '1d748303cc2fd6fc3443af98074443c6d2fb7b693b23bcb25c7566eb0b05b142',
    B / 'FILES.json': '6283d925461d87aeb388dd3b0808a78bf65aaa1576380557691542ff12ded585',
    P / 'FILES.json': '1416ea92142aaaef3898f07f2f1451ecf975468f2bfc2425b19b379d0235db24',
    D / 'DRAFT-FILES.json': '2b3f974511094aceec58e872c9e49a82d670c5c9998580522e2c4133ad67bbfd',
}
counts = {str(p.relative_to(ROOT)): auth(p, h) for p, h in refs.items()}
root_digest = 'b818caeada36694d29e3c0365367928bfc1870ed961860a54810bcf5af859466'
assert sha(R / 'ROOT-FINAL-CHECK.json') == root_digest
assert (R / 'ROOT-FINAL-CHECK.json').read_bytes() == (B / 'ROOT-FINAL-CHECK.json').read_bytes()
assert sha(B / 'DRAFT-FILES.json') == '958c09fc6cf1b47630b0a0f9ad3723d609c8a6a1085710d9b7539b288f2e23b1'
execution = read(B / 'EXECUTION.json')
assert execution['session'] == 24470 and execution['exit'] == 0
assert execution['campaign_session'] == 80904 and execution['campaign_exit'] == 0
assert execution['root_receipt_sha256'] == root_digest
assert execution['checker_draft_sha256'] == sha(B / 'DRAFT-FILES.json')
for name in read(D / 'DRAFT-FILES.json'):
    if name != 'CONFIG.json':
        assert (B / name).read_bytes() == (D / name).read_bytes(), name
old, bound = read(D / 'CONFIG.json'), read(B / 'CONFIG.json')
assert {k for k in old if old[k] != bound[k]} == {'ready_for_execution', 'session_exit', 'terminal_state_sha256'}
assert bound['ready_for_execution'] and bound['session_exit'] == 0 and bound['session'] == 80904
assert sha(R / 'STATE.json') == bound['terminal_state_sha256']
assert execution['terminal_state_sha256'] == bound['terminal_state_sha256']
c, state, receipt = [read(R / n) for n in ['CONFIG.json', 'STATE.json', 'ROOT-FINAL-CHECK.json']]
assert receipt['session'] == 80904 and receipt['exit'] == 0
assert receipt['state_sha256'] == sha(R / 'STATE.json')
assert receipt['final_sha256'] == sha(R / 'FINAL.json')
assert receipt['final_pins_sha256'] == sha(R / 'FINAL-PINS.json')
capture = read(P / 'CAPTURE.json')
for name, item in capture['files'].items():
    assert sha(R / name) == item['sha256'] and (R / name).stat().st_size == item['bytes'], name
assert state['phases'] == read(P / 'snapshot/COMPLETED-PHASES.json')
before, final = read(R / 'BEFORE.json'), read(R / 'FINAL.json')
assert before == final == c['execution_snapshot']
assert final['sources'] == c['source_pins'] and len(final['sources']) == 67
assert len(c['sources']) == len(state['restored_paths']) == 40
assert set(c['sources']) == set(state['restored_paths'])
modified = {n for n, h in final['sources'].items() if h != c['head_pins'][n]}
assert modified == set(c['modified_native_paths']) and len(modified) == 36
assert set(c['sources']) == modified | set(c['candidate_pins'])
for n in c['sources']:
    assert sha(R / 'original' / n) == before['sources'][n]
idx = c['index_expectations']
for k in ['head', 'index_entries_sha256', 'index_diff_sha256']:
    assert idx[k] == final[k]
assert len(idx['staged_paths']) == len(set(idx['staged_paths'])) == 925
resources = read(R / 'RESOURCES.json')
assert resources == c['resource_pins'] and len(resources) == 427
binaries = state['restored_binary_pins']
assert binaries == receipt['restored_binary_pins']
assert set(binaries) == set(read(R / 'ORIGINAL-BINARIES.json')) and len(binaries) == 2
final_pins = {**resources, **final['sources'], **binaries}
assert read(R / 'FINAL-PINS.json') == final_pins and len(final_pins) == receipt['pin_count'] == 496
ids = receipt['installed_tests']
assert ids == c['installed_tests'] == c['epoch_receipt']['installed_tests'] and len(ids) == 11
for n, item in ids.items():
    assert final_pins[n] == item['sha256'] and len(item['identity']) == 2
fixtures = {n: sha(R / f) for n, f in c['install'].items()}
assert len(fixtures) == 2
assert all(final_pins.get(n) is None for n in fixtures)
assert sum(n in resources and resources[n] is None for n in fixtures) == 1
spec = importlib.util.spec_from_file_location('terminal_review_parse', D / 'parse.py')
parser = importlib.util.module_from_spec(spec)
spec.loader.exec_module(parser)
values, summaries = {}, {}
policy = read(R / 'SEMANTIC-FAILURES.json')
for phase in parser.PHASES:
    record = state['phases'][phase]
    expected_sources, expected_pins = parser.phase_pins(c, before, resources, fixtures, record, phase, binaries)
    run = read(R / ('wpt-' + phase) / 'RUN.json')
    events = [json.loads(line) for line in (R / ('wpt-' + phase) / 'raw.json').read_text().splitlines()]
    assert run['before'] == run['after'] == expected_pins
    values[phase], tally, landing = parser.phase(events, run, c, policy)
    assert read(R / (phase + '-LANDING.json')) == landing
    assert read(R / (phase + '-build.json')) == {'command': ['./mach', 'build', 'binaries'], 'exit': 0}
    assert record['build_exit'] == 0
    assert read(R / ('wpt-' + phase) / 'CLEANUP.json') == {'owned_group_absent': True, 'errors': []}
    report = receipt['phases'][phase]
    assert report['source_pins'] == expected_sources and report['binary_pins'] == record['binary_pins']
    assert report['subtests'] == tally and report['landing'] == landing['counts']
    assert report['raw_sha256'] == sha(R / ('wpt-' + phase) / 'raw.json')
    assert report['run_sha256'] == sha(R / ('wpt-' + phase) / 'RUN.json')
    assert len(expected_pins) == report['phase_pin_count'] == 497
    summaries[phase] = {'subtests': tally, 'landing': landing['counts'], 'harness_OK': report['harness_OK']}
comparisons = {}
for phase in parser.PHASES[1:]:
    basis = c['phase_repair_basis'][phase]
    comparison = parser.compare(values['baseline'], values[phase], values[basis], c, phase)
    assert comparison == read(R / (phase + '-COMPARISON.json')) == state['phases'][phase]['semantic_comparison'] == receipt['variants'][phase]
    comparisons[phase] = comparison
assert parser.terminal(state, 0, {}, comparisons) == receipt['status'] == 'COMPARISON_PASSED_VERIFIED_RESTORED'
assert receipt['native_acceptance'] is False and receipt['phase_errors'] == {}
assert {k: receipt[k] for k in ['source_count', 'saved_sources', 'resource_count', 'native_modified_paths', 'staged_paths']} == {'source_count': 67, 'saved_sources': 40, 'resource_count': 427, 'native_modified_paths': 36, 'staged_paths': 925}
refs[R / 'ROOT-FINAL-CHECK.json'] = root_digest
out = {'status': 'SCOPED_RESULTS_AND_ARCHIVED_RESTORATION_GO', 'authenticated_capsules': counts,
       'phase_capture_files_rejoined': len(capture['files']), 'phases': summaries,
       'comparisons': comparisons, 'source_count': 67, 'saved_sources': 40,
       'resource_count': 427, 'final_pin_count': 496, 'native_modified': 36,
       'staged_paths': 925, 'installed_test_identities': 11, 'restored_binary_pins': binaries,
       'campaign_session': 80904, 'campaign_exit': 0, 'root_checker_session_reported': 24470,
       'root_live_corroboration': 'Authenticated root receipt; this review performs no live filesystem/index/binary recheck.',
       'acceptance_recommendation': 'Raw transport scoped acceptance supported; Sign scoped acceptance supported only with raw prerequisite. No fix numbers assigned.',
       'native_acceptance_assigned_by_review': False}
(HERE / 'CHECK.json').write_text(json.dumps(out, indent=2, sort_keys=True) + '\n')
(HERE / 'REFERENCES.json').write_text(json.dumps({str(p.relative_to(ROOT)): h for p, h in refs.items()}, indent=2, sort_keys=True) + '\n')
print(json.dumps({'status': out['status'], 'final_pin_count': 496, 'phases': summaries}))
