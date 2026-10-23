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
import stat
import subprocess

ROOT = Path(__file__).resolve().parent
EXPECTED_FILES = frozenset(['BINDINGS.json', 'SCOPE.md', 'SOURCE-PINS.json', 'TOOLS.json', 'extract.py', 'facade-main.cpp', 'facade-prefix.cpp', 'falseclaims/absent_hidden_ancestor.lean', 'falseclaims/dirty_barrier_coverage.lean', 'falseclaims/dirty_barrier_query.lean', 'falseclaims/external_target_marked.lean', 'input/CANDIDATE.json', 'input/candidate.cpp', 'input/candidate.patch', 'input/native-frame.cpp', 'input/native-pres-shell.cpp', 'input/original.cpp', 'lean/Audit.lean', 'lean/Hidden.lean', 'lean/Rows.lean', 'lean/Subtree.lean', 'replay.py'])

def require(condition, message):
    if not condition:
        raise RuntimeError(message)

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')

def authenticate(pin):
    for f in ROOT.rglob('*'):
        require(stat.S_ISREG(f.lstat().st_mode) or stat.S_ISDIR(f.lstat().st_mode), 'NONREGULAR')
    require(sha(ROOT / 'FILES.json') == pin, 'MANIFEST_PIN')
    manifest = json.loads((ROOT / 'FILES.json').read_text())
    files = manifest['files']
    require(set(files) == EXPECTED_FILES, 'PAYLOAD_ROSTER')
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
    require({str(f.relative_to(ROOT / 'input')): sha(f) for f in (ROOT / 'input').rglob('*') if f.is_file()} == pins['input'], 'SOURCE_ROLE_PINS')
    require(sha(ROOT / 'lean/Hidden.lean') == pins['imported_Hidden_sha256'], 'IMPORTED_MODEL_PIN')
    model = (ROOT / 'lean/Hidden.lean').read_text() + (ROOT / 'lean/Subtree.lean').read_text()
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


summary = {'outcome': 'INCOMPLETE', 'scope': 'subtree marking/query admission projection; not full native proof'}
try:
    lean = tools['lean']['path']
    clang = tools['clang']['path']
    names = []
    for module in ('Hidden', 'Subtree'):
        source = ROOT / 'lean' / (module + '.lean')
        product = out / 'lean' / (module + '.olean')
        products.append(product)
        run('lean-' + module, [lean, '-o', str(product), str(source)])
        names.extend(module + '.' + n for n in re.findall(r'^theorem ([A-Za-z0-9_]+)', source.read_text(), re.M))
    audits, auditerr = run('lean-audits', [lean, str(ROOT / 'lean/Audit.lean')])
    require(len(names) == 66 and re.findall(r"^'([A-Za-z0-9_.]+)'", audits, re.M) == names, 'EXACT_AUDIT_ROSTER')
    require(re.findall(r'#print axioms ([A-Za-z0-9_.]+)', (ROOT / 'lean/Audit.lean').read_text()) == names, 'AUDIT_SOURCE_ROSTER')
    require(not auditerr and 'warning' not in audits, 'AXIOM_AUDIT')
    for line in audits.splitlines():
        match = re.search(r'depends on axioms: \[(.*?)\]', line)
        require(match is not None or 'does not depend on any axioms' in line, 'AUDIT_FORMAT')
        if match:
            require(set(match.group(1).split(', ')) <= {'propext', 'Classical.choice', 'Quot.sound'}, 'AXIOM_ALLOWLIST')
    rows_text, rowerr = run('lean-rows', [lean, '--run', str(ROOT / 'lean/Rows.lean')])
    rows = rows_text.splitlines()
    require(len(rows) == 6144 and all(len(r.split(',')) == 38 and int(r.split(',')[0]) == i for i, r in enumerate(rows)), 'ROW_SCHEMA')
    require(not rowerr, 'LEAN_ROWS_STDERR')
    falseclaims = []
    for source in sorted((ROOT / 'falseclaims').glob('*.lean')):
        stdout, stderr = run('false-' + source.stem, [lean, str(source)], expected=None)
        require('Tactic `decide` proved that the proposition' in stdout and '\nis false' in stdout and not stderr, 'FALSECLAIM_REASON')
        falseclaims.append(source.stem)
    require(len(falseclaims) == 4, 'FALSECLAIM_COUNT')
    variants = ['none', 'omit_mark', 'root_bit_only', 'has_dirty_children_prunes', 'principal_lists_only', 'ignore_table_barrier', 'ignore_dirty_barrier', 'force_clean_query']
    mutations = []
    comparisons = []
    for variant in variants:
        generated = extract.generate(variant)
        if variant != 'none': require(generated != extract.generate(), 'INERT_MUTATION')
        cpp = out / 'native' / (variant + '.cpp')
        cpp.write_text(generated)
        for optimization in ('O0', 'O2'):
            executable = out / 'native' / (variant + '-' + optimization)
            products.append(executable)
            run('compile-' + executable.name, [clang, '-std=c++20', '-' + optimization, '-fsanitize=undefined', '-fno-sanitize-recover=all', str(cpp), '-o', str(executable)])
            stdout, stderr = run('run-' + executable.name, [str(executable)])
            actual = stdout.splitlines()
            require(not stderr and len(actual) == 6144, 'NATIVE_EXECUTION')
            changes = [{'row': i, 'expected': a, 'actual': b} for i, (a, b) in enumerate(zip(rows, actual)) if a != b]
            if variant == 'none':
                require(not changes, 'NATIVE_MODEL_DIFFERENCE')
                comparisons.append({'optimization': optimization, 'rows': len(rows)})
            else:
                require(changes, 'UNDETECTED_MUTANT:' + variant)
                mutations.append({'name': variant, 'optimization': optimization, 'different_rows': len(changes), 'first_difference': changes[0]})
    summary = {'outcome': 'PASS_SCOPED_SUBTREE_PROJECTION', 'manifest_sha256': args.manifest_sha, 'new_audits': 36, 'imported_audits': 30, 'bindings': len(extract.extract()[1]), 'comparisons': comparisons, 'mutants': mutations, 'falseclaims': falseclaims, 'scope': 'marking and query admission; forced traversal/layout completion and native lifecycle closure remain provider obligations'}
finally:
    write_json(out / 'COMMANDS.json', commands)
    for product in products:
        if product.exists(): product.unlink()
    summary['removed_products'] = [str(x.relative_to(out)) for x in products]
    write_json(out / 'SUMMARY.json', summary)
print(json.dumps(summary, sort_keys=True))
