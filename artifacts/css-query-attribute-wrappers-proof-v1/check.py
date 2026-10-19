import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

import bridge

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[1]
TOOLCHAIN = json.loads((BASE / 'TOOLCHAIN-v1.json').read_text())
LEAN = Path(TOOLCHAIN['lean'])
RUSTC = Path(TOOLCHAIN['rustc'])


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(command, path, input_text=None):
    result = subprocess.run([str(c) for c in command], input=input_text, text=True, capture_output=True)
    path.write_text(result.stdout + result.stderr)
    return result


def authenticate(manifest, replacements=None):
    replacements = replacements or {}
    for name, expected in manifest.items():
        path = replacements.get(name, ROOT / name)
        if not path.is_file() or digest(path) != expected:
            raise ValueError('identity mismatch: ' + name)


def audit_lean(path, output):
    source = path.read_text()
    names = re.findall(r'^#print axioms ([A-Za-z_][A-Za-z_0-9]*)$', source, re.M)
    if len(names) != 11 or len(set(names)) != 11:
        raise ValueError('missing or duplicate theorem audit')
    if re.search(r'\b(sorry|admit|unsafe)\b|^\s*axiom\s', source, re.M):
        raise ValueError('untrusted proof declaration')
    result = run([LEAN, path], output)
    lines = result.stdout.splitlines()
    if result.returncode or result.stderr or len(lines) != len(names):
        raise ValueError('Lean failure or unexpected diagnostics')
    audits = {}
    for name, line in zip(names, lines):
        prefix = f"'QueryDependencies.{name}' "
        if line == prefix + 'does not depend on any axioms':
            audits[name] = []
        else:
            match = re.fullmatch(re.escape(prefix) + r'depends on axioms: \[([^\]]*)\]', line)
            if not match:
                raise ValueError('unexpected axiom output')
            axioms = match[1].split(', ')
            if any(a not in {'propext', 'Quot.sound'} for a in axioms):
                raise ValueError('unapproved axioms')
            audits[name] = axioms
    return audits


def lean_controls(out):
    original = (BASE / 'Query.lean').read_text()
    mutations = {
        'skip-negation': ('| .neg c => collect deps c acc', '| .neg _ => acc'),
        'skip-parentheses': ('| .parens c => collect deps c acc', '| .parens _ => acc'),
        'skip-operations': ('| .operation _ cs => collectForest deps cs acc', '| .operation _ _ => acc'),
        'skip-tail': ('| .cons c cs => collectForest deps cs (collect deps c acc)', '| .cons c _ => collect deps c acc'),
        'erase-existing': ('| .style s => deps s ++ acc', '| .style s => deps s'),
        'invent-dependency': ('| .other _ => acc', '| .other _ => 999 :: acc'),
        'swap-leaf': ('| .style s => deps s ++ acc', '| .style s => deps (s + 1) ++ acc'),
    }
    rejected = []
    for name, (old, new) in mutations.items():
        if original.count(old) != 1:
            raise ValueError('ambiguous Lean mutation ' + name)
        path = out / ('lean-mutation-' + name + '.lean')
        path.write_text(original.replace(old, new))
        result = run([LEAN, path], path.with_suffix('.log'))
        if result.returncode == 0 or 'error' not in result.stdout:
            raise ValueError('Lean mutation accepted ' + name)
        rejected.append(name)
    guards = {
        'missing-audit': original.replace('#print axioms evaluation_preserved\n', ''),
        'extra-output': original + '\n#check Nat\n',
        'stderr-output': original + '\n#eval IO.eprintln "unexpected diagnostic"\n',
        'sorry': original.replace(':= by decide', ':= by sorry', 1),
        'axiom': original + '\naxiom forged : False\n',
        'syntax': original + '\nthis is not Lean\n',
    }
    rejected_guards = []
    for name, content in guards.items():
        path = out / ('lean-guard-' + name + '.lean')
        path.write_text(content)
        try:
            audit_lean(path, path.with_suffix('.log'))
        except ValueError as error:
            rejected_guards.append({'name': name, 'reason': str(error)})
        else:
            raise ValueError('Lean guard accepted ' + name)
    return rejected, rejected_guards


def native_run(source, out, label, fixtures):
    path = out / (label + '.rs')
    path.write_text(source)
    binary = out / label
    compile_result = run([RUSTC, '--edition=2021', '-D', 'warnings', path, '-o', binary], out / (label + '-compile.log'))
    if compile_result.returncode or compile_result.stdout or compile_result.stderr:
        raise ValueError('Rust compilation failed ' + label)
    result = run([binary], out / (label + '-run.log'), '\n'.join(f[0] for f in fixtures) + '\n')
    if result.returncode or result.stderr:
        raise ValueError('Rust runtime failed ' + label)
    actual = result.stdout.splitlines()
    if len(actual) != len(fixtures):
        raise ValueError('Rust result count mismatch')
    return sum(got != want for got, (_, want) in zip(actual, fixtures))


def native_controls(before, candidate, out, fixtures):
    p = bridge.parts(candidate)
    source = bridge.native_source(before, candidate)
    mutations = {
        'original-direct-only': (p['collector'], bridge.parts(before)['collector']),
        'skip-negation': ('Self::Not(ref cond) => cond.visit(visitor),', 'Self::Not(..) => {},'),
        'skip-parentheses': ('Self::InParens(ref cond) => cond.visit(visitor),', 'Self::InParens(..) => {},'),
        'first-operation-child-only': ('for cond in conds.iter()', 'for cond in conds.iter().take(1)'),
        'skip-node-callback': ('visitor(self);', ''),
        'erase-existing-set': ('self.visit(&mut |condition| {', 'references.clear(); self.visit(&mut |condition| {'),
    }
    records = []
    for name, (old, new) in mutations.items():
        if source.count(old) != 1:
            raise ValueError('ambiguous native mutation ' + name)
        mismatches = native_run(source.replace(old, new), out, 'native-mutation-' + name, fixtures)
        if not mismatches:
            raise ValueError('native semantic mutation accepted ' + name)
        records.append({'name': name, 'mismatches': mismatches})
    return records


def guards(manifest, before, candidate, out):
    source_rejected = []
    for name in manifest:
        path = out / ('source-control-' + str(len(source_rejected)))
        path.write_bytes((ROOT / name).read_bytes() + b'\nmutation\n')
        try:
            authenticate(manifest, {name: path})
        except ValueError:
            source_rejected.append(name)
        else:
            raise ValueError('source identity mutation accepted')
    preservation_rejected = []
    for name, old, new in [
        ('visitor-change', 'visitor(self);', 'visitor(self); visitor(self);'),
        ('evaluation-change', 'Self::Not(ref c) => !c.matches(context, custom, attribute_tracker),', 'Self::Not(ref c) => c.matches(context, custom, attribute_tracker),'),
        ('parser-change', 'Self::parse_internal(context, input, feature_type, AllowOr::Yes)', 'Self::parse_internal(context, input, feature_type, AllowOr::No)'),
        ('leaf-collector-change', 'Self::Feature(c) => c.collect_attribute_references(references),', 'Self::Feature(_) => {},'),
    ]:
        if old not in candidate:
            raise ValueError('missing preservation mutation')
        try:
            bridge.preservation(before, candidate.replace(old, new, 1))
        except ValueError:
            preservation_rejected.append(name)
        else:
            raise ValueError('preservation mutation accepted')
    return source_rejected, preservation_rejected


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    manifest = json.loads((BASE / 'SOURCE-v1.json').read_text())
    authenticate(manifest)
    if digest(LEAN) != TOOLCHAIN['lean_sha256'] or digest(RUSTC) != TOOLCHAIN['rustc_sha256']:
        raise ValueError('toolchain executable identity mismatch')
    before = (BASE / 'condition-before.rs').read_text()
    candidate = (BASE / 'condition-candidate.rs').read_text()
    preserved = bridge.preservation(before, candidate)
    audits = audit_lean(BASE / 'Query.lean', out / 'lean.log')
    lean_mutations, lean_guards = lean_controls(out)
    fixtures = bridge.fixtures()
    (out / 'fixtures.json').write_text(json.dumps(fixtures, indent=2) + '\n')
    mismatches = native_run(bridge.native_source(before, candidate), out, 'native', fixtures)
    if mismatches:
        raise ValueError('candidate native mismatch')
    native_mutations = native_controls(before, candidate, out, fixtures)
    source_guards, preservation_guards = guards(manifest, before, candidate, out)
    authenticate(manifest)
    receipt = {'result': 'PASS', 'source_manifest_sha256': digest(BASE / 'SOURCE-v1.json'),
               'native_extractions': preserved, 'theorem_axioms': audits,
               'lean_semantic_mutations_rejected': lean_mutations, 'lean_diagnostic_guards': lean_guards,
               'native_cases': len(fixtures), 'native_mismatches': mismatches,
               'fixtures_sha256': digest(out / 'fixtures.json'),
               'original_collector_counterexamples': sum(want.split('|')[0] != want.split('|')[1] for _, want in fixtures),
               'native_mutations': native_mutations, 'source_guards': source_guards,
               'preservation_guards': preservation_guards,
               'limitations': ['native payload and set adapters', 'bounded native differential test', 'leaf dependency contract assumed', 'opaque leaves held stable', 'parser/map/restyle not proved', 'GeneralEnclosed/custom-media hidden dependencies excluded']}
    (out / 'RECEIPT-v1.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(receipt, indent=2))


if __name__ == '__main__':
    main()
