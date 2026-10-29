import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess

HERE = Path(__file__).resolve().parent
CACHE = Path.home() / '.cargo/registry/src/index.crates.io-1949cf8c6b5b557f'
TOOLCHAIN = Path.home() / '.rustup/toolchains/stable-aarch64-apple-darwin/bin'
env = dict(os.environ, CARGO_HOME=str(HERE / 'cargo-home'), CARGO_NET_OFFLINE='true',
           RUSTUP_AUTO_INSTALL='0', RUSTC=str(TOOLCHAIN / 'rustc'))
record = HERE / 'CACHED-COPIES.json'
copied = json.loads(record.read_text()) if record.exists() else []
total = sum(entry['bytes'] for entry in copied)
first = max(int(p.stem.rsplit('-', 1)[1]) for p in HERE.glob('metadata-attempt-*.log')) + 1
for attempt in range(first, first + 12):
    command = [str(TOOLCHAIN / 'cargo'), 'metadata', '--offline', '--format-version', '1',
               '--no-default-features', '--features', 'servo', '--manifest-path', 'Cargo.toml']
    result = subprocess.run(command, cwd=HERE / 'baseline', env=env, capture_output=True)
    (HERE / f'metadata-attempt-{attempt}.json').write_bytes(result.stdout)
    (HERE / f'metadata-attempt-{attempt}.log').write_bytes(result.stderr)
    if result.returncode == 0:
        print('Resolved', attempt)
        break
    error = result.stderr.decode()
    match = re.search(r'no matching package named `([^`]+)`|requirement `([^ =]+) =', error)
    if not match:
        print(error)
        break
    name = match.group(1) or match.group(2)
    choices = [p for p in CACHE.glob(name + '-*')
               if (p / 'Cargo.toml').is_file() and not (HERE / 'vendor' / p.name).exists()]
    if not choices:
        print(error)
        break
    for source in choices:
        size = sum(p.stat().st_size for p in source.rglob('*') if p.is_file())
        assert size < 3000000 and total + size < 15000000
        total += size
        dest = HERE / 'vendor' / source.name
        shutil.copytree(source, dest)
        files = {str(p.relative_to(dest)): hashlib.sha256(p.read_bytes()).hexdigest()
                 for p in dest.rglob('*') if p.is_file() and p.name != '.cargo-checksum.json'}
        archive = Path.home() / '.cargo/registry/cache/index.crates.io-1949cf8c6b5b557f' / (source.name + '.crate')
        package = hashlib.sha256(archive.read_bytes()).hexdigest() if archive.is_file() else None
        (dest / '.cargo-checksum.json').write_text(json.dumps({'files': files, 'package': package}, sort_keys=True))
        copied.append({'source': str(source), 'destination': str(dest), 'bytes': size,
                       'package_sha256': package, 'files': files})
        record.write_text(json.dumps(copied, indent=2, sort_keys=True) + '\n')
        print('Copied cached', source.name, size)
(HERE / 'CACHED-COPIES.json').write_text(json.dumps(copied, indent=2, sort_keys=True) + '\n')
