import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
parser = argparse.ArgumentParser()
parser.add_argument('--manifest-sha', required=True)
parser.add_argument('--lean', required=True)
args = parser.parse_args()
runtime = ('build/', 'imports/language-dictionary-stream-v1/development-build/',
           'imports/language-dictionary-stream-v1/imports/dictionary-stream-v1/development-build/',
           'imports/language-dictionary-stream-v1/imports/dictionary-stream-v1/provider-bridge-v1/development-build/')

def authenticate():
    raw = (ROOT / 'MANIFEST.json').read_bytes()
    assert hashlib.sha256(raw).hexdigest() == args.manifest_sha
    manifest = json.loads(raw)
    for name, digest in manifest['files'].items():
        rel = Path(name)
        assert not rel.is_absolute() and '..' not in rel.parts
        path = ROOT / rel
        assert not path.is_symlink() and path.resolve().is_relative_to(ROOT)
        assert hashlib.sha256(path.read_bytes()).hexdigest() == digest, name
    actual = {str(p.relative_to(ROOT)) for p in ROOT.rglob('*') if p.is_file()
              and not str(p.relative_to(ROOT)).startswith(runtime)}
    assert actual in [set(manifest['files']) | {'MANIFEST.json'},
                      set(manifest['files']) | {'MANIFEST.json', 'FREEZE.json'}]
    return manifest

manifest = authenticate()
OUT = ROOT / 'build'
OUT.mkdir(exist_ok=True)
SOURCE = ROOT / 'imports/language-dictionary-stream-v1'
command = [sys.executable, str(SOURCE / 'check.py'), '--manifest-sha',
           '9479527acc477ed57ba3f9380225c27e88652310ccd7d1a104585a695d5add49', '--lean', args.lean]
with (OUT / 'source-build.log').open('w') as log:
    result = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT)
assert result.returncode == 0, 'Nested complete source replay failed'
print('complete source replay passed', flush=True)

inputs = (ROOT / 'evidence/inputs.txt').read_text()
dictionary = SOURCE / 'imports/dictionary-stream-v1/source/providers/intl/locales/en-US/hyphenation/hyph_en_US.hyf'
records = []
for variant in ['original', 'candidate']:
    binary = SOURCE / 'development-build/dictionary-stream-language' / ('stream-' + variant)
    result = subprocess.run([str(binary), str(dictionary)], input=inputs, capture_output=True,
                            text=True, env=dict(os.environ, UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=1'))
    (OUT / (variant + '.raw.txt')).write_text(result.stdout)
    (OUT / (variant + '.stderr')).write_text(result.stderr)
    assert result.returncode == 0 and not result.stderr
    assert result.stdout == (ROOT / 'evidence' / (variant + '.raw.txt')).read_text()
    cases = {}
    for line in result.stdout.splitlines():
        words = line.split()
        if words[0] == 'shutdown':
            continue
        case = cases.setdefault(words[0], {'callbacks': [], 'providers': []})
        if words[1:3] == ['CALLBACK_ID', 'B']:
            sink, owner, base, offset, length, *values = map(int, words[3:])
            assert len(values) == length
            case['callbacks'].append({'sink': sink, 'owner': owner, 'base': base,
                                      'offset': offset, 'values': values})
        if words[1:4] == ['EVENT', 'provider', 'input']:
            case['providers'].append(list(map(int, words[4:])))
        if words[1] == 'BREAKS':
            case.update(breaks=words[2], glyphs=words[4], errors=words[8])
    for name, case in cases.items():
        assert set(case['errors']) == {'0'}
        derived = [0] * len(case['breaks'])
        for callback in case['callbacks']:
            for index, value in enumerate(callback['values']):
                position = callback['base'] + callback['offset'] + index
                assert 0 <= position < len(derived)
                if value:
                    derived[position] = value
        assert ''.join(map(str, derived)) == case['breaks'] == case['glyphs']
    observations = {}
    for prefix, lf in [('ahom', 4), ('bmp', 3)]:
        whole = cases[prefix + '-whole']['glyphs']
        before = cases[prefix + '-before-lf']['glyphs']
        after = cases[prefix + '-after-lf']['glyphs']
        differences = [i for i, (a, b) in enumerate(zip(whole, before, strict=True)) if a != b]
        observations[prefix] = {'lf': lf, 'whole': whole, 'before_lf': before,
                                'after_lf': after, 'differences': differences,
                                'outside_lf_and_initial_boundary': [i for i in differences if i not in (lf, lf + 1)]}
        assert whole == after
    assert observations['ahom']['outside_lf_and_initial_boundary'] == [6]
    assert observations['bmp']['outside_lf_and_initial_boundary'] == []
    records.append({'variant': variant, 'binary_sha256': hashlib.sha256(binary.read_bytes()).hexdigest(),
                    'cases': cases, 'comparisons': observations})
authenticate()
result = {'status': 'LF_LOCALITY_REFUTED_AT_COMPLETE_NATIVE_API; BROWSER_ADMISSION_OPEN',
          'source_only_rebuild': True, 'files': len(manifest['files']), 'records': records}
(OUT / 'RESULT.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result))
