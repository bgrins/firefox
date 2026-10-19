import hashlib
import json
import os
from pathlib import Path
import re
import resource
import subprocess
import sys

from controls_v2 import LEAN_MUTATIONS, RUST_MUTATIONS

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[1]
LEAN = ROOT / 'artifacts/stylo-bloom-tools/lean-4.35.0-rc4-darwin_aarch64/bin/lean'
RUSTC = Path('/Users/bgrins/.rustup/toolchains/1.97.1-aarch64-apple-darwin/bin/rustc')
DEPS = ROOT / 'objdir-full.noindex/aarch64-apple-darwin/debug/deps'
HOST_DEPS = ROOT / 'objdir-full.noindex/debug/deps'
RLIB = DEPS / 'libcssparser-2873c19d8122c218.rlib'
FAILURES = {
    'PrefixOnly': ['whole_token_classification', 'suffix_rejected'],
    'EraseSign': ['construction_preserves_payload'],
    'WrongPercentage': ['construction_preserves_unit'],
    'ClearTaint': ['primary_refinement', 'accepted_primary', 'primary_tainted'],
    'DiscardFallback': ['rejected_suffix_selects_fallback', 'missing_selects_fallback'],
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_positive(code, stdout, stderr):
    if code != 0 or stderr or stdout != (BASE / 'expected-axioms.txt').read_text():
        raise RuntimeError('Unexpected positive compilation/audit')


def check_negative(source, path, code, stdout, stderr, expected):
    if code != 1 or stderr:
        raise RuntimeError('Unexpected negative terminal')
    declarations = [(i, line) for i, line in enumerate(source.splitlines(), 1)
                    if re.match(r'^(theorem |def |#print|end )', line)]
    spans = {}
    lines = source.splitlines()
    for index, (start, declaration) in enumerate(declarations[:-1]):
        if declaration.startswith('theorem '):
            end = declarations[index + 1][0]
            bodies = [i for i in range(start, end) if ':= by' in lines[i - 1]]
            if len(bodies) != 1:
                raise RuntimeError('Ambiguous proof body')
            spans[declaration.split()[1]] = (bodies[0], end)
    errors = re.findall(r'^(.+):(\d+):\d+: error(?:\([^\n)]*\))?: (.*)$', stdout, re.M)
    if len(re.findall(r'\berror(?:\([^\n)]*\))?:', stdout)) != len(errors):
        raise RuntimeError('Unlocated diagnostic')
    found = []
    for filename, line, message in errors:
        owners = [name for name, (start, end) in spans.items() if start <= int(line) < end]
        if filename != str(path) or len(owners) != 1 or message not in [
            'unsolved goals', 'Tactic `rfl` failed: The left-hand side',
        ]:
            raise RuntimeError('Unexpected proof diagnostic')
        found.append(owners[0])
    if found != expected:
        raise RuntimeError('Wrong failing theorem inventory: ' + repr(found))
    return found


def unit_inventory(units):
    enum = (BASE / 'sort-key-v2.rs').read_text().split('pub enum SortKey {', 1)[1]
    variants = re.findall(r'^    ([A-Z][A-Za-z]*),', enum, re.M)
    expected = ['', '%'] + [name.lower() for name in variants
                           if name not in ['Number', 'Percentage', 'ColorComponent', 'Other']]
    if units != expected or len(units) != 49:
        raise RuntimeError('Unit fixture does not cover the complete enum')


def source_binding():
    toolchain = json.loads((BASE / 'TOOLCHAIN-v1.json').read_text())
    for name, expected in toolchain.items():
        if sha(Path(name)) != expected:
            raise RuntimeError('Changed frozen compiler/library: ' + name)
    manifest = json.loads((BASE / 'SOURCE-v2.json').read_text())
    for name, expected in manifest['sha256'].items():
        if sha(BASE / name) != expected:
            raise RuntimeError('Changed frozen input: ' + name)
    native = ROOT / 'servo/components/style/custom_properties.rs'
    text = native.read_text()
    marker = "fn substitute_one_reference<'a>("
    if text.count(marker) != 1:
        raise RuntimeError('Ambiguous native function')
    start = text.index(marker)
    fragment = text[start:text.index('\n/// Replace `var()`, `env()`, and `attr()`', start)]
    if fragment == (BASE / 'native-before.rs').read_text():
        candidate = False
    elif fragment == (BASE / 'native-proposed-v2.rs').read_text():
        candidate = True
    else:
        raise RuntimeError('Unreviewed native function')
    for name in ['parser.rs', 'tokenizer.rs', 'serializer.rs']:
        if (ROOT / 'third_party/rust/cssparser/src' / name).read_bytes() != (BASE / ('cssparser-' + name)).read_bytes():
            raise RuntimeError('Changed cssparser source')
    text = (ROOT / 'servo/components/style/values/generics/calc.rs').read_text()
    start = text.index('/// This determines the order in which we serialize members of a calc() sum.')
    if text[start:text.index('\n}', start) + 2] != (BASE / 'sort-key-v2.rs').read_text():
        raise RuntimeError('Changed unit enum')
    unit_inventory(json.loads((BASE / 'units-v2.json').read_text()))
    template = (BASE / 'bridge-template-v2.rs').read_text()
    if 'CssString' in template or 'type String' in template:
        raise RuntimeError('Unexpected storage type adaptation')
    body = (BASE / 'candidate-body-v2.rs').read_text().strip().splitlines()
    native_body = (BASE / 'native-proposed-v2.rs').read_text().split('let css = {', 1)[1].split('};', 1)[0]
    native_lines = [line.strip() for line in native_body.splitlines()
                    if line.strip() and not line.strip().startswith('//')]
    if native_lines != [line.replace('s.push_str(unit);', 's.push_str(unit.as_ref());')
                        .replace('Some(s)', 's') for line in body]:
        raise RuntimeError('Harness/native candidate body drift')
    return {'live_native_candidate': candidate, 'native_function_sha256': hashlib.sha256(fragment.encode()).hexdigest(),
            'bridge': 'manual mapping plus bounded execution of proposed body',
            'universal_string_parser_verified': False, 'native_integration_verified': False}


def main():
    if sys.flags.optimize or len(sys.argv) != 2:
        raise RuntimeError('Usage: python3 check_v2.py NEW_OUTPUT_DIRECTORY')
    out = Path(sys.argv[1]).resolve()
    out.mkdir()
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    model = (BASE / 'NumericAttr.lean').read_text()
    if re.search(r'\b(sorry|admit|axiom|unsafe|native_decide)\b', model.replace('#print axioms', '')):
        raise RuntimeError('Unchecked construct')
    files = [BASE / name for name in [
        'NumericAttr.lean', 'check_v2.py', 'controls_v2.py', 'candidate-body-v2.rs', 'bridge-template-v2.rs',
        'expected-axioms.txt', 'SOURCE-v2.json', 'TOOLCHAIN-v1.json', 'README-v2.md', 'REVIEW-v2.md', 'units-v2.json',
    ]] + [LEAN, RUSTC, ROOT / 'servo/components/style/custom_properties.rs']
    for name in ['cssparser', 'phf', 'phf_shared', 'siphasher', 'smallvec', 'serde', 'serde_core', 'dtoa_short', 'dtoa', 'itoa']:
        files += list(DEPS.glob('lib' + name + '-*.rlib'))
    files += list(HOST_DEPS.glob('libcssparser_macros-*.dylib'))
    before = {str(path): sha(path) for path in files}
    binding = source_binding()
    inventory_controls = []
    all_units = json.loads((BASE / 'units-v2.json').read_text())
    for name, units in {
        'missing-seconds': [unit for unit in all_units if unit != 's'],
        'duplicate-unit': all_units + ['s'],
        'unknown-unit': all_units + ['bogus'],
    }.items():
        try:
            unit_inventory(units)
        except RuntimeError:
            inventory_controls.append(name)
        else:
            raise RuntimeError('Accepted corrupted unit inventory')
    commands = []

    def run(command, directory, label, env=None):
        result = subprocess.run(command, cwd=directory, env=env, capture_output=True, text=True)
        (directory / (label + '.stdout')).write_text(result.stdout)
        (directory / (label + '.stderr')).write_text(result.stderr)
        commands.append({'command': command, 'cwd': str(directory), 'exit': result.returncode})
        return result

    positive = None
    lean_controls = {}
    sample = None
    for name, mutation in [('positive', None), *LEAN_MUTATIONS.items()]:
        directory = out / name
        directory.mkdir()
        if mutation is not None and model.count(mutation[0]) != 1:
            raise RuntimeError('Mutation cardinality mismatch')
        text = model if mutation is None else model.replace(*mutation)
        path = directory / 'NumericAttr.lean'
        path.write_text(text)
        env = os.environ.copy()
        env['LEAN_PATH'] = str(directory)
        env.pop('LEAN_SRC_PATH', None)
        command = [str(LEAN), '-DwarningAsError=true', '-Dlinter.unusedSimpArgs=false', '-Dlinter.unusedVariables=false']
        if mutation is None:
            command += ['-o', str(directory / 'NumericAttr.olean')]
        command.append(str(path))
        result = run(command, directory, 'lean', env)
        if mutation is None:
            check_positive(result.returncode, result.stdout, result.stderr)
            positive = result
        else:
            lean_controls[name] = check_negative(text, path, result.returncode, result.stdout, result.stderr, FAILURES[name])
            if name == 'PrefixOnly':
                sample = text, path, result

    text, path, result = sample
    header = re.search(r'^(.+):(\d+):\d+: error: (.*)$', result.stdout, re.M).group(0)
    corruptions = {
        'exit-zero': (0, result.stdout, ''), 'exit-two': (2, result.stdout, ''),
        'stderr': (1, result.stdout, 'noise'), 'empty': (1, '', ''),
        'foreign-file': (1, result.stdout.replace(str(path), str(path) + '-other', 1), ''),
        'outside-proof': (1, re.sub(r':\d+:\d+: error:', ':1:1: error:', result.stdout, count=1), ''),
        'extra-error': (1, result.stdout + '\n' + header + '\n', ''),
        'unlocated': (1, result.stdout + '\nerror: tool failure\n', ''),
        'unknown-name': (1, result.stdout.replace('error: unsolved goals', 'error: Unknown identifier bogus', 1), ''),
        'parse-error': (1, result.stdout.replace('error: unsolved goals', 'error: unexpected token', 1), ''),
    }
    guards = []
    for name, args in corruptions.items():
        try:
            check_negative(text, path, *args, FAILURES['PrefixOnly'])
        except RuntimeError:
            guards.append(name)
        else:
            raise RuntimeError('Accepted corrupted negative evidence')
    for name, args in {
        'positive-exit': (1, positive.stdout, ''),
        'positive-stderr': (0, positive.stdout, 'noise'),
        'positive-axiom': (0, positive.stdout.replace('[propext]', '[sorryAx]', 1), ''),
    }.items():
        try:
            check_positive(*args)
        except RuntimeError:
            guards.append(name)
        else:
            raise RuntimeError('Accepted corrupted positive evidence')

    rust_controls = {}
    template = (BASE / 'bridge-template-v2.rs').read_text()
    body = (BASE / 'candidate-body-v2.rs').read_text()
    units = '&' + json.dumps(json.loads((BASE / 'units-v2.json').read_text()))
    for name, mutation in [('positive', None), *RUST_MUTATIONS.items()]:
        directory = out / ('rust-' + name)
        directory.mkdir()
        if mutation is not None and body.count(mutation[0]) != 1:
            raise RuntimeError('Rust mutation cardinality mismatch')
        candidate = body if mutation is None else body.replace(*mutation)
        source = directory / 'bridge.rs'
        source.write_text(template.replace('CANDIDATE_BODY', candidate).replace('UNITS', units))
        command = [str(RUSTC), '--edition=2021', '-C', 'panic=abort', '-D', 'warnings',
                   '-A', 'unused_variables', '-A', 'unused_mut', str(source),
                   '--extern', 'cssparser=' + str(RLIB), '-L', 'dependency=' + str(DEPS),
                   '-L', 'dependency=' + str(HOST_DEPS), '-o', str(directory / 'bridge')]
        result = run(command, directory, 'compile')
        if result.returncode or result.stdout or result.stderr:
            raise RuntimeError('Rust bridge compilation failed')
        result = run([str(directory / 'bridge')], directory, 'execute')
        if mutation is None:
            if result.returncode or result.stderr or result.stdout != 'bridge cases passed: 2450\n':
                raise RuntimeError('Bridge assertion failed')
        else:
            marker = 'Accepted invalid input' if name == 'PrefixOnly' else 'assertion `left == right` failed'
            if result.returncode != -6 or result.stdout or marker not in result.stderr:
                raise RuntimeError('Wrong Rust mutation failure')
            rust_controls[name] = {'exit': result.returncode, 'assertion_marker': marker}
    run([str(RUSTC), '--version', '--verbose'], out, 'rustc-version')
    run([str(LEAN), '--version'], out, 'lean-version')
    if before != {str(path): sha(path) for path in files}:
        raise RuntimeError('Inputs changed during replay')
    source_binding()
    (out / 'commands.json').write_text(json.dumps(commands, indent=2) + '\n')
    report = {'status': 'pass', 'scope': 'independent token model and bounded proposed-source bridge',
              'audits': 14, 'lean_mutations': lean_controls, 'record_guards': guards,
              'rust_bridge_cases': 2450, 'rust_mutations': rust_controls, 'source_binding': binding,
              'inventory_controls': inventory_controls,
              'inputs': before,
              'outputs': {str(path.relative_to(out)): sha(path) for path in out.rglob('*') if path.is_file()}}
    (out / 'report.json').write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
    print(json.dumps({key: report[key] for key in ['status', 'audits', 'rust_bridge_cases', 'source_binding']}))


if __name__ == '__main__':
    main()
