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
parser = argparse.ArgumentParser()
parser.add_argument('--output', type=Path, required=True)
args = parser.parse_args()
assert not args.output.exists()
args.output.mkdir()
env = dict(os.environ, LEAN_NUM_THREADS='2')
source = HERE / 'RemainderBridge.lean'
command = [str(LEAN), str(source)]
run = subprocess.run(command, cwd=ROOT, env=env, capture_output=True, text=True, timeout=55)
(args.output / 'lean.log').write_text(run.stdout + run.stderr)
assert run.returncode == 0 and 'sorryAx' not in run.stdout and 'warning:' not in run.stdout
assert run.stdout.count('depends on axioms:') == 6
negative = {
    'wrong_remainder_sign': 'example : RoundRemainder.lower (-1) 2 1 < -1 ∧ -1 < RoundRemainder.upper (-1) 2 1 := by decide\n',
    'unbounded_remainder': 'example : RoundRemainder.lower 3 2 3 < 3 ∧ 3 < RoundRemainder.upper 3 2 3 := by decide\n',
    'lower_tie': 'example : RoundRemainder.nearest 3 2 4 = 2 := by decide\n',
}
receipts = {}
for name, claim in negative.items():
    with tempfile.TemporaryDirectory(prefix='round-remainder-negative-') as temporary:
        path = Path(temporary) / (name + '.lean')
        path.write_text(source.read_text() + '\n' + claim)
        bad = subprocess.run([str(LEAN), str(path)], cwd=ROOT, env=env,
                             capture_output=True, text=True, timeout=55)
        (args.output / (name + '.log')).write_text(bad.stdout + bad.stderr)
        assert bad.returncode != 0 and 'error:' in bad.stdout and 'sorryAx' not in bad.stdout
    assert not path.exists()
    receipts[name] = {'claim': claim, 'exit': bad.returncode, 'owned_source_removed': True}
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
result = {'command': command, 'exit': run.returncode, 'threads': 2,
          'timeout_seconds_per_command': 55, 'lean_sha256': sha(LEAN),
          'lean_version': subprocess.run([str(LEAN), '--version'], capture_output=True, text=True, check=True).stdout.strip(),
          'source_sha256': sha(source), 'log_sha256': sha(args.output / 'lean.log'),
          'named_support_results': 6, 'algorithm_results': 4, 'rational_transfer_support_results': 2,
          'new_canonical_registrations': 0, 'negative_controls': receipts,
          'native_browser_index_or_canonical_changes': False, 'new_targets': False}
(args.output / 'RESULT.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
