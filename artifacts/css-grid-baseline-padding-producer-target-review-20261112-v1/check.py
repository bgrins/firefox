from pathlib import Path
import hashlib
import itertools
import json
import re

HERE = Path(__file__).resolve().parent
P = HERE.parent / 'css-grid-baseline-padding-producer-20261112-v1'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(P / 'TARGET-FREEZE.json') == '283c8db357e9a690d063e7103c38b94eb4d269a4dc182e1ff217f577ceafa036'
for name, digest in json.loads((P / 'TARGET-FREEZE.json').read_text()).items():
    assert sha(P / name) == digest, name
sources = json.loads((P / 'SOURCE-HASHES.json').read_text())
for name, digest in sources.items():
    assert sha(P / 'source' / name) == digest, name
grid = (P / 'source/layout/generic/nsGridContainerFrame.cpp').read_text()
reflow = (P / 'source/layout/generic/ReflowInput.cpp').read_text()
assert (P / 'PRODUCER.cpp').read_text().rstrip() in grid
assert (P / 'CONSUMER.cpp').read_text().rstrip() in reflow
assert 'mutable PerLogicalAxis<nscoord> mBaselineOffset;' in grid
roster = re.findall(r'^  ([a-z_]+) :', (P / 'Target.lean').read_text(), re.M)
assert roster == ['encoded_range', 'stored_not_min', 'stored_nonzero', 'no_content',
                  'nonpositive_removed', 'positive_first', 'positive_last',
                  'magnitude_range', 'padding_side_range', 'border_padding_side_range',
                  'border_padding_axis_range', 'nonnegative_side', 'border_reconstruction',
                  'largest_last_witness', 'smallest_removed_witness', 'addition_overflow_witness']
lo, hi = -(1 << 31), (1 << 31) - 1
def encode(offset, content, last):
    adjustment = offset if content else 0
    return 0 if adjustment < 0 else (-adjustment if last else adjustment)
for offset, content, last in itertools.product([lo, lo+1, -1, 0, 1, hi-1, hi], [False, True], [False, True]):
    value = encode(offset, content, last)
    assert -hi <= value <= hi and value != lo
    assert 0 <= abs(value) <= hi
    if not content or offset <= 0:
        assert value == 0
assert encode(hi, True, True) == -hi
assert encode(lo, True, True) == 0
assert hi + abs(encode(1, True, False)) == 1 << 31
bounds = dict(padding_side=[lo, 2*hi], border_padding_side=[2*lo, 3*hi],
              border_padding_axis=[4*lo, 5*hi])
assert bounds == dict(padding_side=[-2147483648, 4294967294],
                      border_padding_side=[-4294967296, 6442450941],
                      border_padding_axis=[-8589934592, 10737418235])
print(json.dumps(dict(status='PASS frozen source and target review checks',
                     target_sha256=sha(P / 'Target.lean'), source_files=len(sources),
                     exact_excerpts=True, clauses=roster, endpoint_arithmetic=bounds,
                     arithmetic_status='Explanatory integer checks, not universal proof',
                     compiler_execution=False, native_reachability_claim=False), indent=2))
