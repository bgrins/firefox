import copy
import hashlib
import itertools
import json
from pathlib import Path
import re
import runpy
import subprocess

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
AUTHOR = ROOT / 'artifacts/css-number-native-bounded-search-20261110-v1'
EXECUTION = AUTHOR / 'execution'
FEATURE = ROOT / 'artifacts/css-number-native-feature-sensitivity-20261110-v3'
MODEL = ROOT / 'artifacts/css-number-lexical-bridge-20261110-v1'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text())


def save(name, value):
    (HERE / name).write_text(json.dumps(value, indent=2) + '\n')


def main():
    author_manifest = read(AUTHOR / 'FILES.json')
    for name, expected in author_manifest.items():
        assert sha(AUTHOR / name) == expected, name
    input_pins = read(EXECUTION / 'INPUTS.json')
    for name, expected in input_pins.items():
        assert sha(ROOT / name) == expected, name
    for base in [FEATURE, MODEL]:
        for name, expected in read(base / 'SOURCE-ONLY.json').items():
            assert sha(base / name) == expected, name
    tools = read(FEATURE / 'TOOLCHAIN.json')
    for kind in ['cargo', 'rustc']:
        assert sha(Path(tools[kind])) == tools[kind + '_sha256']
    commands = read(EXECUTION / 'COMMANDS.json')
    assert len(commands) == 51 and len({r['label'] for r in commands}) == 51
    by_label = {record['label']: record for record in commands}
    for record in commands:
        assert record['exit'] == 0
        for stream in ['stdout', 'stderr']:
            assert sha(EXECUTION / (record['label'] + '.' + stream)) == record[stream + '_sha256']
    cases = read(EXECUTION / 'CASES.json')
    alphabet = '019.+-eEx%'

    def admissible(word):
        digit = lambda char: char in '0123456789'
        return (digit(word[0]) or
                word[0] == '.' and len(word) >= 2 and digit(word[1]) or
                word[0] in '+-' and len(word) >= 2 and digit(word[1]) or
                word[0] in '+-' and len(word) >= 3 and word[1] == '.' and digit(word[2]))

    exhaustive = [''.join(word) for length in range(1, 5)
                  for word in itertools.product(alphabet, repeat=length) if admissible(word)]
    assert len(exhaustive) == 3333 + 333 + 666 + 66 == 4398
    boundary = []
    for n in [8, 16, 32, 64, 128, 256, 1024]:
        x = '9' * n
        boundary.extend([x, '-' + x, '0.' + x, '1e' + x, '1e-' + x,
                         x + 'e-1000', x + '.' + x, x + 'e+', x + 'e-'])
    boundary.extend(['2147483647', '2147483648', '-2147483648', '-2147483649',
                     '4294967295', '16777217', '1e38', '1e39', '1e-45', '1e-46'])
    assert len(boundary) == 73 and not set(boundary) & set(exhaustive)
    words = exhaustive + boundary
    assert len(set(words)) == 4471 and len(cases) == 8942
    for i, word in enumerate(words):
        for mode, case in zip(['single', 'history'], cases[2*i:2*i+2]):
            prefix = '' if mode == 'single' else '/*é*/ '
            expected = dict(id=f'{i}-{mode}', prefix=prefix, prefix_utf8_bytes=len(prefix.encode()),
                warmup=0 if mode == 'single' else 2, tail=word + ('' if mode == 'single' else ' ;'),
                mode=mode, bridge_eligible=True)
            assert case == expected
            assert admissible(case['tail']) and all(0 < ord(c) < 128 and c not in '\r\f' for c in case['tail'])
    assert read(EXECUTION / 'model-input.json') == [[case['tail'], False] for case in cases]
    native_lines = (EXECUTION / 'native-input.tsv').read_text().splitlines()
    assert len(native_lines) == len(cases)
    for case, line in zip(cases, native_lines):
        fields = line.split('\t')
        assert fields == [case['id'], str(case['warmup']), str(case['prefix_utf8_bytes']), case['mode'],
                          (case['prefix'] + case['tail']).encode().hex()]
    reference = runpy.run_path(str(FEATURE / 'inputs/reference_compare.py'))
    schema = runpy.run_path(str(FEATURE / 'strict_model.py'))
    models = schema['read'](EXECUTION / 'model-rows.stdout', cases)
    plain = reference['public_rows']((EXECUTION / 'plain.stdout').read_text())
    instrumented = reference['public_rows']((EXECUTION / 'instrumented.stdout').read_text())
    plain_trace = reference['trace_rows']((EXECUTION / 'plain.stderr').read_text())
    traces = reference['trace_rows']((EXECUTION / 'instrumented.stderr').read_text())
    result = reference['compare'](cases, plain, instrumented, plain_trace, traces, models)
    assert result == read(EXECUTION / 'COMPARISON.json') == read(EXECUTION / 'RESULT.json')['comparison']
    assert result['public_rows'] == 4471 * 6 and result['lexical_comparisons'] == 4471 * 3
    binaries = read(EXECUTION / 'BINARIES.json')
    assert binaries['plain']['sha256'] != binaries['instrumented']['sha256']
    native = (FEATURE / 'inputs/tokenizer.rs').read_bytes()
    instrument = runpy.run_path(str(FEATURE / 'inputs/instrument.py'))['instrument']
    assert binaries['plain']['tokenizer_sha256'] == hashlib.sha256(native).hexdigest()
    assert binaries['instrumented']['tokenizer_sha256'] == hashlib.sha256(instrument(native.decode()).encode()).hexdigest()
    targets = []
    for label in ['plain', 'instrumented']:
        build = by_label[label + '-build']
        target = Path(build['overrides']['CARGO_TARGET_DIR'])
        targets.append(target)
        assert target.name == label and str(target) in binaries[label]['path']
        assert by_label[label]['command'] == [binaries[label]['path']]
        text = (EXECUTION / (label + '-build.stderr')).read_text()
        assert 'Compiling cssparser v0.38.0 ' in text and 'Finished `dev` profile' in text
        assert not Path(binaries[label]['path']).exists() and not target.exists()
    assert targets[0] != targets[1]
    scratch = Path(read(EXECUTION / 'SCRATCH.json')['path'])
    assert not scratch.exists()
    audit = runpy.run_path(str(FEATURE / 'audit.py'))
    dependencies = read(FEATURE / 'DEPENDENCIES.json')
    for label in ['resolve', 'metadata']:
        assert audit['metadata'](read(EXECUTION / (label + '.stdout')),
            Path(by_label[label]['cwd']), dependencies['package_records']) == read(EXECUTION / 'FEATURES.json')
    assert read(EXECUTION / 'FEATURES.json')['cssparser'] == ['default', 'fast_match_byte', 'fast_match_color']
    ordered, active, seen = [], set(), set()

    def visit(name):
        if name in seen:
            return
        source = MODEL / (name.replace('.', '/') + '.lean')
        if not source.exists():
            assert name.split('.')[0] in ['Lean', 'Std', 'Init']
            return
        assert name not in active
        active.add(name)
        for imported in re.findall(r'^import ([^\n]+)$', source.read_text(), re.M):
            for dependency in imported.split():
                assert re.fullmatch(r'[A-Za-z0-9_.]+', dependency)
                visit(dependency)
        active.remove(name); seen.add(name); ordered.append(name)

    visit('Runner')
    assert len(ordered) == 44
    assert [r['label'] for r in commands if r['label'].startswith('model-') and r['label'] != 'model-rows'] == ['model-' + name for name in ordered]
    assert by_label['model-rows']['command'][-2:] == [str(MODEL / 'number.json'), str(EXECUTION / 'model-input.json')]
    prior = read(ROOT / 'artifacts/css-number-lexical-bridge-review-20261110-v1/replay/report.json')
    for name in ordered:
        path = name.replace('.', '/') + '.lean'
        combined = (EXECUTION / ('model-' + name + '.stdout')).read_bytes() + (EXECUTION / ('model-' + name + '.stderr')).read_bytes()
        assert hashlib.sha256(combined).hexdigest() == prior['commands']['build-' + path.replace('/', '-')]['output_sha256']
    payload = ''.join(r['commit'] + ':' + r['path'] + '\n' for r in dependencies['files']).encode()
    objects = subprocess.check_output(['git', '-c', 'core.fsmonitor=false', '-C', str(ROOT), 'cat-file', '--batch'], input=payload)
    offset = 0
    for record in dependencies['files']:
        end = objects.index(b'\n', offset)
        header = objects[offset:end].split(); assert header[1] == b'blob'
        size = int(header[2]); data = objects[end+1:end+1+size]
        assert hashlib.sha256(data).hexdigest() == record['sha256'], record['path']
        assert objects[end+1+size:end+2+size] == b'\n'
        offset = end + 2 + size
    assert offset == len(objects)
    controls = {}

    def reject(label, callback, text):
        try:
            callback()
        except ValueError as error:
            assert text in str(error), (label, error)
            controls[label] = str(error)
        else:
            raise AssertionError(label)

    missing = dict(plain); missing.pop(next(iter(missing)))
    reject('missing-phase', lambda: reference['compare'](cases, missing, missing, plain_trace, traces, models), 'Missing or extra')
    bad = copy.deepcopy(traces); bad[('0-history', 'cached')] = bad[('0-history', 'cold')]
    reject('cache-reexecuted', lambda: reference['compare'](cases, plain, instrumented, plain_trace, bad, models), 'invocation count')
    bad_public = copy.deepcopy(plain); bad_public[('0-single', 'cold')]['has_sign'] = True
    bad_trace = copy.deepcopy(traces); bad_trace[('0-single', 'cold')][0]['has_sign'] = True
    reject('typed-wrong-sign', lambda: reference['compare'](cases, bad_public, bad_public, plain_trace, bad_trace, models), 'Native/JSON lexical mismatch')
    bad_public = copy.deepcopy(plain); bad_public[('0-history', 'reparsed')]['column'] += 1
    reject('reset-column-drift', lambda: reference['compare'](cases, bad_public, bad_public, plain_trace, traces, models), 'Reset changed numeric')
    for label, index, value in [('bool-to-int', 5, 0), ('integer-to-float', 0, 48.0)]:
        bad_model = copy.deepcopy(models)
        if index == 5:
            bad_model[0][2][index] = value
        else:
            bad_model[0][2][index][0] = value
        assert bad_model == models
        reject(label, lambda rows=bad_model: schema['validate'](rows, cases), 'Expected')
    for name, expected in author_manifest.items():
        assert sha(AUTHOR / name) == expected, name
    save('CONTROLS.json', controls)
    save('INPUTS.json', dict(author_manifest_sha256=sha(AUTHOR / 'FILES.json'), author_inputs=input_pins,
        dependencies_manifest_sha256=sha(FEATURE / 'DEPENDENCIES.json'),
        compiler_output_reference_sha256=sha(ROOT / 'artifacts/css-number-lexical-bridge-review-20261110-v1/replay/report.json')))
    save('CHECK.json', dict(status='PASS', author_files=len(author_manifest), command_receipts=len(commands),
        independently_rebuilt_exhaustive_words=len(exhaustive), boundary_words=len(boundary), cases=len(cases),
        comparison=result, model_import_closure=len(ordered), git_dependency_objects=len(dependencies['files']),
        malformed_record_controls=len(controls), distinct_build_target_paths=True, actual_trace_execution=True,
        scratch_absent=True, native_or_lean_compilation_repeated=False))


if __name__ == '__main__':
    main()
