import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys

if not (sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize):
    raise RuntimeError('use python3 -I -S; optimization forbidden')
ROOT = Path(__file__).resolve().parent


def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def read(name):
    return json.loads((ROOT / name).read_text())


def authenticate():
    manifest = read('MANIFEST.json')
    expected = set(manifest) | {'MANIFEST.json', 'FREEZE.json'}
    actual = set()
    expected_dirs = {str(Path(n).parent) for n in expected}
    expected_dirs |= {str(p) for n in expected for p in Path(n).parents if str(p) != '.'}
    expected_dirs.discard('.')
    dirs = set()
    for p in ROOT.rglob('*'):
        name = p.relative_to(ROOT).as_posix()
        if p.is_symlink():
            raise RuntimeError('symlink: ' + name)
        if p.is_file():
            actual.add(name)
        elif p.is_dir():
            dirs.add(name)
        else:
            raise RuntimeError('nonregular input')
    if actual != expected or dirs != expected_dirs:
        raise RuntimeError('closed roster mismatch')
    for name, value in manifest.items():
        if Path(name).is_absolute() or '..' in Path(name).parts or digest(ROOT / name) != value:
            raise RuntimeError('input mismatch: ' + name)
    if digest(ROOT / 'MANIFEST.json') != read('FREEZE.json')['manifest_sha256']:
        raise RuntimeError('manifest mismatch')
    return manifest


manifest = authenticate()
parser = argparse.ArgumentParser()
parser.add_argument('--output', type=Path, required=True)
args = parser.parse_args()
out = args.output.resolve()
if out.exists() or out == ROOT or out.is_relative_to(ROOT):
    raise RuntimeError('absent resolved external output required')
config = read('TOOLCHAIN.json')
lean = Path(config['lean'])
if digest(lean) != config['lean_sha256']:
    raise RuntimeError('Lean executable mismatch')
for name, value in read('TOOLCHAIN-LIBRARY.json').items():
    if digest(lean.parents[1] / name) != value:
        raise RuntimeError('Lean library mismatch: ' + name)
for row in read('SOURCE-BINDINGS.json'):
    source = (ROOT / row['source']).read_bytes()
    value = source[row['start_byte']:row['start_byte'] + row['length_bytes']]
    if value.decode() != row['complete_text'] or hashlib.sha256(value).hexdigest() != row['sha256']:
        raise RuntimeError('source binding mismatch: ' + row['name'])
names = []
for module in ['Span', 'Witnesses']:
    source = (ROOT / 'lean' / (module + '.lean')).read_text()
    if re.search(r'\b(sorry|admit|axiom|unsafe|native_decide)\b', source):
        raise RuntimeError('forbidden Lean token')
    names += ['TerminalSpan.' + n for n in re.findall(r'^theorem (\w+)', source, re.M)]
if names != read('AUDITS.json'):
    raise RuntimeError('audit roster mismatch')
out.mkdir(parents=True)
env = {k: v for k, v in os.environ.items() if not k.startswith(('LEAN_', 'PYTHON'))}
env['LEAN_PATH'] = str(out)
records = []


def run(command, expected=0, marker=None):
    if command[0] == str(lean):
        command = [command[0], '-R', str(ROOT / 'lean'), *command[1:]]
    result = subprocess.run(command, cwd=out, env=env, text=True, capture_output=True)
    records.append({'command': command, 'exit': result.returncode,
                    'stdout': result.stdout, 'stderr': result.stderr})
    (out / 'COMMANDS.json').write_text(json.dumps(records, indent=2) + '\n')
    if result.returncode != expected or (marker and marker not in result.stdout):
        raise RuntimeError('command failed: ' + result.stdout + result.stderr)
    return result.stdout


for module in ['Span', 'Witnesses', 'Mutants']:
    run([str(lean), '-o', str(out / (module + '.olean')), str(ROOT / 'lean' / (module + '.lean'))])
audit = run([str(lean), str(ROOT / 'lean/Audit.lean')])
reports = re.findall(r"'(TerminalSpan\.\w+)' (?:depends on axioms: \[([^]]*)\]|does not depend on any axioms)", audit, re.S)
if [name for name, _ in reports] != names:
    raise RuntimeError('actual axiom roster mismatch')
for name, axioms in reports:
    if set(re.findall(r'\w+(?:\.\w+)*', axioms)) - {'propext', 'Quot.sound', 'Classical.choice'}:
        raise RuntimeError('unapproved axiom: ' + name)
run([str(lean), '--run', str(ROOT / 'lean/Mutants.lean'), 'candidate'], marker='PASS 4 semantic challenges')
for mode, case in [('ascii', 'escaped'), ('metadata', 'escaped'), ('no-reset', 'comment'),
                   ('normalized', 'escaped'), ('inner', 'block')]:
    run([str(lean), '--run', str(ROOT / 'lean/Mutants.lean'), mode], 42,
        'SEMANTIC_MISMATCH ' + mode + ' ' + case)
authenticate()
result = {'status': 'PASS', 'audits': len(names), 'bindings': len(read('SOURCE-BINDINGS.json')),
          'compiled_semantic_mutants': 5, 'mutant_scope': 'Lean model operations; not native Rust mutations',
          'source_translation_proved': False, 'whole_serialization_proved': False}
(out / 'RESULT.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result))
