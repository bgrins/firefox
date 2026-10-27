import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
RUNTIME = HERE.parent / 'css-hidden-svg-matrix-comparison-runtime-v1'
read = lambda p: json.loads(p.read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(RUNTIME / 'FILES.json') == 'd10d6ec3f6e539976bab64fef087e5ab00a12a54692a78f069b98a86a8aa7685'
manifest = read(RUNTIME / 'FILES.json')
assert len(manifest) == 76
for name, digest in manifest.items():
    assert sha(RUNTIME / name) == digest, name
c = read(RUNTIME / 'CONFIG.json')
state, root = read(RUNTIME / 'STATE.json'), read(RUNTIME / 'ROOT-FINAL-CHECK.json')
before, final = read(RUNTIME / 'BEFORE.json'), read(RUNTIME / 'FINAL.json')
assert state['status'] == 'terminal' and state['restored'] is True
assert state['paired_preservation_passed'] is True and state['recovery_errors'] == []
assert 'failure' not in state and state['restore_build_exit'] == 0
assert set(state['restored_paths']) == set(c['sources']) and len(state['restored_paths']) == 27
assert before == final and final['sources'] == c['source_pins'] and len(final['sources']) == 50
for name in c['sources']:
    assert sha(RUNTIME / 'original' / name) == before['sources'][name]
assert root['status'] == 'RESTORED_VERIFIED' and root['session'] == 85899 and root['exit'] == 0
assert root['state_sha256'] == sha(RUNTIME / 'STATE.json')
assert root['final_sha256'] == sha(RUNTIME / 'FINAL.json')
assert root['restored_binary_pins'] == state['restored_binary_pins']
assert root['source_count'] == 50 and root['pin_count'] == 355
assert root['restored_native_paths'] == 27 and root['native_modified_paths_preserved'] == 26
assert root['staged_paths_preserved'] == 925
assert root['installed112_source_and_test_ownership_preserved'] is True
assert root['all_owned_process_groups_cleaned'] and root['both_availability_profiles_removed']
pins = {**read(RUNTIME / 'RESOURCES.json'), **final['sources'], **state['restored_binary_pins']}
assert read(RUNTIME / 'FINAL-PINS.json') == pins and len(pins) == 355
errors = {phase: (RUNTIME / (phase + '-build.log')).read_text().count("KeyError: 'export'")
          for phase in ('baseline', 'candidate', 'restore')}
assert errors == root['build_resource_monitor_keyerrors'] == dict.fromkeys(errors, 4)
phases = read(HERE / 'PHASE-RESULTS.json')
for phase in ('baseline', 'candidate'):
    assert root[phase] == {k: phases['phases'][phase][k] for k in ('pass', 'fail')}
    assert phases['phases'][phase]['raw_sha256'] == sha(RUNTIME / ('wpt-' + phase) / 'raw.json')
    assert phases['phases'][phase]['run_sha256'] == sha(RUNTIME / ('wpt-' + phase) / 'RUN.json')
assert root['repaired'] == phases['repairs']
result = {'runtime_manifest_sha256': sha(RUNTIME / 'FILES.json'),
          'root_receipt_sha256': sha(RUNTIME / 'ROOT-FINAL-CHECK.json'),
          'state_sha256': sha(RUNTIME / 'STATE.json'), 'terminal_restoration_reviewed': True,
          'source_guards': 50, 'restored_originals': 27, 'final_pins': 355,
          'staged_paths_preserved_root_receipt': 925, 'native_inventory_preserved': 26,
          'restored_binary_pins': state['restored_binary_pins'], 'resource_monitor_keyerrors': errors,
          'scoped_recommendation': 'ACCEPT_TWO_PATH_REPAIR', 'live_tree_rechecked_by_reviewer': False}
(HERE / 'FINAL-REVIEW.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
