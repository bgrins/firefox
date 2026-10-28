import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
from fractions import Fraction

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
LEAN = ROOT / 'artifacts/stylo-bloom-tools/lean-4.35.0-rc4-darwin_aarch64/bin/lean'
PINS = {
    'artifacts/css-round-context-quotient-repair-v2/helper.rs': 'da773212cbaaec7277ce1b6effa8c44837b2ebcc28579827f2227de08b27b1b7',
    'artifacts/css-round-context-quotient-model-v1/Rounding.lean': 'e8623e03835a946a09d07ff69685fb1446721acdd807a4a756e07483d755bd46',
    str(LEAN.relative_to(ROOT)): 'd1d9c26a539f54fe839d2aa7760bf1ac1dd76a30b26e2c9684bebf2900038fcf',
}
assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
assert len(sys.argv) == 2
output = Path(sys.argv[1]).resolve()
output.mkdir()
for name, digest in PINS.items():
    assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == digest
assert Fraction('18446744073709551616') == 2 ** 64
assert Fraction('5.42101086242752217003726400434970855712890625e-20') == Fraction(1, 2 ** 64)
assert Fraction('36893488147419103232') == 2 ** 65
results = {}
with tempfile.TemporaryDirectory(prefix='round-overflow-witness-', dir='/private/tmp') as folder:
    work = Path(folder)
    shutil.copyfile(ROOT / 'artifacts/css-round-context-quotient-model-v1/Rounding.lean', work / 'Rounding.lean')
    for name in ['Overflow.lean', 'FalseFinite.lean']:
        shutil.copyfile(HERE / name, work / name)
    env = dict(os.environ, LEAN_PATH=str(work))
    for name in ['Rounding', 'Overflow', 'FalseFinite']:
        command = [str(LEAN), name + '.lean']
        if name != 'FalseFinite':
            command.extend(['-o', name + '.olean'])
        result = subprocess.run(command, cwd=work, env=env, capture_output=True, text=True)
        log = result.stdout + result.stderr
        (output / (name + '.log')).write_text(log)
        results[name] = result.returncode
        if name == 'FalseFinite':
            assert result.returncode != 0 and 'is false' in log, log
        else:
            assert result.returncode == 0, log
    audit = (output / 'Overflow.log').read_text()
    assert audit.count('RoundOverflowWitness.') == 4
    assert 'sorryAx' not in audit and 'Lean.ofReduceBool' not in audit
    for group in re.findall(r'depends on axioms: \[(.*?)\]', audit):
        assert set(group.split(', ')) <= {'propext', 'Classical.choice', 'Quot.sound'}
    compiler = subprocess.check_output(['rustc', '--version'], text=True).strip()
    helper = ROOT / 'artifacts/css-round-context-quotient-repair-v2/helper.rs'
    command = ['rustc', '-O', str(helper), '-o', str(work / 'helper')]
    result = subprocess.run(command, capture_output=True, text=True)
    (output / 'compile.log').write_text(result.stdout + result.stderr)
    assert result.returncode == 0
    result = subprocess.run([str(work / 'helper')], input='5f800000 1f800000\ndf800000 1f800000\n', capture_output=True, text=True)
    (output / 'scalar.log').write_text(result.stdout + result.stderr)
    assert result.returncode == 0
    rows = [line.split() for line in result.stdout.splitlines()]
    assert rows == [['7f800000', '5f800000']] * 4 + [['ff800000', 'df800000']] * 4, rows
    scratch = str(work)
assert not Path(scratch).exists()
(output / 'CHECK.json').write_text(json.dumps({
    'pins': PINS,
    'lean_results': results,
    'scalar_rows': rows,
    'compiler': compiler,
    'scratch_removed': True,
    'browser_execution': False,
    'native_refinement': False,
    'canonical_coverage_increment': 0,
}, indent=2) + '\n')
print(json.dumps({'scalar_cases': len(rows), 'lean_passed': True, 'false_control_rejected': True, 'scratch_removed': True}))
