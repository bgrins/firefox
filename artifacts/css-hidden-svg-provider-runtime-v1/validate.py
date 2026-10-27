import json
import math
import sys


def validate(payload):
    assert payload['compatMode'] == 'CSS1Compat'
    assert payload['scroll'] == [0, 0]
    definitions = [(method, viewbox, hidden)
                   for method in ('getCTM', 'getScreenCTM')
                   for viewbox in (True, False) for hidden in (False, True)]
    assert len(payload['rows']) == len(definitions)
    rows = []
    for row, (method, viewbox, hidden) in zip(payload['rows'], definitions):
        key = f"{method}-{'viewBox' if viewbox else 'no-viewBox'}-{'hidden' if hidden else 'visible'}"
        assert row['key'] == key
        assert (row['method'], row['viewBox'], row['hidden']) == (method, viewbox, hidden)
        origin = [20, 30] if method == 'getScreenCTM' else [0, 0]
        warm = [1, 0, 0, 1, *origin]
        changed = [2 if viewbox else 1, 0, 0, 1, *origin]
        for field in ('warm', 'twinWarm', 'first', 'repeat', 'twinChanged', 'afterBBox',
                      'afterLayout', 'revealed', 'restored', 'twinRestored'):
            value = row[field]
            assert value is None or (isinstance(value, list) and len(value) == 6
                                    and all(type(x) in (int, float) and math.isfinite(x) for x in value))
        for field in ('warmHost', 'hiddenHost', 'hostChanged', 'twinHostChanged',
                      'bbox', 'forcedRect', 'restoredHost'):
            assert len(row[field]) == 4
            assert all(type(x) in (int, float) and math.isfinite(x) for x in row[field])
        checks = {
            'warm': row['warm'] == warm and row['twinWarm'] == warm,
            'warmHost': row['warmHost'] == [20, 30, 100, 100],
            'hiddenHost': row['hiddenHost'] == [20, 30, 100, 100],
            'changedHosts': row['hostChanged'] == row['twinHostChanged'] == [20, 30, 200, 100],
            'visibleTwin': row['twinChanged'] == changed,
            'policy': row['policy'] == ('hidden' if hidden else 'visible'),
            'forcedViewport': row['forcedRect'] == [20, 30, 200, 100],
            'restored': row['restored'] == row['twinRestored'] == warm
                        and row['restoredHost'] == [20, 30, 100, 100],
        }
        matches = {field: row[field] == changed
                   for field in ('first', 'repeat', 'afterBBox', 'afterLayout', 'revealed')}
        rows.append({'key': key, 'calibrated': all(checks.values()), 'checks': checks,
                     'stable': row['first'] == row['repeat'], 'expected': changed,
                     'matched': matches['first'], 'matches': matches,
                     'bboxMatchesLocalShape': row['bbox'] == [10, 20, 30, 40],
                     'observations': row})
    return {'rows': rows, 'calibrated': sum(r['calibrated'] for r in rows),
            'stable': sum(r['stable'] for r in rows),
            'matched': sum(r['matched'] for r in rows),
            'mismatched': sum(not r['matched'] for r in rows)}


if __name__ == '__main__':
    print(json.dumps(validate(json.load(open(sys.argv[1]))), indent=2))
