import argparse
import ast
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
parser = argparse.ArgumentParser()
parser.add_argument('--manifest-sha', required=True)
args = parser.parse_args()
OUT = ROOT / 'build'
BRIDGE = ROOT / 'imports/bridge-v1'

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
    excluded = ('build/', 'imports/bridge-v1/development-build/')
    actual = {str(p.relative_to(ROOT)) for p in ROOT.rglob('*')
              if p.is_file() and not str(p.relative_to(ROOT)).startswith(excluded)}
    assert actual in [set(manifest['files']) | {'MANIFEST.json'},
                      set(manifest['files']) | {'MANIFEST.json', 'FREEZE.json'}]
    return manifest

manifest = authenticate()
print('authenticated', len(manifest['files']), flush=True)
tools = json.loads((ROOT / 'TOOLS.json').read_text())
for name, record in tools.items():
    assert hashlib.sha256(Path(record['path']).read_bytes()).hexdigest() == record['sha256'], name
OUT.mkdir(exist_ok=True)
commands = []

def run(name, command, cwd=None, env=None, input=None):
    command = list(map(str, command))
    print('running', name, flush=True)
    result = subprocess.run(command, cwd=cwd, env=env, input=input, capture_output=True, text=True, timeout=600)
    (OUT / (name + '.log')).write_text(result.stdout + result.stderr)
    commands.append({'name': name, 'command': command, 'exit': result.returncode})
    (OUT / 'COMMANDS.json').write_text(json.dumps(commands, indent=2) + '\n')
    assert result.returncode == 0, (name, result.stderr)
    return result.stdout

env = dict(os.environ, CARGO_HOME=str(OUT / 'cargo-home'), RUSTC=tools['rustc']['path'])
run('icu-build', [tools['cargo']['path'], 'build', '--locked', '--offline', '--target-dir', OUT / 'icu'], BRIDGE / 'icu', env)
run('extract-provider', [sys.executable, BRIDGE / 'native/extract-provider.py'])
deps = OUT / 'icu/debug/deps'
externs = []
for name in ['icu_segmenter', 'icu_provider']:
    libraries = list(deps.glob('lib' + name + '-*.rlib'))
    assert len(libraries) == 1
    externs += ['--extern', name + '=' + str(libraries[0])]
raw = {}
for name in ['lf-complex-sa-domain', 'lf-complex-encoding']:
    run(name + '-compile', [tools['rustc']['path'], '--edition', '2021', ROOT / 'native' / (name + '.rs'),
                           '-L', 'dependency=' + str(deps), *externs, '-o', OUT / name])
    raw[name] = run(name, [OUT / name])
    assert raw[name] == (ROOT / 'evidence' / name / 'raw.txt').read_text()

rows = []
for line in raw['lf-complex-encoding'].splitlines():
    match = re.fullmatch(r'(\S+) (Normal|BreakAll) SCALARS (\[.*?\]) UTF8 (\[.*?\]) UTF16 (\[.*?\]) MAP8 .* EQUAL (true|false)', line)
    assert match, line
    name, mode, scalar_text, utf8_text, utf16_text, equal = match.groups()
    scalars, breaks8, breaks16 = map(ast.literal_eval, [scalar_text, utf8_text, utf16_text])
    starts8, starts16 = [0], [0]
    for scalar in scalars:
        starts8.append(starts8[-1] + len(chr(scalar).encode('utf-8')))
        starts16.append(starts16[-1] + len(chr(scalar).encode('utf-16-le')) // 2)
    positions8 = [starts8.index(x) for x in breaks8]
    positions16 = [starts16.index(x) for x in breaks16]
    assert (positions8 == positions16) == (equal == 'true')
    rows.append({'name': name, 'mode': mode, 'scalars': scalars, 'utf16': breaks16,
                 'positions8': positions8, 'positions16': positions16, 'equal': positions8 == positions16})
assert any(not row['equal'] for row in rows)
assert all(row['equal'] for row in rows if row['mode'] == 'BreakAll')

run('gecko-compile', [tools['clang']['path'], '-std=c++20', '-g', '-O1', '-fsanitize=undefined',
                     '-I', BRIDGE / 'development-build/provider', '-I', BRIDGE / 'provider-crates/icu_capi/bindings/cpp',
                     '-I', BRIDGE / 'source/providers/intl/icu/source/common', '-I', BRIDGE / 'native',
                     ROOT / 'native/provider-main.cpp', OUT / 'icu/debug/liblanguage_break_provider.a',
                     '-licucore', '-framework', 'CoreFoundation', '-framework', 'Security', '-o', OUT / 'gecko-provider'])
inputs = (ROOT / 'evidence/lf-complex-gecko/inputs.txt').read_text()
gecko = run('gecko-provider', [OUT / 'gecko-provider'], input=inputs)
assert gecko == (ROOT / 'evidence/lf-complex-gecko/raw.txt').read_text()
for index, (name, mode) in enumerate([('thai-ahom-thai', 'Normal')] * 3 + [('thai-ahom-thai', 'BreakAll'), ('bmp-unknown', 'Normal')]):
    row = next(row for row in rows if row['name'] == name and row['mode'] == mode)
    length = sum(len(chr(c).encode('utf-16-le')) // 2 for c in row['scalars'])
    expected = ''.join('1' if i in row['utf16'] else '0' for i in range(length))
    assert gecko.splitlines()[index] == expected

lean = ROOT / 'lean/ComplexEncodingCounterexample.lean'
text = lean.read_text()
assert not re.search(r'\b(sorry|admit|axiom|native_decide|bv_decide)\b', text)
leanenv = dict(os.environ, LEAN_PATH=str(OUT))
run('lean', [tools['lean']['path'], '-o', OUT / 'ComplexEncodingCounterexample.olean', lean], env=leanenv)
names = re.findall(r'^theorem (\w+)', text, re.M)
audit = OUT / 'Axioms.lean'
audit.write_text('import ComplexEncodingCounterexample\n' + '\n'.join('#print axioms LanguageBreak.ComplexEncoding.' + name for name in names) + '\n')
axioms = run('axioms', [tools['lean']['path'], audit], env=leanenv)
assert 'sorryAx' not in axioms
for group in re.findall(r'depends on axioms: \[([^]]*)\]', axioms):
    assert set(map(str.strip, group.split(','))) <= {'propext', 'Classical.choice', 'Quot.sound', ''}
authenticate()
result = {'status': 'PROVIDER_COUNTEREXAMPLE_REPRODUCED_NOT_BROWSER_ACCEPTANCE',
          'files': len(manifest['files']), 'rows': rows, 'gecko_vectors': gecko.splitlines(),
          'standard_axiom_reports': len(names), 'source_only_rebuild': True,
          'manifest_sha256': args.manifest_sha}
(OUT / 'RESULT.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result), flush=True)
