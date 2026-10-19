import hashlib
import itertools
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
SOURCE = ROOT / 'servo/components/style/properties/declaration_block.rs'
SOURCE_SHA = '8474218db02f8787c212f47a08be33a468553b4ab809e774f2d26d4ae098812a'


def opposite(a, b):
    return a < 4 and b < 4 and (a < 2) != (b < 2)


def reference(state, action):
    for i, entry in enumerate(state):
        if entry[0] == action[0]:
            if any(opposite(action[0], e[0]) for e in state[i + 1:]):
                return state[:i] + state[i + 1:] + [action]
            return state[:i] + [action] + state[i + 1:]
    return state + [action]


def plan(state, action):
    append = False
    for i in range(len(state) - 1, -1, -1):
        if state[i][0] == action[0]:
            if append:
                return ['move', i]
            return ['none' if state[i] == action else 'replace', i]
        append |= opposite(state[i][0], action[0])
    return ['append', None]


def batched(state, actions):
    plans = [plan(state, a) for a in actions]
    result = list(state)
    indexed = sorted((p[1], i, p[0] == 'move') for i, p in enumerate(plans)
                     if p[0] in ('move', 'replace'))
    for pos, _, remove in reversed(indexed):
        if remove:
            del result[pos]
    removed = 0
    for pos, i, remove in indexed:
        if remove:
            removed += 1
        else:
            plans[i][1] = pos - removed
    for action, (kind, pos) in zip(actions, plans):
        if kind in ('append', 'move'):
            result.append(action)
        elif kind == 'replace':
            result[pos] = action
    return result


def direct(state, actions):
    for action in actions:
        state = reference(state, action)
    return state


def unique_orders():
    for n in range(6):
        yield from itertools.permutations(range(5), n)


def main():
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == SOURCE_SHA
    orders = list(unique_orders())
    uniform = [ids for ids in orders if not any(opposite(a, b) for a in ids for b in ids)]
    actions = [[(k, v, priority) for k, v in zip(ids, values)]
               for ids in uniform for values in itertools.product(range(2), repeat=len(ids))
               for priority in (False, True)]
    checked = 0
    for ids in orders:
        for bits in itertools.product((False, True), repeat=len(ids)):
            state = [(k, 0, bit) for k, bit in zip(ids, bits)]
            for expansion in actions:
                actual = batched(state, expansion)
                expected = direct(state, expansion)
                assert actual == expected, (state, expansion, actual, expected)
                checked += 1
    witnesses = []
    for label, state, expansion in [
        ('mixed-mapping', [(0, 0, False), (2, 0, False)],
         [(0, 0, False), (2, 0, False)]),
        ('duplicate-source', [], [(0, 0, False), (0, 1, False)]),
    ]:
        actual, expected = batched(state, expansion), direct(state, expansion)
        assert actual != expected
        witnesses.append(dict(premise=label, before=state, actions=expansion,
                              batch=actual, sequential=expected))
    record = {
        'status': 'BOUNDED_ABSTRACT_EXPLORATION_PASS_NOT_NATIVE_OR_UNIVERSAL_PROOF',
        'source_sha256': SOURCE_SHA,
        'program_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'checked': checked, 'identities': 5, 'unique_orders': len(orders),
        'uniform_source_orders': len(uniform), 'action_vectors': len(actions),
        'domain': 'One logical group with two physical and two logical IDs; one ungrouped ID. All destination/source identity permutations and subsets; arbitrary destination priorities; each source value equals or differs from the destination seed; shared source priority.',
        'counterexamples_when_premises_removed': witnesses,
        'limits': 'Handwritten list model, no Rust extraction, no concrete parallel-bit/set invariant, no source/provider proof. Checks algorithm ordering and position correction only. Invalid-source witnesses are not reachable browser bug claims.',
    }
    (OUT / 'RESULT.json').write_text(json.dumps(record, indent=2) + '\n')
    print(json.dumps({k: record[k] for k in ('status', 'checked', 'unique_orders', 'uniform_source_orders', 'action_vectors')}))


if __name__ == '__main__':
    main()
