import hashlib, json
from collections import Counter
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sha = lambda b: hashlib.sha256(b).hexdigest()
for path, digest in json.loads((HERE / "REFERENCES.json").read_text()).items():
    assert sha((ROOT / path).read_bytes()) == digest
for url, record in json.loads((HERE / "RESOURCES.json").read_text()).items():
    assert sha((ROOT / record['path']).read_bytes()) == record['sha256']
    if url.endswith('.html'):
        assert (HERE / 'tests' / url.lstrip('/')).read_bytes() == (ROOT / record['path']).read_bytes()
base = (HERE / 'base/dom/base/nsLineBreaker.cpp').read_text()
candidate = (HERE / 'candidate/dom/base/nsLineBreaker.cpp').read_text()
def body(text, signature):
    start = text.index(signature)
    brace = text.index('{', start)
    depth = 1
    end = brace + 1
    while depth:
        depth += (text[end] == '{') - (text[end] == '}')
        end += 1
    return text[start:end]
for signature in ['static mozilla::Maybe<bool> IsChineseOrJapanese(', 'void nsLineBreaker::UpdateCurrentWordLanguage(']:
    assert body(base, signature) == body(candidate, signature)
assert candidate.count('UpdateCurrentWordLanguage(aHyphenationLanguage);') == base.count('UpdateCurrentWordLanguage(aHyphenationLanguage);') == 4
assert candidate.count('IsChineseOrJapanese(aHyphenationLanguage).valueOr(false)') == base.count('IsChineseOrJapanese(aHyphenationLanguage).valueOr(false)') == 2
report = {}
for role in ['original', 'candidate']:
    path = ROOT / ('artifacts/css-language-partition-native-pair-runtime-1/' + role + '-wpt-regression/raw.jsonl')
    rows = [json.loads(line) for line in path.read_text().splitlines()]
    report[role] = {}
    for filename, count in [('inline-ownership',289),('dynamic',19),('pseudo-ownership',4)]:
        page = '/css/css-text/hyphens/hyphenate-limit-chars-' + filename + '.html'
        tests = [r for r in rows if r.get('action') == 'test_status' and r.get('test') == page]
        assert len(tests) == count and len({r['subtest'] for r in tests}) == count
        ends = [r for r in rows if r.get('action') == 'test_end' and r.get('test') == page]
        assert len(ends) == 1 and ends[0]['status'] == 'OK'
        expected = {'PASS':235,'FAIL':54} if filename == 'inline-ownership' else {'PASS':count}
        assert dict(Counter(r['status'] for r in tests)) == expected
        if filename != 'pseudo-ownership':
            assert next(r for r in tests if r['subtest'] == 'English hyphenation dictionary calibration')['status'] == 'PASS'
        report[role][filename] = expected
assert report['original'] == report['candidate']
result = dict(reference_count=len(json.loads((HERE/'REFERENCES.json').read_text())), resource_count=7, unchanged_language_helpers=True, four_buffered_language_calls=True, two_immediate_language_queries=True, prior_language_pair_controls=report, evidence_scope='Saved published-language pair only; not the new ownership candidate', new_native_build=False)
(HERE/'SOURCE-CHECK.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))
