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
    for name in ('INPUTS.json', 'FREEZE.json'):
        manifest = HERE / name
        if manifest.exists():
            entries = json.loads(manifest.read_text())
            if name == 'FREEZE.json':
                entries = entries['files']
            for path, expected in entries.items():
                assert sha(HERE / path) == expected, ('integrity', path)
    base = json.loads((HERE / 'BASE.json').read_text())
    inputs = json.loads((HERE / 'evidence/namespace-original-inputs.json').read_text())
    native = ''
    for name, path in base['native_paths'].items():
        original = HERE / 'original' / name
        assert sha(original) == base['pins'][name] == inputs['pins_before'][path]
        before = original.read_text()
        if name == 'custom_properties.rs':
            old = '    #[inline(always)]\n    pub(crate) fn get_attr(&self, name: &Name) -> Option<&ComputedRegisteredValue> {'
            helper = '    #[inline(always)]\n    pub(crate) fn contains_attr(&self, name: &Name) -> bool {\n        self.attributes.contains_key(name)\n    }\n\n'
            new = helper + old
        else:
            old = 'if context.map().get_attr(&next.name).is_none()'
            new = 'if !context.map().contains_attr(&next.name)'
        assert before.count(old) == 1
        after = before.replace(old, new)
        assert after == (HERE / 'candidate' / name).read_text()
        native += ''.join(difflib.unified_diff(before.splitlines(True), after.splitlines(True),
            fromfile='a/' + path, tofile='b/' + path))
    assert native == (HERE / 'native.patch').read_text()
    html = HERE / 'attr-repeated-invalid-value.html'
    assert sha(html) == base['wpt_sha256']
    wpt = ''.join(difflib.unified_diff([], html.read_text().splitlines(True),
        fromfile='/dev/null', tofile='b/' + base['wpt_path']))
    assert wpt == (HERE / 'wpt.patch').read_text()
    assert native + wpt == (HERE / 'fix.patch').read_text()
    logs = []
    with tempfile.TemporaryDirectory(prefix='tombstone-base-port-') as temporary:
        work = Path(temporary)
        for name, path in base['native_paths'].items():
            target = work / path
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(HERE / 'original' / name, target)
        (work / base['wpt_path']).parent.mkdir(parents=True)
        for reverse in (False, True):
            command = ['patch', '--batch', '--fuzz=0', '-p1', '-i', str(HERE / 'fix.patch')]
            if reverse:
                command.append('-R')
            result = subprocess.run(command, cwd=work, capture_output=True, text=True)
            assert result.returncode == 0, result.stdout + result.stderr
            logs.append({'reverse': reverse, 'output': result.stdout})
            for name, path in base['native_paths'].items():
                folder = 'original' if reverse else 'candidate'
                assert (work / path).read_bytes() == (HERE / folder / name).read_bytes()
            if reverse:
                assert not (work / base['wpt_path']).exists()
            else:
                assert (work / base['wpt_path']).read_bytes() == html.read_bytes()
        script = work / 'wpt.js'
        script.write_text('\n'.join(re.findall(r'<script>(.*?)</script>', html.read_text(), re.S)))
        result = subprocess.run(['node', '--check', str(script)], capture_output=True, text=True)
        assert result.returncode == 0, result.stderr
    print(json.dumps({'status': 'BASE_PORT_SOURCE_CHECK_PASS_UNCOMPILED',
        'native_hunks': 2, 'final_wpt_sha256': base['wpt_sha256'],
        'exact_patch_forward_reverse': logs, 'node_syntax': 'PASS'}, indent=2))

if __name__ == '__main__':
    main()
