import hashlib
import json
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RUN = ROOT / 'artifacts/css-svg-hidden-embedder-comparison-runtime-v1'
read = lambda p: json.loads(p.read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
refs = {}

def capsule(path, expected):
    assert sha(path / 'FILES.json') == expected
    refs[str((path / 'FILES.json').relative_to(ROOT))] = expected
    for name, value in read(path / 'FILES.json').items():
        assert sha(path / name) == value

capsule(RUN, 'e910e5edff9be2845778a64a88f72b70ca45f83b07a18aa81fdf5235c6494e79')
rootReview = ROOT / 'artifacts/css-svg-hidden-embedder-final-root-review-v1'
capsule(rootReview, '8d2bd87abb4a207c0c89a5e837d479e701ce8544e3549a184586dd4acbdaedce')
for name, value in read(rootReview / 'REFERENCES.json').items():
    assert sha(ROOT / name) == value
assert sha(HERE / 'PRELIMINARY-CHECK.json') == '8303d215f01892ceb84fc19059d723b64411d00f9dbe969bcd9a2673e72f1ca0'
prelim = read(HERE / 'PRELIMINARY-CHECK.json')
for name, value in prelim['references'].items():
    assert sha(ROOT / name) == value
state = read(RUN / 'STATE.json')
receipt = read(RUN / 'ROOT-FINAL-CHECK.json')
assert sha(RUN / 'ROOT-FINAL-CHECK.json') == '683bd25ca883c3e3bc6b2a8cd78c5a3fc55504f5b6f286b63c2dc24824b67f73'
assert state['status'] == 'terminal' and state['restored'] is True
assert state['restore_build_exit'] == 0 and state['recovery_errors'] == [] and 'failure' not in state
assert state['paired_preservation_passed'] and state['lint_exit'] == 0
assert receipt['status'] == 'RESTORED_VERIFIED' and receipt['session'] == 83213 and receipt['exit'] == 0
for key, file in [('state_sha256', 'STATE.json'), ('final_sha256', 'FINAL.json'), ('final_pins_sha256', 'FINAL-PINS.json')]:
    assert receipt[key] == sha(RUN / file)
config = read(RUN / 'CONFIG.json')
before, final = read(RUN / 'BEFORE.json'), read(RUN / 'FINAL.json')
assert before == final and final['sources'] == config['source_pins']
assert len(final['sources']) == receipt['source_count'] == 56
assert set(state['restored_paths']) == set(config['sources']) and len(state['restored_paths']) == 33
for name in config['sources']:
    assert sha(RUN / 'original' / name) == final['sources'][name]
assert receipt['native_modified_paths'] == len(config['modified_native_paths']) == 30
assert receipt['staged_paths'] == 925
assert final['index_entries_sha256'] == 'e52cf295947403cec7f6cba85bc15a6b539aaa5591df17101dfb5098e3747e21'
assert final['index_diff_sha256'] == '3ecc566a1cb1a78aab07c4f272b627d59f7888dec4adf563274849a966047272'
assert receipt['installed_tests'] == config['epoch_receipt']['installed_tests'] and len(receipt['installed_tests']) == 8
assert receipt['restored_binary_pins'] == state['restored_binary_pins']
resources = read(RUN / 'RESOURCES.json')
assert len(resources) == receipt['resource_count'] == 347
finalPins = read(RUN / 'FINAL-PINS.json')
assert finalPins == {**resources, **final['sources'], **state['restored_binary_pins']}
assert len(finalPins) == receipt['pin_count'] == 405
assert all(finalPins[name] is None for name in config['install'])
for phase in ['baseline', 'candidate']:
    phaseRecord = state['phases'][phase]
    assert phaseRecord['build_exit'] == 0
    assert hashlib.sha256(json.dumps(phaseRecord, sort_keys=True).encode()).hexdigest() == prelim['phases'][phase]['phase_record_sha256']
    evidence = receipt['phase_evidence'][phase]
    assert evidence['binary_pins'] == phaseRecord['binary_pins']
    assert evidence['raw_sha256'] == sha(RUN / ('wpt-' + phase) / 'raw.json')
    assert evidence['run_sha256'] == sha(RUN / ('wpt-' + phase) / 'RUN.json')
assert receipt['repair_count'] == len(prelim['repairs']) == 20
assert receipt['restore_build_log_sha256'] == sha(RUN / 'restore-build.log')
landing = ROOT / 'artifacts/css-svg-hidden-embedder-landing-v1'
capsule(landing, 'a0125d2fa37e8c2b54e77d1285c48fd3f9795a6f21c244aec722cc66dc21f1b6')
proposal = ROOT / config['proposal']
for variant, native in [('standalone', 'standalone.patch'), ('stack', 'installed-overlay.patch')]:
    body = (landing / (variant + '-gecko-wpt.patch')).read_text()
    prefix = (proposal / native).read_text()
    assert body.startswith(prefix)
    remainder = body[len(prefix):]
    paths = re.findall(r'^\+\+\+ b/(\S+)$', body, re.M)
    assert len(paths) == len(set(paths)) == 6
    assert set(paths) == set(config['candidate_sources']) | set(config['install'])
    fixture = ''.join(line[1:] for line in remainder.splitlines(True) if line.startswith('+') and not line.startswith('+++'))
    assert fixture.encode() == (RUN / 'fixture.html').read_bytes()
(HERE / 'FINAL-CHECK.json').write_text(json.dumps({
    'status': 'GO_SCOPED_RESULTS_AND_RESTORATION', 'runtime_manifest': refs[str((RUN / 'FILES.json').relative_to(ROOT))],
    'root_receipt_sha256': sha(RUN / 'ROOT-FINAL-CHECK.json'), 'session': 83213, 'exit': 0,
    'baseline': {'PASS': 32, 'FAIL': 20}, 'candidate': {'PASS': 52, 'FAIL': 0},
    'repairs': {'visible_overlap114': 8, 'hidden_additional': 12}, 'controls_preserved': 28,
    'restored': True, 'restoration_build_exit': 0, 'restored_binary_pins': state['restored_binary_pins'],
    'independent_live_read': False, 'restoration_live_verification_by': str(rootReview.relative_to(ROOT)),
    'landing_native_prefixes_and_fixture_exact': True, 'mixed_stack_integration_pending': True,
    'accepted_new_bug': False, 'preliminary_unchanged_sha256': sha(HERE / 'PRELIMINARY-CHECK.json'),
    'references': refs}, indent=2) + '\n')
print('PASS: exact paired evidence, authenticated restoration, and six-path packaging')
