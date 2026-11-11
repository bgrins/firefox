import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parent
MANIFEST = '''[package]
name = "css-number-feature-gate"
version = "0.1.0"
edition = "2024"

[workspace]
resolver = "2"

[[bin]]
name = "numeric"
path = "driver.rs"

[dependencies]
cssparser = { git = "https://github.com/servo/rust-cssparser", rev = "9f3ceddf398f5ce4ab76fdad1b42ccb6c578a926", default-features = true }

[profile.dev]
opt-level = 1
debug = 0
debug-assertions = false
overflow-checks = false
codegen-units = 16
incremental = false
panic = "unwind"
'''
CONFIG = '''[net]
offline = true

[source.crates-io]
replace-with = "vendored-sources"

[source."git+https://github.com/servo/rust-cssparser?rev=9f3ceddf398f5ce4ab76fdad1b42ccb6c578a926"]
git = "https://github.com/servo/rust-cssparser"
rev = "9f3ceddf398f5ce4ab76fdad1b42ccb6c578a926"
replace-with = "vendored-sources"

[source.vendored-sources]
directory = "vendor"
'''


def seed_lock(packages):
    root = {'name': 'css-number-feature-gate', 'version': '0.1.0', 'dependencies': ['cssparser']}
    text = 'version = 4\n'
    for package in [root] + [packages[name] for name in sorted(packages)]:
        text += '\n[[package]]\n'
        for field in ['name', 'version', 'source', 'checksum', 'dependencies']:
            if field in package:
                text += field + ' = ' + json.dumps(package[field]) + '\n'
    return text


def materialize(repository, output):
    output.mkdir(parents=True, exist_ok=False)
    dependencies = json.loads((ROOT / 'DEPENDENCIES.json').read_text())
    for record in dependencies['files']:
        raw = subprocess.check_output(['git', '-c', 'core.fsmonitor=false', '-C', str(repository), 'show', record['commit'] + ':' + record['path']])
        if hashlib.sha256(raw).hexdigest() != record['sha256']:
            raise ValueError('Source object changed: ' + record['path'])
        destination = output / record['destination']
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(raw)
    (output / '.cargo').mkdir()
    (output / '.cargo/config.toml').write_text(CONFIG)
    (output / 'Cargo.toml').write_text(MANIFEST)
    (output / 'Cargo.lock').write_text(seed_lock(dependencies['package_records']))
    shutil.copyfile(ROOT / 'inputs/driver.rs', output / 'driver.rs')


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--repository', required=True, type=Path)
    p.add_argument('--out', required=True, type=Path)
    a = p.parse_args()
    materialize(a.repository.resolve(), a.out.resolve())


if __name__ == '__main__':
    main()
