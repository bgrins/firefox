#!/usr/bin/env python3
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def selected(text, selector):
    if selector == 'complete KeyframeCustomPropertiesBuilder struct and impl':
        start = text.index('pub struct KeyframeCustomPropertiesBuilder')
        end = text.index('\n}\n', text.index("impl<'a> KeyframeCustomPropertiesBuilder", start)) + 3
    elif selector == 'complete Iterator impl for AnimationValueIterator':
        start = text.index("impl<'a, 'cx, 'cx_a: 'cx> Iterator for AnimationValueIterator")
        end = text.index('\n}\n', start) + 3
    else:
        indent = 0 if selector.startswith('pub extern') or selector.startswith('pub fn handle_') else 4
        start = text.index(' ' * indent + selector)
        end = text.index('\n' + ' ' * indent + '}', start) + indent + 2
    return text[start:end]


def main():
    freeze = json.loads((ROOT / 'FREEZE.json').read_text())
    assert sha(ROOT / 'MANIFEST.json') == freeze['manifest_sha256']
    manifest = json.loads((ROOT / 'MANIFEST.json').read_text())
    actual = {str(p.relative_to(ROOT)) for p in ROOT.rglob('*') if p.is_file()}
    assert actual == set(manifest) | {'MANIFEST.json', 'FREEZE.json'}
    for name, expected in manifest.items():
        path = ROOT / name
        assert path.resolve().is_relative_to(ROOT) and not path.is_symlink()
        assert sha(path) == expected, name
    inputs = json.loads((ROOT / 'INPUTS.json').read_text())
    for name, expected in inputs['files'].items():
        assert sha(ROOT / name) == expected
    for row in json.loads((ROOT / 'BODY-CHECKS.json').read_text()):
        values = {}
        for label in ('base', 'head', 'current'):
            values[label] = selected((ROOT / 'source' / label / row['path']).read_text(), row['selector'])
            assert hashlib.sha256(values[label].encode()).hexdigest() == row['sha256'][label]
        assert (values['base'] == values['head']) == row['base_head_equal']
        assert (values['head'] == values['current']) == row['head_current_equal']
    patch = (ROOT / 'endpoint-native.patch').read_text()
    paths = ['servo/ports/geckolib/glue.rs', 'servo/components/style/properties_and_values/value.rs']
    applications = json.loads((ROOT / 'APPLICATION.json').read_text())
    with tempfile.TemporaryDirectory(prefix='keyframe-patch-check-') as tmp:
        for row in applications:
            dst = Path(tmp) / row['base']
            for name in paths:
                path = dst / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes((ROOT / 'source' / row['base'] / name).read_bytes())
            result = subprocess.run(['patch', '-p1', '--batch', '--fuzz=0'], cwd=dst, input=patch, text=True, capture_output=True)
            assert result.returncode == 0, result.stdout + result.stderr
            for name in paths:
                assert sha(dst / name) == row['sha256'][name]
                if row['base'] == 'head':
                    assert (dst / name).read_bytes() == (ROOT / 'source/current' / name).read_bytes()
            result = subprocess.run(['patch', '-p1', '--batch', '--fuzz=0', '--reverse'], cwd=dst, input=patch, text=True, capture_output=True)
            assert result.returncode == 0
            for name in paths:
                assert (dst / name).read_bytes() == (ROOT / 'source' / row['base'] / name).read_bytes()
    print(json.dumps({'inputs': len(manifest), 'source_snapshots': 21, 'selected_bodies': 8,
                      'patch_bases_applied_reversed': 2, 'isolated_compile_runtime': 'NOT_RUN'}))


if __name__ == '__main__':
    main()
