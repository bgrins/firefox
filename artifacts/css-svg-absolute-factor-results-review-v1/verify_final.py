import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RUNTIME = ROOT / 'artifacts/css-svg-absolute-factor-comparison-runtime-v1'
read = lambda p: json.loads(p.read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
manifest_sha = '664b5832622ef0b013141ec2e98243866649284b24cc4fbacfd88f26dafe28c9'
assert sha(RUNTIME / 'FILES.json') == manifest_sha
manifest = read(RUNTIME / 'FILES.json')
for name, digest in manifest.items():
    assert sha(RUNTIME / name) == digest, name
state = read(RUNTIME / 'STATE.json')
receipt = read(RUNTIME / 'ROOT-FINAL-CHECK.json')
c = read(RUNTIME / 'CONFIG.json')
before, final = read(RUNTIME / 'BEFORE.json'), read(RUNTIME / 'FINAL.json')
assert receipt['status'] == 'RESTORED_VERIFIED' and receipt['exit'] == 0
assert receipt['state_sha256'] == sha(RUNTIME / 'STATE.json')
assert receipt['final_sha256'] == sha(RUNTIME / 'FINAL.json')
assert receipt['final_pins_sha256'] == sha(RUNTIME / 'FINAL-PINS.json')
assert state['status'] == 'terminal' and state['restored'] is True
assert state['restore_build_exit'] == 0 and not state['recovery_errors'] and 'failure' not in state
assert state['paired_preservation_passed'] and state['lint_exit'] == 0
assert final == before and final['sources'] == c['source_pins']
assert len(final['sources']) == receipt['source_count'] == 53
assert sorted(state['restored_paths']) == sorted(c['sources'])
assert len(c['sources']) == receipt['restored_original_paths'] == 30
for name in c['sources']:
    assert sha(RUNTIME / 'original' / name) == final['sources'][name], name
pins = read(RUNTIME / 'FINAL-PINS.json')
assert pins == {**read(RUNTIME / 'RESOURCES.json'), **final['sources'], **state['restored_binary_pins']}
assert len(pins) == receipt['pin_count'] == 383
assert receipt['restored_binary_pins'] == state['restored_binary_pins']
assert receipt['installed_tests'] == c['epoch_receipt']['installed_tests']
assert len(receipt['installed_tests']) == 5
assert all(pins[n] == v['sha256'] for n, v in receipt['installed_tests'].items())
assert all(pins[n] is None for n in c['install'])
assert receipt['native_modified_paths'] == len(c['modified_native_paths']) == 29
assert receipt['staged_paths'] == 925
phases = read(HERE / 'PHASES.json')
for phase in ('baseline', 'candidate'):
    assert sha(RUNTIME / ('wpt-' + phase) / 'raw.json') == phases['phases'][phase]['raw_sha256']
    assert sha(RUNTIME / ('wpt-' + phase) / 'RUN.json') == phases['phases'][phase]['run_sha256']
logs = {name: (RUNTIME / name).read_text(errors='replace').count('KeyError:')
        for name in ('baseline-build.log', 'candidate-build.log', 'restore-build.log')}
result = {'runtime_manifest_sha256': manifest_sha, 'payloads_authenticated': len(manifest),
          'root_receipt_sha256': sha(RUNTIME / 'ROOT-FINAL-CHECK.json'),
          'terminal_exit': 0, 'restore_build_exit': 0, 'restored_sources': 30,
          'source_guards': 53, 'persistent_role_pins': 383, 'staged_paths': 925,
          'old_native_paths': 29, 'old_installed_test_identities': 5,
          'restored_binary_pins': state['restored_binary_pins'],
          'retained_build_log_KeyErrors': logs,
          'historical_preservation_only': True,
          'recommendation': 'SCOPED_ACCEPTANCE_OF_EXACT_THREE_PATH_PROPOSAL'}
(HERE / 'FINAL-REVIEW.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
