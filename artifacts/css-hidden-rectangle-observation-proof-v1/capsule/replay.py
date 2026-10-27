import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise SystemExit('Require python3 -I -S without optimization')
sys.dont_write_bytecode = True
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import tempfile

parser = argparse.ArgumentParser()
parser.add_argument('--manifest-sha', required=True)
parser.add_argument('--repo', type=Path, required=True)
parser.add_argument('--output', type=Path, required=True)
args = parser.parse_args()
here = Path(__file__).resolve().parent
repo = args.repo.resolve()
out = args.output.resolve()
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
read = lambda path: json.loads(path.read_text())

def need(ok, message):
    if not ok:
        raise RuntimeError(message)

def authenticate(base, pins):
    for name, digest in pins.items():
        need(not Path(name).is_absolute() and '..' not in Path(name).parts, 'unsafe path')
        file = base / name
        need(stat.S_ISREG(file.lstat().st_mode) and sha(file) == digest, 'changed input ' + name)

need(not out.exists() and out != here and here not in out.parents and out not in here.parents,
     'fresh output outside capsule required')
need(sha(here / 'FILES.json') == args.manifest_sha, 'manifest identity')
manifest = read(here / 'FILES.json')
actual = set()
for path in here.rglob('*'):
    mode = path.lstat().st_mode
    if stat.S_ISDIR(mode):
        continue
    need(stat.S_ISREG(mode), 'nonregular capsule input')
    actual.add(path.relative_to(here).as_posix())
need(actual == set(manifest) | {'FILES.json'}, 'closed capsule roster')
authenticate(here, manifest)
imports = read(here / 'IMPORTS.json')
need(set(imports) == {'Hidden.lean', 'Subtree.lean', 'CssSemantics/TransitionMachine.lean'}, 'import roster')
authenticate(repo, {item['path']: item['sha256'] for item in imports.values()})
binding = read(here / 'BINDINGS.json')
authenticate(repo, binding['files'])
cases = [case for case in read(repo / binding['measurement_path']) if case['index'] == binding['case_index']]
need(len(cases) == 1 and cases[0]['name'] == binding['case_name'], 'measurement case')
rows = [row for row in cases[0]['rows'] if row['stage'] == binding['stage']]
need(len(rows) == 1 and all(rows[0][key] == binding[key] for key in ['first', 'repeat', 'visible']),
     'measurement rectangle binding')
lean = read(here / 'TOOLS.json')['lean']
need(sha(Path(lean['path'])) == lean['sha256'], 'compiler identity')
names = read(here / 'AUDITS.json')
source_names = []
for file, namespace in [('CssSemantics/ProviderObservation.lean', 'CssSemantics.ProviderObservation'),
                        ('MathMLRectObservation.lean', 'MathMLRectObservation')]:
    source_names.extend(namespace + '.' + name for name in
        re.findall(r'^theorem (\w+)', (here / 'lean' / file).read_text(), re.M))
need(names == source_names == re.findall(r'#print axioms ([\w.]+)',
     (here / 'lean/Audit.lean').read_text()), 'exact audit roster')
need({p.name for p in (here / 'falseclaims').iterdir()} == {'ObserveBefore.lean', 'SelectedSizeOnly.lean'},
     'negative control roster')
out.mkdir(parents=True)
commands = []
summary = {'status': 'INCOMPLETE'}

def run(name, source, work, env, output=False, success=True):
    command = [lean['path']] + (['-o', source.removesuffix('.lean') + '.olean'] if output else []) + [source]
    result = subprocess.run(command, cwd=work, env=env, capture_output=True, text=True, timeout=60)
    (out / (name + '.stdout')).write_text(result.stdout)
    (out / (name + '.stderr')).write_text(result.stderr)
    commands.append({'name': name, 'command': command, 'exit': result.returncode})
    need((result.returncode == 0) if success else (result.returncode != 0), 'unexpected compiler exit ' + name)
    return result.stdout, result.stderr

try:
    with tempfile.TemporaryDirectory(prefix='rectangle-proof-', dir=out) as directory:
        work = Path(directory)
        env = dict(os.environ, LEAN_PATH=str(work))
        for target, item in imports.items():
            destination = work / target
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes((repo / item['path']).read_bytes())
        for source in (here / 'lean').rglob('*.lean'):
            destination = work / source.relative_to(here / 'lean')
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(source.read_bytes())
        for source in ['CssSemantics/TransitionMachine.lean', 'Hidden.lean', 'Subtree.lean',
                       'CssSemantics/ProviderObservation.lean', 'MathMLRectObservation.lean']:
            stdout, stderr = run(Path(source).stem, source, work, env, output=True)
            need(not stdout and not stderr, 'unexpected compiler diagnostics')
        stdout, stderr = run('Audit', 'Audit.lean', work, env)
        need(not stderr and re.findall(r"^'([\w.]+)'", stdout, re.M) == names, 'audit output roster')
        for line in stdout.splitlines():
            match = re.search(r'depends on axioms: \[(.*?)\]', line)
            need(match is not None or 'does not depend on any axioms' in line, 'audit format')
            if match:
                need(set(match[1].split(', ')) <= {'propext', 'Quot.sound'}, 'unexpected axiom')
        for source in sorted((here / 'falseclaims').glob('*.lean')):
            (work / source.name).write_bytes(source.read_bytes())
            stdout, stderr = run(source.stem, source.name, work, env, success=False)
            need(not stderr and 'Tactic `decide` proved that the proposition' in stdout
                 and 'is false' in stdout, 'negative control did not refute its proposition')
        summary = {'status': 'PASS_SCOPED_RECTANGLE_OBSERVATION_MODEL', 'audited_names': names,
            'negative_controls': ['ObserveBefore', 'SelectedSizeOnly'],
            'world_preserved_by_erasure': True, 'native_correctness_proved': False,
            'full_CSSOM_geometry_proved': False, 'compiler_sha256': lean['sha256']}
except BaseException as error:
    summary['failure'] = repr(error)
    raise
finally:
    summary['temporary_products_removed'] = not any(path.is_dir() for path in out.iterdir())
    (out / 'COMMANDS.json').write_text(json.dumps(commands, indent=2) + '\n')
    (out / 'SUMMARY.json').write_text(json.dumps(summary, indent=2) + '\n')
print(json.dumps(summary))
