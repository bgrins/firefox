import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

import bridge

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[1]
TOOLS = json.loads((BASE / 'TOOLCHAIN-v1.json').read_text())
THEOREMS = ['nonnegative', 'allocation_matches_final', 'least_share_contract',
            'least_share_unique', 'unchanged_when_nonnegative', 'contribution_bounds',
            'representable_intermediates', 'spacing_lower_bound', 'finite_contribution_sum',
            'accumulation_representable', 'old_negative_counterexample',
            'remainders_not_preserved', 'percentage_path_excluded']


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(command, log, stdin=None):
    p = subprocess.run([str(x) for x in command], input=stdin, text=True, capture_output=True)
    log.write_text(p.stdout + p.stderr)
    return p


def authenticate(manifest, replacements=None):
    replacements = replacements or {}
    for name, expected in manifest.items():
        path = replacements.get(name, ROOT / name)
        if not path.is_file() or digest(path) != expected:
            raise ValueError('identity mismatch: ' + name)


def audit_lean(path, log):
    source = path.read_text()
    names = re.findall(r'^#print axioms (\w+)$', source, re.M)
    if names != THEOREMS:
        raise ValueError('theorem audit inventory changed')
    if re.search(r'\b(sorry|admit|unsafe)\b|^\s*axiom\s', source, re.M):
        raise ValueError('untrusted proof declaration')
    p = run([TOOLS['lean'], path], log)
    if p.returncode or p.stderr or len(p.stdout.splitlines()) != len(names):
        raise ValueError('Lean error or unexpected diagnostics')
    audits = {}
    for name, line in zip(names, p.stdout.splitlines()):
        prefix = f"'SpanSpacing.{name}' "
        if line == prefix + 'does not depend on any axioms':
            audits[name] = []
            continue
        match = re.fullmatch(re.escape(prefix) + r'depends on axioms: \[([^\]]+)\]', line)
        if not match:
            raise ValueError('unexpected axiom report')
        axioms = match[1].split(', ')
        if not set(axioms) <= {'propext', 'Quot.sound', 'Classical.choice'}:
            raise ValueError('unapproved axiom')
        audits[name] = axioms
    return audits


def mutate(text, old, new):
    if text.count(old) != 1:
        raise ValueError('ambiguous mutation: ' + old)
    return text.replace(old, new, 1)


def lean_controls(out):
    original = (BASE / 'SpanSpacing.lean').read_text()
    mutations = {
        'remove-clamp': ('max 0 (raw extent spacing span)', 'raw extent spacing span'),
        'clamp-to-one': ('max 0 (raw extent spacing span)', 'max 1 (raw extent spacing span)'),
        'final-condition-reversed': ('if value < 0 then 0 else value', 'if value > 0 then 0 else value'),
        'omit-spacing-numerator': ('(extent + spacing).tdiv span - spacing', 'extent.tdiv span - spacing'),
        'wrong-divisor': ('(extent + spacing).tdiv span - spacing', '(extent + spacing).tdiv (span + 1) - spacing'),
        'drop-accumulated-share': ('accumulate (base + x) xs\n', 'accumulate base xs\n'),
        'omit-accumulation-bound': ('0 ≤ x ∧ base + x ≤ 2147483647 ∧ safeTrace', '0 ≤ x ∧ True ∧ safeTrace'),
    }
    rejected = []
    for name, (old, new) in mutations.items():
        path = out / ('lean-mutation-' + name + '.lean')
        path.write_text(mutate(original, old, new))
        p = run([TOOLS['lean'], path], path.with_suffix('.log'))
        if not p.returncode or 'error:' not in p.stdout:
            raise ValueError('semantic Lean mutation accepted: ' + name)
        rejected.append(name)
    diagnostics = {
        'missing-audit': original.replace('#print axioms nonnegative\n', ''),
        'extra-output': original + '\n#check Nat\n',
        'stderr-output': original + '\n#eval IO.eprintln "unexpected diagnostic"\n',
        'sorry': original.replace(':= by\n  decide', ':= by\n  sorry', 1),
        'axiom': original + '\naxiom fabricated : False\n',
        'syntax': original + '\nthis is not Lean\n',
    }
    guards = []
    for name, content in diagnostics.items():
        path = out / ('lean-guard-' + name + '.lean')
        path.write_text(content)
        try:
            audit_lean(path, path.with_suffix('.log'))
        except ValueError:
            guards.append(name)
        else:
            raise ValueError('Lean diagnostic guard accepted: ' + name)
    return rejected, guards


def compile_source(source, out, name):
    path, binary = out / (name + '.cpp'), out / name
    path.write_text(source)
    p = run([TOOLS['clang'], '-std=c++20', '-O2', '-Wall', '-Wextra', '-Werror',
             '-fsanitize=undefined', '-fno-sanitize-recover=all', path, '-o', binary],
            out / (name + '-compile.log'))
    if p.returncode or p.stdout or p.stderr:
        raise ValueError('compile error or diagnostic: ' + name)
    return binary


def native_run(source, fixtures, out, name):
    binary = compile_source(source, out, name)
    p = run([binary], out / (name + '-run.log'),
            ''.join(' '.join(map(str, case)) + '\n' for case in fixtures))
    if p.returncode or p.stderr:
        raise ValueError('native error or diagnostic: ' + name)
    actual = [list(map(int, line.split())) for line in p.stdout.splitlines()]
    if len(actual) != len(fixtures):
        raise ValueError('native result count changed')
    return sum(value != bridge.expected(case) for value, case in zip(actual, fixtures)), actual


def native_controls(source, candidate, fixtures, out):
    snippets = bridge.snippets(candidate)
    branch = snippets['candidate.inc']
    changes = {
        'remove-clamp': (bridge.BINDING['candidate_assignment'], bridge.BINDING['original_assignment']),
        'clamp-to-one': ('std::max(0, ((cellISize + spacing) / colSpan) - spacing)',
                         'std::max(1, ((cellISize + spacing) / colSpan) - spacing)'),
        'omit-numerator-spacing': ('std::max(0, ((cellISize + spacing) / colSpan) - spacing)',
                                  'std::max(0, (cellISize / colSpan) - spacing)'),
        'wrong-divisor': ('std::max(0, ((cellISize + spacing) / colSpan) - spacing)',
                          'std::max(0, ((cellISize + spacing) / std::max(1, colSpan - 1)) - spacing)'),
        'skip-two-column-span': (branch, branch.replace('colSpan > 1', 'colSpan > 2')),
        'subtract-accumulation': ('result += cellISize;', 'result -= cellISize;'),
        'remove-final-clamp': ('if (colISize < 0) {', 'if (false) {'),
    }
    rejected = []
    control_cases = [(*case[:3], 0) for case in fixtures]
    for name, (old, new) in changes.items():
        mismatches, _ = native_run(mutate(source, old, new), control_cases, out, 'native-mutation-' + name)
        if not mismatches:
            raise ValueError('native mutation accepted: ' + name)
        rejected.append({'name': name, 'mismatches': mismatches})
    return rejected


def source_controls(manifest, candidate, out):
    identities = []
    path = out / 'identity-guard-input'
    for name in manifest:
        path.write_bytes((ROOT / name).read_bytes() + b'\nchanged\n')
        try:
            authenticate(manifest, {name: path})
        except ValueError:
            identities.append(name)
        else:
            raise ValueError('source identity guard accepted')
    changes = {
        'percentage-policy': ('result -= spacing * (colSpan - 1);', 'result += spacing * (colSpan - 1);'),
        'intrinsic-mode': ('aRenderingContext, cellFrame, IntrinsicISizeType::MinISize',
                           'aRenderingContext, cellFrame, IntrinsicISizeType::PrefISize'),
        'final-clamp': ('if (colISize < 0) {', 'if (colISize > 0) {'),
        'accumulator': ('result += cellISize;', 'result -= cellISize;'),
    }
    preservation = []
    for name, (old, new) in changes.items():
        if old not in candidate:
            raise ValueError('missing preservation control')
        changed = candidate.replace(old, new, 1)
        try:
            bridge.validate(changed)
        except ValueError:
            preservation.append(name)
        else:
            raise ValueError('full-file preservation guard accepted')
    return identities, preservation


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    out = parser.parse_args().out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    manifest = json.loads((BASE / 'SOURCE-v1.json').read_text())
    authenticate(manifest)
    for tool in ['lean', 'clang']:
        if digest(Path(TOOLS[tool])) != TOOLS[tool + '_sha256']:
            raise ValueError('toolchain binary changed: ' + tool)
    candidate = (ROOT / bridge.BINDING['native_path']).read_text()
    bridge.validate(candidate)
    snippets = bridge.snippets(candidate)
    for name, value in snippets.items():
        if (BASE / name).read_text() != value + '\n':
            raise ValueError('extracted snippet drift: ' + name)
    audits = audit_lean(BASE / 'SpanSpacing.lean', out / 'lean.log')
    lean_mutations, lean_guards = lean_controls(out)
    fixtures = bridge.fixtures()
    (out / 'fixtures.json').write_text(json.dumps(fixtures, separators=(',', ':')) + '\n')
    source = bridge.source(candidate)
    mismatches, actual = native_run(source, fixtures, out, 'native')
    if mismatches:
        raise ValueError('candidate violates independent finite oracle')
    native_mutations = native_controls(source, candidate, fixtures, out)
    for case, values in zip(fixtures, actual):
        if not 0 <= values[1] <= case[0] or values[1] != values[2] or values[3] < case[3]:
            raise ValueError('native contract mismatch')
    unsafe = run([out / 'native'], out / 'ub-overflow-control.log', '2147483647 1 2 0\n')
    if not unsafe.returncode or 'signed integer overflow' not in unsafe.stderr:
        raise ValueError('overflow premise control did not trip UBSan')
    native_guards = []
    for name, altered in {
        'compiler-warning': source + '\n#warning deliberate diagnostic\n',
        'compiler-syntax': source + '\nthis is not C++;\n',
        'runtime-stderr': source.replace('int main() {', 'int main() { std::cerr << "unexpected diagnostic";'),
    }.items():
        try:
            native_run(altered, fixtures[:1], out, 'native-guard-' + name)
        except ValueError:
            native_guards.append(name)
        else:
            raise ValueError('native diagnostic guard accepted')
    identities, preservation = source_controls(manifest, candidate, out)
    authenticate(manifest)
    receipt = {'result': 'PASS', 'manifest_sha256': digest(BASE / 'SOURCE-v1.json'),
        'theorem_axioms': audits, 'lean_mutations': lean_mutations, 'lean_diagnostic_guards': lean_guards,
        'native_cases': len(fixtures), 'old_negative_counterexamples': sum(row[0] < 0 for row in actual),
        'native_mutations': native_mutations, 'native_diagnostic_guards': native_guards,
        'overflow_premise_control': 'UBSan rejected unrepresentable addition',
        'identity_guards': identities, 'preservation_guards': preservation,
        'extractions': {name: bridge.sha(value) for name, value in snippets.items()},
        'fixture_sha256': digest(out / 'fixtures.json'),
        'limits': ['supplied nonnegative intrinsic extent and spacing; positive span',
                   'representable addition, division operands, subtraction and accumulation',
                   'spacing lower bound excludes percentage subtraction and other negative contributions',
                   'no exact remainder preservation, overflow fix, intrinsic measurement or full table proof']}
    (out / 'RECEIPT-v1.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(receipt, indent=2))


if __name__ == '__main__':
    main()
