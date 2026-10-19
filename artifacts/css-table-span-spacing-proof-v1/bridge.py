import hashlib
import itertools
import json
import random
import re
from pathlib import Path

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[1]
BINDING = json.loads((BASE / 'BINDING-v1.json').read_text())
MAX = 2147483647


def sha(data):
    return hashlib.sha256(data.encode() if isinstance(data, str) else data).hexdigest()


def block(source, marker):
    if source.count(marker) != 1:
        raise ValueError('ambiguous block: ' + marker)
    start = source.index(marker)
    opening = source.index('{', start)
    depth, end = 1, opening + 1
    while depth:
        depth += (source[end] == '{') - (source[end] == '}')
        end += 1
    return source[start:end]


def validate(candidate):
    new, old = BINDING['candidate_assignment'], BINDING['original_assignment']
    if candidate.count(new) != 1:
        raise ValueError('candidate assignment changed')
    original = candidate.replace(new, old, 1)
    if sha(original) != BINDING['before_sha256']:
        raise ValueError('source outside the sole permitted assignment changed')
    if sha(candidate) != BINDING['candidate_sha256']:
        raise ValueError('candidate identity changed')
    return original


def snippets(candidate):
    original = validate(candidate)
    def minimum(source):
        fun = block(source, 'nscoord FixedTableLayoutStrategy::GetMinISize(')
        branch = block(fun, 'if (styleISize->ConvertsToLength() || styleISize->IsMinContent() ||')
        span = block(branch, 'if (colSpan > 1) {')
        accumulation = 'result += cellISize;'
        if branch.count(accumulation) != 1:
            raise ValueError('accumulation changed')
        return span, accumulation
    final_fun = block(candidate, 'void FixedTableLayoutStrategy::ComputeColumnISizes(')
    final = block(final_fun, 'if (colSpan > 1) {')
    new, addition = minimum(candidate)
    old, old_addition = minimum(original)
    assert addition == old_addition
    return {'candidate.inc': new, 'original.inc': old, 'allocation.inc': final,
            'accumulation.inc': addition}


def source(candidate):
    extracted = snippets(candidate)
    coord = (ROOT / BINDING['nscoord_path']).read_text()
    if sha(coord) != BINDING['nscoord_sha256']:
        raise ValueError('nscoord source drift')
    alias = re.search(r'^using nscoord = int32_t;$', coord, re.M)
    if not alias:
        raise ValueError('nscoord type changed')
    prefix = (BASE / 'bridge-prefix.cpp').read_text() + '\n' + alias[0] + '\n'
    return '\n'.join([prefix,
        'nscoord original(nscoord cellISize, nscoord spacing, int32_t colSpan) {',
        extracted['original.inc'], 'return cellISize;\n}',
        'nscoord candidate(nscoord cellISize, nscoord spacing, int32_t colSpan, nscoord& result) {',
        extracted['candidate.inc'], extracted['accumulation.inc'], 'return cellISize;\n}',
        'nscoord allocation(nscoord colISize, nscoord spacing, int32_t colSpan) {',
        'SpacingFrame frame{spacing}; auto* mTableFrame = &frame; int32_t col = 0;',
        extracted['allocation.inc'], 'return colISize;\n}',
        (BASE / 'bridge-suffix.cpp').read_text()])


def expected(case):
    extent, spacing, span, base = case
    assert 0 <= extent and 0 <= spacing and 0 < span <= MAX
    assert extent + spacing <= MAX and 0 <= base <= MAX
    quotient, _remainder = divmod(extent + spacing, span)
    original = quotient - spacing if span > 1 else extent
    share = (0 if quotient < spacing else quotient - spacing) if span > 1 else extent
    assert base + share <= MAX
    return [original, share, share, base + share]


def fixtures():
    cases = set()
    def add(c, s, k, b=0):
        case = (c, s, k, b)
        expected(case)
        cases.add(case)
    for c, s, k in itertools.product(range(41), range(21), range(1, 9)):
        for base in [0, 1000]:
            add(c, s, k, base)
    edges = [0, 1, 2, 59, 60, 61, 120, 1024, (1 << 30) - 1, MAX - 1, MAX]
    for c, s, k in itertools.product(edges, edges, [1, 2, 3, 7, 1024, MAX]):
        if c + s <= MAX:
            add(c, s, k)
            share = expected((c, s, k, 0))[1]
            add(c, s, k, MAX - share)
    rng = random.Random(20261018)
    for _ in range(4096):
        s = rng.randrange(MAX + 1)
        c = rng.randrange(MAX - s + 1)
        k = rng.choice([1, 2, 3, 1000, rng.randrange(1, MAX + 1)])
        share = expected((c, s, k, 0))[1]
        add(c, s, k, rng.randrange(MAX - share + 1))
    for s in [1, 60, 1000]:
        for k in range(2, 20):
            for delta in [-1, 0, 1, k - 1, k]:
                c = (k - 1) * s + delta
                if c >= 0:
                    add(c, s, k, (k + 1) * s)
    return sorted(cases)
