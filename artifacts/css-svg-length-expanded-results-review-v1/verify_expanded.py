import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RUN = ROOT / 'artifacts/css-svg-length-expanded-tests-runtime-v1'
def read(p):
    return json.loads(p.read_text())
def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()
def auth(p, base):
    for name, digest in read(p).items():
        assert sha(base / name) == digest, name

assert sha(RUN / 'FILES.json') == '22c11105d1682efb8c6fa33b6f4091b0902d32c4b756f3a9150493fc9df3a132'
auth(RUN / 'FILES.json', RUN)
assert len(read(RUN / 'FILES.json')) == 19
assert sha(RUN / 'INPUTS.json') == '3253a865558c2ae870001261229180b2105f151a075ec040f27ecd97e29e1870'
auth(RUN / 'INPUTS.json', RUN)
auth(RUN / 'REFERENCES.json', ROOT)
assert sha(RUN / 'ROOT-FINAL-CHECK.json') == '137197004e72e86af82950e2e3d54b14a5e44bd9978f368d7ecf69a8f677be9a'
c, before, final, state, receipt, owned, installation = [read(RUN / name) for name in
    ('CONFIG.json', 'BEFORE.json', 'FINAL.json', 'STATE.json', 'ROOT-FINAL-CHECK.json', 'OWNED-TEST.json', 'TEST-INSTALLATION.json')]
assert receipt['status'] == 'TEST_SCOPE_INSTALLED_VERIFIED' and receipt['session'] == 34175 and receipt['exit'] == 0
assert receipt['state_sha256'] == sha(RUN / 'STATE.json') and receipt['final_sha256'] == sha(RUN / 'FINAL.json')
assert state['status'] == 'terminal' and state['complete'] and state['expanded_test_installed']
assert state['native_changes'] is False and state['expanded_acceptance'] is False and 'failure' not in state
assert state['lint_exit'] == read(RUN / 'fixture-lint.json')['exit'] == receipt['lint_exit'] == 0
assert before['snapshot'] == final['snapshot'] and len(final['snapshot']['sources']) == receipt['source_count'] == 52
assert final['pins'] == {**before['pins'], owned['path']: owned['sha256']} == read(RUN / 'PHASE-PINS.json')
assert len(final['pins']) == receipt['pin_count'] == 372
assert before['pins'][owned['path']] is None
assert installation['before'] == before and installation['after'] == final and installation['owned_test'] == owned
assert receipt['native_modified_paths'] == 29 and receipt['staged_paths_preserved'] == 925
assert receipt['native_sources_index_binaries_unchanged'] and receipt['prior4_test_identities_preserved'] and receipt['new_font_test_identity_verified']
assert receipt['installed_tests'] == {**c['installed_tests'], owned['path']: {'identity': owned['identity'], 'sha256': owned['sha256']}}
prior = ROOT / 'artifacts/css-svg-length-conversion-install-runtime-v1'
assert read(prior / 'FINAL.json') == final['snapshot']
assert receipt['installed_binary_pins'] == read(prior / 'INSTALLATION.json')['binary_pins']
for name, digest in read(prior / 'FINAL-PINS.json').items():
    assert final['pins'][name] == digest
for name, digest in receipt['installed_binary_pins'].items():
    assert final['pins'][name] == digest
assert c['installed_tests'] == read(prior / 'ROOT-FINAL-CHECK.json')['installed_tests']

proposal = ROOT / 'artifacts/css-svg-length-conversion-expanded-v1'
assert sha(proposal / 'FILES.json') == '9e6c40f99394f444f8e889804869d16977d639fe1fdb0fd13fe6ab46352122a3'
auth(proposal / 'FILES.json', proposal)
patch = (proposal / 'standalone.patch').read_bytes()
oldpatch = (ROOT / 'artifacts/css-svg-length-conversion-repair-v1/standalone.patch').read_bytes()
assert patch.startswith(oldpatch) and patch.count(b'\n+++ b/') == 4 and oldpatch.count(b'\n+++ b/') == 3
assert sha(proposal / 'standalone.patch') == '71ba0fb56a7027b8e2721670b4cea8e36b351fcc33747fbdf2c84a623cedcde1'
assert sha(proposal / 'candidate' / owned['path']) == owned['sha256']
font_review = read(HERE / 'FONT-REVIEW.json')
for name, facts in font_review['phases'].items():
    phase = ROOT / 'artifacts' / name
    assert sha(phase / 'FILES.json') == facts['files_sha256']
    auth(phase / 'FILES.json', phase)
    assert sha(phase / 'wpt-font/raw.json') == facts['raw_sha256']
    assert (phase / 'fixture.html').read_bytes() == (proposal / 'candidate' / owned['path']).read_bytes()

run = read(RUN / 'wpt-expanded/RUN.json')
events = [json.loads(line) for line in (RUN / 'wpt-expanded/raw.json').read_text().splitlines()]
rows = [e for e in events if e.get('action') == 'test_status']
starts = [e for e in events if e.get('action') == 'test_start']
ends = [e for e in events if e.get('action') == 'test_end']
assert rows == run['rows'] and starts == run['starts'] and ends == run['ends']
assert len(rows) == len({(e['test'], e['subtest']) for e in rows}) == 15
assert {(e['test'], e['subtest']) for e in rows} == {(test, name) for test, names in c['expected_subtests'].items() for name in names}
assert all(e['status'] == 'PASS' for e in rows) and len(starts) == len(ends) == 2
assert {e['test'] for e in starts} == {e['test'] for e in ends} == set(c['expected_subtests'])
assert all(e['status'] == 'OK' for e in ends)
assert sum(e.get('action') == 'suite_start' for e in events) == sum(e.get('action') == 'suite_end' for e in events) == 1
assert run['complete'] and run['exit'] == 0 and run['infrastructure_faults'] == []
assert run['before'] == run['after'] == final['pins']
assert read(RUN / 'wpt-expanded/CLEANUP.json') == {'owned_group_absent': True, 'errors': []}
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
        assert not any(text in event.get('message', '') + event.get('data', '') for text in ('PROCESS-CRASH', 'TEST-UNEXPECTED-ERROR', 'TEST-UNEXPECTED-TIMEOUT'))
result = {'recommendation': 'SCOPED_TEST_EXPANSION_ACCEPTANCE_FOR_EXISTING_FIX114',
          'runtime_manifest_sha256': sha(RUN / 'FILES.json'), 'root_receipt_sha256': sha(RUN / 'ROOT-FINAL-CHECK.json'),
          'patch_sha256': sha(proposal / 'standalone.patch'), 'native_implementation_unchanged': True,
          'viewport_cases': 9, 'font_cases': 6, 'combined_pass': 15, 'files_ok': 2, 'lint_exit': 0,
          'font_repairs': 4, 'sources': 52, 'preserved_roles': 372, 'native_differences': 29,
          'staged_paths_preserved': 925, 'installed_test_identities': 5,
          'installed_binary_pins': receipt['installed_binary_pins'], 'new_native_build': False,
          'reviewer_native_index_browser_build_actions': False}
(HERE / 'EXPANDED-REVIEW.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
