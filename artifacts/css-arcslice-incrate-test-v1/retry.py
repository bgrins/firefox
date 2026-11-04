from pathlib import Path
import hashlib
import json
import os
import shutil
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OLD = ROOT / 'artifacts/stylo-bloom-tools/creusot-gate/matcher-dyn-capability-candidate/backend-v1/actual-context-v1/header-swap-defect-v1'
TC = OLD / 'rustup/toolchains/nightly-2026-09-17-aarch64-apple-darwin'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
sources = json.loads((HERE / 'SOURCES.json').read_text())
command = json.loads((HERE / 'COMMAND.json').read_text())
for name, digest in sources.items():
    assert sha(HERE / 'workspace' / name) == digest
env = dict(os.environ, RUSTUP_HOME=str(OLD / 'rustup'), CARGO_HOME=str(OLD / 'cargo-home'),
           CARGO_TARGET_DIR=str(HERE / 'target'), PATH=str(TC / 'bin') + ':/Users/bgrins/.cargo/bin:/usr/bin:/bin:/usr/sbin:/sbin')
with (HERE / 'cargo-test.log').open('w') as log:
    result = subprocess.run(command, cwd=HERE / 'workspace', env=env, stdout=log, stderr=subprocess.STDOUT, timeout=300)
for name, digest in sources.items():
    assert sha(HERE / 'workspace' / name) == digest
output = (HERE / 'cargo-test.log').read_text()
passed = result.returncode == 0 and 'test arc_slice::tests::empty_slices_preserve_element_layout ... ok' in output
if passed:
    shutil.rmtree(HERE / 'target')
    shutil.rmtree(HERE / 'vendor')
record = {'exit': result.returncode, 'named_regression_passed': passed,
          'actual_style_traits_cfg_test': passed, 'source_hashes_verified_after': True,
          'target_removed': not (HERE / 'target').exists(), 'vendor_copy_removed': not (HERE / 'vendor').exists(),
          'log_sha256': sha(HERE / 'cargo-test.log'), 'command': command}
(HERE / 'RESULT.json').write_text(json.dumps(record, indent=2) + '\n')
print(json.dumps(record), flush=True)
raise SystemExit(0 if passed else 1)
