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
assert sha(R / 'native.patch') == pins['native_patch_sha256']
assert sha(R / 'test.html') == pins['test_sha256']
a=(R/'before-custom-properties.rs').read_text();b=(R/'candidate-custom-properties.rs').read_text();p=(R/'native.patch').read_text()
assert patch_text(a,p)==b and patch_text(b,p,True)==a
for mode, info in read('PACKAGING.json').items():
    if mode not in ['head','standalone']:continue
    p=R/(mode+'-native-wpt.patch')
    assert sha(p)==info['sha256']
    parts=p.read_text().split('diff --git ')[1:]
    assert len(parts)==2
    native=next(x for x in parts if x.startswith('a/servo/'))
    wpt=next(x for x in parts if x.startswith('a/testing/'))
    a=(R/('package-'+mode)/'original.rs').read_text();b=(R/('package-'+mode)/'candidate.rs').read_text()
    assert patch_text(a,native)==b and patch_text(b,native,True)==a
    assert patch_text('',wpt)==(R/'test.html').read_text()
    assert patch_text((R/'test.html').read_text(),wpt,True)==''
    assert sha(R/('package-'+mode)/'candidate.rs')==info['source_sha256']
    assert '.trim_ascii_start()' in b and 'last_non_whitespace_token_type' not in b
raw=lambda f:[json.loads(x) for x in (R/f).read_text().splitlines()]
base=raw('baseline-wpt.json');now=raw('candidate-wpt-v1/raw.json');prior=raw('prior415/raw.json')
status=lambda rs:[r for r in rs if r.get('action')=='test_status']
key=lambda r:(r['test'],r['subtest'])
obs=lambda r:(r['status'],r.get('message'))
bas=status(base);cur=status(now);old=status(prior)
assert len(bas)==20 and collections.Counter(r['status'] for r in bas)=={'FAIL':16,'PASS':4}
assert all('Set expected' in r['message'] for r in bas if r['status']=='FAIL')
assert len(cur)==len({key(r) for r in cur})==435
assert len(old)==415
curmap={key(r):obs(r) for r in cur}
assert all(curmap[key(r)]==obs(r) for r in old)
new=[r for r in cur if key(r) in {key(b) for b in bas}]
assert len(new)==20 and all(r['status']=='PASS' for r in new)
ends=[r for r in now if r.get('action')=='test_end']
run=read('candidate-wpt-v1/RUN.json')
assert run['before']==run['after'] and run['stable'] and run['complete']
assert run['exit']==run['build_exit']==0 and run['rows']==cur and run['harness']==ends
assert len(ends)==23 and all(r['status']=='OK' for r in ends)
assert {r['test'] for r in ends}=={x.removeprefix('testing/web-platform/tests') for x in run['command'] if x.startswith('testing/')}
assert sum(r.get('action')=='suite_end' for r in now)==1
assert run['before'][pins['source']]==pins['candidate_sha256']
assert run['before'][pins['test']]==pins['test_sha256']
print(json.dumps({'status':'PASS','new_before':{'FAIL':16,'PASS':4},'new_after':{'PASS':20},'unchanged_status_message_pairs':415,'harness_OK':23,'source_binary_stable':True,'pure_patch_apply_reverse':True,'isolated_variant_runtime':False},indent=2))
