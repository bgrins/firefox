import itertools
import json
from pathlib import Path

NODES = range(3)
SCHEME = 2


def oracle(base, defaults):
    edges = {v: set(base[v]) for v in NODES}
    while True:
        reach = {v: set(edges[v]) for v in NODES}
        for _ in NODES:
            reach = {v: reach[v] | {z for w in reach[v] for z in reach[w]} for v in NODES}
        extra = {(v, SCHEME) for v in (0, 1) if defaults[v] and v in reach[v]}
        if all(w in edges[v] for v, w in extra):
            groups = {frozenset(w for w in NODES if w == v or (w in reach[v] and v in reach[w])) for v in NODES}
            return edges, groups
        for v, w in extra:
            edges[v].add(w)


def staged(base, defaults, order, early_only=False):
    edges = {v: set(base[v]) for v in NODES}
    indices, low, stack, active, groups = {}, {}, [], set(), set()

    def visit(v):
        indices[v] = low[v] = len(indices)
        stack.append(v)
        active.add(v)

        def link(w):
            if w not in indices:
                visit(w)
                if w in active:
                    low[v] = min(low[v], low[w])
            elif w in active:
                low[v] = min(low[v], indices[w])

        if early_only and v in (0, 1) and defaults[v] and v in edges[v]:
            edges[v].add(SCHEME)
        for w in sorted(edges[v]):
            link(w)
        cyclic = low[v] < indices[v] or stack[-1] != v or v in edges[v]
        if not early_only and v in (0, 1) and defaults[v] and cyclic and SCHEME not in edges[v]:
            edges[v].add(SCHEME)
            link(SCHEME)
        if low[v] == indices[v]:
            component = set()
            while True:
                w = stack.pop()
                active.remove(w)
                component.add(w)
                if w == v:
                    break
            groups.add(frozenset(component))

    for v in order:
        if v not in indices:
            visit(v)
    assert not stack and not active
    return edges, groups


def main():
    count = 0
    for bits in range(1 << 9):
        base = {v: {w for w in NODES if bits & (1 << (v * 3 + w))} for v in NODES}
        for flags in itertools.product((False, True), repeat=2):
            expected = oracle(base, flags)
            for order in itertools.permutations(NODES):
                actual = staged(base, flags, order)
                assert actual == expected, (base, flags, order, actual, expected)
                count += 1
    base = {0: {1}, 1: {0}, 2: set()}
    flags = (True, False)
    assert staged(base, flags, (0, 1, 2), early_only=True) != oracle(base, flags)
    record = {'cases': count, 'vertices': 3, 'custom_vertices': [0, 1],
              'scheme_vertex': SCHEME, 'orders_per_graph': 6,
              'oracle': 'independent transitive-closure least fixed point of cyclic-custom default edges',
              'compared': ['all added edges', 'SCC partition'],
              'early_only_counterexample': {'edges': {'0': [1], '1': [0], '2': []}, 'default_flags': flags},
              'native_algorithm_executed': False, 'unbounded_proof': False}
    path = Path(__file__).with_name('CLOSURE-CHECK.json')
    with path.open('x') as stream:
        json.dump(record, stream, indent=2)
        stream.write('\n')
    print(json.dumps(record))


if __name__ == '__main__':
    main()
