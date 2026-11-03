from pathlib import Path
import hashlib
import importlib.util
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
RUNTIME = ROOT / 'artifacts/css-root-font-startup-trace-late-runtime-v1'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
raw = RUNTIME / 'firefox-closed.log'
assert sha(raw) == 'f099833a0a36df6dcb50d95248064f269ae14fa4a23bbba994e5b8fa639a6101'
extractor = ROOT / 'artifacts/css-root-font-startup-trace-log-extractor-v1/extract.py'
assert sha(extractor) == '4da9331bf46b889497ae3d5c608422491a4b4ff398919b789da39c275f2c7ed3'
spec = importlib.util.spec_from_file_location('read_only_rfst', extractor)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
actual = module.extract(raw.read_bytes())
recorded = json.loads((RUNTIME / 'RFST.json').read_bytes())
assert actual == {k: v for k, v in recorded.items() if k != 'input_path'}
observation, = json.loads((RUNTIME / 'OBSERVATIONS.json').read_bytes())
assert observation['mode'] == 'late'
assert [observation[k] for k in ('first', 'settled', 'afterCalibration')] == ['46px'] * 3
assert observation['rootSize'] == '32px' and observation['plainSize'] == '64px'
assert observation['precondition'] == {'root': '23px', 'target': '11px', 'rootAnimations': 0, 'childAnimations': 0}
assert observation['targetRestyle']['value'] == '64px'
assert observation['targetRestyle']['sameChildAnimation'] and observation['targetRestyle']['sameRootAnimation']
root, child, effect, device = '0x10b40c7c0', '0x10b40c970', '0x10b130f10', '0x101c7d820'
rows = actual['records']
child_rows = [r for r in rows if child in [r['fields'].get(k) for k in ('node', 'target_node', 'input_node')]]
conversions = [(r['line'], r['fields']['px']) for r in child_rows if r.get('event') == 'converted-font']
assert conversions == [(11210, '46'), (11212, '46'), (11217, '46'), (11219, '46'), (11274, '64'), (11276, '64'), (11482, '64'), (11484, '64')]
builds = [(r['line'], r['fields']['changed']) for r in rows if r.get('event') == 'built-properties' and r['fields'].get('effect') == effect]
assert builds == [(11213, '1'), (11220, '0'), (11277, '1'), (11485, '0')]
selected = [r for r in rows if 11184 <= r['line'] <= 11278 or 11466 <= r['line'] <= 11486]
by_line = {r['line']: r for r in rows}
assert by_line[11225]['fields']['node'] == root and by_line[11225]['fields']['device'] == device
assert by_line[11225]['fields']['px'] == '32'
assert by_line[11225]['fields']['flags'] == 'TraversalFlags(AnimationOnly | ParallelTraversal)'
assert by_line[11261]['fields']['kind'] == 'Some(CascadeOnly)'
assert by_line[11262]['fields']['mask'] == '0x4'
assert by_line[11270]['fields']['mask'] == '4'
assert by_line[11273]['fields']['device'] == device and by_line[11273]['fields']['reference_px'] == '32'
assert by_line[11474]['fields']['kind'] == 'Some(MatchAndCascade)'
assert by_line[11475]['fields']['mask'] == '0xc'
assert not any(r.get('event') == 'restyle' and 'FinalAnimationTraversal' in r['fields'].get('flags', '') for r in child_rows)
(HERE / 'TRACE-EXCERPT.json').write_text(json.dumps(selected, indent=2) + '\n')
(HERE / 'TRACE-EXCERPT.txt').write_text(''.join(f"{r['line']}: {r['raw']}" for r in selected))
result = {'raw_sha256': sha(raw), 'extractor_matches_saved_output': True,
          'raw_rfst_records': len(rows), 'excerpt_records': len(selected),
          'cohort_addresses': {'root': root, 'child': child, 'child_effect': effect, 'device': device},
          'child_conversions': conversions, 'child_built_changed': builds,
          'observed_values': [observation['first'], observation['settled'], observation['afterCalibration'], observation['targetRestyle']['value']],
          'js_phase_markers_present': False, 'native_downstream_queue_trace_present': False,
          'no_native_or_browser_actions': True}
(HERE / 'RESULT.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
