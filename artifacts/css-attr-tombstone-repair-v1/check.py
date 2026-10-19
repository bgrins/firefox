#!/usr/bin/env python3
import difflib
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    for manifest in ('INPUTS.json', 'FREEZE.json'):
        path = HERE / manifest
        if path.exists():
            entries = json.loads(path.read_text())
            if manifest == 'FREEZE.json':
                entries = entries['files']
            for name, expected in entries.items():
                assert sha(HERE / name) == expected, ('integrity', name)
    base = json.loads((HERE / 'BASE.json').read_text())
    fetch = json.loads((HERE / 'evidence/probe-FETCH.json').read_text())
    assert fetch['status'] == 200
    assert sha(HERE / 'evidence/probe-css-values-5.html') == fetch['sha256']
    spec = (HERE / 'evidence/probe-css-values-5.html').read_text()
    for anchor in ('attr-substitution', 'substitute-arbitrary-substitution-function', 'guarded', 'substitution'):
        assert 'id="' + anchor + '"' in spec, anchor
    assert sha(HERE / 'evidence/probe-INPUTS.json') == base['frozen_probe_inputs_sha256']
    for name, expected in base['pins'].items():
        assert sha(HERE / 'original' / name) == expected, name
    custom = (HERE / 'original/custom_properties.rs').read_text()
    helper = '''    #[inline(always)]
    pub(crate) fn contains_attr(&self, name: &Name, namespace: &Namespace) -> bool {
        self.attributes
            .get(namespace)
            .is_some_and(|attributes| attributes.contains_key(name))
    }

'''
    anchor = '    #[inline(always)]\n    pub(crate) fn get_attr(\n'
    assert custom.count(anchor) == 1
    assert custom.replace(anchor, helper + anchor) == (HERE / 'candidate/custom_properties.rs').read_text()
    cascade = (HERE / 'original/properties__cascade.rs').read_text()
    old = 'if context.map().get_attr(&next.name, namespace).is_none()'
    assert cascade.count(old) == 1
    assert cascade.replace(old, 'if !context.map().contains_attr(&next.name, namespace)') == (HERE / 'candidate/properties__cascade.rs').read_text()
    native = ''
    for name, path in base['native_paths'].items():
        native += ''.join(difflib.unified_diff(
            (HERE / 'original' / name).read_text().splitlines(True),
            (HERE / 'candidate' / name).read_text().splitlines(True),
            fromfile='a/' + path, tofile='b/' + path))
    assert native == (HERE / 'native.patch').read_text()
    html = (HERE / 'attr-repeated-invalid-value.html').read_text()
    wpt = ''.join(difflib.unified_diff([], html.splitlines(True),
        fromfile='/dev/null', tofile='b/' + base['wpt_path']))
    assert wpt == (HERE / 'wpt.patch').read_text()
    assert native + wpt == (HERE / 'fix.patch').read_text()
    assert html.count('    name: ') == 10
    receipt = json.loads((HERE / 'evidence/baseline-v1-receipt.json').read_text())
    assert receipt['all_inputs_unchanged'] and receipt['suite_end_count'] == 1
    assert list(receipt['counts'].values()) == [{'PASS': 7, 'FAIL': 4, 'OK': 1}]
    for name, path in base['native_paths'].items():
        assert receipt['pins_before'][path] == base['pins'][name]
    expected_failures = {'repeat-cycle', 'repeat-invalid', 'repeat-two-node-cycle', 'same-cycle-value-different-names'}
    assert {s['subtest'] for s in receipt['statuses'] if s.get('status') == 'FAIL'} == expected_failures
    diagnostic_path = 'testing/web-platform/tests/css/css-values/attr-cycle-repeated-reference.html'
    assert sha(HERE / 'evidence/frozen-diagnostic-probe.html') == receipt['pins_before'][diagnostic_path]
    with tempfile.TemporaryDirectory(prefix='attr-tombstone-check-') as temp:
        work = Path(temp)
        for name, path in base['native_paths'].items():
            target = work / path
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(HERE / 'original' / name, target)
        (work / base['wpt_path']).parent.mkdir(parents=True)
        steps = []
        for reverse in (False, True):
            command = ['patch', '--batch', '--fuzz=0', '-p1', '-i', str(HERE / 'fix.patch')]
            if reverse:
                command.append('-R')
            process = subprocess.run(command, cwd=work, text=True, capture_output=True)
            assert process.returncode == 0, process.stdout + process.stderr
            steps.append({'reverse': reverse, 'output': process.stdout})
            for name, path in base['native_paths'].items():
                directory = 'original' if reverse else 'candidate'
                assert (work / path).read_bytes() == (HERE / directory / name).read_bytes()
            if reverse:
                assert not (work / base['wpt_path']).exists()
            else:
                assert (work / base['wpt_path']).read_text() == html
        script = '\n'.join(re.findall(r'<script>(.*?)</script>', html, re.S))
        (work / 'wpt.js').write_text(script)
        process = subprocess.run(['node', '--check', str(work / 'wpt.js')], text=True, capture_output=True)
        assert process.returncode == 0, process.stderr
    print(json.dumps({'status': 'ARTIFACT_SOURCE_CHECK_PASS_RUNTIME_PENDING',
        'minimal_native_hunks': 2, 'final_wpt_tests': 10,
        'diagnostic_baseline': {'FAIL': 4, 'PASS': 7, 'OK': 1},
        'exact_patch_forward_reverse': steps, 'node_syntax': 'PASS'}, indent=2))

if __name__ == '__main__':
    main()
