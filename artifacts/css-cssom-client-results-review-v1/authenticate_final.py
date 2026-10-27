import hashlib
import json
from pathlib import Path

D = Path(__file__).resolve().parent
ROOT = D.parents[1]
R = ROOT / 'artifacts/css-cssom-client-comparison-runtime-v1'
def read(p):
    return json.loads(p.read_text())
def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

assert sha(R / 'FILES.json') == 'bb25bc23a5cdcf4c198f01da3955445c3a643758ce16839ae9ef7e256a36e0c8'
manifest = read(R / 'FILES.json')
for name, digest in manifest.items():
    assert sha(R / name) == digest, name
c, state = read(R / 'CONFIG.json'), read(R / 'STATE.json')
receipt = read(R / 'ROOT-FINAL-CHECK.json')
assert state['status'] == 'terminal' and state['restored'] is True
assert state['restore_build_exit'] == 0 and state['recovery_errors'] == [] and 'failure' not in state
assert state['paired_preservation_passed'] is True and state['baseline_reused'] is True
assert state['accepted_native_repair'] is False and state['lint_exit'] == 0
assert state['restored_paths'] == c['sources'] and len(c['sources']) == 31
before, final = read(R / 'BEFORE.json'), read(R / 'FINAL.json')
assert before == final and final['sources'] == c['source_pins'] and len(final['sources']) == 48
for name in c['sources']:
    assert sha(R / 'original' / name) == final['sources'][name]
pins = read(R / 'FINAL-PINS.json')
assert pins == {**read(R / 'RESOURCES.json'), **final['sources'], **state['restored_binary_pins']}
assert len(pins) == 336 and len(read(R / 'RESOURCES.json')) == 334
assert receipt['status'] == 'RESTORED_VERIFIED' and receipt['session'] == 70646 and receipt['exit'] == 0
assert receipt['state_sha256'] == sha(R / 'STATE.json')
assert receipt['final_sha256'] == sha(R / 'FINAL.json')
assert receipt['restored_binary_pins'] == state['restored_binary_pins']
for key, value in {'source_count':48, 'restored_source_count':31, 'resource_count':334,
                   'pin_count':336, 'existing_stage_paths':925, 'main_pass':40,
                   'main_repairs':10, 'unchanged_controls':130}.items():
    assert receipt[key] == value
for key in ('head_index_preserved', 'native_diff_preserved', 'installed112_preserved',
            'existing32_body_inode_preserved', 'owned8_removed', 'cleanup_verified'):
    assert receipt[key] is True
results = read(D / 'RESULTS.json')
assert receipt['fresh_baseline'] == results['fresh_baseline']
assert receipt['combined_baseline'] == results['combined_baseline']
assert receipt['candidate'] == results['candidate']
assert receipt['acceptance'] == 'PENDING_INDEPENDENT_TERMINAL_REVIEW'
phase_receipt = read(R / 'ROOT-PHASE-CHECK.json')
assert phase_receipt['status'] == 'PHASES_VERIFIED_RESTORATION_PENDING'
assert phase_receipt['restoration_verified'] is False
for phase in ('baseline', 'candidate'):
    assert state['phases'][phase]['build_exit'] == 0
    assert sha(R / ('wpt-' + phase) / 'raw.json') == results['raw_pins'][phase] == phase_receipt['phases'][phase]['raw_sha256']
    assert sha(R / ('wpt-' + phase) / 'RUN.json') == results['run_pins'][phase] == phase_receipt['phases'][phase]['run_sha256']
    assert read(R / ('wpt-' + phase) / 'CLEANUP.json') == {'owned_group_absent':True, 'errors':[]}
assert final['sources']['dom/base/Element.cpp'] == '5770fd0f1134284626ed42152e4b1c1d054cf509ae99e2ebcaf08d5ae00c0913'
assert final['sources']['dom/base/Element.h'] == '67fe061712f504dc717fedf0f27ac981e8ddc99874d97cb99f0b44da0aab55dc'
assert pins['testing/web-platform/tests/css/cssom-view/offset-scroll-integer-precision.html'] == '18c47e1acbf0a546a975fe5dc92c297a38a71e228a7b6ec576a58bc71c06078b'
assert pins['testing/web-platform/tests/css/cssom-view/client-size-integer-precision.html'] is None
monitor_counts = {name:(R/name).read_text(errors='replace').count("KeyError: 'export'")
                  for name in ('baseline-build.log','candidate-build.log','restore-build.log')}
result = {'status':'RESULTS_AND_HISTORICAL_RESTORATION_VERIFIED',
    'runtime_files_sha256':sha(R/'FILES.json'), 'payloads_authenticated':len(manifest),
    'state_sha256':sha(R/'STATE.json'), 'root_final_check_sha256':sha(R/'ROOT-FINAL-CHECK.json'),
    'source_guards':48, 'original_bodies':31, 'restored_pin_map':336,
    'root_verified_staged_payloads':925, 'restored_binary_pins':state['restored_binary_pins'],
    'monitor_export_keyerror_counts':monitor_counts, 'historical_phase_receipt_retained':True,
    'later_live_state_asserted':False, 'native_acceptance':False,
    'recommendation':'ACCEPT_EXPANDED_FIX112_SCOPED_INTEGER_CONVERSIONS',
    'scope':'Element.cpp and Element.h plus exact32 offset/scroll and8 client WPT; one existing fix112 family, no automatic new report'}
(D/'FINAL-REVIEW.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))
