import collections
import hashlib
import json
from pathlib import Path
import re
import sys

if not (sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize):
    raise RuntimeError('use python3 -I -S')
R = Path(__file__).resolve().parent


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def read(p):
    return json.loads((R / p).read_text())


def patch_text(original, patch, reverse=False):
    old = original.splitlines(keepends=True)
    out = []
    cursor = 0
    lines = patch.splitlines(keepends=True)
    i = 0
    while i < len(lines):
        match = re.match(r'@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@', lines[i])
        if not match:
            i += 1
            continue
        a, ac, b, bc = [int(x) if x is not None else 1 for x in match.groups()]
        start, count, written = (b, bc, ac) if reverse else (a, ac, bc)
        pos = start - 1 if start else 0
        assert cursor <= pos <= len(old)
        out += old[cursor:pos]
        cursor = pos
        consumed = produced = 0
        i += 1
        while i < len(lines) and not lines[i].startswith(('@@ ', 'diff --git ')):
            line = lines[i]
            if line.startswith('\\'):
                raise AssertionError('unsupported no-newline marker')
            assert line[:1] in (' ', '+', '-')
            tag = line[0]
            if reverse:
                tag = {'+': '-', '-': '+', ' ': ' '}[tag]
            text = line[1:]
            if tag in (' ', '-'):
                assert cursor < len(old) and old[cursor] == text
                cursor += 1
                consumed += 1
            if tag in (' ', '+'):
                out.append(text)
                produced += 1
            i += 1
        assert (consumed, produced) == (count, written)
    out += old[cursor:]
    return ''.join(out)


pins = read('CANDIDATE.json')
assert sha(R / 'before-custom-properties.rs') == pins['original_sha256']
assert sha(R / 'candidate-custom-properties.rs') == pins['candidate_sha256']
assert sha(R / 'native.patch') == pins['patch_sha256']
a = (R / 'before-custom-properties.rs').read_text()
b = (R / 'candidate-custom-properties.rs').read_text()
p = (R / 'native.patch').read_text()
assert patch_text(a, p) == b and patch_text(b, p, True) == a
packaging = read('PACKAGING.json')
for mode in ['head', 'standalone']:
    patch = R / (mode + '-native-wpt.patch')
    assert sha(patch) == packaging[mode]['sha256']
    parts = patch.read_text().split('diff --git ')[1:]
    assert len(parts) == 2
    native = next(p for p in parts if p.startswith('a/servo/'))
    wpt = next(p for p in parts if p.startswith('a/testing/'))
    before = (R / ('package-' + mode) / 'original.rs').read_text()
    after = (R / ('package-' + mode) / 'candidate.rs').read_text()
    assert patch_text(before, native) == after and patch_text(after, native, True) == before
    assert patch_text('', wpt) == (R / 'test.html').read_text()
    assert patch_text((R / 'test.html').read_text(), wpt, True) == ''
    assert '.trim_ascii_start()' in after
    assert sha(R / ('package-' + mode) / 'candidate.rs') == packaging[mode]['source_sha256']
raw = [json.loads(line) for line in (R / 'candidate-wpt-v1/raw.json').read_text().splitlines()]
run = read('candidate-wpt-v1/RUN.json')
rows = [r for r in raw if r.get('action') == 'test_status']
ends = [r for r in raw if r.get('action') == 'test_end']
assert run['complete'] and run['exit'] == run['build_exit'] == 0
assert run['before'] == run['after'] and run['stable']
assert rows == run['rows'] and ends == run['harness']
assert sum(r.get('action') == 'suite_end' for r in raw) == 1
assert len(ends) == 22 and all(r['status'] == 'OK' for r in ends)
tests = {arg.removeprefix('testing/web-platform/tests') for arg in run['command'] if arg.startswith('testing/')}
assert {r['test'] for r in ends} == tests and len(tests) == 22
key = lambda r: (r['test'], r['subtest'])
now = {key(r): (r['status'], r.get('message')) for r in rows}
assert len(rows) == len(now) == 415
prior_raw = [json.loads(line) for line in (R / 'prior375/raw.json').read_text().splitlines()]
prior = {key(r): (r['status'], r.get('message')) for r in prior_raw if r.get('action') == 'test_status'}
assert len(prior) == 375 and all(now[k] == value for k, value in prior.items())
new_test = '/css/css-variables/trailing-whitespace-token-boundary.html'
new = {key(r): r for r in rows if r['test'] == new_test}
space = ['space','tab','line feed','carriage return','form feed','CRLF','mixed whitespace']
boundaries = ['number and unit','number and percent','dimension and identifier','two identifiers']
names = [f'{boundary} after {s}' for s in space for boundary in boundaries]
names += [f'{boundary} {ending}' for boundary in boundaries for ending in ['without whitespace','after a retained comment']]
names += ['Valid dimension','Valid multiplication','Fallback retains its whitespace','Empty substitution']
assert set(new) == {(new_test,n) for n in names} and len(names) == 40
assert all(r['status'] == 'PASS' for r in new.values())
base = read('baseline-wpt.json')
assert base['source_sha256'] == pins['original_sha256']
assert base['wpt_sha256'] == sha(R / 'test.html') == run['before']['testing/web-platform/tests'+new_test]
old = {key(r): r for r in base['rows']}
assert set(old) == set(new) and len(old) == len(base['rows']) == 40
assert collections.Counter(r['status'] for r in old.values()) == {'FAIL':28,'PASS':12}
assert run['before']['servo/components/style/custom_properties.rs'] == pins['candidate_sha256']
result = {'status':'PASS','source_patch_apply_reverse':True,'head_and_upstream_retained_blob_apply_reverse':True,
          'new_baseline':{'FAIL':28,'PASS':12},'new_candidate':{'PASS':40},'prior_status_message_pairs_unchanged':375,
          'candidate_harness_OK':22,'source_and_binary_pins_stable':True,
          'scope':'No isolated browser/build of packaged variants; no universal tokenizer/substitution proof'}
print(json.dumps(result,indent=2))
