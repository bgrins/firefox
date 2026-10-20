#!/usr/bin/env python3
import argparse
from collections import Counter
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PROBE = HERE / 'inputs/artifacts/css-view-transition-types-probe-v1'
FIX = HERE / 'inputs/artifacts/css-view-transition-types-fix-v1'
BINDING = 'objdir-full.noindex/dom/bindings/ViewTransitionBinding.cpp'
DOC = 'dom/base/Document.cpp'
WPT = 'testing/web-platform/tests/css/css-view-transitions/view-transition-types-initial-duplicates.html'

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def read(path):
    return json.loads(path.read_text())

def patch_apply(base, patch):
    lines = patch.splitlines(keepends=True)
    hunks = []
    for line in lines:
        if line.startswith('@@ '):
            hunks.append([])
        elif hunks and line[:1] in (' ', '+', '-'):
            hunks[-1].append(line)
    assert hunks
    for hunk in hunks:
        before = ''.join(x[1:] for x in hunk if x[0] in ' -')
        after = ''.join(x[1:] for x in hunk if x[0] in ' +')
        if before:
            assert base.count(before) == 1
            base = base.replace(before, after, 1)
        else:
            assert not base
            base = after
    return base

class Resources(HTMLParser):
    def __init__(self):
        super().__init__()
        self.src = []
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'src' in attrs:
            self.src.append(attrs['src'])
        if tag == 'link' and set(attrs.get('rel', '').split()) & {'stylesheet', 'match', 'mismatch'}:
            self.src.append(attrs['href'])

def oracle():
    initial = [[], ['a'], ['a','a'], ['a','b','a'], ['b','a','a'], ['a','b','b'], ['a','A','a']]
    rows = []
    for items in initial:
        for operation in ['delete a', 'delete b', 'clear']:
            before = list(dict.fromkeys(items))
            after = list(before)
            old_native = list(items)
            ret = None
            if operation == 'clear':
                after.clear()
                old_native.clear()
            else:
                key = operation[-1]
                ret = key in after
                if ret:
                    after.remove(key)
                    old_native.remove(key)
            mismatches = [key for key in ['a','b','A','absent'] if (key in old_native) != (key in after)]
            rows.append({'subtest': json.dumps(items,separators=(',',':'))+' followed by '+operation,
                         'initial': items, 'operation': operation, 'initial_order': before,
                         'updated_order': after, 'delete_return': ret,
                         'original_expected_status': 'FAIL' if mismatches else 'PASS',
                         'original_selector_mismatches': mismatches})
    return rows

def run_record(directory, phase, expected, exit_code, live):
    receipt = read(directory / (phase+'-receipt.json'))
    inputs = read(directory / (phase+'-inputs.json'))
    assert all(receipt[k] == v for k,v in inputs.items())
    pins = receipt['pins_before']
    assert len(pins) == 22 and pins == receipt['pins_after']
    assert receipt['all_inputs_unchanged'] is True
    assert receipt['absent_before'] == receipt['absent_after']
    assert len(receipt['absent_before']) == 1
    rows = [json.loads(x) for x in (directory/(phase+'.jsonl')).read_text().splitlines()]
    statuses = [r for r in rows if r.get('action') in ('test_status','test_end')]
    assert statuses == receipt['statuses']
    assert sum(r.get('action') == 'suite_end' for r in rows) == receipt['suite_end_count'] == 1
    assert Counter(r['status'] for r in statuses) == Counter(expected)
    assert receipt['exit_code'] == exit_code
    assert len({(r['action'],r['test'],r.get('subtest')) for r in statuses}) == len(statuses)
    counts = {}
    for row in statuses:
        counts.setdefault(row['test'], Counter())[row['status']] += 1
    assert counts == receipt['counts']
    snapshots = directory/(phase+'-sources')
    assert len(list(snapshots.iterdir())) == 19
    for name, sha in pins.items():
        if name == BINDING:
            assert digest(HERE/'inputs'/name) == sha
        elif not name.startswith('objdir-'):
            assert digest(snapshots/name.replace('/','__')) == sha
        if live and phase != 'original-v1' and not (name.startswith('objdir-') and name != BINDING):
            assert digest(ROOT/name) == sha, name
    if live:
        assert all(not (ROOT/name).exists() for name in receipt['absent_after'])
    for name in receipt['tests']:
        source = (snapshots/name.replace('/','__')).read_text()
        parser = Resources(); parser.feed(source)
        assert parser.src == ['/resources/testharness.js','/resources/testharnessreport.js']
        assert not re.search(r'\b(?:fetch|importScripts)\s*\(|\burl\s*\(|\bimport\s', source)
        for resource in parser.src:
            assert 'testing/web-platform/tests'+resource in pins
    assert '--headless' in receipt['command'] and '--processes=1' in receipt['command']
    return receipt

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--live',action='store_true')
    parser.add_argument('--checks-only',action='store_true')
    args = parser.parse_args()
    if not args.checks_only:
        manifest = read(HERE/'MANIFEST.json')
        actual = {str(p.relative_to(HERE)):digest(p) for p in HERE.rglob('*') if p.is_file() and p != HERE/'MANIFEST.json'}
        assert actual == manifest
    origins = read(HERE/'ORIGINS.json')
    for origin, record in origins.items():
        assert digest(HERE/record['snapshot']) == record['sha256']
        if args.live:
            assert digest(ROOT/origin) == record['sha256'], origin
    specs = read(HERE/'spec/FETCH.json')
    for name, record in specs.items():
        assert digest(HERE/'spec'/(name+'.html')) == record['sha256']
    original = run_record(PROBE,'original-v1',{'FAIL':5,'PASS':16,'OK':1},1,args.live)
    candidate = run_record(PROBE,'candidate-v1',{'PASS':21,'OK':1},0,args.live)
    existing = run_record(FIX,'existing-candidate-v1',{'PASS':3,'OK':1},0,args.live)
    shared = original['pins_before'].keys() & candidate['pins_before'].keys()
    changes = sorted(name for name in shared if original['pins_before'][name] != candidate['pins_before'][name])
    assert changes == [DOC,'objdir-full.noindex/dist/Nightly.app/Contents/MacOS/XUL','objdir-full.noindex/dist/Nightly.app/Contents/MacOS/firefox']
    assert len(shared) == 21
    assert (PROBE/'run_probe-v1.py').read_text().replace('assert phase == "original-v1"','assert phase == "candidate-v1"') == (PROBE/'run_candidate-v1.py').read_text()
    shared_existing = candidate['pins_before'].keys() & existing['pins_before'].keys()
    assert len(shared_existing) == 20
    assert all(candidate['pins_before'][name] == existing['pins_before'][name] for name in shared_existing)
    expected = oracle()
    assert read(HERE/'ORACLES.json') == expected
    old_status = {r['subtest']:r for r in original['statuses'] if r['action']=='test_status'}
    new_status = {r['subtest']:r for r in candidate['statuses'] if r['action']=='test_status'}
    assert old_status.keys() == new_status.keys() == {r['subtest'] for r in expected}
    for row in expected:
        observed = old_status[row['subtest']]
        assert observed['status'] == row['original_expected_status']
        assert new_status[row['subtest']]['status'] == 'PASS'
        if row['original_selector_mismatches']:
            assert len(row['original_selector_mismatches']) == 1
            key = row['original_selector_mismatches'][0]
            assert observed['message'] == f'assert_equals: updated selector membership for {key} expected false but got true'
    patch_path = FIX/'fix-candidate-v1.patch'
    patch = patch_path.read_text()
    blocks = re.split(r'(?m)^diff --git ',patch)[1:]
    assert len(blocks) == 2
    assert blocks[0].startswith('a/'+DOC+' b/'+DOC+'\n')
    assert blocks[1].startswith('a/'+WPT+' b/'+WPT+'\n')
    prepared = read(FIX/'prepare-native-v1/candidate-inputs.json')
    standalone = read(FIX/'standalone-apply-v1.json')
    assert standalone['patch_sha256'] == digest(patch_path)
    assert standalone['fix_paths'] == prepared
    for name,sha in prepared.items():
        assert digest(FIX/'prepare-native-v1/candidate'/name) == sha
        assert candidate['pins_before'][name] == sha
    old_doc = (FIX/'prepare-native-v1/original'/DOC).read_text()
    assert hashlib.sha256(old_doc.encode()).hexdigest() == original['pins_before'][DOC]
    new_doc = patch_apply(old_doc,blocks[0])
    assert new_doc == (FIX/'prepare-native-v1/candidate'/DOC).read_text()
    assert patch_apply('',blocks[1]) == (FIX/'prepare-native-v1/candidate'/WPT).read_text()
    base_results = []
    for check in standalone['checks']:
        assert check['check_exit'] == check['apply_exit'] == 0
        assert check['only_startup_deduplication'] and check['WPT_exact']
        assert check['isolated_build_performed'] is False
        source = FIX/'standalone-bases-v1'/check['label']/DOC
        repaired = patch_apply(source.read_text(),blocks[0])
        assert repaired != source.read_text()
        base_results.append({'label':check['label'],'revision':check['revision'],'base_sha256':digest(source),'repaired_sha256':hashlib.sha256(repaired.encode()).hexdigest()})
    scout = read(HERE/'inputs/artifacts/css-breadth-audit-round25-v1/view-transitions/INPUTS.json')
    for name in ['servo/components/style/gecko/wrapper.rs','servo/components/style/gecko/selector_parser.rs']:
        row = next(x for x in scout['sources'] if x['origin']==name)
        assert digest(HERE/'inputs'/name) == row['sha256']
        assert digest(HERE/'inputs/artifacts/css-breadth-audit-round25-v1/view-transitions'/row['snapshot']) == row['sha256']
    cycle = read(FIX/'CANDIDATE-CYCLE-v1.json')
    assert {x['label']:x['exit'] for x in cycle} == {'build-v1':0,'candidate-driver-v1':0,'lint-v1':1}
    assert read(FIX/'FORMAT-v1.json')['exit'] == 0
    assert '0 errors, 1 warning' in (FIX/'lint-v1.log').read_text()
    print(json.dumps({'decision':'ACCEPT scoped native/WPT repair','origins':len(origins),'run_pins_each':22,'snapshots_each':19,'generated_binding_authenticated':True,'paired_identities':21,'baseline':{'FAIL':5,'PASS':16,'OK':1},'candidate':{'PASS':21,'OK':1},'existing_candidate':{'PASS':3,'OK':1},'changed_shared_pins':changes,'standalone':base_results,'formal_proof':False,'live_checked':args.live},indent=2))

if __name__ == '__main__':
    main()
