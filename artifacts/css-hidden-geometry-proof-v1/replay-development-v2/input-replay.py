import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise SystemExit('REJECT: run python3 -I -S without -O')
sys.dont_write_bytecode = True
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parent

def require(condition, message):
    if not condition:
        raise RuntimeError(message)

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')

def authenticate(pin):
    require(sha(ROOT / 'FILES.json') == pin, 'MANIFEST_PIN')
    manifest = json.loads((ROOT / 'FILES.json').read_text())
    files = manifest['files']
    require(all(not Path(n).is_absolute() and '..' not in Path(n).parts for n in files), 'UNSAFE_PATH')
    actual = {str(f.relative_to(ROOT)) for f in ROOT.rglob('*') if not f.is_dir()}
    require(not any(f.is_symlink() for f in ROOT.rglob('*')), 'SYMLINK')
    require(actual == set(files) | {'FILES.json', 'FREEZE.json'}, 'CLOSED_ROSTER')
    expected_dirs = {str(parent) for n in files for parent in Path(n).parents if str(parent) != '.'}
    actual_dirs = {str(f.relative_to(ROOT)) for f in ROOT.rglob('*') if f.is_dir()}
    require(actual_dirs == expected_dirs, 'CLOSED_DIRECTORIES')
    for n, value in files.items():
        require(sha(ROOT / n) == value, 'PAYLOAD_HASH:' + n)
    freeze = json.loads((ROOT / 'FREEZE.json').read_text())
    require(freeze == {'FILES_sha256': pin, 'payload_count': len(files)}, 'FREEZE')
    pins = json.loads((ROOT / 'SOURCE-PINS.json').read_text())
    require({str(f.relative_to(ROOT / 'input')): sha(f) for f in (ROOT / 'input').rglob('*') if f.is_file()} == pins['files'], 'SOURCE_ROLE_PINS')
    model = (ROOT / 'lean/Hidden.lean').read_text()
    require(not re.search(r'\b(sorry|admit|axiom|native_decide|unsafe)\b', model), 'MODEL_PROOF_ESCAPE')
    return manifest

parser = argparse.ArgumentParser()
parser.add_argument('--manifest-sha', required=True)
parser.add_argument('--out', type=Path)
parser.add_argument('--verify-only', action='store_true')
args = parser.parse_args()
manifest = authenticate(args.manifest_sha)
spec = importlib.util.spec_from_file_location('hidden_extract', ROOT / 'extract.py')
extract = importlib.util.module_from_spec(spec)
spec.loader.exec_module(extract)
require(extract.extract()[1] == json.loads((ROOT / 'BINDINGS.json').read_text()), 'SOURCE_BINDINGS')
if args.verify_only:
    print(json.dumps({'verified': len(manifest['files']), 'bindings': len(extract.extract()[1])}))
    raise SystemExit(0)
require(args.out is not None, 'OUTPUT_REQUIRED')
out = args.out.resolve()
require(out != ROOT and ROOT not in out.parents and out not in ROOT.parents, 'OUTPUT_OVERLAP')
require(not out.exists(), 'OUTPUT_EXISTS')
tools = json.loads((ROOT / 'TOOLS.json').read_text())
for tool in tools.values():
    require(sha(Path(tool['path'])) == tool['sha256'], 'TOOL_PIN')
    require(subprocess.check_output([tool['path'], '--version'], text=True) == tool['version'], 'TOOL_VERSION')
out.mkdir(parents=True)
(out / 'lean').mkdir()
(out / 'native').mkdir()
env = {k: os.environ[k] for k in ('PATH', 'HOME', 'TMPDIR') if k in os.environ}
env['LEAN_PATH'] = str(out / 'lean')
commands = []
products = []

def run(name, cmd, expected=0, cwd=None):
    result = subprocess.run(cmd, cwd=cwd or ROOT / 'lean', env=env, capture_output=True, text=True)
    (out / (name + '.stdout')).write_text(result.stdout)
    (out / (name + '.stderr')).write_text(result.stderr)
    commands.append({'name': name, 'argv': [str(x) for x in cmd], 'exit': result.returncode})
    require(result.returncode == expected if expected is not None else result.returncode != 0, 'COMMAND_EXIT:' + name)
    return result.stdout, result.stderr

summary = {'outcome': 'INCOMPLETE', 'scope': 'bounded extracted state-machine calibration; not full native proof'}
try:
    lean = tools['lean']['path']
    clang = tools['clang']['path']
    olean = out / 'lean/Hidden.olean'
    products.append(olean)
    run('lean-model', [lean, '-o', str(olean), str(ROOT / 'lean/Hidden.lean')])
    audits, auditerr = run('lean-audits', [lean, str(ROOT / 'lean/Audit.lean')])
    names = re.findall(r'^theorem ([A-Za-z0-9_]+)', (ROOT / 'lean/Hidden.lean').read_text(), re.M)
    require(len(names) == 29 and len(audits.splitlines()) == len(names), 'AUDIT_COUNT')
    require('sorryAx' not in audits and not auditerr and 'warning' not in audits, 'AXIOM_AUDIT')
    for line in audits.splitlines():
        match = re.search(r'depends on axioms: \[(.*?)\]', line)
        require(match is not None or 'does not depend on any axioms' in line, 'AUDIT_FORMAT')
        if match:
            require(set(match.group(1).split(', ')) <= {'propext', 'Classical.choice', 'Quot.sound'}, 'AXIOM_ALLOWLIST')
    lean_rows = {}
    for variant in ('old', 'repaired'):
        result, err = run('lean-rows-' + variant, [lean, '--run', str(ROOT / 'lean/Rows.lean'), variant])
        rows = result.splitlines()
        require(len(rows) == 192 and all(len(r.split(',')) == 14 and int(r.split(',')[0]) == i for i, r in enumerate(rows)), 'ROW_SCHEMA')
        require(not err, 'LEAN_ROWS_STDERR')
        lean_rows[variant] = rows
    falseclaims = []
    for source in sorted((ROOT / 'falseclaims').glob('*.lean')):
        stdout, stderr = run('false-' + source.stem, [lean, str(source)], expected=None)
        require('Tactic `decide` proved that the proposition' in stdout and '\nis false' in stdout and 'error' in stdout and not stderr, 'FALSECLAIM_REASON')
        falseclaims.append(source.stem)
    require(len(falseclaims) == 4, 'FALSECLAIM_COUNT')
    comparisons = []
    for variant in ('old', 'repaired'):
        cpp = out / 'native' / (variant + '.cpp')
        cpp.write_text(extract.generate(variant == 'repaired'))
        for optimization in ('O0', 'O2'):
            executable = out / 'native' / (variant + '-' + optimization)
            products.append(executable)
            run('compile-' + executable.name, [clang, '-std=c++20', '-' + optimization, '-fsanitize=undefined', '-fno-sanitize-recover=all', str(cpp), '-o', str(executable)])
            stdout, stderr = run('run-' + executable.name, [str(executable)])
            require(not stderr and stdout.splitlines() == lean_rows[variant], 'NATIVE_MODEL_DIFFERENCE:' + executable.name)
            comparisons.append({'variant': variant, 'optimization': optimization, 'rows': 192})
    mutants = []
    for name in ('drop_dirty_mark', 'reuse_dirty', 'omit_cb_key', 'skip_publication', 'force_clean_query', 'ignore_forced_set'):
        generated = extract.generate(True, name)
        require(generated != extract.generate(True), 'INERT_MUTATION:' + name)
        cpp = out / 'native' / (name + '.cpp')
        cpp.write_text(generated)
        for optimization in ('O0', 'O2'):
            executable = out / 'native' / (name + '-' + optimization)
            products.append(executable)
            run('compile-' + executable.name, [clang, '-std=c++20', '-' + optimization, '-fsanitize=undefined', '-fno-sanitize-recover=all', str(cpp), '-o', str(executable)])
            stdout, stderr = run('run-' + executable.name, [str(executable)])
            rows = stdout.splitlines()
            require(not stderr and len(rows) == 192, 'MUTANT_EXECUTION')
            differences = [{'row': i, 'expected': a, 'actual': b} for i, (a, b) in enumerate(zip(lean_rows['repaired'], rows)) if a != b]
            require(differences, 'UNDETECTED_MUTANT:' + name)
            mutants.append({'name': name, 'optimization': optimization, 'different_rows': len(differences), 'first_difference': differences[0]})
    changes = [{'row': i, 'old': a, 'repaired': b} for i, (a, b) in enumerate(zip(lean_rows['old'], lean_rows['repaired'])) if a != b]
    write_json(out / 'CHANGES.json', changes)
    summary = {'outcome': 'PASS_SCOPED_MODEL_AND_CALIBRATION', 'manifest_sha256': args.manifest_sha, 'audits': len(names), 'falseclaims': falseclaims, 'bindings': len(extract.extract()[1]), 'comparisons': comparisons, 'mutants': mutants, 'old_repaired_differing_rows': len(changes), 'scope': 'direct-item model and bounded extracted facade only; descendant/caller/provider obligations remain open'}
finally:
    write_json(out / 'COMMANDS.json', commands)
    for product in products:
        if product.exists():
            product.unlink()
    summary['removed_products'] = [str(x.relative_to(out)) for x in products]
    write_json(out / 'SUMMARY.json', summary)
print(json.dumps(summary, sort_keys=True))
