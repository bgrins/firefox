from pathlib import Path
import argparse
import hashlib
import json
import math
import struct
import subprocess
import tempfile

p = Path(__file__).resolve().parent
parser = argparse.ArgumentParser()
parser.add_argument('--output', required=True)
out = Path(parser.parse_args().output)
assert not out.exists()
out.mkdir()
refs = json.loads((p / 'REFERENCES.json').read_text())
root = p.parent.parent
assert all(hashlib.sha256((root / n).read_bytes()).hexdigest() == digest for n, digest in refs.items())
source = (root / 'artifacts/css-round-runtime-finite-comparison-data-v1/candidate/combined/servo/components/style/values/generics/calc.rs').read_text()
start = source.index('impl ModRemOp {')
assert source[start:source.index('/// The strategy', start)].rstrip() + '\n' == (p / 'ModRemOp.rs').read_text()
assert (p / 'ModRemOp.rs').read_text() in (p / 'helper.rs').read_text()
rows = []
guards = []
version = subprocess.run(['rustc', '--version'], capture_output=True, text=True, check=True).stdout.strip()
with tempfile.TemporaryDirectory(prefix='finite-mod-', dir='/private/tmp') as tmp:
    executable = Path(tmp) / 'helper'
    for opt in [0, 2]:
        compile = subprocess.run(['rustc', '--edition=2024', '-C', f'opt-level={opt}', '-C', 'overflow-checks=yes',
                                  str(p / 'helper.rs'), '-o', str(executable)], capture_output=True, text=True)
        (out / f'compile-{opt}.log').write_text(compile.stdout + compile.stderr)
        assert compile.returncode == 0
        run = subprocess.run([str(executable)], capture_output=True, text=True, check=True)
        (out / f'run-{opt}.log').write_text(run.stdout)
        current = []
        current_guards = []
        for line in run.stdout.splitlines():
            if line.startswith('guard '):
                _, name, bits = line.split()
                expected = dict(mod_negative_zero='80000000', mod_positive_zero='00000000',
                                rem_negative_zero='80000000', rem_positive_zero='00000000',
                                mod_same_inf='3f800000', mod_opposite_inf=None,
                                rem_positive_inf='bf800000', rem_negative_inf='3f800000')[name]
                assert bits == expected if expected is not None else math.isnan(struct.unpack('!f', bytes.fromhex(bits))[0])
                current_guards.append(dict(name=name, bits=bits, expected=expected))
                continue
            op, aa, bb, abits, bbits, resultbits, quotientbits = line.split()
            a, b = int(aa), int(bb)
            decode = lambda x: struct.unpack('!f', bytes.fromhex(x))[0]
            assert decode(abits) == a and decode(bbits) == b
            q = a // b if op == 'mod' else (abs(a) // abs(b)) * (1 if a * b >= 0 else -1)
            expected = a - b * q
            assert abs(expected) < abs(b)
            actual = decode(resultbits)
            current.append(dict(op=op, a=a, b=b, result_bits=resultbits,
                                quotient_bits=quotientbits, actual=actual, expected=expected,
                                same_numeric_value=actual == expected))
        assert len(current) == 40
        if rows:
            assert current == rows
            assert current_guards == guards
        rows = current
        guards = current_guards
        assert len(guards) == 8
        executable.unlink()
(out / 'ROWS.json').write_text(json.dumps(rows, indent=2) + '\n')
(out / 'GUARDS.json').write_text(json.dumps(guards, indent=2) + '\n')
bad = [r for r in rows if not r['same_numeric_value']]
assert len(bad) == 8 and all(abs(r['a']) == 33554432 and abs(r['b']) == 3 for r in bad)
(out / 'CHECK.json').write_text(json.dumps(dict(status='FINITE_BACKEND_SOURCE_PREDICTION_CONFIRMED',
    compiler=version, rows_per_optimization=40, optimizations=[0, 2], mismatches_per_optimization=len(bad),
    finite_controls_per_optimization=32, special_guards_per_optimization=8,
    exact_native_apply_body=True, oracle='integer floor/truncating quotient; exact integer inputs/results',
    temporary_executable_removed=True, scratch_removed=not Path(tmp).exists(), browser_executed=False,
    native_tree_modified=False, compiler_pipeline_refinement=False), indent=2) + '\n')
