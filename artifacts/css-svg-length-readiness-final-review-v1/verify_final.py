import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RUNTIME = ROOT / 'artifacts/css-svg-length-readiness-comparison-runtime-v1'
read = lambda p: json.loads(p.read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
manifest_sha = 'fcc56466c381827efcfc00e70fbfa418e90db7092b6eb4fa6440901e2321384d'
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
assert len(pins) == receipt['pin_count'] == 392
assert receipt['restored_binary_pins'] == state['restored_binary_pins']
assert receipt['installed_tests'] == c['epoch_receipt']['installed_tests']
assert len(receipt['installed_tests']) == 7
assert all(pins[n] == v['sha256'] for n, v in receipt['installed_tests'].items())
assert all(pins[n] is None for n in c['install'])
assert receipt['native_modified_paths'] == len(c['modified_native_paths']) == 30
assert receipt['staged_paths'] == 925
phase_review = ROOT / 'artifacts/css-svg-length-readiness-results-review-v2'
assert sha(phase_review / 'FILES.json') == 'efbb17211e8891e0b35eb9ebf520794bb07a2ec51daeb592d294f14ddee5b975'
for name, digest in read(phase_review / 'FILES.json').items():
    assert sha(phase_review / name) == digest
assert read(phase_review / 'COMPLETED-PHASE-RECEIPTS.json') == state['phases']
phases = read(phase_review / 'PHASES.json')
for phase in ('baseline', 'candidate'):
    assert sha(RUNTIME / ('wpt-' + phase) / 'raw.json') == phases['phases'][phase]['raw_sha256']
    assert sha(RUNTIME / ('wpt-' + phase) / 'RUN.json') == phases['phases'][phase]['run_sha256']
logs = {name: (RUNTIME / name).read_text(errors='replace').count('KeyError:')
        for name in ('baseline-build.log', 'candidate-build.log', 'restore-build.log')}
result = {'runtime_manifest_sha256': manifest_sha, 'payloads_authenticated': len(manifest),
          'root_receipt_sha256': sha(RUNTIME / 'ROOT-FINAL-CHECK.json'),
          'terminal_exit': 0, 'restore_build_exit': 0, 'restored_sources': 30,
          'source_guards': 53, 'persistent_role_pins': 392, 'staged_paths': 925,
          'old_native_paths': 30, 'old_installed_test_identities': 7,
          'restored_binary_pins': state['restored_binary_pins'],
          'retained_build_log_KeyErrors': logs,
          'historical_preservation_only': True,
          'recommendation': 'SCOPED_EXPANSION_OF114_TO25LANDING_CASES_NOT_INSTALLATION'}
(HERE / 'FINAL-REVIEW.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
