import hashlib
import random
from pathlib import Path

BASE = Path(__file__).resolve().parent


def block(source, marker, start=0):
    begin = source.index(marker, start)
    opening = source.index('{', begin)
    level = 1
    end = opening + 1
    while level:
        if source[end] == '{':
            level += 1
        elif source[end] == '}':
            level -= 1
        end += 1
    return source[begin:end]


def parts(source):
    start = source.index('impl QueryCondition {')
    return {
        'operator': block(source, 'pub enum Operator {'),
        'enum': block(source, 'pub enum QueryCondition {'),
        'visitor': block(source, 'fn visit<F>', start),
        'collector': block(source, 'pub fn collect_attribute_references', start),
    }


def preservation(before, candidate):
    old = parts(before)
    new = parts(candidate)
    if before.replace(old['collector'], new['collector'], 1) != candidate:
        raise ValueError('change outside the QueryCondition collector')
    if old['visitor'] != new['visitor'] or old['enum'] != new['enum']:
        raise ValueError('visitor or enum changed')
    return {name: hashlib.sha256(text.encode()).hexdigest() for name, text in new.items()}


def native_source(before, candidate):
    p = parts(candidate)
    original = parts(before)['collector'].replace('fn collect_attribute_references', 'fn original_collect_attribute_references', 1)
    return '\n\n'.join([
        '#![allow(dead_code)]',
        (BASE / 'bridge-prefix.rs').read_text(),
        '#[derive(Clone, Copy)]\n' + p['operator'],
        p['enum'],
        'impl QueryCondition {\n' + p['visitor'] + '\n' + p['collector'] + '\n' + original + '\n}',
        (BASE / 'bridge-suffix.rs').read_text(),
    ])


def dependencies(identifier):
    choices = [[], [3, 5], [3, 3], [11], [5, 11, 19], [identifier, 23]]
    return choices[identifier % 6]


def serialize(node):
    kind, value = node
    if kind in 'NP':
        return kind + ':0 ' + serialize(value)
    if kind in 'AO':
        return kind + ':' + str(len(value)) + (' ' if value else '') + ' '.join(map(serialize, value))
    return f'{kind}:{value}'


def leaves(node):
    kind, value = node
    if kind in 'NP':
        return leaves(value)
    if kind in 'AO':
        return [leaf for child in value for leaf in leaves(child)]
    return [node]


def fixtures():
    terminals = [('S', n) for n in range(6)] + [(k, 90) for k in 'FCMG']
    nodes = list(terminals)
    for terminal in terminals:
        for depth in range(1, 17):
            node = terminal
            for n in range(depth):
                node = ('NP'[n % 2], node)
            nodes.append(node)
    for op in 'AO':
        nodes.append((op, []))
        for left in terminals:
            for right in terminals:
                nodes.append((op, [left, right]))
        nodes.append((op, [('P', terminal) for terminal in terminals] * 100))
    rng = random.Random(72026)

    def tree(depth):
        if depth == 0 or rng.randrange(4) == 0:
            return rng.choice(terminals)
        kind = rng.choice('NPAO')
        return (kind, tree(depth - 1) if kind in 'NP' else [tree(depth - 1) for _ in range(rng.randrange(5))])

    nodes.extend(tree(7) for _ in range(700))
    result = []
    for index, node in enumerate(nodes):
        seed = {101, 3} if index % 2 else set()
        expected = seed | {a for kind, identifier in leaves(node) if kind == 'S' for a in dependencies(identifier)}
        original = seed | (set(dependencies(node[1])) if node[0] == 'S' else set())
        text = serialize(node)
        render = lambda xs: ','.join(map(str, sorted(xs)))
        result.append((render(seed) + '|' + text, render(expected) + '|' + render(original) + '|' + text))
    return result
