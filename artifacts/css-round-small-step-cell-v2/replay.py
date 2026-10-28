import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
LEAN = ROOT / 'artifacts/stylo-bloom-tools/lean-4.35.0-rc4-darwin_aarch64/bin/lean'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
parser = argparse.ArgumentParser()
parser.add_argument('--output', type=Path, required=True)
output = parser.parse_args().output
assert not output.exists()
assert sha(LEAN) == 'd1d9c26a539f54fe839d2aa7760bf1ac1dd76a30b26e2c9684bebf2900038fcf'
output.mkdir()
source = HERE / 'SmallStep.lean'
env = dict(os.environ, LEAN_NUM_THREADS='2')
run = subprocess.run([str(LEAN), str(source)], cwd=ROOT, env=env,
                     capture_output=True, text=True, timeout=55)
log = run.stdout + run.stderr
(output / 'lean.log').write_text(log)
assert run.returncode == 0 and 'sorryAx' not in log and 'warning:' not in log
assert log.count('depends on axioms:') == 3
negative = {
    'midpoint_unique': 'example : RoundSmallStep.distance 4 3 < RoundSmallStep.distance 2 3 := by decide\n',
    'symmetric_binade_radius': 'example : RoundSmallStep.distance 8 5 < RoundSmallStep.distance 4 5 := by decide\n',
    'ignore_reconstruction_error': 'example : RoundSmallStep.distance 17 11 < RoundSmallStep.distance 9 11 := by decide\n',
}
failures = {}
for name, claim in negative.items():
    with tempfile.TemporaryDirectory(prefix='round-cell-negative-') as temporary:
        file = Path(temporary) / (name + '.lean')
        file.write_text(source.read_text() + '\n' + claim)
        bad = subprocess.run([str(LEAN), str(file)], cwd=ROOT, env=env,
                             capture_output=True, text=True, timeout=55)
        result = bad.stdout + bad.stderr
        (output / (name + '.log')).write_text(result)
        assert bad.returncode != 0 and 'error:' in result and 'sorryAx' not in result
    assert not file.exists()
    failures[name] = {'claim': claim, 'exit': bad.returncode, 'owned_source_removed': True}
receipt = {'status': 'PASS_CONDITIONAL_SMALL_STEP_LEMMAS', 'exit': run.returncode,
           'lean_sha256': sha(LEAN), 'source_sha256': sha(source), 'log_sha256': sha(output / 'lean.log'),
           'threads': 2, 'timeout_per_process': 55, 'named_support_results': 3,
           'negative_controls': failures, 'canonical_registrations': 0,
           'native_or_index_or_browser_or_canonical_changes': False,
           'universal_f32_to_f64_to_f32_refinement': False, 'compiler_products_created': False}
(output / 'RESULT.json').write_text(json.dumps(receipt, indent=2) + '\n')
print(json.dumps(receipt, indent=2))
