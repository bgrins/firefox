import copy
import itertools


def frame(parent=1, pos=0, bits=0, rect=(0, 0, 10, 10)):
    return dict(parent=parent, target=-1, previous=-1, pos=pos, bits=bits,
                nested=-1, disabled=0, logical=[0, 100], rect=list(rect), offset=17,
                lists=[])


def base(mode=0):
    return dict(id=0, name='', mode=mode, enabled=1, highlight=0, old=-1,
                frames=[frame(-1), frame(0), frame(), frame()])


def validate(case):
    nodes = case['frames']
    n = len(nodes)
    assert 3 <= n <= 64
    for i, f in enumerate(nodes):
        assert 0 <= f['pos'] <= 4 and 0 <= f['bits'] < 16384
        assert all(-1 <= f[k] < n for k in ['parent', 'target', 'previous', 'nested'])
        assert len({kind for kind, _ in f['lists']}) == len(f['lists'])
        assert all(0 <= kind <= 5 and all(0 <= j < n for j in ids) for kind, ids in f['lists'])
        seen = {i}; p = f['parent']
        while p >= 0:
            assert p not in seen, 'parent cycle'
            seen.add(p); p = nodes[p]['parent']
    def acyclic(i, ancestors):
        assert i not in ancestors, 'traversal cycle'
        f = nodes[i]
        edges = [j for _, ids in f['lists'] for j in ids]
        if f['target'] >= 0:
            edges.append(f['target'])
        for j in edges:
            acyclic(j, ancestors | {i})
    for i in range(n):
        acyclic(i, set())
    if case['old'] >= 0:
        p = case['old']; seen = set()
        while p != 1:
            assert p >= 0 and p not in seen
            seen.add(p); p = nodes[p]['parent']


def can_maintain(case, i):
    f = case['frames'][i]
    return bool(case['enabled'] and not f['disabled'] and not f['bits'] & 8192
                and f['logical'][0 if f['bits'] & 2048 else 1] != 0
                and not f['bits'] & 1024)


def observed(case, i):
    f = case['frames'][i]; b = f['bits']
    x, y, w, h = f['rect']
    visible = max(x, 0) < min(x + w, 100) and max(y, 0) < min(y + h, 100)
    full = visible and x >= 0 and y >= 0 and x + w <= 100 and y + h <= 100
    return dict(fixed=f['pos'] == 3, sticky=bool(b & 2),
                text=bool(b & 1 and not b & 4096), continuation=f['previous'] >= 0,
                opted=bool(b & 8192), br=bool(b & 4),
                chrome=bool(b & 8 and not b & 4096), pseudo=bool(b & 16),
                replaced=bool(b & 32), inline=bool(b & 64), anon=bool(b & 128),
                nested=bool(b & 256 and (f['nested'] >= 0 or can_maintain(case, i))),
                visible=visible, full=full)


def classify(o, repaired=True):
    forbidden = (o['text'] and o['continuation']) or o['opted'] or o['sticky']
    forbidden = forbidden or (repaired and o['fixed']) or o['br']
    forbidden = forbidden or (o['chrome'] and not o['pseudo'])
    if forbidden:
        return 0
    descend = not (o['nested'] or o['replaced'])
    if not o['text'] and ((o['inline'] and not o['replaced']) or o['anon']):
        return 1 if descend else 0
    if not o['visible']:
        return 0
    if descend and o['continuation']:
        return 1
    return 3 if o['full'] or not descend else 2


def oracle(case, repaired=True):
    nodes = case['frames']; trace = []
    flags = [0] * len(nodes)
    def mark(i, value, log):
        while i != 1:
            assert i >= 0
            flags[i] = value
            if log:
                trace.append(f'F{i}:{value}')
            i = nodes[i]['parent']
    if case['old'] >= 0:
        mark(case['old'], 1, False)
    def examine(i):
        o = observed(case, i)
        trace.append(f'E{i}')
        early = ((o['text'] and o['continuation']) or o['opted'] or o['sticky']
                 or (repaired and o['fixed']) or o['br'] or (o['chrome'] and not o['pseudo']))
        if not early:
            trace.append(f'Q{i}')
            if o['text'] or not ((o['inline'] and not o['replaced']) or o['anon']):
                trace.append(f'B{i}')
        return classify(o, repaired)
    def search_list(ids):
        for original in ids:
            i = original
            if nodes[i]['target'] >= 0:
                trace.append(f'H{i}')
                i = nodes[i]['target']
                if i != original:
                    p = nodes[i]['parent']; inside = False
                    while p >= 0:
                        inside |= p == 0
                        p = nodes[p]['parent']
                    trace.append(f'P{i}:{int(inside)}')
                    if not inside:
                        continue
            decision = examine(i)
            if decision == 0:
                continue
            if decision == 3:
                return i
            child = search(i)
            if child >= 0:
                return child
            if decision == 2:
                return i
        return -1
    def search(i):
        trace.append(f'L{i}')
        for kind, ids in nodes[i]['lists']:
            if kind in [1, 2, 3]:
                continue
            result = search_list(ids)
            if result >= 0:
                return result
        trace.append(f'A{i}')
        ids = next((ids for kind, ids in nodes[i]['lists'] if kind == 1), [])
        return search_list(ids)
    if case['mode'] == 1:
        result = examine(2)
        return dict(values=[case['id'], result, 0, 1, 0, *flags], events=trace)
    result = search(1) if can_maintain(case, 0) else -1
    suboptimal = int(result >= 0 and nodes[result]['bits'] & 512 != 0)
    if case['old'] != result:
        if case['old'] >= 0:
            mark(case['old'], 0, True)
            if case['highlight']:
                trace.append(f'I{case["old"]}')
        if result >= 0:
            mark(result, 1, True)
            if case['highlight']:
                trace.append(f'I{result}')
    offset = 0
    if result >= 0:
        trace.append(f'O{result}'); offset = nodes[result]['offset']
    return dict(values=[case['id'], result, offset, 0, suboptimal, *flags], events=trace)


def wire(c):
    tokens = [c['id'], c['mode'], len(c['frames']), c['enabled'], c['highlight'], c['old']]
    for f in c['frames']:
        tokens += [f['parent'], f['target'], f['previous'], f['pos'], f['bits'], f['nested'],
                   f['disabled'], *f['logical'], *f['rect'], f['offset']]
    for f in c['frames']:
        tokens.append(len(f['lists']))
        for kind, ids in f['lists']:
            tokens += [kind, len(ids), *ids]
    return ' '.join(map(str, tokens))


def corpus():
    cases = []
    def add(c, name):
        c = copy.deepcopy(c); c['id'] = len(cases); c['name'] = name
        validate(c); cases.append(c)
    for pos, bits, rect in itertools.product(range(5), range(256),
                                             [(0, 0, 10, 10), (95, 0, 10, 10), (200, 0, 10, 10)]):
        c = base(1); c['frames'][2] = frame(pos=pos, bits=bits, rect=rect)
        add(c, f'classifier-{pos}-{bits}-{rect[0]}')
    for pos, bits, continuation, rect in itertools.product(range(5),
            [0, 1, 32, 64, 128, 256, 512, 1024, 2048, 4096 | 9, 8192], [False, True],
            [(0, 0, 0, 10), (95, 0, 10, 10), (0, 0, 10, 10)]):
        c = base(1); c['frames'][2] = frame(pos=pos, bits=bits, rect=rect)
        c['frames'][2]['previous'] = 3 if continuation else -1
        add(c, 'classifier-boundary')
    for pos, parentBits, rectangle, childPos, tailPos in itertools.product(range(5),
            [0, 2, 64, 128, 8192], [(0, 0, 10, 10), (95, 0, 10, 10)], [0, 3], [0, 3]):
        c = base(); c['frames'] += [frame(parent=2, pos=childPos)]
        c['frames'][1]['lists'] = [(0, [2, 3])]
        c['frames'][2] = frame(pos=pos, bits=parentBits, rect=rectangle)
        c['frames'][2]['lists'] = [(0, [4])]
        c['frames'][3]['pos'] = tailPos
        add(c, 'nested-priority')
    for pos, outside, listKind, old, highlight in itertools.product(range(5), [False, True],
            range(6), [-1, 3], [0, 1]):
        c = base(); c['frames'] += [frame(pos=pos)]
        c['frames'][2]['target'] = 4
        c['frames'][4]['parent'] = -1 if outside else 1
        c['frames'][1]['lists'] = [(listKind, [2]), (5 if listKind != 5 else 0, [3])]
        c['old'] = old; c['highlight'] = highlight
        add(c, 'placeholder-and-lists')
    for pos, childBits, old in itertools.product(range(5), [0, 64, 8192], [-1, 2, 3]):
        c = base(); c['frames'] += [frame(parent=2, bits=childBits)]
        c['frames'][1]['lists'] = [(0, [3]), (1, [2])]
        c['frames'][3]['bits'] = 8192
        c['frames'][2] = frame(pos=pos, rect=(95, 0, 10, 10))
        c['frames'][2]['lists'] = [(0, [4])]
        c['old'] = old
        add(c, 'absolute-second-pass')
    for pos, disabled, rootBits, logical, enabled in itertools.product(range(5), [0, 1],
            [0, 1024, 2048, 8192], [(0, 100), (100, 0), (0, 0)], [0, 1]):
        c = base(); c['frames'][1]['lists'] = [(0, [2, 3])]
        c['frames'][0].update(disabled=disabled, bits=rootBits, logical=list(logical))
        c['frames'][2]['pos'] = pos; c['frames'][2]['bits'] = 512
        c['enabled'] = enabled; c['old'] = 3
        add(c, 'selection-gates')
    for bits, nested, disabled, rect in itertools.product([256, 256 | 64, 256 | 128, 32],
            [-1, 3], [0, 1], [(95, 0, 10, 10), (0, 0, 10, 10)]):
        c = base(); c['frames'][1]['lists'] = [(0, [2, 3])]
        c['frames'][2] = frame(bits=bits, rect=rect)
        c['frames'][2].update(nested=nested, disabled=disabled)
        c['frames'] += [frame(parent=2)]
        c['frames'][2]['lists'] = [(0, [4])]
        add(c, 'nested-scroller')
    c = base(); c['frames'] += [frame(parent=2)]
    c['frames'][1]['lists'] = [(0, [2]), (1, [4])]
    c['frames'][2]['pos'] = 3; c['frames'][2]['lists'] = [(0, [4])]
    add(c, 'abstract-alternate-route-not-a-gecko-reachability-claim')
    c = base(); c['frames'] += [frame(pos=3)]
    c['frames'][2]['target'] = 4; c['frames'][3]['bits'] = 8192
    c['frames'][1]['lists'] = [(0, [2, 3]), (1, [4])]
    add(c, 'duplicate-fixed-placeholder-and-absolute')
    return cases
