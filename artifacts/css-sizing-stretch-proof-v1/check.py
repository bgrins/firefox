import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys

from bridge import generate
from controls import CPP_MUTATIONS, LEAN_MUTATIONS
from diagnostics import negative
from prepare import extract

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[1]
LEAN = ROOT / 'artifacts/stylo-bloom-tools/lean-4.35.0-rc4-darwin_aarch64/bin/lean'
CLANG = Path('/usr/bin/clang++')
DECIDE = 'Tactic `decide` proved that the proposition'
ERRORS = {
    'omit-auto': [('selection_refinement', DECIDE)] * 2 + [('fixed_witness', DECIDE)],
    'omit-end-margin': [('selection_refinement', DECIDE)] * 2 + [('auto_preserved', 'unsolved goals'), ('other_sizes_preserved', 'unsolved goals')],
    'omit-clamp-fill': [('selection_refinement', DECIDE)] * 23 + [('auto_preserved', 'unsolved goals'), ('other_sizes_preserved', 'unsolved goals'), ('clamping_has_fill', 'unsolved goals')],
}
CPP_ERRORS = {
    'omit-auto': '1 alignment=0 mask=5',
    'auto-to-maxcontent': '0 alignment=0 mask=5',
    'ignore-margins': '0 alignment=0 mask=13',
    'omit-clamp-fill': '0 alignment=0 mask=45',
    'retain-unconstrained-clamp': '0 alignment=0 mask=33',
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sources(read, live=False):
    rows = json.loads((BASE / 'SOURCE-v1.json').read_text())
    for r in rows:
        text = read(r['snapshot'])
        if hashlib.sha256(text.encode()).hexdigest() != r['sha256']:
            raise RuntimeError('Source drift ' + r['snapshot'])
        if live and r['snapshot'] != 'native-before.cpp':
            if extract((ROOT / r['source']).read_text(), r['marker']) != text:
                raise RuntimeError('Live source drift ' + r['source'])
    return rows


def main():
    if sys.flags.optimize or len(sys.argv) not in [2, 3] or (len(sys.argv) == 3 and sys.argv[2] != '--live'):
        raise RuntimeError('Usage: check.py NEW_OUTPUT_DIRECTORY [--live]')
    out = Path(sys.argv[1]).resolve()
    out.mkdir()
    live = len(sys.argv) == 3
    read = lambda n: (BASE / n).read_text()
    rows = sources(read, live)
    names = read('tooling-paths-v1.txt').splitlines()
    if len(names) != len(set(names)) or any(Path(n).name != n for n in names):
        raise RuntimeError('Bad source inventory')
    toolchain = json.loads(read('TOOLCHAIN-v1.json'))
    pins = [BASE / n for n in names] + [Path(n) for n in toolchain]
    if live:
        pins += [ROOT / r['source'] for r in rows if r['snapshot'] != 'native-before.cpp']
    before = {str(p): sha(p) for p in pins}
    for name, digest in toolchain.items():
        if sha(Path(name)) != digest:
            raise RuntimeError('Toolchain drift')
    controls = []
    for r in rows:
        try:
            sources(lambda n: read(n) + '\n' if n == r['snapshot'] else read(n))
        except RuntimeError:
            controls.append(r['snapshot'])
        else:
            raise RuntimeError('Accepted source corruption')
    commands = []

    def run(command, directory, label, env=None):
        p = subprocess.run(command, cwd=directory, env=env, capture_output=True, text=True)
        (directory / (label + '.stdout')).write_text(p.stdout)
        (directory / (label + '.stderr')).write_text(p.stderr)
        commands.append({'command': command, 'cwd': str(directory), 'exit': p.returncode})
        return p

    model = read('Stretch.lean')
    if re.search(r'\b(sorry|admit|axiom|unsafe|native_decide)\b', model.replace('#print axioms', '')):
        raise RuntimeError('Unchecked construct')
    lean_controls = {}
    samples = {}
    for name, mutation in [('positive', None), *LEAN_MUTATIONS.items()]:
        directory = out / name
        directory.mkdir()
        if mutation and model.split('def oldNative')[0].count(mutation[0]) != 1:
            raise RuntimeError('Mutation cardinality')
        text = model if mutation is None else model.replace(*mutation, 1)
        path = directory / 'Stretch.lean'
        path.write_text(text)
        env = os.environ.copy()
        env['LEAN_PATH'] = str(directory)
        env.pop('LEAN_SRC_PATH', None)
        command = [str(LEAN), '-DwarningAsError=true', '-DmaxRecDepth=4096', '-DmaxHeartbeats=4000000']
        if mutation is None:
            command += ['-o', str(directory / 'Stretch.olean')]
        p = run(command + [str(path)], directory, 'lean', env)
        if mutation is None:
            if p.returncode != 0 or p.stderr or p.stdout != read('expected-axioms.txt'):
                raise RuntimeError('Positive proof/audit failed')
        else:
            lean_controls[name] = negative(text, path, p.returncode, p.stdout, p.stderr, ERRORS[name])
            samples[name] = (text, path, p)
    text, path, p = samples['omit-auto']
    header = re.search(r'^.+:\d+:\d+: error:.*$', p.stdout, re.M).group(0)
    fakes = {
        'exit-zero': (0, p.stdout, ''), 'exit-two': (2, p.stdout, ''),
        'stderr': (1, p.stdout, 'noise'), 'empty': (1, '', ''),
        'foreign-file': (1, p.stdout.replace(str(path), str(path) + '-other', 1), ''),
        'outside-proof': (1, re.sub(r':\d+:\d+: error:', ':1:1: error:', p.stdout, count=1), ''),
        'extra-error': (1, p.stdout + '\n' + header + '\n', ''),
        'unlocated': (1, p.stdout + '\nerror: noise\n', ''),
        'parse-error': (1, p.stdout.replace(DECIDE, 'unexpected token', 1), ''),
    }
    diagnostic_controls = []
    for name, (code, stdout, stderr) in fakes.items():
        try:
            negative(text, path, code, stdout, stderr, ERRORS['omit-auto'])
        except RuntimeError:
            diagnostic_controls.append(name)
        else:
            raise RuntimeError('Accepted forged diagnostic')
    cpp_controls = {}
    native = read('native-candidate.cpp')
    for name, mutation in [('positive', None), *CPP_MUTATIONS.items()]:
        directory = out / ('cpp-' + name)
        directory.mkdir()
        if mutation and native.count(mutation[0]) != 1:
            raise RuntimeError('C++ mutation cardinality ' + name)
        text = native if mutation is None else native.replace(*mutation)
        path = directory / 'bridge.cpp'
        path.write_text(generate(text))
        exe = directory / 'bridge'
        p = run([str(CLANG), '-std=c++17', str(path), '-o', str(exe)], directory, 'compile')
        if p.returncode or p.stdout or p.stderr:
            raise RuntimeError('C++ compile failed ' + name)
        p = run([str(exe)], directory, 'run')
        expected = '4800 cases\n' if mutation is None else 'mismatch size=' + CPP_ERRORS[name] + ' measure=0\n'
        if p.returncode != (0 if mutation is None else 1) or p.stderr or p.stdout != expected:
            raise RuntimeError('Wrong C++ terminal ' + name)
        if mutation:
            cpp_controls[name] = {'exit': p.returncode, 'stdout': p.stdout}
    after = {str(p): sha(p) for p in pins}
    if after != before:
        raise RuntimeError('Input drift during execution')
    result = {'status': 'accepted', 'live_source_check': live, 'sha256': before,
              'commands': commands, 'theorem_audits': 12, 'finite_contexts': 960,
              'cpp_cases': 4800, 'lean_controls': lean_controls,
              'cpp_controls': cpp_controls, 'source_controls': controls,
              'diagnostic_controls': diagnostic_controls,
              'limits': ['Initial inline self-stretch selection only, not final used geometry.',
                         'Clamping state is a preserved native policy, not a proof of Grid automatic minimum semantics.',
                         'Mock methods and finite adapters; style resolution, caller dispatch, arithmetic range, later sizing and compiler semantics remain premises.',
                         'Caller snapshots are manually reviewed provenance, not executed by the C++ bridge.']}
    (out / 'PROOF-v1.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k: result[k] for k in ['status', 'theorem_audits', 'finite_contexts', 'cpp_cases']}))

if __name__ == '__main__':
    main()
