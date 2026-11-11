import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PROTOCOL = ROOT / 'artifacts/css-number-native-differential-protocol-20261110-v1'
MODEL = ROOT / 'artifacts/css-number-lexical-bridge-20261110-v1'
LEAN = ROOT / 'artifacts/stylo-bloom-tools/lean-4.35.0-rc4-darwin_aarch64/bin/lean'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text())


def save(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n')


def main():
    assert sys.flags.isolated and not sys.flags.optimize
    assert digest(PROTOCOL / 'SOURCE-ONLY.json') == '85f92d0dd4674b3bd8f6b16f53b75859cc8511ce05002d0d89edf3c4ca9adadf'
    assert digest(MODEL / 'SOURCE-ONLY.json') == 'da110adb89e5f7ef20ca2cc24f92fa4b9cff428f9751a16940ecb0d9b73427ba'
    for directory in [PROTOCOL, MODEL]:
        for name, expected in read(directory / 'SOURCE-ONLY.json').items():
            assert digest(directory / name) == expected, name
    execution = HERE / 'execution'
    execution.mkdir()
    scratch = execution / 'scratch'
    scratch.mkdir()
    commands = []

    def run(label, command, cwd=ROOT, stdin=None, env=None):
        stdout = execution / (label + '.stdout')
        stderr = execution / (label + '.stderr')
        with stdout.open('wb') as output, stderr.open('wb') as errors:
            result = subprocess.run([str(x) for x in command], cwd=cwd, input=stdin,
                                    env=env, stdout=output, stderr=errors)
        row = dict(label=label, command=[str(x) for x in command], cwd=str(cwd),
                   exit=result.returncode, stdout_sha256=digest(stdout), stderr_sha256=digest(stderr))
        commands.append(row)
        save(execution / 'COMMANDS.json', commands)
        assert result.returncode == 0, label
        return stdout.read_bytes(), stderr.read_bytes()

    materialized = scratch / 'materialized'
    materialized.mkdir()
    for row in read(PROTOCOL / 'MATERIALIZE.json')['files']:
        data = subprocess.check_output(['git', '-c', 'core.fsmonitor=false', 'show',
                                        row['commit'] + ':' + row['path']], cwd=ROOT)
        assert hashlib.sha256(data).hexdigest() == row['sha256']
        destination = materialized / row['destination']
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(data)
    shutil.copyfile(PROTOCOL / 'driver.rs', materialized / 'driver.rs')
    shutil.copyfile(PROTOCOL / 'inputs/legacy-toolchain.json', materialized / 'TOOLCHAIN.json')
    shutil.copytree(PROTOCOL / 'prepared', materialized / 'corpus')
    binaries = {}
    for variant in ['plain', 'instrumented']:
        output = scratch / variant
        command = [sys.executable, '-B', PROTOCOL / 'build.py', '--source', materialized, '--out', output]
        if variant == 'instrumented':
            command.append('--instrumented')
        try:
            run('build-' + variant, command)
        finally:
            for name in ['COMMANDS.json', 'BUILD.json']:
                if (output / name).exists():
                    shutil.copyfile(output / name, execution / (variant + '-' + name))
        binaries[variant] = digest(output / 'numeric')
        run('native-' + variant, [output / 'numeric'], stdin=(PROTOCOL / 'prepared/native-input.tsv').read_bytes())

    model = scratch / 'model'
    model.mkdir()
    for name in read(MODEL / 'SOURCE-ONLY.json'):
        destination = model / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(MODEL / name, destination)
    previous = read(ROOT / 'artifacts/css-number-lexical-bridge-review-20261110-v1/replay/report.json')
    assert digest(LEAN) == 'd1d9c26a539f54fe839d2aa7760bf1ac1dd76a30b26e2c9684bebf2900038fcf'
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
                for dependency in line.removeprefix('import ').split():
                    assert re.fullmatch(r'[A-Za-z0-9_.]+', dependency), dependency
                    visit(dependency)
        visiting.remove(name)
        completed.add(name)
        ordered.append(name)

    visit('Runner')
    for name in ordered:
        path = name.replace('.', '/') + '.lean'
        stdout, stderr = run('model-' + name, [LEAN, '-o', path[:-5] + '.olean', path],
                             cwd=model, env=dict(os.environ, LEAN_PATH=str(model)))
        accepted = previous['commands']['build-' + path.replace('/', '-')]['output_sha256']
        assert hashlib.sha256(stdout + stderr).hexdigest() == accepted, name
    run('model-rows', [LEAN, '--run', 'Runner.lean', MODEL / 'number.json',
                       PROTOCOL / 'prepared/model-input.json'], cwd=model,
        env=dict(os.environ, LEAN_PATH=str(model)))
    run('compare', [sys.executable, '-I', PROTOCOL / 'compare.py',
                    '--cases', PROTOCOL / 'prepared/CASES.json',
                    '--plain', execution / 'native-plain.stdout',
                    '--instrumented', execution / 'native-instrumented.stdout',
                    '--plain-trace', execution / 'native-plain.stderr',
                    '--trace', execution / 'native-instrumented.stderr',
                    '--model', execution / 'model-rows.stdout',
                    '--out', execution / 'COMPARISON.json'])
    for directory in [PROTOCOL, MODEL]:
        for name, expected in read(directory / 'SOURCE-ONLY.json').items():
            assert digest(directory / name) == expected, name
    save(execution / 'RESULT.json', dict(status='PASS', binaries=binaries,
                                        model_modules=len(ordered), comparison=read(execution / 'COMPARISON.json'),
                                        production_feature_equivalence=False, compiled_native_mutants=False,
                                        scratch_removal_pending=True))
    print(json.dumps(read(execution / 'RESULT.json'), indent=2))


if __name__ == '__main__':
    main()
