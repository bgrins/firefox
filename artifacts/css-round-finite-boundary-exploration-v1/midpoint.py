import hashlib
import importlib.util
import json
from pathlib import Path
import random
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('boundary', HERE / 'replay.py')
model = importlib.util.module_from_spec(spec)
spec.loader.exec_module(model)
rng = random.Random(0x4d4944504f494e54)
mantissas = [0x800001, 0xaaaaab, 0xffffff] + [rng.randrange(0x800000, 0x1000000) | 1 for _ in range(125)]
pairs, products = set(), set()
for m in mantissas:
    for shift in range(1, 27):
        modulus = 1 << shift
        inverse = pow(m, -1, modulus)
        for delta in (-2, -1, 0, 1, 2):
            for cycle in (0, 1, 2):
                q = ((modulus // 2 + delta) * inverse) % modulus + cycle * modulus
                product = q * m
                if product.bit_length() - 24 != shift:
                    continue
                if product % modulus != modulus // 2 + delta:
                    continue
                for exponent in (1, 2, 24, 64, 126, 200, 230):
                    b = exponent << 23 | (m - (1 << 23))
                    exact = product << (exponent - 1)
                    projected = model.encode(exact)
                    if projected >= 0x7f800000:
                        continue
                    products.add((b, q, delta))
                    for offset in (-1, 0, 1):
                        a = projected + offset
                        if 0 <= a < 0x7f800000:
                            for sign in (0, 0x80000000):
                                pairs.add((a | sign, b))
pairs = sorted(pairs)
input_text = ''.join(f'{a:08x} {b:08x}\n' for a, b in pairs)
helper = HERE / 'validation/helper.rs'
receipt = json.loads((HERE / 'validation/RESULT.json').read_text())
assert hashlib.sha256(helper.read_bytes()).hexdigest() == receipt['helper_sha256']
with tempfile.TemporaryDirectory(prefix='round-midpoint-') as temporary:
    binary = Path(temporary) / 'helper'
    build = subprocess.run(['rustc', '--edition=2021', '-C', 'opt-level=0', '-C', 'overflow-checks=yes', str(helper), '-o', str(binary)], capture_output=True, text=True, timeout=55)
    assert build.returncode == 0
    run = subprocess.run([str(binary)], input=input_text, capture_output=True, text=True, timeout=55)
    assert run.returncode == 0 and not run.stderr
lines = run.stdout.splitlines()
assert len(lines) == len(pairs)
differences, remainder_differences = [], 0
for (a, b), line in zip(pairs, lines):
    remainder, *actual = [int(word, 16) for word in line.split()]
    expected = model.reference(a, b)
    r = abs(model.units(a)) % model.units(b)
    wanted_r = model.encode(-r if a >> 31 else r, bool(a >> 31))
    remainder_differences += remainder != wanted_r
    for mode, got, wanted in zip(model.MODES, actual, expected):
        if got != wanted:
            differences.append({'a': f'{a:08x}', 'b': f'{b:08x}', 'mode': mode, 'actual': f'{got:08x}', 'expected': f'{wanted:08x}'})
print(json.dumps({'construction': 'Odd 24-bit step mantissa inversion modulo 2^shift; exact q*step significand lies at a binary32 midpoint or one/two product-grid units beside it. Adjacent input floats and both signs.', 'constructed_products': len(products), 'unique_pairs': len(pairs), 'checks': len(pairs) * 4, 'candidate_difference_count': len(differences), 'candidate_differences': differences[:100], 'remainder_differences': remainder_differences, 'build_exit': build.returncode, 'run_exit': run.returncode, 'products_removed': not binary.exists(), 'input_sha256': hashlib.sha256(input_text.encode()).hexdigest(), 'output_sha256': hashlib.sha256(run.stdout.encode()).hexdigest(), 'universal_proof': False}, indent=2))
