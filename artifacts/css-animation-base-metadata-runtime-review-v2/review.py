from pathlib import Path
from collections import Counter
import hashlib
import json

here = Path(__file__).resolve().parent
repo = here.parents[1]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read = lambda p: json.loads(p.read_text())
for name, digest in read(here / 'INPUTS.json').items():
    assert sha(repo / name) == digest, name
root = repo / 'artifacts/css-animation-base-metadata-paired-root-v1'
pair = read(root / 'PAIR.json')
assert pair['complete'] and pair['phase'] == 'done'
assert pair['build']['exit'] == 0 and pair['stable_after']

def observations(path):
    raw = [json.loads(s) for s in path.read_text().splitlines()]
    assert sum(x.get('action') == 'suite_end' for x in raw) == 1
    assert not any(x.get('action') == 'crash' for x in raw)
    rows = [x for x in raw if x.get('action') == 'test_status']
    ends = [x for x in raw if x.get('action') == 'test_end']
    keyed = {(x['test'], x['subtest']): x['status'] for x in rows}
    assert len(keyed) == len(rows)
    assert len({x['test'] for x in ends}) == len(ends)
    assert all(x['status'] == 'OK' for x in ends)
    return rows, ends, keyed

before, before_ends, before_map = observations(root / 'baseline/raw.json')
after, after_ends, after_map = observations(root / 'candidate/raw.json')
assert before == pair['baseline']['rows'] and before_ends == pair['baseline']['harness']
assert after == pair['candidate']['rows'] and after_ends == pair['candidate']['harness']
assert len(before) == 8 and len(before_ends) == 1
expected = []
for direction in ['clean to tainted', 'tainted to clean']:
    expected += [(f'Neutral start {direction}, same payload', 'FAIL'),
                 (f'Neutral start {direction}, different payload', 'PASS'),
                 (f'Neutral end {direction}, same payload', 'FAIL'),
                 (f'Explicit replacement ignores base {direction}', 'PASS')]
assert [(x['subtest'], x['status']) for x in before] == expected
for row in before:
    if row['status'] == 'FAIL':
        assert row['message'].startswith('assert_equals: Immediate effect URL taint expected ')
        assert '.html:71:8' in row['stack']
endpoint = repo / 'artifacts/css-animation-endpoint-paired-root-v1'
regression = repo / 'artifacts/css-animation-endpoint-final-root-v1'
ep_rows, ep_ends, ep_map = observations(endpoint / 'candidate/raw.json')
reg_rows, reg_ends, reg_map = observations(regression / 'setKeyframes-raw.json')
ep = read(endpoint / 'PAIR.json')
reg = read(regression / 'REGRESSIONS.json')
assert ep_rows == ep['candidate_wpt']['rows']
assert reg_rows == reg['rows'] and reg['stable_after']
assert not (before_map.keys() & ep_map.keys() or before_map.keys() & reg_map.keys() or ep_map.keys() & reg_map.keys())
joined = before_map | ep_map | reg_map
assert len(joined) == len(after) == 189 and len(after_ends) == 14
assert joined.keys() == after_map.keys() and set(after_map.values()) == {'PASS'}
changes = [{'identity': list(k), 'before': joined[k], 'after': after_map[k]} for k in joined if joined[k] != after_map[k]]
assert len(changes) == 4 and {tuple(x['identity']) for x in changes} == {k for k, v in before_map.items() if v == 'FAIL'}
assert sorted(changes, key=lambda x:x['identity']) == sorted(pair['changes'], key=lambda x:x['identity'])
old = read(repo / 'artifacts/css-animation-base-metadata-root-v1/RUN.json')
probe_path = 'testing/web-platform/tests/css/css-values/animation-base-equal-payload-taint.html'
expected_pins = old['pins'].copy()
expected_pins[probe_path] = sha(root / 'probe-v2.html')
assert expected_pins == pair['pins_before']
changes_in_pins = {k for k in pair['pins_before'] if pair['pins_before'][k] != pair['pins_after'][k]}
assert pair['pins_before'].keys() == pair['pins_after'].keys()
source = 'dom/animation/KeyframeEffect.cpp'
binaries = {'objdir-full.noindex/dist/Nightly.app/Contents/MacOS/' + n for n in ['firefox', 'XUL']}
assert changes_in_pins == {source} | binaries
assert pair['pins_after'][source] == pair['candidate_source_sha256'] == sha(root / 'KeyframeEffect.formatted.cpp')
assert pair['baseline']['stable'] and pair['baseline']['exit'] == 1 and pair['candidate']['exit'] == 0
supplement = read(root / 'SUPPLEMENTAL-REGRESSION-PINS.json')
assert supplement['phase_before'] == 'building' and supplement['candidate_raw_absent_before']
assert supplement['before_match_previous_regression'] and supplement['after']['pins_unchanged']
assert supplement['after']['phase'] == 'done' and supplement['after']['pair_sha256'] == sha(root / 'PAIR.json')
extra = {k:v for k,v in reg['pins'].items() if k not in pair['pins_before']}
assert extra == supplement['extra_regression_pins']
assert len(extra) == 1
transfer = read(regression / 'FORMAT-TRANSFER.json')
reg_pins = reg['pins'].copy()
assert reg_pins[transfer['path']] == transfer['before_sha256']
old_source = (repo / 'artifacts/css-animation-base-metadata-audit-v1/source' / transfer['path']).read_bytes()
assert hashlib.sha256(old_source).hexdigest() == transfer['before_sha256']
assert old_source.count(transfer['old'].encode()) == 1
assert hashlib.sha256(old_source.replace(transfer['old'].encode(), transfer['new'].encode())).hexdigest() == transfer['after_sha256']
reg_pins[transfer['path']] = transfer['after_sha256']
assert all(reg_pins[k] == pair['pins_before'][k] for k in reg_pins if k in pair['pins_before'])
assert sum(x == "KeyError: 'export'" for x in (root / 'candidate/build.log').read_text().splitlines()) == 4
probe_original = (repo / 'artifacts/css-animation-base-metadata-audit-v1/probe.html').read_text()
insert = '''  const beforeSeek = observe(target);
  assert_equals(beforeSeek.payload, immediate.payload,
                "Control flushes preserve sampled payload");
  assert_equals(beforeSeek.image, immediate.image,
                "Control flushes preserve sampled URL taint");
'''
needle = '  animation.currentTime = time + 1;'
assert probe_original.count(needle) == 1
assert probe_original.replace(needle, insert + needle) == (root / 'probe-v2.html').read_text()
assert (root / 'KeyframeEffect.formatted.cpp').read_bytes() == (repo / 'artifacts/css-animation-base-metadata-review-v1/KeyframeEffect.candidate.cpp').read_bytes()
result = {'status':'PASS','baseline':dict(Counter(before_map.values())),'joined_reference':dict(Counter(joined.values())),
          'candidate':dict(Counter(after_map.values())),'harnesses':len(after_ends),'improvements':changes,
          'unchanged':185,'changed_pins':sorted(changes_in_pins),
          'claim':'fresh eight-case baseline plus historical101+80 references, candidate189; no new browser run by reviewer'}
print(json.dumps(result,indent=2))
