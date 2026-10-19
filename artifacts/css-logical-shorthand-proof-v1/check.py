import hashlib
import json
import os
from pathlib import Path
import re
import resource
import subprocess
import sys

from bridge import generate, inventory
from controls import LEAN_MUTATIONS, RUST_MUTATIONS
from prepare import extract

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[1]
LEAN = ROOT / 'artifacts/stylo-bloom-tools/lean-4.35.0-rc4-darwin_aarch64/bin/lean'
RUSTC = Path('/Users/bgrins/.rustup/toolchains/1.97.1-aarch64-apple-darwin/bin/rustc')
OMEGA = 'omega could not prove the goal:'
SUBST = "Tactic `subst` failed: did not find equation for eliminating 'd'"
APP = 'Application type mismatch: The argument'
ERRORS = {
    'MappingBeforeCount': [('priority_refinement', OMEGA)] * 2 + [('old_counterexample', 'Tactic `decide` proved that the proposition')],
    'OmitLogicalTie': [('priority_refinement', OMEGA)] * 2,
    'ReverseIDL': [('priority_refinement', OMEGA)] * 2,
    'ReverseCount': [('priority_refinement', OMEGA)] * 4,
    'DropMatch': [('first_member', SUBST), ('first_none', 'unsolved goals'), ('sorted_first_wins', SUBST)],
    'WrongTarget': [('first_member', SUBST), ('first_member', APP), ('first_member', APP), ('first_none', 'unsolved goals'), ('sorted_first_wins', SUBST), ('sorted_first_wins', APP)],
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def negative(source, path, code, stdout, stderr, expected):
    if code != 1 or stderr:
        raise RuntimeError('Wrong negative terminal')
    lines = source.splitlines()
    decls = [(i, line) for i, line in enumerate(lines, 1) if re.match(r'^(theorem |def |instance |structure |#print|end )', line)]
    spans = {}
    for j, (start, line) in enumerate(decls[:-1]):
        if line.startswith('theorem '):
            end = decls[j + 1][0]
            bodies = [i for i in range(start, end) if ':= by' in lines[i - 1]]
            if not bodies:
                raise RuntimeError('Ambiguous proof body')
            spans[line.split()[1]] = (bodies[0], end)
    headers = re.findall(r'^(.+):(\d+):\d+: error(?:\([^\n)]*\))?: (.*)$', stdout, re.M)
    if len(re.findall(r'\berror(?:\([^\n)]*\))?:', stdout)) != len(headers):
        raise RuntimeError('Unlocated diagnostic')
    found = []
    for filename, line, message in headers:
        owners = [n for n, (a, b) in spans.items() if a <= int(line) < b]
        if filename != str(path) or len(owners) != 1:
            raise RuntimeError('Foreign diagnostic')
        found.append((owners[0], message))
    if found != expected:
        raise RuntimeError('Wrong failing theorem inventory: ' + repr(found))
    return found


def sources(read, live=False):
    records = json.loads((BASE / 'SOURCE-v1.json').read_text())
    for row in records:
        text = read(row['snapshot'])
        if hashlib.sha256(text.encode()).hexdigest() != row['sha256']:
            raise RuntimeError('Source snapshot changed: ' + row['snapshot'])
        if live and row['snapshot'] != 'native-before.rs':
            if extract((ROOT / row['source']).read_text(), row['kind']) != text:
                raise RuntimeError('Live source drift: ' + row['source'])
    return records


def main():
    if sys.flags.optimize or len(sys.argv) not in [2, 3] or (len(sys.argv) == 3 and sys.argv[2] != '--live'):
        raise RuntimeError('Usage: python3 check.py NEW_OUTPUT_DIRECTORY [--live]')
    out = Path(sys.argv[1]).resolve()
    out.mkdir()
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    live = len(sys.argv) == 3
    read = lambda n: (BASE / n).read_text()
    records = sources(read, live)
    data = inventory()
    if data != json.loads(read('inventory-v1.json')):
        raise RuntimeError('Inventory fixture mismatch')
    toolchain = json.loads(read('TOOLCHAIN-v1.json'))
    for name, expected in toolchain.items():
        if sha(Path(name)) != expected:
            raise RuntimeError('Toolchain drift')
    names = (BASE / 'tooling-paths-v1.txt').read_text().splitlines()
    pins = [BASE / n for n in names] + [LEAN, RUSTC]
    if live:
        pins += [ROOT / r['source'] for r in records if r['snapshot'] != 'native-before.rs']
    before = {str(p): sha(p) for p in pins}
    source_controls = []
    for row in records:
        changed = row['snapshot']
        try:
            sources(lambda n: read(n) + '\n' if n == changed else read(n))
        except RuntimeError:
            source_controls.append(changed)
        else:
            raise RuntimeError('Accepted corrupted source')
    inventory_controls = []
    mutations = {
        'missing-shorthand': ('generated-shorthands.rs', '        All = 94,', ''),
        'missing-member': ('generated-shorthands.rs', 'LonghandId::MarginTop,', 'LonghandId::UnknownProperty,'),
        'bad-idl-order': ('generated-idl.rs', '            60,', '            61,'),
        'missing-bitset-word': ('generated-logical.rs', ', 0x6]', ']'),
    }
    for label, (name, old, new) in mutations.items():
        if old not in read(name):
            raise RuntimeError('Bad inventory mutation')
        try:
            inventory(lambda n: read(n).replace(old, new, 1) if n == name else read(n))
        except RuntimeError:
            inventory_controls.append(label)
        else:
            raise RuntimeError('Accepted invalid inventory')
    commands = []

    def run(command, directory, label, env=None):
        p = subprocess.run(command, cwd=directory, env=env, capture_output=True, text=True)
        (directory / (label + '.stdout')).write_text(p.stdout)
        (directory / (label + '.stderr')).write_text(p.stderr)
        commands.append({'command': command, 'cwd': str(directory), 'exit': p.returncode})
        return p

    model = read('Priority.lean')
    if re.search(r'\b(sorry|admit|axiom|unsafe|native_decide)\b', model.replace('#print axioms', '')):
        raise RuntimeError('Unchecked construct')
    lean_controls = {}
    samples = {}
    for name, mutation in [('positive', None), *LEAN_MUTATIONS.items()]:
        directory = out / name
        directory.mkdir()
        if mutation and model.count(mutation[0]) != 1:
            raise RuntimeError('Mutation cardinality')
        text = model if mutation is None else model.replace(*mutation)
        path = directory / 'Priority.lean'
        path.write_text(text)
        env = os.environ.copy()
        env['LEAN_PATH'] = str(directory)
        env.pop('LEAN_SRC_PATH', None)
        command = [str(LEAN), '-DwarningAsError=true', '-Dlinter.unusedSimpArgs=false', '-Dlinter.unusedVariables=false']
        if mutation is None:
            command += ['-o', str(directory / 'Priority.olean')]
        p = run(command + [str(path)], directory, 'lean', env)
        if mutation is None:
            if p.returncode != 0 or p.stderr or p.stdout != read('expected-axioms.txt'):
                raise RuntimeError('Positive proof/audit failed')
        else:
            lean_controls[name] = negative(text, path, p.returncode, p.stdout, p.stderr, ERRORS[name])
            samples[name] = (text, path, p)
    text, path, p = samples['OmitLogicalTie']
    header = re.search(r'^.+:\d+:\d+: error:.*$', p.stdout, re.M).group(0)
    fake = {
        'exit-zero': (0, p.stdout, ''), 'exit-two': (2, p.stdout, ''),
        'stderr': (1, p.stdout, 'noise'), 'empty': (1, '', ''),
        'foreign-file': (1, p.stdout.replace(str(path), str(path) + '-other', 1), ''),
        'outside-proof': (1, re.sub(r':\d+:\d+: error:', ':1:1: error:', p.stdout, count=1), ''),
        'extra-error': (1, p.stdout + '\n' + header + '\n', ''),
        'unlocated': (1, p.stdout + '\nerror: noise\n', ''),
        'parse-error': (1, p.stdout.replace(OMEGA, "unexpected token", 1), ''),
    }
    record_controls = []
    for label, (code, stdout, stderr) in fake.items():
        try:
            negative(text, path, code, stdout, stderr, ERRORS['OmitLogicalTie'])
        except RuntimeError:
            record_controls.append(label)
        else:
            raise RuntimeError('Accepted forged proof result')
    rust_controls = {}
    native = read('native-candidate.rs')
    for name, mutation in [('positive', None), *RUST_MUTATIONS.items()]:
        directory = out / ('rust-' + name)
        directory.mkdir()
        if mutation and native.count(mutation[0]) != 1:
            raise RuntimeError('Rust mutation cardinality: ' + name)
        text = native if mutation is None else native.replace(*mutation)
        path = directory / 'bridge.rs'
        path.write_text(generate(text, data))
        executable = directory / 'bridge'
        p = run([str(RUSTC), '-Awarnings', str(path), '-o', str(executable)], directory, 'compile')
        if p.returncode != 0 or p.stdout or p.stderr:
            raise RuntimeError('Rust compilation failed: ' + name)
        p = run([str(executable)], directory, 'run')
        if mutation is None:
            if p.returncode != 0 or p.stderr or p.stdout != '527 properties, 277729 ordered pairs\n':
                raise RuntimeError('Positive bridge failed')
        else:
            expected = {
                'MappingBeforeCount': ('432 433', 'Less', 'Greater'),
                'OmitLogicalTie': ('433 465', 'Less', 'Greater'),
                'ReverseLogicalTie': ('433 465', 'Less', 'Greater'),
                'ReverseCount': ('432 433', 'Less', 'Greater'),
                'ReverseIDL': ('432 435', 'Greater', 'Less'),
            }[name]
            found = re.findall(r'assertion `left == right` failed: pair (\d+ \d+)\n  left: (Less|Equal|Greater)\n right: (Less|Equal|Greater)', p.stderr)
            if p.returncode != 101 or p.stdout or found != [expected] or str(path) not in p.stderr:
                raise RuntimeError('Wrong Rust negative failure: ' + name + repr(found))
            rust_controls[name] = {'exit': p.returncode, 'pair': expected[0], 'actual': expected[1], 'expected': expected[2]}
    after = {str(p): sha(p) for p in pins}
    if before != after:
        raise RuntimeError('Inputs changed during run')
    result = {'status': 'accepted', 'live_source_check': live, 'theorem_audits': len(re.findall(r'^#print axioms ', model, re.M)), 'lean_controls': lean_controls, 'rust_controls': rust_controls, 'record_controls': record_controls, 'source_controls': source_controls, 'inventory_controls': inventory_controls, 'bridge_properties': 527, 'bridge_ordered_pairs': 277729, 'sha256': before, 'commands': commands, 'limits': ['Non-custom Lean model; native custom prepass excluded.', 'Sorting/permutation and target-expansion premises; value agreement requires winner-value uniqueness.', 'Generated finite inventory and mock representations; native pref filtering, aliases, parsing, conversions, and compiler semantics not proved.', 'Mixed all shorthand excluded from uniform-filter theorem; native count dominance/pref behavior is a separate source-review obligation.']}
    (out / 'PROOF-v1.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k: result[k] for k in ['status', 'live_source_check', 'theorem_audits', 'bridge_properties', 'bridge_ordered_pairs']}))

if __name__ == '__main__':
    main()
