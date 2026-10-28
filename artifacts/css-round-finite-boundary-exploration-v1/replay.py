import argparse
import hashlib
import json
import os
from pathlib import Path
import random
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'artifacts/css-round-context-quotient-repair-v1/helper.rs'
MODES = ('Nearest', 'Up', 'Down', 'ToZero')


def units(bits):
    exponent = (bits >> 23) & 255
    assert exponent != 255
    fraction = bits & 0x7fffff
    value = fraction if exponent == 0 else ((1 << 23) + fraction) << (exponent - 1)
    return -value if bits >> 31 else value


def encode(value, negative_zero=False):
    sign = 0x80000000 if value < 0 or value == 0 and negative_zero else 0
    value = abs(value)
    if value < 1 << 23:
        return sign | value
    shift = max(0, value.bit_length() - 24)
    mantissa, remainder = divmod(value, 1 << shift)
    if shift and (remainder * 2 > 1 << shift or remainder * 2 == 1 << shift and mantissa & 1):
        mantissa += 1
    if mantissa == 1 << 24:
        mantissa >>= 1
        shift += 1
    exponent = shift + 1
    if exponent >= 255:
        return sign | 0x7f800000
    return sign | exponent << 23 | (mantissa - (1 << 23))


def reference(a_bits, b_bits):
    a, b = units(a_bits), abs(units(b_bits))
    assert b > 0
    quotient, remainder = divmod(a, b)
    if remainder == 0:
        return (a_bits,) * 4
    lower, upper = quotient * b, (quotient + 1) * b
    selected = (lower if a - lower < upper - a else upper,
                upper, lower, lower if a > 0 else upper)
    return tuple(encode(x, x == 0 and a < 0) for x in selected)


def cases():
    rng = random.Random(0x524f554e44)
    for ea in range(255):
        for eb in range(255):
            for profile in range(4):
                fa, fb = ((0, 1), (0x7fffff, 0x7fffff),
                          (0x400000, 0x2aaaab), (rng.randrange(1 << 23), rng.randrange(1 << 23)))[profile]
                a, b = ea << 23 | fa, eb << 23 | fb
                if not b:
                    b = 1
                sign = ((ea + eb + profile) & 1) << 31
                yield 'exponent_cross_product', a | sign, b | (profile % 2 << 31)
    for _ in range(100000):
        yield 'random_finite', rng.randrange(0x7f800000) | rng.randrange(2) << 31, rng.randrange(1, 0x7f800000) | rng.randrange(2) << 31
    for exponent in range(255):
        for fraction in (0, 1, 0x3fffff, 0x400000, 0x7ffffe, 0x7fffff):
            center = exponent << 23 | fraction
            for a in range(max(0, center - 2), min(0x7f800000, center + 3)):
                for step_exp in (0, max(0, exponent - 25), max(0, exponent - 24), max(0, exponent - 23), min(254, exponent + 1)):
                    for delta in (-1, 0, 1):
                        b = min(0x7f7fffff, max(1, (step_exp << 23) + delta))
                        for sign in (0, 0x80000000):
                            yield 'binade_and_half_ulp', a | sign, b
    for bit in range(277):
        for numerator in (1, 3, 5, 7, 0xffffff):
            b = numerator << bit
            b_bits = encode(b)
            if b_bits >= 0x7f800000 or units(b_bits) != b:
                continue
            for q in (0, 1, 2, 3, 0x7ffffe):
                if b % 2:
                    continue
                midpoint = q * b + b // 2
                a_bits = encode(midpoint)
                if a_bits >= 0x7f800000 or units(a_bits) != midpoint:
                    continue
                for neighbor in (-1, 0, 1):
                    a = a_bits + neighbor
                    if not 0 <= a < 0x7f800000:
                        continue
                    for sign in (0, 0x80000000):
                        yield 'exact_tie_and_neighbors', a | sign, b_bits


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    assert not args.output.exists()
    args.output.mkdir()
    source = SOURCE.read_bytes()
    assert hashlib.sha256(source).hexdigest() == '400590490cabfdef97bafc2d57b15d3b995a3d8fc254ca4b759abfecccecbb6d'
    prefix = source.decode().split('fn main() {')[0]
    program = prefix + '''fn main() {
    use std::io::{self, Read, Write};
    let mut input = String::new(); io::stdin().read_to_string(&mut input).unwrap();
    let stdout = io::stdout(); let mut out = io::BufWriter::new(stdout.lock());
    for line in input.lines() {
        let mut words = line.split_whitespace();
        let a = f32::from_bits(u32::from_str_radix(words.next().unwrap(),16).unwrap());
        let b = f32::from_bits(u32::from_str_radix(words.next().unwrap(),16).unwrap());
        write!(out, "{:08x}", (a % b.abs()).to_bits()).unwrap();
        for strategy in [RoundingStrategy::Nearest, RoundingStrategy::Up, RoundingStrategy::Down, RoundingStrategy::ToZero] {
            write!(out, " {:08x}", candidate(a,b,strategy).unwrap().0.to_bits()).unwrap();
        }
        writeln!(out).unwrap();
    }
}
'''
    (args.output / 'helper.rs').write_text(program)
    inputs = list(cases())
    input_text = ''.join(f'{a:08x} {b:08x}\n' for _, a, b in inputs)
    with tempfile.TemporaryDirectory(prefix='round-finite-boundary-') as temporary:
        executable = Path(temporary) / 'helper'
        command = ['rustc', '--edition=2021', '-C', 'opt-level=0', '-C', 'overflow-checks=yes', str(args.output / 'helper.rs'), '-o', str(executable)]
        build = subprocess.run(command, capture_output=True, text=True, timeout=55)
        (args.output / 'build.log').write_text(build.stdout + build.stderr)
        assert build.returncode == 0
        run = subprocess.run([str(executable)], input=input_text, capture_output=True, text=True, timeout=55)
        assert run.returncode == 0 and not run.stderr
    lines = run.stdout.splitlines()
    assert len(lines) == len(inputs)
    counts, differences, remainder_differences = {}, [], []
    for (family, a, b), line in zip(inputs, lines):
        counts[family] = counts.get(family, 0) + 1
        remainder, *actual = [int(word, 16) for word in line.split()]
        expected = reference(a, b)
        exact_remainder = abs(units(a)) % abs(units(b))
        expected_remainder = encode(-exact_remainder if a >> 31 else exact_remainder, bool(a >> 31))
        if remainder != expected_remainder:
            remainder_differences.append({'family': family, 'a': f'{a:08x}', 'b': f'{b:08x}', 'actual': f'{remainder:08x}', 'expected': f'{expected_remainder:08x}'})
        for mode, got, want in zip(MODES, actual, expected):
            if got != want:
                differences.append({'family': family, 'a': f'{a:08x}', 'b': f'{b:08x}', 'mode': mode, 'actual': f'{got:08x}', 'expected': f'{want:08x}'})
    receipt = {'compiler': subprocess.run(['rustc', '--version'], capture_output=True, text=True, check=True).stdout.strip(), 'build_exit': build.returncode, 'run_exit': run.returncode, 'pairs': len(inputs), 'checks': len(inputs) * 4, 'families': counts, 'candidate_difference_count': len(differences), 'candidate_differences': differences[:100], 'remainder_difference_count': len(remainder_differences), 'remainder_differences': remainder_differences[:100], 'input_sha256': hashlib.sha256(input_text.encode()).hexdigest(), 'output_sha256': hashlib.sha256(run.stdout.encode()).hexdigest(), 'helper_sha256': hashlib.sha256(program.encode()).hexdigest(), 'products_removed': not executable.exists(), 'universal_proof': False}
    (args.output / 'RESULT.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(receipt, indent=2))


if __name__ == '__main__':
    main()
