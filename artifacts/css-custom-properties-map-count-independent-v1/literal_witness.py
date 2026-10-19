import json

class Node:
    def __init__(self, parent=None):
        self.own = {}
        self.parent = parent
        self.length = parent.length if parent else 0

    def get(self, key):
        if key in self.own:
            return self.own[key]
        return self.parent.get(key) if self.parent else None

    def insert(self, key, value, corrected):
        if corrected:
            self.length += int(value is not None) - int(self.get(key) is not None)
        else:
            new = key not in self.own
            if new and (self.parent is None or self.parent.get(key) is None):
                self.length += 1
        self.own[key] = value

    def effective(self):
        merged = self.parent.effective() if self.parent else {}
        for key, value in self.own.items():
            if value is None:
                merged.pop(key, None)
            else:
                merged[key] = value
        return merged

    def entries(self, corrected_iterator):
        current = self
        descendants = []
        out = []
        while current is not None:
            for key, value in current.own.items():
                if corrected_iterator and any(key in d.own for d in descendants):
                    continue
                out.append((key, value))
            descendants.append(current)
            current = current.parent
        return out

def chain(corrected):
    outer = Node()
    outer.insert('target', '10px', corrected)
    for i in range(8):
        outer.insert(f'outer-{i}', 'outer', corrected)
    middle = Node(outer)
    middle.insert('target', None, corrected)
    for i in range(8):
        middle.insert(f'middle-{i}', 'middle', corrected)
    leaf = Node(middle)
    leaf.insert('target', '20px', corrected)
    return outer, middle, leaf

rows = []
for fixed_count in (False, True):
    outer, middle, leaf = chain(fixed_count)
    assert len(outer.own) == len(middle.own) == 9
    assert len(leaf.effective()) == 17
    assert [x.length for x in (outer, middle, leaf)] == ([9, 16, 17] if fixed_count else [9, 17, 18])
    for fixed_iterator in (False, True):
        raw = leaf.entries(fixed_iterator)
        indexed = [e for e in raw if e[1] is not None] if fixed_count else raw
        rows.append({'fixed_count': fixed_count, 'fixed_iterator': fixed_iterator,
                     'stored_counts': [x.length for x in (outer, middle, leaf)],
                     'effective_live_count': len(leaf.effective()),
                     'raw_iterator': raw, 'indexed_stream_length': len(indexed),
                     'index_below_len_without_entry': [i for i in range(leaf.length) if i >= len(indexed)],
                     'exposed_prefix': indexed[:leaf.length]})
assert rows[1]['index_below_len_without_entry'] == [17]
assert rows[3]['index_below_len_without_entry'] == []
assert len({k for k, v in rows[3]['exposed_prefix']}) == 17
flat = []
for corrected in (False, True):
    n = Node()
    n.insert('target', '20px', corrected)
    n.insert('sentinel', 'sentinel', corrected)
    n.insert('target', None, corrected)
    before = n.length
    n.insert('target', '', corrected)
    flat.append({'corrected': corrected, 'removed_count': before, 'valid_empty_count': n.length,
                 'valid_empty_is_present': n.get('target') is not None})
assert flat == [{'corrected': False, 'removed_count': 2, 'valid_empty_count': 2, 'valid_empty_is_present': True},
                {'corrected': True, 'removed_count': 1, 'valid_empty_count': 2, 'valid_empty_is_present': True}]
print(json.dumps({'chain': rows, 'flat': flat, 'scope': 'literal source-shaped Python transition witness; not native execution, universal proof or Arc implementation'}, indent=2))
