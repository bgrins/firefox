import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys

from controls import MUTATIONS

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[1]
LEAN = ROOT / 'artifacts/stylo-bloom-tools/lean-4.35.0-rc4-darwin_aarch64/bin/lean'
AUDITS = [
    'dispatch_refinement', 'rem_infinite_identity', 'mod_same_sign_identity',
    'mod_opposite_sign_nan', 'generated_negative_zero_preserved',
    'infinite_dividend_rejected', 'nan_infectious_left', 'nan_infectious_right',
    'zero_divisor_rejected', 'finite_backend_unchanged', 'old_mod_fails_nonzero',
    'old_rem_fails_nonzero',
]
EXPECTED = ''.join(f"'ModRemInfinity.{name}' depends on axioms: [propext]\n" for name in AUDITS)
FAILURES = {
    'RemoveIdentity': ['dispatch_refinement'] * 8 + ['rem_infinite_identity', 'mod_same_sign_identity'],
    'AcceptInfiniteDividend': ['dispatch_refinement'] * 2,
    'ApplyModExceptionToRem': ['dispatch_refinement'] * 4 + ['rem_infinite_identity'],
    'EraseZeroSign': ['dispatch_refinement'] * 2 + ['rem_infinite_identity', 'mod_same_sign_identity'],
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def positive(code, stdout, stderr):
    if code != 0 or stdout != EXPECTED or stderr:
        raise RuntimeError('Positive compilation or audit mismatch')


def negative(source, path, code, stdout, stderr, expected):
    if code != 1 or stderr:
        raise RuntimeError('Negative terminal mismatch')
    lines = source.splitlines()
    declarations = [(i, s) for i, s in enumerate(lines, 1)
                    if re.match(r'^(theorem |def |#print|end )', s)]
    spans = {}
    for index, (start, declaration) in enumerate(declarations[:-1]):
        if declaration.startswith('theorem '):
            end = declarations[index + 1][0]
            body = [i for i in range(start, end) if ':= by' in lines[i - 1]]
            if len(body) != 1:
                raise RuntimeError('Ambiguous proof body')
            spans[declaration.split()[1]] = (body[0], end)
    errors = re.findall(r'^(.+):(\d+):\d+: error(?:\([^\n)]*\))?: (.*)$', stdout, re.M)
    if len(re.findall(r'\berror(?:\([^\n)]*\))?:', stdout)) != len(errors):
        raise RuntimeError('Unlocated error')
    found = []
    for filename, line, message in errors:
        owners = [name for name, (start, end) in spans.items() if start <= int(line) < end]
        if filename != str(path) or len(owners) != 1 or message != 'unsolved goals':
            raise RuntimeError('Unexpected diagnostic')
        found.append(owners[0])
    if found != expected:
        raise RuntimeError('Proof failure inventory mismatch: ' + repr(found))
    return found


def source_binding():
    source = ROOT / 'servo/components/style/values/generics/calc.rs'
    text = source.read_text()
    marker = 'impl ModRemOp {'
    if text.count(marker) != 1:
        raise RuntimeError('Ambiguous native helper')
    start = text.index(marker)
    fragment = text[start:text.index('\n}\n', start) + 3]
    manifest = json.loads((BASE / 'SOURCE-v1.json').read_text())
    for name, field in [('old-dispatch.rs', 'old_fragment_sha256'),
                        ('proposed-dispatch.rs', 'proposed_fragment_sha256')]:
        if sha(BASE / name) != manifest[field]:
            raise RuntimeError('Source snapshot changed')
    if fragment == (BASE / 'old-dispatch.rs').read_text():
        candidate = False
    elif fragment == (BASE / 'proposed-dispatch.rs').read_text():
        candidate = True
    else:
        raise RuntimeError('Unreviewed native helper')
    spec = json.loads((BASE / 'SPEC-v1.json').read_text())
    for name, digest in spec['excerpts'].items():
        if sha(BASE / name) != digest:
            raise RuntimeError('Spec excerpt changed')
    return {'source_path': str(source), 'live_source_sha256': sha(source),
            'live_candidate_verified': candidate, 'bridge': 'manual',
            'native_numerical_accuracy_verified': False}


def main():
    if sys.flags.optimize or len(sys.argv) != 2:
        raise RuntimeError('Usage: python3 check.py NEW_OUTPUT_DIRECTORY')
    out = Path(sys.argv[1]).resolve()
    out.mkdir()
    model = (BASE / 'Dispatch.lean').read_text()
    if re.search(r'\b(sorry|admit|axiom|unsafe)\b', model.replace('#print axioms', '')):
        raise RuntimeError('Unchecked construct')
    files = [BASE / name for name in [
        'Dispatch.lean', 'check.py', 'controls.py', 'README.md', 'REVIEW.md',
        'SOURCE-v1.json', 'SPEC-v1.json', 'old-dispatch.rs', 'proposed-dispatch.rs',
        'values4-round-infinities.txt', 'values4-calc-ieee.txt',
    ]] + [LEAN, ROOT / 'servo/components/style/values/generics/calc.rs']
    before = {str(path): sha(path) for path in files}
    binding = source_binding()
    commands = []

    def compile_case(name, text, good=False):
        directory = out / name
        directory.mkdir()
        path = directory / 'Dispatch.lean'
        path.write_text(text)
        env = os.environ.copy()
        env['LEAN_PATH'] = str(directory)
        env.pop('LEAN_SRC_PATH', None)
        command = [str(LEAN), '-DwarningAsError=true', '-Dlinter.unusedSimpArgs=false']
        if good:
            command += ['-o', str(directory / 'Dispatch.olean')]
        command.append(str(path))
        result = subprocess.run(command, cwd=directory, env=env, capture_output=True, text=True)
        (directory / 'stdout').write_text(result.stdout)
        (directory / 'stderr').write_text(result.stderr)
        commands.append({'command': command, 'cwd': str(directory), 'exit': result.returncode,
                         'LEAN_PATH': str(directory), 'LEAN_SRC_PATH': None})
        return path, result

    _, good = compile_case('positive', model, True)
    positive(good.returncode, good.stdout, good.stderr)
    controls = {}
    sample = None
    for name, (old, new) in MUTATIONS.items():
        if model.count(old) != 1:
            raise RuntimeError('Mutation cardinality mismatch')
        text = model.replace(old, new)
        path, result = compile_case(name, text)
        controls[name] = negative(text, path, result.returncode, result.stdout,
                                  result.stderr, FAILURES[name])
        if name == 'RemoveIdentity':
            sample = text, path, result
    text, path, result = sample
    header = re.search(r'^(.+):(\d+):\d+: error: (.*)$', result.stdout, re.M).group(0)
    corruptions = {
        'exit-zero': (0, result.stdout, ''),
        'exit-two': (2, result.stdout, ''),
        'stderr': (1, result.stdout, 'noise'),
        'empty': (1, '', ''),
        'foreign-file': (1, result.stdout.replace(str(path), str(path) + '-other', 1), ''),
        'outside-body': (1, re.sub(r':\d+:\d+: error:', ':1:1: error:', result.stdout, count=1), ''),
        'extra-error': (1, result.stdout + '\n' + header + '\n', ''),
        'unlocated': (1, result.stdout + '\nerror: tool failure\n', ''),
        'unknown-name': (1, result.stdout.replace('error: unsolved goals', 'error: Unknown identifier bogus', 1), ''),
        'parse-error': (1, result.stdout.replace('error: unsolved goals', 'error: unexpected token', 1), ''),
    }
    rejected = []
    for name, args in corruptions.items():
        try:
            negative(text, path, *args, FAILURES['RemoveIdentity'])
        except RuntimeError:
            rejected.append(name)
        else:
            raise RuntimeError('Accepted corrupted negative record')
    for name, args in {
        'positive-exit': (1, good.stdout, ''),
        'positive-stderr': (0, good.stdout, 'noise'),
        'positive-axiom': (0, good.stdout.replace('[propext]', '[sorryAx]', 1), ''),
    }.items():
        try:
            positive(*args)
        except RuntimeError:
            rejected.append(name)
        else:
            raise RuntimeError('Accepted corrupted positive record')
    if before != {str(path): sha(path) for path in files}:
        raise RuntimeError('Inputs changed during run')
    (out / 'commands.json').write_text(json.dumps(commands, indent=2) + '\n')
    report = {'status': 'pass', 'scope': 'conditional dispatch refinement',
              'audits': AUDITS, 'controls': controls, 'record_guards': rejected,
              'source_binding': binding, 'inputs': before,
              'outputs': {str(path.relative_to(out)): sha(path) for path in out.rglob('*') if path.is_file()}}
    (out / 'report.json').write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
    print(json.dumps({'status': 'pass', 'audits': len(AUDITS), 'mutations': len(controls),
                      'record_guards': len(rejected), 'live_candidate_verified': binding['live_candidate_verified']}))


if __name__ == '__main__':
    main()
