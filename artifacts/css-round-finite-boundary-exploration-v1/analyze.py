import hashlib
import importlib.util
import json
from pathlib import Path
from fractions import Fraction

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('boundary', HERE / 'replay.py')
model = importlib.util.module_from_spec(spec)
spec.loader.exec_module(model)


def round53(value):
    sign = -1 if value < 0 else 1
    value = abs(value)
    shift = max(0, value.bit_length() - 53)
    q, r = divmod(value, 1 << shift)
    if shift and (2 * r > 1 << shift or 2 * r == 1 << shift and q & 1):
        q += 1
    return sign * (q << shift)


def binary_search_projection(value, negative_zero=False):
    sign = 0x80000000 if value < 0 or value == 0 and negative_zero else 0
    value = abs(value)
    maximum = model.units(0x7f7fffff)
    if value >= maximum + (1 << 252):
        return sign | 0x7f800000
    if value >= maximum:
        return sign | 0x7f7fffff
    low, high = 0, 0x7f7fffff
    while low + 1 < high:
        middle = (low + high) // 2
        if model.units(middle) <= value:
            low = middle
        else:
            high = middle
    dl, dh = value - model.units(low), model.units(high) - value
    return sign | (low if dl < dh or dl == dh and low % 2 == 0 else high)


counts = {'pairs': 0, 'nonzero_remainders': 0, 'inexact_reconstruction_pairs': 0,
          'nearest_choice_disagreements': 0, 'projected_model_differences': 0,
          'independent_projection_checks': 0, 'fraction_bounds_checks': 0}
examples = {}
model_output = hashlib.sha256()
for index, (family, ab, bb) in enumerate(model.cases()):
    counts['pairs'] += 1
    a, b = model.units(ab), abs(model.units(bb))
    remainder = abs(a) % b
    r = -remainder if a < 0 else remainder
    expected = model.reference(ab, bb)
    if remainder == 0:
        actual = (ab,) * 4
    else:
        counts['nonzero_remainders'] += 1
        exact_l, exact_u = (a // b) * b, (a // b + 1) * b
        toward_zero = round53(a - r)
        l, u = (round53(toward_zero - b), toward_zero) if a < 0 else (toward_zero, round53(toward_zero + b))
        nearest = l if round53(a - l) < round53(u - a) else u
        tozero = l if abs(l) < abs(u) else u
        selected = (nearest, u, l, tozero)
        actual = tuple(model.encode(x, x == 0 and a < 0) for x in selected)
        if (l, u) != (exact_l, exact_u):
            counts['inexact_reconstruction_pairs'] += 1
            examples.setdefault('inexact_reconstruction', {'a_bits': f'{ab:08x}', 'b_bits': f'{bb:08x}', 'exact_lower_units': str(exact_l), 'exact_upper_units': str(exact_u), 'binary64_lower_units': str(l), 'binary64_upper_units': str(u), 'actual_bits': [f'{x:08x}' for x in actual], 'expected_bits': [f'{x:08x}' for x in expected]})
        native_selects_lower = round53(a - l) < round53(u - a)
        exact_selects_lower = a - exact_l < exact_u - a
        if native_selects_lower != exact_selects_lower:
            counts['nearest_choice_disagreements'] += 1
            examples.setdefault('nearest_choice_disagreement', {'a_bits': f'{ab:08x}', 'b_bits': f'{bb:08x}', 'binary64_selects_lower': native_selects_lower, 'exact_selects_lower': exact_selects_lower, 'lower_projected': f'{model.encode(exact_l):08x}', 'upper_projected': f'{model.encode(exact_u):08x}', 'actual': f'{actual[0]:08x}', 'expected': f'{expected[0]:08x}'})
        if index % 509 == 0:
            rational_a, rational_b = Fraction(a, 1 << 149), Fraction(b, 1 << 149)
            quotient = rational_a / rational_b
            floor = quotient.numerator // quotient.denominator
            assert Fraction(exact_l, 1 << 149) == floor * rational_b
            assert Fraction(exact_u, 1 << 149) == (floor + 1) * rational_b
            counts['fraction_bounds_checks'] += 1
            for x, got in zip(selected, actual):
                assert binary_search_projection(x, x == 0 and a < 0) == got
                counts['independent_projection_checks'] += 1
    counts['projected_model_differences'] += sum(x != y for x, y in zip(actual, expected))
    rb = model.encode(r, bool(ab >> 31))
    model_output.update((' '.join(f'{x:08x}' for x in (rb, *actual)) + '\n').encode())
receipt = json.loads((HERE / 'validation/RESULT.json').read_text())
assert counts['pairs'] == receipt['pairs']
assert model_output.hexdigest() == receipt['output_sha256']
assert counts['projected_model_differences'] == 0
result = {'counts': counts, 'examples': examples,
          'simulated_native_output_sha256': model_output.hexdigest(),
          'matches_complete_native_output_digest': True,
          'universal_proof': False,
          'simulation_scope': 'integer-grid nearest-even binary64 operations; finite inputs and nonzero finite step; all relevant magnitudes are normal binary64 and far below overflow'}
print(json.dumps(result, indent=2))
