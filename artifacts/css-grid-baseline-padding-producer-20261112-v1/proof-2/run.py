import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


out = HERE / sys.argv[1]
assert out.parent == HERE and not out.exists()
out.mkdir()
lean = ROOT / 'artifacts/stylo-bloom-tools/lean-4.35.0-rc4-darwin_aarch64/bin/lean'
assert sha(lean) == 'd1d9c26a539f54fe839d2aa7760bf1ac1dd76a30b26e2c9684bebf2900038fcf'
process_path = ROOT / 'artifacts/css-exact-containing-block-candidate-20261112-v1/process.py'
for name, digest in json.loads((HERE / 'TARGET-FREEZE.json').read_text()).items():
    assert sha(HERE / name) == digest
assert (HERE / 'Proof.lean').read_text().startswith((HERE / 'Target.lean').read_text())
assert (HERE / 'Strength.lean').read_text().startswith((HERE / 'Proof.lean').read_text())
names = ['Target.lean', 'Proof.lean', 'Strength.lean', 'TARGET-FREEZE.json', 'run.py']
for name in names:
    (out / name).write_bytes((HERE / name).read_bytes())
(out / 'process.py').write_bytes(process_path.read_bytes())
inputs = {str(path): sha(path) for path in [lean, process_path, *[HERE / name for name in names]]}
(out / 'INPUTS.json').write_text(json.dumps(inputs, indent=2) + '\n')
spec = importlib.util.spec_from_file_location('owned_process', process_path)
process = importlib.util.module_from_spec(spec)
spec.loader.exec_module(process)
runner = process.Runner(out)
env = dict(os.environ)
env.pop('LEAN_PATH', None)
env.pop('LEAN_SRC_PATH', None)
record, log = runner.run([str(lean), str(out / 'Strength.lean')], ROOT, env, 'strength', timeout=45)
unchanged = all(sha(Path(path)) == digest for path, digest in inputs.items())
(out / 'RESULT.json').write_text(json.dumps(dict(exit=record['exit'], inputs_unchanged=unchanged,
    groups_absent=record['group_absent'], output_cache_created=False), indent=2) + '\n')
print(log)
sys.exit(record['exit'] if unchanged else 1)
