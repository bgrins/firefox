#!/usr/bin/env python3
"""Authenticate source capsules, then check patches without compiling Gecko."""
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


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path):
    return json.loads(path.read_text())


def authenticate():
    freeze = load(P / 'FREEZE.json')
    assert sha(P / 'INPUTS.json') == freeze['inputs_sha256']
    inputs = load(P / 'INPUTS.json')
    assert len(inputs) == freeze['entries']
    for rel, expected in inputs.items():
        assert sha(P / rel) == expected, rel
    base = P.parent / 'css-fontface-provider-integration-v1'
    dep = load(P / 'DEPENDENCIES.json')['css-fontface-provider-integration-v1']
    assert sha(base / 'FREEZE.json') == dep['freeze_sha256']
    assert sha(base / 'INPUTS.json') == dep['inputs_sha256']
    for rel, expected in load(base / 'INPUTS.json').items():
        assert sha(base / rel) == expected, rel
    return base, inputs


def main():
    base, inputs = authenticate()
    pins = load(P / 'NATIVE-PINS.json')
    assert len(pins) == 16
    oldpins = load(base / 'NATIVE-PINS.json')
    assert pins.keys() == oldpins.keys()
    native, formatting = [], []
    commands = load(P / 'COMMANDS.json')
    assert len(commands) == len(pins)
    tool = load(P / 'TOOLCHAIN.json')
    for (name, row), command in zip(pins.items(), commands):
        assert sha(P / 'original' / name) == row['original'] == oldpins[name]['original']
        assert (P / 'original' / name).read_bytes() == (base / 'original' / name).read_bytes()
        original = (P / 'original' / name).read_text()
        expected = (base / 'candidate' / name).read_text()
        if name == 'layout/style/FontFaceImpl.cpp':
            old = '  RefPtr<StyleLockedFontFaceRule> descriptors =\n      Servo_FontFaceRule_Clone(GetData()).Consume();'
            new = '  RefPtr<StyleLockedFontFaceRule> descriptors = GetData();\n  if (previousEntry) {\n    descriptors = Servo_FontFaceRule_Clone(descriptors).Consume();\n  }'
            assert expected.count(old) == 1
            expected = expected.replace(old, new)
            comment = '  // Parse without publishing descriptors until provider preparation succeeds.'
            assert expected.count(comment) == 1
            expected = expected.replace(comment, '  // Prepare existing providers before publishing new descriptors.')
        preformat = (P / 'preformat' / name).read_text()
        final = (P / 'candidate' / name).read_text()
        assert preformat == expected, name
        assert re.sub(r'\s+', '', preformat) == re.sub(r'\s+', '', final), name
        assert sha(P / 'candidate' / name) == row['candidate'] == command['candidate']
        assert sha(P / 'preformat' / name) == command['preformat']
        assert command['original'] == row['original'] and command['exit_code'] == 0
        ranges = [f'--lines={j1 + 1}:{max(j1 + 1, j2)}'
                  for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(
                      a=original.splitlines(), b=preformat.splitlines(), autojunk=False).get_opcodes()
                  if tag != 'equal']
        argv = command['command']
        assert argv[0] == tool['clang_format'] and argv[1] == '--style=file'
        assert argv[2].endswith('/' + name) and argv[3:] == ranges
        native.extend(difflib.unified_diff(original.splitlines(True), final.splitlines(True),
                                         fromfile='a/' + name, tofile='b/' + name))
        formatting.extend(difflib.unified_diff(preformat.splitlines(True), final.splitlines(True),
                                             fromfile='preformat/' + name, tofile='candidate/' + name))
    assert ''.join(native) == (P / 'native.patch').read_text()
    assert ''.join(formatting) == (P / 'format.patch').read_text()
    for name in ['check.py', 'prepare.py']:
        ast.parse((P / name).read_text())
    with tempfile.TemporaryDirectory(prefix='source-replay-', dir=P) as tmp:
        tree = Path(tmp)
        shutil.copytree(P / 'original', tree, dirs_exist_ok=True)
        for reverse, label in [(False, 'candidate'), (True, 'original')]:
            argv = ['patch', '--batch', '--fuzz=0', '-p1', '-i', str(P / 'native.patch')]
            if reverse:
                argv.append('-R')
            result = subprocess.run(argv, cwd=tree, capture_output=True, text=True)
            assert result.returncode == 0, (result.stdout, result.stderr)
            for name, row in pins.items():
                assert sha(tree / name) == row[label], (label, name)
    print(json.dumps({'status': 'PASS_SOURCE_ONLY', 'inputs': len(inputs),
                      'dependency_inputs': 108, 'native_files': 16,
                      'exact_apply_reverse': True, 'adaptation': 'conditional clone only',
                      'formatting': 'recorded commands and reviewed whitespace delta',
                      'formatter_rerun': False, 'native_build_or_browser_run': False}, indent=2))


if __name__ == '__main__':
    main()
