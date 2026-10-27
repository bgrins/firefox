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

def need(ok, reason):
    if not ok:
        raise RuntimeError(reason)

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

parser = argparse.ArgumentParser()
parser.add_argument('--manifest-sha', required=True)
parser.add_argument('--output', type=Path, required=True)
parser.add_argument('--timing-state', type=Path)
args = parser.parse_args()
here = Path(__file__).resolve().parent
out = args.output.resolve()
need(not out.exists() and out != here and here not in out.parents
     and out not in here.parents, 'Require fresh external output')
need(stat.S_ISREG((here/'FILES.json').lstat().st_mode), 'Manifest must be regular')
need(sha(here/'FILES.json') == args.manifest_sha, 'External manifest pin')
files = json.loads((here/'FILES.json').read_text())
directories = {p.as_posix() for name in files for p in Path(name).parents if p.as_posix() != '.'}
actual = set()
for f in here.rglob('*'):
    name = f.relative_to(here).as_posix()
    mode = f.lstat().st_mode
    if stat.S_ISDIR(mode):
        need(name in directories, 'Unexpected directory '+name)
    else:
        need(stat.S_ISREG(mode), 'Nonregular input '+name)
        actual.add(name)
need(actual == set(files) | {'FILES.json', 'FREEZE.json'}, 'Closed file roster')
for name, pin in files.items():
    need(not Path(name).is_absolute() and '..' not in Path(name).parts, 'Unsafe path')
    need(sha(here/name) == pin, 'Input hash '+name)
mapping = json.loads((here/'SOURCE-MAP.json').read_text())
for name, pin in mapping['imports'].items():
    need(sha(here/'lean'/(name+'.lean')) == pin, 'Imported model '+name)
methods = json.loads((here/'provenance/source-audit-METHODS.json').read_text())
for name, pin in methods.items():
    need(sha(here/'source'/(name+'.cpp')) == pin, 'Retained source method '+name)
lean = json.loads((here/'TOOLS.json').read_text())['lean']
need(sha(Path(lean['path'])) == lean['sha256'], 'Lean executable pin')
names = json.loads((here/'AUDITS.json').read_text())
need(names == ['FloatReady.'+n for n in re.findall(r'^theorem (\w+)',
     (here/'lean/FloatReady.lean').read_text(), re.M)], 'Exact theorem roster')
need(names == re.findall(r'#print axioms ([\w.]+)',
     (here/'lean/Audit.lean').read_text()), 'Exact audit source roster')
out.mkdir(parents=True)
commands = []
summary = {'status': 'INCOMPLETE'}
cleanup = {'generated_paths': [], 'removed_bytes': 0}

def run(name, argv, work, success=True):
    if args.timing_state:
        state = json.loads(args.timing_state.read_text())['status']
        need(not state.startswith('cost '), 'Performance timing hold active')
    result = subprocess.run(argv, cwd=work, env=dict(os.environ, LEAN_PATH=str(work)),
                            capture_output=True, text=True)
    (out/(name+'.stdout')).write_text(result.stdout)
    (out/(name+'.stderr')).write_text(result.stderr)
    commands.append({'name': name, 'argv': argv, 'cwd': str(work), 'exit': result.returncode})
    need((result.returncode == 0) if success else (result.returncode != 0), 'Exit '+name)
    return result.stdout, result.stderr

try:
    with tempfile.TemporaryDirectory(prefix='owned-lean-', dir=out) as temp:
        work = Path(temp)
        try:
            for f in (here/'lean').glob('*.lean'):
                (work/f.name).write_bytes(f.read_bytes())
            for name in ['Hidden', 'Subtree', 'LineReady', 'FloatReady']:
                stdout, stderr = run(name, [lean['path'], '-o', name+'.olean', name+'.lean'], work)
                need(not stdout and not stderr, 'Unexpected compiler diagnostic '+name)
            stdout, stderr = run('audit', [lean['path'], 'Audit.lean'], work)
            need(not stderr and re.findall(r"^'([\w.]+)'", stdout, re.M) == names, 'Exact audited names')
            for line in stdout.splitlines():
                match = re.search(r'depends on axioms: \[(.*?)\]', line)
                need(match is not None or 'does not depend on any axioms' in line, 'Audit format')
                if match:
                    need(set(match.group(1).split(', ')) <= {'propext', 'Quot.sound', 'Classical.choice'}, 'Unexpected axiom')
            for f in sorted((here/'falseclaims').glob('*.lean')):
                (work/f.name).write_bytes(f.read_bytes())
                stdout, stderr = run('false-'+f.stem, [lean['path'], f.name], work, False)
                need('Tactic `decide` proved that the proposition' in stdout
                     and 'is false' in stdout and not stderr, 'Falseclaim rejected for wrong reason')
            summary = {'status': 'PASS_SCOPED_INSTANTIATION', 'new_audits': len(names),
                       'imported_modules': ['Hidden', 'Subtree', 'LineReady'], 'falseclaims': 4,
                       'native_execution': False, 'native_projection_closed': False}
        finally:
            cleanup['generated_paths'] = [str(f) for f in work.rglob('*') if f.is_file()]
            cleanup['removed_bytes'] = sum(f.stat().st_size for f in work.rglob('*') if f.is_file())
finally:
    cleanup['remaining_generated_directories'] = [str(f) for f in out.iterdir() if f.is_dir()]
    (out/'CLEANUP.json').write_text(json.dumps(cleanup, indent=2)+'\n')
    (out/'COMMANDS.json').write_text(json.dumps(commands, indent=2)+'\n')
    (out/'SUMMARY.json').write_text(json.dumps(summary, indent=2)+'\n')
print(json.dumps(summary))
