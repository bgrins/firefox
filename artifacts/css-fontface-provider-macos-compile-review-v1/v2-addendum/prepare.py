import difflib
import hashlib
import json
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
BASE = HERE.parent / 'css-fontface-provider-integration-v1'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(BASE / 'FREEZE.json') == 'd7e6842185d313abf0189a9f75420a328727ba04698d173273c0cdd17f6baa84'
assert sha(BASE / 'INPUTS.json') == '0842b7621b1254640e19a67a982b385b9015ada56df60114fe4ffdafa767b0a7'
for name, digest in json.loads((BASE / 'INPUTS.json').read_text()).items():
    assert sha(BASE / name) == digest, name
tool = json.loads((HERE / 'TOOLCHAIN.json').read_text())
assert sha(Path(tool['clang_format'])) == tool['sha256']
assert sha(REPO / tool['config']) == tool['config_sha256']
pins = json.loads((BASE / 'NATIVE-PINS.json').read_text())
patches = []
formats = []
commands = []
for name, pin in pins.items():
    original = (BASE / 'original' / name).read_text()
    candidate = (BASE / 'candidate' / name).read_text()
    if name == 'layout/style/FontFaceImpl.cpp':
        old = '  RefPtr<StyleLockedFontFaceRule> descriptors =\n      Servo_FontFaceRule_Clone(GetData()).Consume();'
        new = '  RefPtr<StyleLockedFontFaceRule> descriptors = GetData();\n  if (previousEntry) {\n    descriptors = Servo_FontFaceRule_Clone(descriptors).Consume();\n  }'
        assert candidate.count(old) == 1
        candidate = candidate.replace(old, new).replace(
            '  // Parse without publishing descriptors until provider preparation succeeds.',
            '  // Prepare existing providers before publishing new descriptors.')
    preformat = HERE / 'preformat' / name
    preformat.parent.mkdir(parents=True, exist_ok=True)
    preformat.write_text(candidate)
    ranges = []
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(
            a=original.splitlines(), b=candidate.splitlines(), autojunk=False).get_opcodes():
        if tag != 'equal':
            ranges.append(f'--lines={j1 + 1}:{max(j1 + 1, j2)}')
    command = [tool['clang_format'], '--style=file', '--assume-filename=' + str(REPO / name), *ranges]
    result = subprocess.run(command, input=candidate, text=True, capture_output=True)
    assert result.returncode == 0, result.stderr
    formatted = result.stdout
    # clang-format edits are reviewed separately; preserve the exact input/output.
    output = HERE / 'candidate' / name
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(formatted)
    patches.extend(difflib.unified_diff(original.splitlines(True), formatted.splitlines(True),
                                      fromfile='a/' + name, tofile='b/' + name))
    formats.extend(difflib.unified_diff(candidate.splitlines(True), formatted.splitlines(True),
                                      fromfile='preformat/' + name, tofile='candidate/' + name))
    commands.append({'command': command, 'exit_code': result.returncode,
                     'original': pin['original'], 'preformat': sha(preformat),
                     'candidate': sha(output)})
(HERE / 'native.patch').write_text(''.join(patches))
(HERE / 'format.patch').write_text(''.join(formats))
(HERE / 'COMMANDS.json').write_text(json.dumps(commands, indent=2) + '\n')
(HERE / 'NATIVE-PINS.json').write_text(json.dumps({name: {'original': row['original'],
    'candidate': sha(HERE / 'candidate' / name)} for name, row in pins.items()}, indent=2) + '\n')
print(json.dumps({'native_files': len(pins), 'patch_sha256': sha(HERE / 'native.patch'),
                  'format_patch_sha256': sha(HERE / 'format.patch')}))
