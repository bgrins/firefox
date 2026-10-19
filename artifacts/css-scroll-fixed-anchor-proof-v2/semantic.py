import copy

import fixtures


def target(case, slot):
    value = case['frames'][slot]['target']
    return slot if value < 0 else value


def eligible(case, slot):
    real = target(case, slot)
    if real == slot:
        return True
    parent = case['frames'][real]['parent']
    while parent >= 0:
        if parent == 0:
            return True
        parent = case['frames'][parent]['parent']
    return False


def schedule(case, parent):
    lists = case['frames'][parent]['lists']
    return [(0, kind, ids, kind in [1, 2, 3]) for kind, ids in lists] + [
        (1, 1, next((ids for kind, ids in lists if kind == 1), []), False)]


def rank(case):
    nodes = case['frames']
    ranks = {}
    def visit(parent, active):
        assert parent not in active, 'effective traversal cycle'
        if parent in ranks:
            return ranks[parent]
        edges = [target(case, slot) for _, _, ids, skip in schedule(case, parent)
                 if not skip for slot in ids if eligible(case, slot)]
        ranks[parent] = max((visit(child, active | {parent}) + 1 for child in edges), default=0)
        return ranks[parent]
    for parent in range(len(nodes)):
        visit(parent, set())
    return [ranks[i] for i in range(len(nodes))]


def validate(case):
    nodes = case['frames']
    n = len(nodes)
    for i, f in enumerate(nodes):
        assert all(-1 <= f[k] < n for k in ['parent', 'target', 'previous', 'nested'])
        assert len(f['lists']) <= 6
        assert all(0 <= k <= 5 and all(0 <= j < n for j in ids) for k, ids in f['lists'])
        seen = {i}
        parent = f['parent']
        while parent >= 0:
            assert parent not in seen
            seen.add(parent)
            parent = nodes[parent]['parent']
    return rank(case)


def oracle(case, repaired):
    if case['mode'] == 1:
        decision = fixtures.classify(fixtures.observed(case, 2), repaired)
        return decision, [f'D2:{decision}']
    trace = []
    stack = []
    def push(parent):
        trace.append(f'E{parent}')
        stack.append(dict(parent=parent, schedule=schedule(case, parent), at=0,
                          slots=None, next_slot=0, waiting=None))
    if not fixtures.can_maintain(case, 0):
        return -1, ['Z-1']
    push(1)
    answer = -1
    while stack:
        current = stack[-1]
        result = None
        if current['slots'] is None:
            if current['at'] == len(current['schedule']):
                result = -1
            else:
                phase, kind, ids, skip = current['schedule'][current['at']]
                current['at'] += 1
                if skip:
                    trace.append(f'K{current["parent"]}:{kind}')
                    continue
                trace.append(f'L{current["parent"]}:{phase}:{kind}')
                current['slots'] = ids
                current['next_slot'] = 0
                continue
        elif current['next_slot'] == len(current['slots']):
            current['slots'] = None
            continue
        else:
            slot = current['slots'][current['next_slot']]
            current['next_slot'] += 1
            real = target(case, slot)
            accepted = eligible(case, slot)
            trace.append(f'R{slot}:{real}:{int(accepted)}')
            if not accepted:
                continue
            decision = fixtures.classify(fixtures.observed(case, real), repaired)
            trace.append(f'D{real}:{decision}')
            if decision == 0:
                continue
            if decision == 3:
                trace.append(f'U{real}:{real}')
                result = real
            else:
                trace.append(f'N{real}')
                current['waiting'] = (decision, real)
                push(real)
                continue
        while result is not None:
            completed = stack.pop()
            trace.append(f'F{completed["parent"]}:{result}:0')
            if not stack:
                answer = result
                break
            decision, candidate = stack[-1]['waiting']
            stack[-1]['waiting'] = None
            if result >= 0:
                trace.append(f'U{candidate}:{result}')
            elif decision == 2:
                trace.extend([f'B{candidate}', f'U{candidate}:{candidate}'])
                result = candidate
            else:
                result = None
    trace.append(f'Z{answer}')
    return answer, trace


def corpus():
    cases = fixtures.corpus()
    def add(c, name):
        c = copy.deepcopy(c)
        c.update(id=len(cases), name=name)
        validate(c)
        cases.append(c)
    c = fixtures.base()
    c['frames'][1]['lists'] = [(0, [2, 3])]
    c['frames'][2]['target'] = 2
    add(c, 'abstract-self-target-identity-no-ancestor-provider')
    c['frames'][2].update(parent=-1, pos=3, bits=8192)
    add(c, 'abstract-self-target-outside-but-opted-out')
    c = fixtures.base()
    c['frames'][2]['pos'] = 3
    c['frames'][1]['lists'] = [(1, [2]), (1, [3])]
    add(c, 'abstract-duplicate-absolute-kind-first-match-only')
    c['frames'][1]['lists'] = [(0, [2]), (0, [3])]
    add(c, 'abstract-duplicate-ordinary-kind-retains-both')
    c = fixtures.base()
    c['frames'][1]['lists'] = [(0, []), (2, [2]), (3, [3]), (1, [])]
    add(c, 'empty-and-skipped-list-boundaries')
    c['frames'][1]['lists'] = []
    add(c, 'same-null-winner-distinct-empty-list-flow')
    c = fixtures.base()
    c['frames'] += [fixtures.frame(parent=2, rect=(95, 0, 10, 10)), fixtures.frame(parent=4, pos=3)]
    c['frames'][1]['lists'] = [(0, [2, 3])]
    c['frames'][2]['bits'] = 64
    c['frames'][2]['lists'] = [(0, [4])]
    c['frames'][4]['lists'] = [(0, [5])]
    add(c, 'nested-pass-return-after-traverse-fallback')
    return cases
