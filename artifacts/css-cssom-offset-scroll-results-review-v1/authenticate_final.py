import hashlib
import json
from pathlib import Path

D = Path(__file__).resolve().parent
ROOT = D.parents[1]
R = ROOT / 'artifacts/css-cssom-offset-scroll-comparison-runtime-v1'
def read(p):
    return json.loads(p.read_text())
def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

assert sha(R / 'FILES.json') == '64d9b9edfef3ab226c91d530646b9ae0d7ace76524669ea8a2482f6fd571d7b8'
manifest = read(R / 'FILES.json')
for name, digest in manifest.items():
    assert sha(R / name) == digest, name
c, state = read(R / 'CONFIG.json'), read(R / 'STATE.json')
root_receipt = read(R / 'ROOT-FINAL-CHECK.json')
assert state['status'] == 'terminal' and state['restored'] is True
assert state['restore_build_exit'] == 0 and state['recovery_errors'] == [] and 'failure' not in state
assert state['paired_preservation_passed'] is True and state['baseline_reused'] is True
assert state['accepted_native_repair'] is False
assert state['restored_paths'] == c['sources'] and len(c['sources']) == 30
before, final = read(R / 'BEFORE.json'), read(R / 'FINAL.json')
assert before == final and final['sources'] == c['source_pins'] and len(final['sources']) == 47
for name in c['sources']:
    assert sha(R / 'original' / name) == final['sources'][name]
assert read(R / 'FINAL-PINS.json') == {**read(R / 'RESOURCES.json'),
    **final['sources'], **state['restored_binary_pins']}
assert len(read(R / 'FINAL-PINS.json')) == 318
assert root_receipt['status'] == 'COMPARISON_PASSED_RESTORATION_VERIFIED'
assert root_receipt['session'] == 64175 and root_receipt['exit'] == 0
for name in ('baseline_build_exit', 'candidate_build_exit', 'candidate_wpt_exit', 'restore_build_exit'):
    assert root_receipt[name] == 0
assert root_receipt['state_sha256'] == sha(R / 'STATE.json')
assert root_receipt['final_sha256'] == sha(R / 'FINAL.json')
assert root_receipt['restored_binary_pins'] == state['restored_binary_pins']
assert root_receipt['candidate_subtests'] == {'PASS': 137, 'FAIL': 4}
assert root_receipt['baseline_subtests'] == {'PASS': 53, 'FAIL': 8}
assert root_receipt['repairs'] == 8 and root_receipt['regressions'] == root_receipt['changed_failures'] == 0
for name in ('index_preserved', 'native_diff_preserved', 'owned_wpt_removed', 'both_cleanup_verified'):
    assert root_receipt[name] is True
assert root_receipt['native_acceptance'] is False
results = read(D / 'RESULTS.json')
for phase in ('baseline', 'candidate'):
    assert sha(R / ('wpt-' + phase) / 'raw.json') == results['raw_pins'][phase]
    assert sha(R / ('wpt-' + phase) / 'RUN.json') == results['run_pins'][phase]
    assert read(R / ('wpt-' + phase) / 'CLEANUP.json') == {'owned_group_absent': True, 'errors': []}
monitor_counts = {name: (R / name).read_text(errors='replace').count("KeyError: 'export'")
                  for name in ('baseline-build.log', 'candidate-build.log', 'restore-build.log')}
receipt = {'status': 'RESULTS_AND_HISTORICAL_RESTORATION_VERIFIED',
    'runtime_files_sha256': sha(R / 'FILES.json'), 'payloads_authenticated': len(manifest),
    'state_sha256': sha(R / 'STATE.json'), 'root_final_check_sha256': sha(R / 'ROOT-FINAL-CHECK.json'),
    'source_guards': 47, 'original_bodies': 30, 'restored_pin_map': 318,
    'head_and_index_snapshot_identical': True, 'root_verified_staged_payloads': 925,
    'restored_binary_pins': state['restored_binary_pins'], 'monitor_export_keyerror_counts': monitor_counts,
    'later_live_state_asserted': False, 'native_acceptance': False,
    'recommendation': 'ACCEPT_SCOPED_OFFSET_SCROLL_INTEGER_REPAIR',
    'scope': 'one Element.cpp helper and exact32-case WPT; root owns acceptance and packaging'}
(D / 'FINAL-REVIEW.json').write_text(json.dumps(receipt, indent=2) + '\n')
print(json.dumps(receipt))
