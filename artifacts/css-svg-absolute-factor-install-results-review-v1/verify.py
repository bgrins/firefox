import collections
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RUNTIME = ROOT / 'artifacts/css-svg-absolute-factor-install-runtime-v1'
read = lambda p: json.loads(p.read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(RUNTIME / 'FILES.json') == '5347ca14b0ab8cb5b7efface85c32a5441137943c9b7152b2d00026e677c8294'
manifest = read(RUNTIME / 'FILES.json')
for name, digest in manifest.items():
    assert sha(RUNTIME / name) == digest, name
c, state, root = [read(RUNTIME / f) for f in ('CONFIG.json', 'STATE.json', 'ROOT-FINAL-CHECK.json')]
before, final, install = [read(RUNTIME / f) for f in ('BEFORE.json', 'FINAL.json', 'INSTALLATION.json')]
assert root['status'] == 'INSTALLED_VERIFIED' and root['fix'] == 115 and root['exit'] == 0
assert root['state_sha256'] == sha(RUNTIME / 'STATE.json')
assert root['final_sha256'] == sha(RUNTIME / 'FINAL.json')
assert root['final_pins_sha256'] == sha(RUNTIME / 'FINAL-PINS.json')
assert state['status'] == 'terminal' and state['installed'] and not state['recovery_errors']
assert state['build_exit'] == state['lint_exit'] == 0 and 'failure' not in state
assert install['before'] == before and install['after'] == final
assert before['sources'] == c['source_pins']
assert final['sources'] == {**before['sources'], **c['candidate_pins']}
assert set(c['candidate_pins']) == {'dom/svg/SVGLength.cpp'}
assert all(final[k] == before[k] for k in ('head', 'index_diff_sha256', 'index_entries_sha256'))
assert root['native_modified_paths'] == len(c['modified_native_paths']) + 1 == 30
assert root['staged_paths'] == 925 and len(final['sources']) == root['source_count'] == 53
assert root['installed_tests'] == {**c['installed_tests'], **install['owned_tests']}
assert len(root['installed_tests']) == 7 and set(install['owned_tests']) == set(c['install'])
for name, item in install['owned_tests'].items():
    assert item['sha256'] == sha(RUNTIME / c['install'][name])
assert install['installed_source_pins'] == c['candidate_pins']
assert install['binary_pins'] == root['installed_binary_pins'] == state['installed_binary_pins']
assert install['acceptance_sha256'] == state['acceptance_sha256'] == c['acceptance_sha256']
assert sha(ROOT / c['acceptance']) == c['acceptance_sha256']
spec = importlib.util.spec_from_file_location('tests', ROOT / 'artifacts/css-svg-absolute-factor-comparison-v1/tests.py')
tests = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tests)
directory = RUNTIME / 'wpt-candidate'
events = [json.loads(line) for line in (directory / 'raw.json').read_text().splitlines()]
run = read(directory / 'RUN.json')
rows = [e for e in events if e.get('action') == 'test_status']
ends = [e for e in events if e.get('action') == 'test_end']
starts = [e for e in events if e.get('action') == 'test_start']
assert rows == run['rows'] and ends == run['ends'] and starts == run['starts']
keys = [(r['test'], r['subtest']) for r in rows]
assert len(keys) == len(set(keys)) == 16
assert set(keys) == {(name, label) for name, labels in c['expected_subtests'].items() for label in labels}
assert all(r['status'] == 'PASS' for r in rows)
assert len(ends) == len(starts) == 2 and all(e['status'] == 'OK' for e in ends)
assert {e['test'] for e in ends} == {e['test'] for e in starts} == set(c['expected_subtests'])
assert not tests.infrastructure_faults(events) and not run['infrastructure_faults']
assert run['exit'] == 0 and run['complete'] and run['before'] == run['after']
assert read(directory / 'CLEANUP.json') == {'owned_group_absent': True, 'errors': []}
pins = {**read(RUNTIME / 'RESOURCES.json'), **final['sources'],
        **{name: item['sha256'] for name, item in install['owned_tests'].items()},
        **state['installed_binary_pins']}
assert pins == read(RUNTIME / 'FINAL-PINS.json') == run['before']
assert len(pins) == root['pin_count'] == 383
result = {'runtime_files_sha256': sha(RUNTIME / 'FILES.json'), 'payloads_authenticated': len(manifest),
          'root_receipt_sha256': sha(RUNTIME / 'ROOT-FINAL-CHECK.json'),
          'raw_counts': dict(collections.Counter(r['status'] for r in rows)), 'files_ok': 2,
          'build_exit': 0, 'lint_exit': 0, 'sources': 53, 'pins': 383,
          'native_paths': 30, 'staged_paths': 925, 'installed_tests': 7,
          'binary_pins': state['installed_binary_pins'],
          'build_log_KeyErrors': (RUNTIME / 'installed-build.log').read_text().count('KeyError:'),
          'verdict': 'INSTALLED115_EVIDENCE_VERIFIED_HISTORICALLY'}
(HERE / 'CHECK.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
