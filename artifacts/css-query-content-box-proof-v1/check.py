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


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(command, output, input_text=None):
    result = subprocess.run([str(c) for c in command], input=input_text, capture_output=True, text=True)
    output.write_text(result.stdout + result.stderr)
    return result


def authenticate(manifest, replacements=None):
    replacements = replacements or {}
    for name, expected in manifest.items():
        path = replacements.get(name, ROOT / name)
        if not path.is_file() or digest(path) != expected:
            raise ValueError('identity mismatch: ' + name)


def audit_lean(path, log):
    source = path.read_text()
    names = re.findall(r'^#print axioms ([A-Za-z_][A-Za-z_0-9]*)$', source, re.M)
    if len(names) != 11 or len(set(names)) != 11:
        raise ValueError('missing or duplicate theorem audit')
    if re.search(r'\b(sorry|admit|unsafe)\b|^\s*axiom\s', source, re.M):
        raise ValueError('untrusted proof declaration')
    result = run([TOOLCHAIN['lean'], path], log)
    lines = result.stdout.splitlines()
    if result.returncode or result.stderr or len(lines) != len(names):
        raise ValueError('Lean failure or unexpected diagnostics')
    audits = {}
    for name, line in zip(names, lines):
        prefix = f"'ContentSizeCache.{name}' "
        if line == prefix + 'does not depend on any axioms':
            audits[name] = []
        elif line == prefix + 'depends on axioms: [propext]':
            audits[name] = ['propext']
        else:
            raise ValueError('unapproved axiom output')
    return audits


def lean_controls(out):
    original = (BASE / 'ContentSize.lean').read_text()
    changes = {
        'ignore-size': ('| .size => before = after', '| .size => True'),
        'size-width-only': ('| .size => before = after', '| .size => before.width = after.width'),
        'inline-physical-width': ('inlineSize beforeVertical before = inlineSize afterVertical after', 'before.width = after.width'),
        'expose-untracked-width': ('| .inline => !vertical', '| .inline => true'),
        'expose-untracked-height': ('| .inline => vertical', '| .inline => true'),
        'erase-projected-sizes': ('if n < 0 then none else some n', 'if n < 0 then none else none'),
    }
    rejected = []
    for name, (old, new) in changes.items():
        if original.count(old) != 1:
            raise ValueError('ambiguous mutation ' + name)
        path = out / ('lean-mutation-' + name + '.lean')
        path.write_text(original.replace(old, new))
        result = run([TOOLCHAIN['lean'], path], path.with_suffix('.log'))
        if result.returncode == 0 or 'error' not in result.stdout:
            raise ValueError('Lean mutation accepted ' + name)
        rejected.append(name)
    controls = {
        'missing-audit': original.replace('#print axioms key_preserves_observable\n', ''),
        'extra-output': original + '\n#check Nat\n',
        'stderr-output': original + '\n#eval IO.eprintln "unexpected diagnostic"\n',
        'sorry': original.replace(':= by decide', ':= by sorry', 1),
        'axiom': original + '\naxiom forged : False\n',
        'syntax': original + '\nthis is not Lean\n',
    }
    guards = []
    for name, content in controls.items():
        path = out / ('lean-guard-' + name + '.lean')
        path.write_text(content)
        try:
            audit_lean(path, path.with_suffix('.log'))
        except ValueError as error:
            guards.append({'name': name, 'reason': str(error)})
        else:
            raise ValueError('diagnostic guard accepted')
    return rejected, guards


def compiled_run(source, fixtures, out, name, rust=False):
    path = out / (name + ('.rs' if rust else '.cpp'))
    path.write_text(source)
    binary = out / name
    command = ([TOOLCHAIN['rustc'], '--edition=2021', '-D', 'warnings'] if rust else
               [TOOLCHAIN['clang'], '-std=c++20', '-Wall', '-Wextra', '-Werror', '-fsanitize=undefined', '-fno-sanitize-recover=all'])
    result = run(command + [path, '-o', binary], out / (name + '-compile.log'))
    if result.returncode or result.stdout or result.stderr:
        raise ValueError('compile error/diagnostic: ' + name)
    result = run([binary], out / (name + '-run.log'), '\n'.join(' '.join(map(str, f[0])) for f in fixtures) + '\n')
    if result.returncode or result.stderr:
        raise ValueError('native runtime failure: ' + name)
    actual = [list(map(int, line.split())) for line in result.stdout.splitlines()]
    if len(actual) != len(fixtures):
        raise ValueError('native output count mismatch')
    return sum(a != e for a, (_, e) in zip(actual, fixtures)), actual


def native_controls(source, fixtures, out):
    initializer = bridge.initializer(source)
    changes = {
        'restore-border-key': (initializer, initializer.replace('frame->GetContentRectRelativeToSelf().Size()', 'frame->GetSize()')),
        'ignore-size-change': ('return mSize != aNewState.mSize;', 'return false;'),
        'inline-width-only': ('return LogicalSize(mWm, mSize).ISize(mWm);', 'return mSize.width;'),
        'project-border-box': ('nsSize size = frame->GetContentRectRelativeToSelf().Size();', 'nsSize size = frame->GetSize();'),
        'swap-width-availability': ('isVertical ? containAxes.mBContained : containAxes.mIContained', 'isVertical ? containAxes.mIContained : containAxes.mBContained'),
        'ignore-type-change': ('if (mType != aNewState.mType)', 'if (false)'),
    }
    rejected = []
    for name, (old, new) in changes.items():
        if source.count(old) != 1:
            raise ValueError('ambiguous native mutation: ' + name)
        count, _ = compiled_run(source.replace(old, new), fixtures, out, 'native-mutation-' + name)
        if not count:
            raise ValueError('native mutation accepted')
        rejected.append({'name': name, 'mismatches': count})
    return rejected


def mask_controls(source, fixtures, out):
    changes = {
        'wrong-inline-axis': ('if wm.is_horizontal()', 'if wm.is_vertical()'),
        'drop-size-height': ('height: size.height,', 'height: None,'),
        'drop-block-feature-axis': ('| Self::CONTAINER_REQUIRES_BLOCK_AXIS', ''),
    }
    rejected = []
    for name, (old, new) in changes.items():
        if old not in source:
            raise ValueError('missing mask mutation')
        count, _ = compiled_run(source.replace(old, new, 1), fixtures, out, 'mask-mutation-' + name, True)
        if not count:
            raise ValueError('mask mutation accepted')
        rejected.append({'name': name, 'mismatches': count})
    return rejected


def source_guards(manifest, before, candidate, out):
    rejected = []
    for name in manifest:
        path = out / ('source-guard-' + str(len(rejected)))
        path.write_bytes((ROOT / name).read_bytes() + b'\nchanged\n')
        try:
            authenticate(manifest, {name: path})
        except ValueError:
            rejected.append(name)
        else:
            raise ValueError('source guard accepted')
    preservation = []
    for name, old, new in [
        ('wrong-getter', 'frame->GetContentRectRelativeToSelf().Size()', 'frame->GetSize()'),
        ('comparator-change', 'return mSize != aNewState.mSize;', 'return false;'),
        ('writing-mode-change', 'frame->GetWritingMode(),', 'WritingMode(),'),
        ('once-per-flush-change', 'if (NS_WARN_IF(!mUpdatedContainerQueryContents.EnsureInserted(', 'if (NS_WARN_IF(mUpdatedContainerQueryContents.EnsureInserted('),
    ]:
        if old not in candidate:
            raise ValueError('missing preservation mutation')
        try:
            bridge.preservation(before, candidate.replace(old, new, 1))
        except ValueError:
            preservation.append(name)
        else:
            raise ValueError('preservation guard accepted')
    return rejected, preservation


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    manifest = json.loads((BASE / 'SOURCE-v1.json').read_text())
    authenticate(manifest)
    for name in ['lean', 'rustc', 'clang']:
        if digest(Path(TOOLCHAIN[name])) != TOOLCHAIN[name + '_sha256']:
            raise ValueError('toolchain executable identity mismatch')
    before = (BASE / 'before-nsPresContext.cpp').read_text()
    candidate = (BASE / 'candidate-nsPresContext.cpp').read_text()
    preserved = bridge.preservation(before, candidate)
    audits = audit_lean(BASE / 'ContentSize.lean', out / 'lean.log')
    lean_mutations, diagnostic_guards = lean_controls(out)
    cases = bridge.fixtures()
    fixtures = [(a + b, bridge.expected(a, b)) for a, b in cases]
    (out / 'fixtures.json').write_text(json.dumps(fixtures, separators=(',', ':')) + '\n')
    source = bridge.source(before, candidate, (BASE / 'native-GeckoBindings.cpp').read_text())
    count, actual = compiled_run(source, fixtures, out, 'native')
    if count:
        raise ValueError('native candidate mismatch')
    premise_cases = 0
    old_counterexamples = 0
    for (a, b), result in zip(cases, actual):
        if bridge.premises(a, b):
            premise_cases += 1
            first, second = bridge.eligible(a, result[2:4]), bridge.eligible(b, result[4:6])
            if not result[0] and first != second:
                raise ValueError('native cache-observable contract violated under premises')
            if not result[1] and first != second:
                old_counterexamples += 1
    native_mutations = native_controls(source, fixtures, out)
    masks = bridge.mask_source((BASE / 'native-container_rule.rs').read_text(), (BASE / 'native-feature.rs').read_text())
    mask_fixtures = bridge.mask_fixtures()
    count, _ = compiled_run(masks, mask_fixtures, out, 'masks', True)
    if count:
        raise ValueError('native consumer mask mismatch')
    mask_mutations = mask_controls(masks, mask_fixtures, out)
    identity_guards, preservation_guards = source_guards(manifest, before, candidate, out)
    authenticate(manifest)
    receipt = {'result': 'PASS', 'source_manifest_sha256': digest(BASE / 'SOURCE-v1.json'),
               'native_extractions': preserved, 'theorem_axioms': audits,
               'lean_mutations': lean_mutations, 'diagnostic_guards': diagnostic_guards,
               'native_cases': len(cases), 'native_cases_under_premises': premise_cases,
               'old_border_key_counterexamples': old_counterexamples,
               'native_mutations': native_mutations, 'consumer_mask_cases': len(mask_fixtures),
               'consumer_mask_mutations': mask_mutations, 'identity_guards': identity_guards,
               'preservation_guards': preservation_guards,
               'fixture_sha256': digest(out / 'fixtures.json'),
               'limits': ['fixed type/writing orientation/availability', 'type-eligible consumer axes only',
                          'supplied current content size', 'native adapter semantics assumed',
                          'not a layout/selection/lifecycle/scrollbar/convergence proof']}
    (out / 'RECEIPT-v1.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(receipt, indent=2))


if __name__ == '__main__':
    main()
