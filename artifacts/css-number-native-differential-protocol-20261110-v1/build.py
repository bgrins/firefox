import argparse
import hashlib
import json
from pathlib import Path
import runpy
import shutil
import subprocess

ROOT = Path(__file__).resolve().parent


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--source', required=True, type=Path)
    p.add_argument('--out', required=True, type=Path)
    p.add_argument('--instrumented', action='store_true')
    a = p.parse_args()
    source, out = a.source.resolve(), a.out.resolve()
    for record in json.loads((ROOT / 'MATERIALIZE.json').read_text())['files']:
        if hashlib.sha256((source / record['destination']).read_bytes()).hexdigest() != record['sha256']:
            raise ValueError('Materialized input changed: ' + record['destination'])
    if (source / 'driver.rs').read_bytes() != (ROOT / 'driver.rs').read_bytes():
        raise ValueError('Driver changed')
    if (source / 'TOOLCHAIN.json').read_bytes() != (ROOT / 'inputs/legacy-toolchain.json').read_bytes():
        raise ValueError('Toolchain declaration changed')
    config = json.loads((source / 'TOOLCHAIN.json').read_text())
    rustc = Path(config['rustc'])
    if hashlib.sha256(rustc.read_bytes()).hexdigest() != config['rustc_sha256']:
        raise ValueError('Pinned Rust compiler changed')
    out.mkdir(parents=True, exist_ok=False)
    shutil.copytree(source / 'vendor', out / 'vendor')
    shutil.copyfile(source / 'driver.rs', out / 'driver.rs')
    if a.instrumented:
        path = out / 'vendor/cssparser/src/tokenizer.rs'
        path.write_text(runpy.run_path(str(ROOT / 'instrument.py'))['instrument'](path.read_text()))
    commands = []

    def run(command):
        result = subprocess.run([str(x) for x in command], cwd=out, capture_output=True, text=True)
        commands.append(dict(command=[str(x) for x in command], exit=result.returncode,
            stdout=result.stdout, stderr=result.stderr))
        (out / 'COMMANDS.json').write_text(json.dumps(commands, indent=2) + '\n')
        if result.returncode:
            raise RuntimeError('Native compile failed; inspect COMMANDS.json')

    for name, edition, deps in [('dtoa', '2015', []), ('dtoa-short', '2015', ['dtoa']),
            ('itoa', '2018', []), ('smallvec', '2018', []),
            ('cssparser', '2024', ['dtoa-short', 'itoa', 'smallvec'])]:
        crate = name.replace('-', '_')
        command = [rustc, '--crate-name', crate, '--crate-type', 'rlib', '--edition', edition,
            '-C', 'opt-level=1', '-L', 'dependency=' + str(out),
            out / 'vendor' / name / 'src/lib.rs', '-o', out / ('lib' + crate + '.rlib')]
        for dep in deps:
            dep = dep.replace('-', '_')
            command += ['--extern', dep + '=' + str(out / ('lib' + dep + '.rlib'))]
        run(command)
    run([rustc, '--edition', '2024', '-C', 'opt-level=1', '-L', 'dependency=' + str(out),
        '--extern', 'cssparser=' + str(out / 'libcssparser.rlib'), out / 'driver.rs', '-o', out / 'numeric'])
    (out / 'BUILD.json').write_text(json.dumps(dict(mode='direct-rustc-no-features',
        instrumented=a.instrumented, native_execution_performed=False,
        production_feature_equivalence=False), indent=2) + '\n')


if __name__ == '__main__':
    main()
