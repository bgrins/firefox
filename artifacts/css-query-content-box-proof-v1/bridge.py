import hashlib
import itertools
import random
import re
from pathlib import Path

BASE = Path(__file__).resolve().parent


def block(source, marker):
    start = source.index(marker)
    opening = source.index('{', start)
    depth, end = 1, opening + 1
    while depth:
        depth += (source[end] == '{') - (source[end] == '}')
        end += 1
    return source[start:end]


def initializer(source):
    match = re.search(r'const QueryContainerState newState\{[^;]*\};', source)
    if not match:
        raise ValueError('missing initializer')
    return match[0]


def preservation(before, candidate):
    old, new = initializer(before), initializer(candidate)
    if old.count('frame->GetSize()') != 1:
        raise ValueError('unexpected original getter')
    expected = old.replace('frame->GetSize()', 'frame->GetContentRectRelativeToSelf().Size()')
    compact = lambda s: re.sub(r'\s+', '', s)
    if compact(expected) != compact(new):
        raise ValueError('candidate initializer is not the intended getter replacement')
    if before.replace(old, new, 1) != candidate:
        raise ValueError('source change outside initializer')
    state = block(candidate, 'struct QueryContainerState {') + ';'
    return {'initializer_sha256': hashlib.sha256(new.encode()).hexdigest(),
            'state_sha256': hashlib.sha256(state.encode()).hexdigest()}


def source(before, candidate, bindings):
    state = block(candidate, 'struct QueryContainerState {') + ';'
    projection = block(bindings, 'void Gecko_GetQueryContainerSize(')
    def constructor(name, native):
        return ('QueryContainerState ' + name + '(nsIFrame* frame) {\n'
                'auto type = frame->StyleDisplay()->mContainerType;\n' +
                initializer(native) + '\nreturn newState;\n}')
    return '\n\n'.join([(BASE / 'bridge-prefix.cpp').read_text(), state, projection,
                         constructor('candidateState', candidate), constructor('originalState', before),
                         (BASE / 'bridge-suffix.cpp').read_text()])


def changed(before, after, content=True):
    if before[0] != after[0]:
        return True
    index = 4 if content else 2
    if before[0] & 2:
        return before[index:index+2] != after[index:index+2]
    if before[0] & 1:
        return before[index + before[1]] != after[index + after[1]]
    return False


def project(frame):
    _, vertical, _, _, width, height, inline, block_axis, present, contents = frame
    if not present or contents:
        return [-1, -1]
    return [max(-1, width) if (block_axis if vertical else inline) else -1,
            max(-1, height) if (inline if vertical else block_axis) else -1]


def eligible(frame, raw):
    kind, vertical = frame[:2]
    if kind & 2:
        return raw
    if kind & 1:
        return [-1, raw[1]] if vertical else [raw[0], -1]
    return [-1, -1]


def premises(before, after):
    return before[:2] == after[:2] and before[6:] == after[6:]


def fixtures():
    cases = []
    sizes = [(0, 0), (1, 2), (100, 60), (60, 100), (2147483647, 0),
             (0, 2147483647), (-1, 50), (-2147483648, 1)]
    for kind, vertical, inline, block_axis, present, contents in itertools.product(range(8), range(2), range(2), range(2), range(2), range(2)):
        for before_size, after_size in itertools.product(sizes, sizes):
            before = [kind, vertical, 100, 100, *before_size, inline, block_axis, present, contents]
            after = [kind, vertical, 100, 100, *after_size, inline, block_axis, present, contents]
            cases.append((before, after))
    rng = random.Random(102026)
    for _ in range(1000):
        def frame():
            return [rng.randrange(8), rng.randrange(2), *rng.choice(sizes), *rng.choice(sizes),
                    *(rng.randrange(2) for _ in range(4))]
        cases.append((frame(), frame()))
    return cases


def expected(before, after):
    return [int(changed(before, after)), int(changed(before, after, False)), *project(before), *project(after)]


def mask_source(container, flags):
    axis = block(container, 'fn container_type_axes(')
    method = block(container, 'fn evaluate_potential_size_container<E>(')
    offset = method.index('if container_type.intersects(ContainerType::SIZE)')
    mask = method[offset:method.rfind('}')].strip()
    all_axes = block(flags, 'pub fn all_container_axes()')
    return '\n\n'.join([(BASE / 'mask-prefix.rs').read_text(),
        'impl FeatureFlags {\n' + all_axes + '\n}', axis,
        'fn mask(container_type: ContainerType, wm: WritingMode, size: ContainerSizeQueryResult) -> TraversalResult<ContainerSizeQueryResult> {\n' + mask + '\n}',
        (BASE / 'mask-suffix.rs').read_text()])


def mask_fixtures():
    result = []
    for kind, vertical, width, height in itertools.product(range(8), range(2), [-1, 0, 1, 100, 2147483647], [-1, 0, 1, 60, 2147483647]):
        flags = 60 if kind & 2 else (36 if vertical else 20) if kind & 1 else 0
        masked = eligible([kind, vertical], [width, height])
        result.append(([kind, vertical, width, height], [flags, *masked]))
    return result
