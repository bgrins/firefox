import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from controls import MUTATIONS

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[1]
LEAN = ROOT / 'artifacts/stylo-bloom-tools/lean-4.35.0-rc4-darwin_aarch64/bin/lean'
NAMES = ['complementary_ratio', 'step_refinement', 'step_nonnegative', 'fold_refinement',
         'zero_prefix_retains_zero', 'positive_step_unchanged', 'raw_step_unchanged',
         'raw_fold_unchanged', 'channel_compatible', 'channel_fold', 'forward_witness',
         'reverse_witness', 'numeric_final', 'repeated_zero_prefix', 'alpha_carry',
         'missing_prefix', 'raw_cancellation']
EXPECTED = ''.join("'ZeroPrefix." + n + "' depends on axioms: [propext, Classical.choice, Quot.sound]\n" for n in NAMES)
REWRITE = 'Tactic `rewrite` failed: Did not find an occurrence of the pattern'
DECIDE = 'Tactic `decide` failed to reduce'
UNSOLVED = 'unsolved goals'
ZERO_ERRORS = [('step_refinement', REWRITE), ('zero_prefix_retains_zero', UNSOLVED)] + [(n, DECIDE) for n in ['forward_witness', 'reverse_witness', 'repeated_zero_prefix', 'alpha_carry', 'missing_prefix']]
ERRORS = {
    'SkipNormalizedZero': ZERO_ERRORS,
    'ZeroInterpolationWeights': ZERO_ERRORS,
    'GivePrefixUnitWeight': [(n, UNSOLVED) for n in ['step_refinement', 'zero_prefix_retains_zero', 'raw_step_unchanged']] + [(n, DECIDE) for n in ['numeric_final', 'repeated_zero_prefix']],
    'NormalizeRawCancellation': [('step_refinement', REWRITE), ('step_refinement', REWRITE), ('raw_step_unchanged', UNSOLVED), ('raw_cancellation', DECIDE)],
}

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def negative(source, path, code, stdout, stderr, expected):
    if code != 1 or stderr:
        raise RuntimeError('Negative exit or stderr mismatch')
    lines = source.splitlines()
    declarations = [(i, line) for i, line in enumerate(lines, 1) if re.match(r'^(theorem |def |#print|end )', line)]
    spans = {}
    for (start, line), (end, _) in zip(declarations, declarations[1:]):
        if line.startswith('theorem '):
            bodies = [i for i in range(start, end) if ':= by' in lines[i-1]]
            if bodies:
                spans[line.split()[1]] = (bodies[0], end)
    headers = re.findall(r'^(.+):(\d+):\d+: error(?:\([^\n)]*\))?: (.*)$', stdout, re.M)
    if len(headers) != len(re.findall(r'\berror(?:\([^\n)]*\))?:', stdout)):
        raise RuntimeError('Unlocated diagnostic')
    found = []
    for filename, line, message in headers:
        owners = [name for name, (start, end) in spans.items() if start <= int(line) < end]
        if filename != str(path) or len(owners) != 1:
            raise RuntimeError('Diagnostic outside proof')
        found.append((owners[0], message))
    if found != expected:
        raise RuntimeError('Unexpected proof failures: ' + repr(found))
    return found

def main():
    if len(sys.argv) != 2 or sys.flags.optimize:
        raise RuntimeError('Usage: python3 check.py NEW_OUTPUT_DIRECTORY')
    out = Path(sys.argv[1]).resolve()
    out.mkdir()
    source = (BASE / 'Fold.lean').read_text()
    if re.search(r'\b(sorry|admit|axiom|unsafe|native_decide)\b', source.replace('#print axioms', '')):
        raise RuntimeError('Unchecked construct')
    pins = [BASE / name for name in ['Fold.lean', 'controls.py', 'check.py', 'README.md']] + [LEAN]
    before = {str(p): sha(p) for p in pins}
    runs = []
    def compile_case(name, text):
        directory = out / name
        directory.mkdir()
        path = directory / 'Fold.lean'
        path.write_text(text)
        env = os.environ.copy()
        env['LEAN_PATH'] = str(directory)
        env.pop('LEAN_SRC_PATH', None)
        command = [str(LEAN), '-DwarningAsError=true', '-Dlinter.unusedSimpArgs=false', '-o', str(directory / 'Fold.olean'), str(path)]
        result = subprocess.run(command, cwd=directory, env=env, capture_output=True, text=True)
        (directory / 'stdout').write_text(result.stdout)
        (directory / 'stderr').write_text(result.stderr)
        runs.append({'name': name, 'command': command, 'cwd': str(directory), 'exit': result.returncode})
        return path, result
    _, good = compile_case('positive', source)
    if good.returncode != 0 or good.stdout != EXPECTED or good.stderr:
        raise RuntimeError('Positive theorem or axiom inventory mismatch')
    controls = {}
    samples = []
    for name, replacements in MUTATIONS.items():
        text = source
        for old, new in replacements:
            required = 2 if name == 'GivePrefixUnitWeight' else 1
            if text.count(old) != required:
                raise RuntimeError('Mutation cardinality mismatch')
            text = text.replace(old, new, 1)
        path, result = compile_case(name, text)
        controls[name] = negative(text, path, result.returncode, result.stdout, result.stderr, ERRORS[name])
        samples.append((text, path, result, ERRORS[name]))
    text, path, result, expected = samples[0]
    bad = {
        'exit-zero': (0, result.stdout, ''), 'exit-two': (2, result.stdout, ''),
        'stderr': (1, result.stdout, 'noise'), 'empty': (1, '', ''),
        'foreign-file': (1, result.stdout.replace(str(path), str(path)+'-foreign'), ''),
        'outside-body': (1, re.sub(r':\d+:\d+: error:', ':1:1: error:', result.stdout, count=1), ''),
        'unlocated': (1, result.stdout+'\nerror: tool failure\n', ''),
        'parse-error': (1, result.stdout.replace(REWRITE, 'unexpected token', 1), ''),
        'unknown-identifier': (1, result.stdout.replace(REWRITE, 'Unknown identifier test', 1), ''),
    }
    rejected = []
    for name, args in bad.items():
        try:
            negative(text, path, *args, expected)
        except RuntimeError:
            rejected.append(name)
        else:
            raise RuntimeError('Malformed evidence accepted: '+name)
    if before != {str(p): sha(p) for p in pins}:
        raise RuntimeError('Inputs changed during replay')
    report = {'status': 'checked-model-only', 'native_source_bound': False,
              'audits': NAMES, 'controls': controls, 'record_controls': rejected,
              'pins': before, 'runs': runs,
              'limits': 'Prepared rational fold contract; no source extraction, IEEE proof, or browser verification.'}
    (out/'report.json').write_text(json.dumps(report, indent=2, sort_keys=True)+'\n')
    print(json.dumps({'status': report['status'], 'audits': len(NAMES), 'semantic_controls': len(controls), 'record_controls': len(rejected)}))

if __name__ == '__main__':
    main()
