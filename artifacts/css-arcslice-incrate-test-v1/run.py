from pathlib import Path
import hashlib
import json
import os
import shutil
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE = ROOT / 'artifacts/css-arcslice-empty-layout-validation-v1/current'
DELIVERY = ROOT / 'artifacts/css-arcslice-empty-layout-fix-v1'
PREVIOUS = ROOT / 'artifacts/css-arcslice-empty-layout-unit-check-v1'
OLD = ROOT / 'artifacts/stylo-bloom-tools/creusot-gate/matcher-dyn-capability-candidate/backend-v1/actual-context-v1/header-swap-defect-v1'
TC = OLD / 'rustup/toolchains/nightly-2026-09-17-aarch64-apple-darwin'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
workspace = HERE / 'workspace'
target = HERE / 'target'
vendor_path = HERE / 'vendor'
assert not workspace.exists() and not target.exists() and not vendor_path.exists()
shutil.copytree(BASE, workspace)
roles = json.loads((DELIVERY / 'DELIVERY-ROLES.json').read_text())['current']
for name, role in roles.items():
    if name.endswith('.rs'):
        source = ROOT / role['candidate_capture']
        assert sha(source) == role['candidate_sha256']
        shutil.copyfile(source, workspace / name)
source_hashes = {str(p.relative_to(workspace)): sha(p) for p in workspace.rglob('*') if p.is_file() and p.name != 'Cargo.lock'}
(HERE / 'SOURCES.json').write_text(json.dumps(source_hashes, indent=2) + '\n')
vendor = json.loads((PREVIOUS / 'VENDOR.json').read_text())
for folder, row in vendor.items():
    for name, digest in row['files'].items():
        assert sha(ROOT / folder / name) == digest
    destination = vendor_path / Path(folder).name
    shutil.copytree(ROOT / folder, destination)
    checksum = json.loads((destination / '.cargo-checksum.json').read_text())
    checksum['files'] = {str(p.relative_to(destination)): sha(p) for p in destination.rglob('*') if p.is_file() and p.name != '.cargo-checksum.json'}
    (destination / '.cargo-checksum.json').write_text(json.dumps(checksum))
    assert sha(destination / '.cargo-checksum.json') == row['temporary_checksum_sha256']
env = dict(os.environ, RUSTUP_HOME=str(OLD / 'rustup'), CARGO_HOME=str(OLD / 'cargo-home'),
           CARGO_TARGET_DIR=str(target), PATH=str(TC / 'bin') + ':/Users/bgrins/.cargo/bin:/usr/bin:/bin:/usr/sbin:/sbin')
command = [str(TC / 'bin/cargo'), 'test', '--offline', '-j', '2', '--manifest-path',
           str(workspace / 'Cargo.toml'), '-p', 'style_traits', '--lib',
           '--config', 'source.crates-io.replace-with="vendored-sources"',
           '--config', 'source.vendored-sources.directory=' + json.dumps(str(vendor_path)),
           '--', '--nocapture', '--test-threads=1']
(HERE / 'COMMAND.json').write_text(json.dumps(command, indent=2) + '\n')
with (HERE / 'cargo-test.log').open('w') as log:
    result = subprocess.run(command, cwd=workspace, env=env, stdout=log, stderr=subprocess.STDOUT, timeout=300)
for name, digest in source_hashes.items():
    assert sha(workspace / name) == digest
for folder, row in vendor.items():
    for name, digest in row['files'].items():
        assert sha(ROOT / folder / name) == digest
output = (HERE / 'cargo-test.log').read_text()
passed = result.returncode == 0 and 'test arc_slice::tests::empty_slices_preserve_element_layout ... ok' in output
if passed:
    shutil.rmtree(target)
    shutil.rmtree(vendor_path)
record = {'exit': result.returncode, 'named_regression_passed': passed,
          'actual_style_traits_cfg_test': passed, 'source_hashes_verified_after': True,
          'original_vendor_hashes_verified_after': True, 'target_removed': not target.exists(),
          'vendor_copy_removed': not vendor_path.exists(), 'log_sha256': sha(HERE / 'cargo-test.log'),
          'command': command}
(HERE / 'RESULT.json').write_text(json.dumps(record, indent=2) + '\n')
print(json.dumps(record), flush=True)
raise SystemExit(0 if passed else 1)
