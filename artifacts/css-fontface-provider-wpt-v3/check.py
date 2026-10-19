#!/usr/bin/env python3
import ast
import difflib
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

P = Path(__file__).resolve().parent
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
load = lambda p: json.loads(p.read_text())


def run(args, cwd=P):
    result = subprocess.run(args, cwd=cwd, capture_output=True, text=True)
    assert result.returncode == 0, (args, result.stdout, result.stderr)
    return result.stdout


def assigned_regex(path, name):
    tree = ast.parse(path.read_text())
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == name for t in node.targets):
            pattern = ast.literal_eval(node.value.args[0])
            return re.compile(pattern, re.IGNORECASE if name == 'ahem_font_re' else 0)
    raise AssertionError(name)


def main():
    freeze = load(P / 'FREEZE.json')
    assert sha(P / 'INPUTS.json') == freeze['inputs_sha256']
    inputs = load(P / 'INPUTS.json')
    assert len(inputs) == freeze['entries']
    for rel, expected in inputs.items():
        assert sha(P / rel) == expected, rel
    change = load(P / 'TRANSFORMATION.json')
    base = P.parent / 'css-fontface-provider-integration-v1'
    assert sha(base / 'FREEZE.json') == change['integration_v1_freeze_sha256']
    assert sha(base / 'INPUTS.json') == change['integration_v1_inputs_sha256']
    for rel, expected in load(base / 'INPUTS.json').items():
        assert sha(base / rel) == expected, rel
    assert (P / 'register.cjs').read_bytes() == (base / 'register.cjs').read_bytes()
    assert (P / 'CASES.json').read_bytes() == (base / 'CASES.json').read_bytes()
    pins = load(P / 'TEST-PINS.json')
    patch = []
    lint = P / 'source/testing/web-platform/tests/tools/lint/lint.py'
    sourcefile = P / 'source/testing/web-platform/tests/tools/manifest/sourcefile.py'
    ahem = assigned_regex(lint, 'ahem_font_re')
    meta = assigned_regex(sourcefile, 'js_meta_re')
    assert 'b"title", b"quic", b"spec"' in lint.read_text()
    assert 'if meta == "spec":' in sourcefile.read_text()
    for rel, row in pins.items():
        name = Path(rel).name
        original = (P / 'original' / name).read_text()
        candidate = (P / 'proposal' / name).read_text()
        assert sha(P / 'original' / name) == row['v2'] == load(base / 'TEST-PINS.json')[rel]['proposed']
        assert sha(P / 'proposal' / name) == row['v3']
        assert original.count(change['old_ternary']) == 1
        expected = original.replace(change['old_ternary'], change['new_ternary'])
        if name.endswith('.any.js'):
            marker = '// META: global=window,dedicatedworker\n'
            assert expected.count(marker) == 1
            expected = expected.replace(marker, marker + change['added_js_metadata'])
            headers = [meta.fullmatch(line) for line in candidate.encode().splitlines()[:4]]
            assert all(headers)
            assert [match.group(1) for match in headers] == [b'title', b'global', b'spec', b'spec']
        else:
            assert ahem.search(original.encode())
            assert not ahem.search(candidate.encode())
        assert candidate == expected, name
        patch.extend(difflib.unified_diff(original.splitlines(True), candidate.splitlines(True),
                                         fromfile='a/' + rel, tofile='b/' + rel))
    assert ''.join(patch) == (P / 'wpt-v2-to-v3.patch').read_text()
    expected_cases = load(P / 'CASES.json')
    assert json.loads(run(['node', str(P / 'register.cjs'), str(P)])) == expected_cases
    assert list(map(len, expected_cases.values())) == [12, 28, 28]
    with tempfile.TemporaryDirectory(prefix='source-check-', dir=P) as temp:
        tree = Path(temp)
        for rel in pins:
            target = tree / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(P / 'original' / Path(rel).name, target)
        run(['patch', '--batch', '--fuzz=0', '-p1', '-i', str(P / 'wpt-v2-to-v3.patch')], tree)
        for rel, row in pins.items():
            assert sha(tree / rel) == row['v3']
            source = tree / rel
            if source.suffix == '.html':
                scripts = re.findall(r'<script>(.*?)</script>', source.read_text(), re.S)
                assert len(scripts) == 1
                source = tree / 'inline.js'
                source.write_text(scripts[0])
            run(['node', '--check', str(source)])
        run(['patch', '--batch', '--fuzz=0', '-R', '-p1', '-i', str(P / 'wpt-v2-to-v3.patch')], tree)
        (tree / 'proposal').mkdir()
        for rel, row in pins.items():
            assert sha(tree / rel) == row['v2']
            shutil.copyfile(tree / rel, tree / 'proposal' / Path(rel).name)
        assert json.loads(run(['node', str(P / 'register.cjs'), str(tree)])) == expected_cases
    print(json.dumps({'status': 'PASS_SOURCE_ONLY', 'inputs': len(inputs),
                      'exact_cases': [12, 28, 28], 'callbacks_executed': False,
                      'syntax': 'both candidates pass node --check', 'metadata_key': 'spec',
                      'original_html_ahem_regex_match': True, 'candidate_html_ahem_regex_match': False,
                      'exact_apply_reverse': True, 'browser_or_build_run': False}, indent=2))


if __name__ == '__main__':
    main()
