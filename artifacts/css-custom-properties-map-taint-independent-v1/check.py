import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize, 'invoke Python with -I -S without optimization'
ROOT = Path(__file__).absolute().parent


def unique(pairs):
    out = {}
    for key, value in pairs:
        assert key not in out, 'duplicate JSON key'
        out[key] = value
    return out


def read(name):
    return json.loads((ROOT / name).read_text(), object_pairs_hook=unique)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def authenticate():
    assert not any(p.is_symlink() for p in [ROOT, *ROOT.parents]), 'source path symlink'
    for p in ROOT.rglob('*'):
        assert not p.is_symlink() and (p.is_dir() or p.is_file()), 'nonregular input'
    freeze = read('FREEZE.json')
    assert sha(ROOT / 'MANIFEST.json') == freeze['manifest_sha256'], 'manifest hash'
    assert sha(ROOT / 'check.py') == freeze['checker_sha256'], 'checker hash'
    pins = read('MANIFEST.json')
    expected = set(pins) | {'MANIFEST.json', 'FREEZE.json'}
    assert {str(p.relative_to(ROOT)) for p in ROOT.rglob('*') if p.is_file()} == expected, 'closed file roster'
    expected_dirs = {str(p) for name in expected for p in Path(name).parents if str(p) != '.'}
    assert {str(p.relative_to(ROOT)) for p in ROOT.rglob('*') if p.is_dir()} == expected_dirs, 'closed directory roster'
    for name, pin in pins.items():
        p = Path(name)
        assert not p.is_absolute() and '..' not in p.parts and str(p) == name, 'unsafe input name'
        assert sha(ROOT / p) == pin, 'input hash: ' + name
    return pins


def main():
    pins = authenticate()
    import difflib
    paths = ['servo/components/style/custom_properties_map.rs', 'servo/components/style/properties/cascade.rs']
    patch = ''
    for name in paths:
        original = (ROOT / 'source' / name).read_text()
        candidate = (ROOT / 'candidate' / name).read_text()
        if name.endswith('custom_properties_map.rs'):
            old = 'if self.get(name) == value.as_ref() {'
            new = 'if can_deduplicate_values(self.get(name), value.as_ref()) {'
        else:
            old = 'if let Some(existing_value) = existing_value.as_universal() {\n                    return existing_value != value;'
            new = 'if let Some(existing_unparsed) = existing_value.as_universal() {\n                    return existing_value.attr_tainted != value.is_attr_tainted()\n                        || existing_unparsed != value;'
        assert original.count(old) == candidate.count(new) == 1
        assert original.replace(old, new) == candidate
        assert candidate.replace(new, old) == original
        patch += ''.join(difflib.unified_diff(original.splitlines(True), candidate.splitlines(True), fromfile='a/' + name, tofile='b/' + name))
    assert patch == (ROOT / 'proposed.patch').read_text()
    source = read('SOURCE-PINS.json')
    for record in source:
        assert sha(ROOT / 'source' / record['path']) == record['sha256']
    bindings = read('SOURCE-BINDINGS.json')
    assert len(bindings) == 26
    for row in bindings:
        s = (ROOT / 'source' / row['file']).read_text()
        start = s.index(row['signature'], s.index(row['scope']) if row['scope'] else 0)
        indentation = 4 if row['signature'].startswith('    ') else 0
        end = s.index('\n' + ' ' * indentation + '}', start) + indentation + 2
        body = s[start:end]
        assert body == row['body'] and hashlib.sha256(body.encode()).hexdigest() == row['sha256']
        assert len(s[:start].encode()) == row['start_byte'] and len(s[:end].encode()) == row['end_byte']
    html = (ROOT / 'prior/map-taint-equality.html').read_text()
    js = (ROOT / 'prior/map-taint-equality.js').read_text()
    assert html.split('<script>')[1].split('</script>')[0].strip() == js.strip()
    expected = read('prior/EXPECTED-IDENTITIES.json')
    assert re.findall(r'^checkCase\("([^"\n]+)"', js, re.M) == expected and len(expected) == 9
    baseline = read('root-baseline-RUN.json')
    assert [r['subtest'] for r in baseline['rows']] == expected
    assert [r['status'] for r in baseline['rows']] == ['FAIL','PASS','PASS','FAIL','PASS','FAIL','FAIL','PASS','PASS']
    assert baseline['exit'] == 1 and all(baseline['stable_after'].values()) and baseline['build_receipt_stable']
    raw = [json.loads(line, object_pairs_hook=unique) for line in (ROOT / 'root-baseline-raw.jsonl').read_text().splitlines()]
    normalized = [{key: r.get(key) for key in ['test','subtest','status','expected','message','stack']} for r in raw if r.get('action') == 'test_status']
    assert normalized == baseline['rows']
    assert [r.get('status') for r in raw if r.get('action') == 'test_end'] == ['OK']
    assert baseline['pins']['testing/web-platform/tests/css/css-values/map-taint-equality.html'] == sha(ROOT / 'prior/map-taint-equality.html')
    for name in paths:
        assert baseline['pins'][name] == sha(ROOT / 'source' / name)
    prior = read('prior/MANIFEST.json')
    assert sha(ROOT / 'prior/MANIFEST.json') == read('prior/FREEZE.json')['manifest_sha256']
    for name in ['REPORT.md','map-taint-equality.html','map-taint-equality.js','EXPECTED-IDENTITIES.json','SOURCE-PINS.json']:
        assert sha(ROOT / 'prior' / name) == prior['files'][name]
    print(json.dumps({'inputs':len(pins),'complete_source_bindings':len(bindings),'patch_sites':2,'root_baseline':{'fail':4,'pass':5,'harness':'OK'},'native_browser_or_tests_executed':False,'candidate_status':'UNCOMPILED_UNEXECUTED'}))

if __name__ == '__main__':
    main()
