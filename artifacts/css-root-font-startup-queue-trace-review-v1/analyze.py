import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RUNTIME = ROOT / 'artifacts/css-root-font-startup-queue-trace-late-runtime-v1'
EXTRACT = ROOT / 'artifacts/css-root-font-startup-trace-log-extractor-v2/extract.py'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(EXTRACT) == '46e880859b25a9f722d5235aeb36964b1b7d16a7cce1be3d53f8c1e2d442acef'
raw = (RUNTIME / 'firefox-closed.log').read_bytes()
assert hashlib.sha256(raw).hexdigest() == '198f8c8d0522918c66cf7e6f20ec7dad4793b0f207f5376ad5018449583b0f58'
spec = importlib.util.spec_from_file_location('saved_rfst', EXTRACT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
result = module.extract(raw)
saved = json.loads((RUNTIME / 'RFST.json').read_bytes())
saved.pop('input_path')
assert result == saved
rows = result['records']
by_line = {r['line']: r for r in rows}
raw_lines = raw.splitlines(keepends=True)
for r in rows:
    assert r['raw'].encode('utf-8', errors='surrogateescape') == raw_lines[r['line'] - 1]

root = '0x10ab0ca90'
child = '0x10ab0cf10'
effect = '0x10a8310e0'
device = '0x100951820'
style_set = '0x10a94f400'
compositor = '0x1014dff20'
document = '0x1015aef00'

def event(line, name, **fields):
    row = by_line[line]
    assert row['recognized'] and row['event'] == name
    assert not row.get('duplicate_fields') and not row.get('multiple_markers')
    for key, value in fields.items():
        assert row['fields'][key] == value, (line, key, row['fields'])

event(13518, 'root-published', node=root, px='23', device=device)
event(13686, 'document-enter', set=style_set, document=document)
event(13694, 'document-pass-begin', set=style_set, **{'pass': '1'})
event(13695, 'document-subtree', set=style_set, root_node=root, **{'pass': '1'})
for line in [13729, 13731, 13745, 13747]:
    event(line, 'converted-font', node=child, px='46')
event(13755, 'pre-selected', compositor=compositor, target_node=child, pseudo='95', level='0', posted='1')
event(13757, 'pre-remaining', compositor=compositor, level='0', count='0')
event(13760, 'document-pass-begin', set=style_set, **{'pass': '2'})
event(13761, 'document-subtree', set=style_set, root_node=root, **{'pass': '2'})
event(13765, 'root-published', node=root, px='32', device=device,
      flags='TraversalFlags(AnimationOnly | ParallelTraversal)')
event(13801, 'restyle', node=child, kind='Some(CascadeOnly)', admitted_animation='true')
event(13802, 'tasks', node=child, mask='0x4')
event(13810, 'delivery', input_node=child, target_node=child, pseudo='95', mask='4')
event(13812, 'build-properties', effect=effect, target_node=child)
for line in [13813, 13815]:
    event(line, 'rem-basis', device=device, reference_px='32', factor='2')
for line in [13814, 13816]:
    event(line, 'converted-font', node=child, px='64')
event(13817, 'built-properties', effect=effect, changed='1')
event(13818, 'request', compositor=compositor, target_node=child, pseudo='95', level='0', type='2', posted_before='0')
event(13819, 'request-post', compositor=compositor, target_node=child, pseudo='95', level='0', skip='0')
event(13820, 'post-deferred', compositor=compositor, target_node=child, normalized_node=child,
      pseudo='95', level='0', pretraverse='0')
event(13822, 'document-exit', set=style_set)
for line in [13824, 13827]:
    event(line, 'document-no-root', set=style_set)
event(14289, 'document-enter', set=style_set, document=document)
event(14291, 'pre-enter', compositor=compositor)
event(14292, 'pre-queue', compositor=compositor, level='0', count='1')
event(14294, 'pre-selected', compositor=compositor, target_node=child, pseudo='95', level='0', posted='1')
event(14295, 'pre-remaining', compositor=compositor, level='0', count='0')
event(14299, 'document-subtree', set=style_set, root_node=child, **{'pass': '1'})
event(14301, 'restyle', node=child, flags='TraversalFlags(AnimationOnly | ParallelTraversal)')
event(14308, 'restyle', node=child, kind='Some(MatchAndCascade)', hint='RestyleHint(RESTYLE_SELF)')
event(14309, 'tasks', node=child, mask='0xc')
event(14314, 'build-properties', effect=effect, target_node=child)
event(14319, 'built-properties', effect=effect, changed='0')

critical = [r for r in rows if 13686 <= r['line'] <= 14331]
assert all(r['recognized'] and not r.get('duplicate_fields') and not r.get('multiple_markers') for r in critical)
gap = [r for r in rows if 13820 < r['line'] < 14294]
assert not any(r.get('event') == 'pre-selected' and r['fields'].get('target_node') == child for r in gap)
assert not any(r['fields'].get('compositor') == compositor for r in gap if r['line'] < 14291)
assert not any(r.get('event') == 'request' and r['fields'].get('target_node') == child for r in gap)
assert not any(r.get('event') == 'document-pass-begin' and r['fields'].get('set') == style_set
               for r in rows if 13760 < r['line'] < 13822)
assert not any(r.get('event') in ['document-enter', 'document-subtree'] and r['fields'].get('set') != style_set
               for r in rows if 13686 <= r['line'] <= 13822)

observations = json.loads((RUNTIME / 'OBSERVATIONS.json').read_bytes())
assert len(observations) == 1
o = observations[0]
assert o['mode'] == 'late' and o['standards']
assert o['precondition'] == {'root': '23px', 'target': '11px', 'rootAnimations': 0, 'childAnimations': 0}
assert [o['first'], o['settled'], o['afterCalibration'], o['targetRestyle']['value']] == ['46px', '46px', '46px', '64px']
assert o['rootSize'] == o['targetRestyle']['rootSize'] == '32px'
assert o['plainSize'] == o['targetRestyle']['plainSize'] == '64px'
assert o['targetRestyle']['background'] == 'rgb(1, 2, 3)'
assert o['targetRestyle']['sameRootAnimation'] and o['targetRestyle']['sameChildAnimation']
assert o['rootAnimationCount'] == o['childAnimationCount'] == o['targetRestyle']['rootAnimationCount'] == o['targetRestyle']['childAnimationCount'] == 1
for key in ['rootAnimation', 'childAnimation']:
    a = o[key]
    assert a['cssAnimation'] and a['targetMatches'] and a['pseudoElement'] is None
    assert a['name'] == a['expectedName'] and a['playState'] == 'paused' and a['progress'] == 0
for key in ['root', 'child']:
    a = o['targetRestyle'][key]
    assert a['cssAnimation'] and a['targetMatches'] and a['pseudoElement'] is None
    assert a['name'] == a['expectedName'] and a['playState'] == 'paused' and a['progress'] == 0

line_numbers = [13518, *range(13686, 13828), *range(14289, 14332)]
excerpt = [{'line': n, 'raw': raw_lines[n - 1].decode('utf-8', errors='surrogateescape')} for n in line_numbers]
(HERE / 'TRACE-EXCERPT.json').write_text(json.dumps(excerpt, indent=2, ensure_ascii=True) + '\n')
(HERE / 'TRACE-EXCERPT.txt').write_text(''.join(f"{r['line']}: {r['raw']}" for r in excerpt), errors='surrogateescape')
output = {'raw_sha256': hashlib.sha256(raw).hexdigest(), 'extractor_matches_saved_output': True,
    'rfst_records': len(rows), 'excerpt_lines': len(excerpt),
    'cohort': {'root': root, 'child': child, 'effect': effect, 'device': device,
               'set': style_set, 'compositor': compositor, 'document': document},
    'sequence': {'outer_second_pass': 13760, 'root_32_publication': 13765,
        'child_64_changed': 13817, 'request': 13818, 'non_skipped_post': 13819,
        'actual_deferred_branch': 13820, 'document_exit': 13822,
        'no_root_entries': [13824, 13827], 'later_target_selection': 14294,
        'later_animation_restyle': 14301, 'later_normal_match': 14308, 'later_64_unchanged': 14319},
    'critical_interval_ambiguous_rfst_records': 0, 'matching_target_selection_in_gap': False,
    'matching_compositor_event_before_later_preenter': False, 'new_matching_request_in_gap': False,
    'observations': [o['first'], o['settled'], o['afterCalibration'], o['targetRestyle']['value']],
    'js_native_phase_markers': False, 'installed_style_directly_logged': False,
    'separate_effect_identity_measured_by_browser': False, 'native_fix_proposed': False}
(HERE / 'RESULT.json').write_text(json.dumps(output, indent=2) + '\n')
print(json.dumps(output, indent=2))
