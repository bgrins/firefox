import argparse
import hashlib
import json
import os
from pathlib import Path
import runpy
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n')


def main():
    assert sys.flags.isolated and not sys.flags.optimize
    parser = argparse.ArgumentParser()
    parser.add_argument('--repository', required=True, type=Path)
    parser.add_argument('--out', required=True, type=Path)
    args = parser.parse_args()
    if (ROOT / 'SOURCE-ONLY.json').exists():
        for name, expected in json.loads((ROOT / 'SOURCE-ONLY.json').read_text()).items():
            assert sha(ROOT / name) == expected, name
    output = args.out.resolve()
    output.mkdir(parents=True, exist_ok=False)
    prepare = runpy.run_path(str(ROOT / 'prepare.py'))
    audit = runpy.run_path(str(ROOT / 'audit.py'))
    tools = json.loads((ROOT / 'TOOLCHAIN.json').read_text())
    deps = json.loads((ROOT / 'DEPENDENCIES.json').read_text())
    cargo, rustc = Path(tools['cargo']), Path(tools['rustc'])
    assert sha(cargo) == tools['cargo_sha256'] and sha(rustc) == tools['rustc_sha256']
    commands = []
    with tempfile.TemporaryDirectory(prefix='css-number-feature-resolution-') as directory:
        scratch = Path(directory)
        workspace = scratch / 'workspace'
        prepare['materialize'](args.repository.resolve(), workspace)
        (output / 'seed-Cargo.lock').write_bytes((workspace / 'Cargo.lock').read_bytes())
        env = {k: v for k, v in os.environ.items() if not k.startswith(('CARGO_', 'RUST'))}
        env.update(CARGO_HOME=str(scratch / 'cargo-home'), CARGO_TARGET_DIR=str(scratch / 'target'),
            CARGO_NET_OFFLINE='true', RUSTC=str(rustc), PYTHONDONTWRITEBYTECODE='1')
        feature_records = []
        for label, mode in [('resolve', '--offline'), ('frozen', '--frozen')]:
            argv = [str(cargo), 'metadata', mode, '--format-version=1', '--filter-platform=' + audit['HOST']]
            stdout, stderr = output / (label + '.stdout'), output / (label + '.stderr')
            with stdout.open('wb') as out, stderr.open('wb') as err:
                result = subprocess.run(argv, cwd=workspace, env=env, stdout=out, stderr=err)
            commands.append(dict(command=argv, label=label, exit=result.returncode,
                stdout_sha256=sha(stdout), stderr_sha256=sha(stderr)))
            save(output / 'COMMANDS.json', commands)
            assert result.returncode == 0, label
            feature_records.append(audit['metadata'](json.loads(stdout.read_text()), workspace, deps['package_records']))
            if label == 'resolve':
                lock_hash = sha(workspace / 'Cargo.lock')
                (output / 'resolved-Cargo.lock').write_bytes((workspace / 'Cargo.lock').read_bytes())
            else:
                assert sha(workspace / 'Cargo.lock') == lock_hash
        assert feature_records[0] == feature_records[1]
        save(output / 'FEATURES.json', feature_records[1])
        audit['vendor'](workspace, deps['files'], (ROOT / 'inputs/tokenizer.rs').read_bytes(),
            (workspace / 'vendor/cssparser/.cargo-checksum.json').read_bytes())
        assert not (scratch / 'target').exists()
    save(output / 'REPORT.json', dict(status='PASS', offline_metadata_then_frozen_metadata=True,
        features=feature_records[1]['cssparser'], seed_lock_sha256=sha(output / 'seed-Cargo.lock'),
        resolved_lock_sha256=lock_hash, source_files_unchanged=len(deps['files']),
        native_builds=0, native_runs=0, target_directory_created=False, temporary_workspace_removed=True))


if __name__ == '__main__':
    main()
