import ast
from collections import Counter
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import random
import struct
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = ROOT / 'artifacts/css-round-context-quotient-repair-v2'
MODES = ['Nearest', 'Up', 'Down', 'ToZero']


def units(bits):
    exponent, mantissa = (bits >> 23) & 255, bits & 0x7fffff
    assert exponent != 255
    value = mantissa if exponent == 0 else ((1 << 23) | mantissa) << (exponent - 1)
    return -value if bits >> 31 else value


def encode(value, negative_zero=False):
    sign = 0x80000000 if value < 0 or value == 0 and negative_zero else 0
    value = abs(value)
    if value < 1 << 23:
        return sign | value
    shift = value.bit_length() - 24
    q, remainder = divmod(value, 1 << shift)
    if shift and (remainder > 1 << (shift - 1) or remainder == 1 << (shift - 1) and q & 1):
        q += 1
    if q == 1 << 24:
        q >>= 1
        shift += 1
    exponent = shift + 1
    return sign | (0x7f800000 if exponent >= 255 else (exponent << 23) | (q - (1 << 23)))


def oracle(a, b):
    value, step = units(a), abs(units(b))
    quotient, rem = divmod(value, step)
    if rem == 0:
        return [a] * 4
    lower, upper = quotient * step, (quotient + 1) * step
    choices = [lower if rem < step - rem else upper, upper, lower, lower if value > 0 else upper]
    return [encode(x, value < 0) for x in choices]


def main():
    manifest = json.loads((SOURCE / 'FILES.json').read_text())
    assert hashlib.sha256((SOURCE / 'FILES.json').read_bytes()).hexdigest() == 'b371092fccf2e570f2a5577376d5cd5adfc559e1c28e1c7e6e493277837b2529'
    for name, digest in manifest.items():
        assert hashlib.sha256((SOURCE / name).read_bytes()).hexdigest() == digest
    definitions = ast.parse((SOURCE / 'check_helper.py').read_text())
    scope = {'Fraction': Fraction}
    selected = [node for node in definitions.body if isinstance(node, ast.FunctionDef) and node.name in ('rational', 'rounded_bits', 'oracle')]
    exec(compile(ast.Module(body=selected, type_ignores=[]), '<sealed Fraction oracle>', 'exec'), scope)
    rng = random.Random(14320261028)
    pairs = []
    batches = Counter()
    def add(label, a, b):
        if a & 0x7f800000 == 0x7f800000 or b & 0x7fffffff == 0 or b & 0x7f800000 == 0x7f800000:
            return
        pairs.append((a, b))
        batches[label] += 1
    for a in range(256):
        for b in range(1, 256):
            for sa, sb in ((0, 0), (0x80000000, 0), (0, 0x80000000), (0x80000000, 0x80000000)):
                add('exhaustive_low_subnormal_magnitudes_0_255_both_signs', a | sa, b | sb)
    mantissas = [(0, 1), (0x7fffff, 0x7ffffe), (0x400000, 0x2aaaab), (1, 0x7fffff)]
    for ea in range(255):
        for eb in range(255):
            for ma, mb in mantissas:
                a, b = (ea << 23) | ma, (eb << 23) | mb
                add('all_finite_exponent_pairs_selected_mantissas', a, b)
                add('all_finite_exponent_pairs_selected_mantissas', a | 0x80000000, b)
    for _ in range(100000):
        add('uniform_bit_patterns', rng.getrandbits(32), rng.getrandbits(32))
    for _ in range(2000):
        b = rng.randrange(1, 0x7f800000)
        for quotient in (1, 2, 3, 7, (1 << 23) - 1, 1 << 23, (1 << 24) - 1, 1 << 24, 1 << 29, 1 << 53):
            for center in (encode(units(b) * quotient), encode(units(b) * (2 * quotient + 1) // 2)):
                for delta in (-1, 0, 1):
                    a = center + delta
                    if 0 <= a < 0x7f800000:
                        add('near_multiple_and_half_step_boundaries', a, b)
                        add('near_multiple_and_half_step_boundaries', a | 0x80000000, b)
    for a in (0, 0x80000000, 1, 0x80000001, 0x007fffff, 0x00800000, 0x00800001, 0x7f7ffffe, 0x7f7fffff, 0xff7fffff):
        for b in (1, 2, 3, 0x007fffff, 0x00800000, 0x00800001, 0x3eaaaaab, 0x3f800000, 0x7f000000, 0x7f7fffff):
            add('explicit_transition_overflow_signed_zero', a, b)
    cross = random.Random(9143).sample(pairs, 2048)
    for a, b in cross:
        assert oracle(a, b) == [scope['oracle'](a, b, mode) for mode in MODES]
    source = (SOURCE / 'helper.rs').read_text()
    program = source[:source.index('fn main()')] + '''fn main() {
    use std::io::{self, Read, Write};
    let mut input = Vec::new(); io::stdin().read_to_end(&mut input).unwrap();
    let mut out = io::BufWriter::new(io::stdout().lock());
    for bytes in input.chunks_exact(8) {
        let a=f32::from_bits(u32::from_le_bytes(bytes[0..4].try_into().unwrap()));
        let b=f32::from_bits(u32::from_le_bytes(bytes[4..8].try_into().unwrap()));
        out.write_all(&(a % b.abs()).to_bits().to_le_bytes()).unwrap();
        for strategy in [RoundingStrategy::Nearest, RoundingStrategy::Up, RoundingStrategy::Down, RoundingStrategy::ToZero] {
            out.write_all(&old(a,b,strategy).unwrap().0.to_bits().to_le_bytes()).unwrap();
            out.write_all(&candidate(a,b,strategy).unwrap().0.to_bits().to_le_bytes()).unwrap();
        }
    }
}
'''
    (HERE / 'helper.rs').write_text(program)
    inputs = b''.join(struct.pack('<II', a, b) for a, b in pairs)
    with tempfile.TemporaryDirectory(prefix='round-independent-arithmetic-') as directory:
        binary = Path(directory) / 'helper'
        build = subprocess.run(['rustc', '--edition=2021', '-C', 'opt-level=2', str(HERE / 'helper.rs'), '-o', str(binary)], capture_output=True, check=True)
        execution = subprocess.run([str(binary)], input=inputs, capture_output=True, check=True)
    assert len(execution.stdout) == len(pairs) * 36
    counts = Counter()
    differences = []
    remainder_differences = []
    for (a, b), output in zip(pairs, struct.iter_unpack('<9I', execution.stdout)):
        value, step = units(a), abs(units(b))
        rem = abs(value) % step
        expected_rem = encode(-rem if value < 0 else rem, bool(a >> 31))
        if output[0] != expected_rem:
            remainder_differences.append([f'{a:08x}', f'{b:08x}', f'{output[0]:08x}', f'{expected_rem:08x}'])
        exact = oracle(a, b)
        counts['exact_ties'] += (abs(value) % step) * 2 == step
        counts['quotient_at_least_2pow53'] += abs(value) >= step * (1 << 53)
        counts['input_subnormal_pairs'] += 0 < (a & 0x7fffffff) < 0x800000 or (b & 0x7fffffff) < 0x800000
        for i, mode in enumerate(MODES):
            old, candidate = output[1 + 2 * i:3 + 2 * i]
            counts['old_mismatches'] += old != exact[i]
            counts['candidate_mismatches'] += candidate != exact[i]
            counts['oracle_negative_zero'] += exact[i] == 0x80000000
            counts['oracle_infinity'] += exact[i] & 0x7fffffff == 0x7f800000
            if candidate != exact[i] and len(differences) < 100:
                differences.append({'a': f'{a:08x}', 'b': f'{b:08x}', 'strategy': mode, 'old': f'{old:08x}', 'candidate': f'{candidate:08x}', 'exact': f'{exact[i]:08x}'})
    result = {'pairs': len(pairs), 'strategy_checks': 4 * len(pairs), 'batches': dict(batches), 'counts': dict(counts),
              'fraction_oracle_cross_checks': len(cross) * 4, 'candidate_examples': differences,
              'remainder_mismatches': len(remainder_differences), 'remainder_examples': remainder_differences[:10],
              'compiler': subprocess.check_output(['rustc', '--version'], text=True).strip(),
              'compile_exit': build.returncode, 'execution_exit': execution.returncode,
              'input_sha256': hashlib.sha256(inputs).hexdigest(), 'output_sha256': hashlib.sha256(execution.stdout).hexdigest(),
              'temporary_binary_removed': not binary.exists(), 'native_or_browser_compilation': False, 'exhaustive_binary32_claim': False}
    (HERE / 'RESULT.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2), flush=True)


if __name__ == '__main__':
    main()
