import hashlib
import itertools
from pathlib import Path

BASE = Path(__file__).resolve().parent
SIGNATURE = 'void TransformReferenceBox::EnsureDimensionsAreCached()'
REMOVED = '      // TODO: Implement this in the following patches.\n      return;\n'


def extract(source):
    start = source.index(SIGNATURE)
    brace = source.index('{', start)
    depth, end = 1, brace + 1
    while depth:
        depth += (source[end] == '{') - (source[end] == '}')
        end += 1
    return source[start:end]


def preservation(before, candidate):
    old = extract(before)
    marker = '    case StyleTransformBox::StrokeBox:\n' + REMOVED
    if old.count(marker) != 1:
        raise ValueError('original stroke marker mismatch')
    expected = before.replace(old, old.replace(marker, '    case StyleTransformBox::StrokeBox:\n'), 1)
    if expected != candidate:
        raise ValueError('whole-file preservation mismatch')
    return {'original_function_sha256': hashlib.sha256(old.encode()).hexdigest(),
            'candidate_function_sha256': hashlib.sha256(extract(candidate).encode()).hexdigest(),
            'allowed_change': 'delete exactly StrokeBox TODO and return; all other bytes identical',
            'UNIFIED_CONTINUATIONS': 'undefined in native bridge; disabled branch retained textually'}


def source(native):
    return (BASE/'bridge-prefix.cpp').read_text() + '\n' + extract(native) + '\n' + (BASE/'bridge-suffix.cpp').read_text()


def fixtures():
    result = []
    geometries = [
        ([12,18,120,60], [30,-24,180,90], [-42,54,240,150]),
        ([-60,30,48,96], [-120,72,150,210], [90,-84,300,180]),
        ([0,0,0,0], [0,0,0,0], [12,24,0,0]),
        ([6,12,0,60], [-18,30,0,120], [-36,42,60,0]),
        ([-12,-18,60,0], [24,30,120,0], [42,48,0,60]),
        ([600,-1200,3600,6000], [120,-180,9000,12000], [1800,-2400,18000,24000]),
        ([6,6,6,6], [-6,-6,12,18], [24,30,36,42]),
    ]
    for tag, svg, cached, needs, divisor, geometry in itertools.product(range(5), range(2), range(2), range(2), [1,2,3], geometries):
        content, border, svgrect = [list(r) for r in geometry]
        svgrect[0] += 6*tag
        initial = [-333, 444, 777, 888]
        result.append(make_fixture(tag, svg, cached, needs, divisor, False, content, border, svgrect, initial))
    for tag, needs in itertools.product(range(5), range(2)):
        result.append(make_fixture(tag, 0, 1, needs, 2, True, *geometries[0], [9,-9,15,21]))
    return result


def make_fixture(tag, svg, cached, needs, divisor, absent, content, border, svgrect, initial):
    assert not absent or cached
    counts = [0]*8
    output = list(initial)
    old_output = list(initial)
    if not cached:
        counts[0] = counts[1] = counts[2] = 1
        if svg:
            output = list(svgrect)
            counts[6] = 1
        else:
            counts[3] = 1
            if tag in [0,1]:
                output = list(content)
                counts[4] = 1
            else:
                output = [0,0,border[2],border[3]]
                counts[5] = 1
        if needs:
            assert all(v % divisor == 0 for v in output)
            output = [v//divisor for v in output]
            counts[7] = 1
        old_output = list(output)
    old_counts = list(counts)
    if not cached and not svg and tag == 2:
        old_output = list(initial)
        old_counts[5] = old_counts[7] = 0
    def encode(rect, calls):
        one = ' '.join(map(str, [1]+rect+calls))
        return one+'|'+one
    return {'input': ' '.join(map(str, [tag,svg,cached,needs,divisor,int(absent)]+content+border+svgrect+initial)),
            'expected': encode(output, counts), 'original_expected': encode(old_output, old_counts),
            'tag':tag, 'svg':bool(svg), 'cached':bool(cached), 'unzoom':bool(needs), 'divisor':divisor, 'absent_frame':absent}
