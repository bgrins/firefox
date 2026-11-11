import hashlib
import itertools
import json
import os
from pathlib import Path
import re
import runpy
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
FEATURE = ROOT / 'artifacts/css-number-native-feature-sensitivity-20261110-v3'
MODEL = ROOT / 'artifacts/css-number-lexical-bridge-20261110-v1'
LEAN = ROOT / 'artifacts/stylo-bloom-tools/lean-4.35.0-rc4-darwin_aarch64/bin/lean'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n')


def read(path):
    return json.loads(path.read_text())


def starts_number(text):
    text = text[1:] if text[:1] in ('+', '-') else text
    return bool(text) and (text[0] in '0123456789' or
                           len(text) > 1 and text[0] == '.' and text[1] in '0123456789')


def corpus():
    alphabet = '019.+-eEx%'
    words = [''.join(chars) for size in range(1, 5)
             for chars in itertools.product(alphabet, repeat=size)
             if starts_number(''.join(chars))]
    boundary = []
    for count in [8, 16, 32, 64, 128, 256, 1024]:
        digits = '9' * count
        for text in [digits, '-' + digits, '0.' + digits, '1e' + digits,
                     '1e-' + digits, digits + 'e-1000', digits + '.' + digits,
                     digits + 'e+', digits + 'e-']:
            boundary.append(text)
    boundary += ['2147483647', '2147483648', '-2147483648', '-2147483649',
                 '4294967295', '16777217', '1e38', '1e39', '1e-45', '1e-46']
    assert len(words) == len(set(words))
    tails = list(dict.fromkeys(words + boundary))
    cases = []
    for index, tail in enumerate(tails):
        for history in [False, True]:
            prefix = '/*é*/ ' if history else ''
            cases.append(dict(id=f'{index}-' + ('history' if history else 'single'),
                              prefix=prefix, prefix_utf8_bytes=len(prefix.encode()),
                              warmup=2 if history else 0,
                              tail=tail + (' ;' if history else ''),
                              mode='history' if history else 'single',
                              bridge_eligible=True))
    return cases, dict(alphabet=alphabet, maximum_exhaustive_length=4,
                       exhaustive_words=len(words), boundary_words=len(boundary),
                       unique_tails=len(tails), history_prefix='/*é*/ ',
                       number_entry_filter='optional sign followed by digit or dot then digit')


def main():
    assert sys.flags.isolated and not sys.flags.optimize
    assert sha(FEATURE / 'SOURCE-ONLY.json') == '2a1c3512b0421a05fe1b7fcb9f9a6cb7a7e3b8652cbd0629ae53a20b12f10ac6'
    assert sha(MODEL / 'SOURCE-ONLY.json') == 'da110adb89e5f7ef20ca2cc24f92fa4b9cff428f9751a16940ecb0d9b73427ba'
    assert sha(LEAN) == 'd1d9c26a539f54fe839d2aa7760bf1ac1dd76a30b26e2c9684bebf2900038fcf'
    for directory in [FEATURE, MODEL]:
        for name, expected in read(directory / 'SOURCE-ONLY.json').items():
            assert sha(directory / name) == expected, name
    output = HERE / 'execution'
    output.mkdir(exist_ok=False)
    cases, bounds = corpus()
    save(output / 'CASES.json', cases)
    save(output / 'BOUNDS.json', bounds)
    save(output / 'model-input.json', [[case['tail'], False] for case in cases])
    native_input = ''.join(f"{case['id']}\t{case['warmup']}\t{case['prefix_utf8_bytes']}\t{case['mode']}\t"
                           + (case['prefix'] + case['tail']).encode().hex() + '\n' for case in cases)
    (output / 'native-input.tsv').write_text(native_input)
    save(output / 'INPUTS.json', {str(p.relative_to(ROOT)): sha(p) for p in
         [HERE / 'run.py', FEATURE / 'SOURCE-ONLY.json', MODEL / 'SOURCE-ONLY.json',
          output / 'CASES.json', output / 'model-input.json', output / 'native-input.tsv']})
    prepared = runpy.run_path(str(FEATURE / 'prepare.py'))
    audit = runpy.run_path(str(FEATURE / 'audit.py'))
    instrument = runpy.run_path(str(FEATURE / 'inputs/instrument.py'))['instrument']
    reference = runpy.run_path(str(FEATURE / 'inputs/reference_compare.py'))
    schema = runpy.run_path(str(FEATURE / 'strict_model.py'))
    tools = read(FEATURE / 'TOOLCHAIN.json')
    cargo, rustc = Path(tools['cargo']), Path(tools['rustc'])
    assert sha(cargo) == tools['cargo_sha256'] and sha(rustc) == tools['rustc_sha256']
    commands, binaries = [], {}
    env = {k: v for k, v in os.environ.items() if not k.startswith(('CARGO_', 'RUST', 'LEAN_'))}
    env['PYTHONDONTWRITEBYTECODE'] = '1'

    def run(label, command, cwd, stdin=None, extra_env=None):
        stdout, stderr = output / (label + '.stdout'), output / (label + '.stderr')
        with stdout.open('wb') as out, stderr.open('wb') as err:
            result = subprocess.run([str(x) for x in command], cwd=cwd,
                                    env=dict(env, **(extra_env or {})), input=stdin,
                                    stdout=out, stderr=err)
        commands.append(dict(label=label, command=[str(x) for x in command], cwd=str(cwd),
                             exit=result.returncode, stdout_sha256=sha(stdout),
                             stderr_sha256=sha(stderr), overrides=extra_env))
        save(output / 'COMMANDS.json', commands)
        assert result.returncode == 0, label
        return stdout.read_bytes(), stderr.read_bytes()

    with tempfile.TemporaryDirectory(prefix='css-number-bounded-search-') as directory:
        scratch = Path(directory)
        save(output / 'SCRATCH.json', dict(path=str(scratch)))
        workspace = scratch / 'workspace'
        prepared['materialize'](ROOT, workspace)
        env.update(CARGO_HOME=str(scratch / 'cargo-home'), CARGO_NET_OFFLINE='true', RUSTC=str(rustc))
        dependency = read(FEATURE / 'DEPENDENCIES.json')
        original = (workspace / 'vendor/cssparser/src/tokenizer.rs').read_bytes()
        sums = read(workspace / 'vendor/cssparser/.cargo-checksum.json')
        raw, _ = run('resolve', [cargo, 'metadata', '--offline', '--format-version=1',
                                '--filter-platform=' + audit['HOST']], workspace)
        features = audit['metadata'](json.loads(raw), workspace, dependency['package_records'])
        save(output / 'FEATURES.json', features)
        shutil.copyfile(workspace / 'Cargo.lock', output / 'Cargo.lock')
        lock_hash = sha(workspace / 'Cargo.lock')
        raw, _ = run('metadata', [cargo, 'metadata', '--frozen', '--format-version=1',
                                 '--filter-platform=' + audit['HOST']], workspace)
        assert audit['metadata'](json.loads(raw), workspace, dependency['package_records']) == features
        for label in ['plain', 'instrumented']:
            target = scratch / 'targets' / label
            assert not target.exists()
            actual = original if label == 'plain' else instrument(original.decode()).encode()
            sums['files']['src/tokenizer.rs'] = hashlib.sha256(actual).hexdigest()
            checksum = (json.dumps(sums, separators=(',', ':')) + '\n').encode()
            (workspace / 'vendor/cssparser/src/tokenizer.rs').write_bytes(actual)
            (workspace / 'vendor/cssparser/.cargo-checksum.json').write_bytes(checksum)
            audit['vendor'](workspace, dependency['files'], actual, checksum)
            run(label + '-build', [cargo, 'build', '--frozen', '--target', audit['HOST'], '--bin', 'numeric'],
                workspace, extra_env={'CARGO_TARGET_DIR': str(target)})
            binary = target / audit['HOST'] / 'debug/numeric'
            binaries[label] = dict(path=str(binary), sha256=sha(binary),
                                   tokenizer_sha256=hashlib.sha256(actual).hexdigest())
            save(output / 'BINARIES.json', binaries)
            run(label, [binary], workspace, stdin=native_input.encode())
            audit['vendor'](workspace, dependency['files'], actual, checksum)
            assert sha(workspace / 'Cargo.lock') == lock_hash
        assert binaries['plain']['sha256'] != binaries['instrumented']['sha256']
        model = scratch / 'model'
        model.mkdir()
        for name in read(MODEL / 'SOURCE-ONLY.json'):
            destination = model / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(MODEL / name, destination)
        ordered, visiting, completed = [], set(), set()

        def visit(name):
            if name in completed:
                return
            assert name not in visiting, name
            source = model / (name.replace('.', '/') + '.lean')
            if not source.exists():
                assert name.split('.')[0] in ['Lean', 'Std', 'Init'], name
                return
            visiting.add(name)
            for line in source.read_text().splitlines():
                if line.startswith('import '):
                    for dependency_name in line.removeprefix('import ').split():
                        assert re.fullmatch(r'[A-Za-z0-9_.]+', dependency_name)
                        visit(dependency_name)
            visiting.remove(name)
            completed.add(name)
            ordered.append(name)

        visit('Runner')
        prior = read(ROOT / 'artifacts/css-number-lexical-bridge-review-20261110-v1/replay/report.json')
        for name in ordered:
            path = name.replace('.', '/') + '.lean'
            stdout, stderr = run('model-' + name, [LEAN, '-o', path[:-5] + '.olean', path], model,
                                 extra_env={'LEAN_PATH': str(model)})
            expected = prior['commands']['build-' + path.replace('/', '-')]['output_sha256']
            assert hashlib.sha256(stdout + stderr).hexdigest() == expected, name
        run('model-rows', [LEAN, '--run', 'Runner.lean', MODEL / 'number.json', output / 'model-input.json'],
            model, extra_env={'LEAN_PATH': str(model)})
        model_rows = schema['read'](output / 'model-rows.stdout', cases)
        result = reference['compare'](cases,
            reference['public_rows']((output / 'plain.stdout').read_text()),
            reference['public_rows']((output / 'instrumented.stdout').read_text()),
            reference['trace_rows']((output / 'plain.stderr').read_text()),
            reference['trace_rows']((output / 'instrumented.stderr').read_text()), model_rows)
        save(output / 'COMPARISON.json', result)
    assert not scratch.exists()
    for directory in [FEATURE, MODEL]:
        for name, expected in read(directory / 'SOURCE-ONLY.json').items():
            assert sha(directory / name) == expected, name
    save(output / 'RESULT.json', dict(status='PASS', comparison=result, bounds=bounds,
         fresh_native_binaries=2, model_modules=len(ordered), temporary_targets_removed=True,
         full_gecko_equivalence=False, float_conversion_proved=False, native_refinement_proved=False))
    print(json.dumps(read(output / 'RESULT.json')))


if __name__ == '__main__':
    main()
