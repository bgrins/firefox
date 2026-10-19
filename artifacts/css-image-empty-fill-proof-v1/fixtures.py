from copy import deepcopy
from fractions import Fraction as F
from itertools import product
import random


def layer(**values):
    result = dict(prep=0, draw=0, alpha=F(1, 2), width=40, height=40,
                  x=0, y=0, op=0, mode=1, dirty=1, repeatx=0, repeaty=0,
                  fixed=0, clip=[0, 0, 40, 40], blend=0, clipkind=-1)
    result.update(values)
    return result


def case(layers=None, **values):
    result = dict(mode=0, selected=0, mask=1, custom=0, dirty=1, op=0,
                  env=72, flags=0, initial=F(1, 2), opacity=F(1),
                  target=[-7, 11, 53, 61], matrix=[2, 1, -1, 3, 17, -23],
                  layers=layers if layers is not None else [layer()])
    result.update(values)
    return result


def corpus():
    result = []
    outcomes = [dict(width=0), dict(height=0), dict(x=100), dict(y=-100),
                dict(alpha=F(0)), dict(alpha=F(1)), dict(prep=4), dict(prep=6)]
    for mask, selected, outcome, op, mode, dirty, custom, initial, opacity in product(
            range(2), [-1, 0], outcomes, range(4), [1, 2], range(2), range(2),
            [F(0), F(1, 2), F(1)], [F(1, 2), F(1)]):
        result.append(case([layer(op=op, mode=mode, **outcome), layer()],
            mask=mask, selected=selected, op=op, dirty=dirty, custom=custom,
            initial=initial, opacity=opacity))
    for op, mode, outcome, upper, selected in product(range(4), [1, 2], outcomes,
            [F(0), F(1, 2), F(1)], [-1, 0, 1, 2]):
        result.append(case([layer(alpha=upper), layer(op=op, mode=mode, **outcome), layer()],
            selected=selected, op=op))
    rng = random.Random(9142026)
    for i in range(2200):
        layers = []
        count = rng.randrange(4)
        for _ in range(count):
            layers.append(layer(prep=rng.choice([0, 0, 0, 4, 6]),
                draw=rng.randrange(9), alpha=F(rng.randrange(5), 4),
                width=rng.choice([0, -1, 10, 40, 60]), height=rng.choice([0, 10, 40]),
                x=rng.choice([-100, -10, 0, 10, 100]), y=rng.choice([-100, 0, 10, 100]),
                op=rng.randrange(4), mode=rng.randrange(3), dirty=rng.randrange(2),
                repeatx=rng.randrange(4), repeaty=rng.randrange(4), fixed=rng.randrange(2),
                clip=rng.choice([[0, 0, 40, 40], [5, 7, 22, 19], [0, 0, 0, 40]]),
                blend=rng.randrange(4)))
        result.append(case(layers, selected=rng.choice([-1] + list(range(count))),
            mode=int(i % 5 == 0 and count > 0), mask=rng.randrange(2),
            custom=rng.randrange(2), dirty=rng.randrange(2), op=rng.randrange(4),
            env=rng.randrange(2048), flags=rng.choice([0, 2, 4, 16, 22]),
            initial=F(rng.randrange(5), 4), opacity=F(rng.randrange(5), 4)))
    for prep, fixed, paginated, transformed, page in product([0, 4, 6], range(2),
            range(2), range(2), range(2)):
        result.append(case([layer(prep=prep, fixed=fixed)], mode=1,
            env=72+128*paginated+256*transformed+512*page, flags=4))
    for op, mode, clipkind in product(range(4), [1, 2], range(3)):
        result.append(case([layer(clipkind=clipkind), layer(width=0, op=op, mode=mode, clipkind=clipkind),
                            layer(clipkind=clipkind)], selected=-1))
    for i, entry in enumerate(result):
        entry['id'] = i
        entry['target'] = [[0, 0, 40, 40], [7, -13, 53, 61], [-21, -9, 71, 43]][i % 3]
        entry['matrix'] = [[1, 0, 0, 1, 0, 0], [2, 1, -1, 3, 17, -23],
                           [0, -2, 3, 0, -31, 5]][(i // 3) % 3]
    return result


def wire(c):
    values = [c['id'], c['mode'], len(c['layers']), c['selected'], c['mask'],
              c['custom'], c['dirty'], c['op'], c['env'], c['flags'],
              c['initial'], c['opacity'], *c['target'], *c['matrix']]
    for l in c['layers'] or [layer()]:
        values.extend([l['prep'], l['draw'], l['alpha'], l['width'], l['height'],
                       l['x'], l['y'], l['op'], l['mode'], l['dirty'],
                       l['repeatx'], l['repeaty'], l['fixed'], *l['clip'], l['blend'], l['clipkind']])
    return ' '.join(str(float(v)) if isinstance(v, F) else str(v) for v in values)


def compose(op, s, d):
    return [s + d - s*d, s - s*d, s*d, s + d - 2*s*d][op]


def combine(left, right):
    if left == 0:
        return right
    if 8 in (left, right):
        return 8
    if left in (1, 6) and right not in (0, 1):
        return right
    return left


def intersection(a, b):
    x, y = max(a[0], b[0]), max(a[1], b[1])
    w, h = min(a[0]+a[2], b[0]+b[2])-x, min(a[1]+a[3], b[1]+b[3])-y
    return [x, y, w, h] if w > 0 and h > 0 else [x, y, 0, 0]


def empty(r):
    return r[2] <= 0 or r[3] <= 0


def preparation(c, l, clip):
    transformed = bool(c['env'] & 256) if l['prep'] == 0 or l['fixed'] else False
    base = dict(ready=l['prep'] == 0, transformed=transformed, dest=[0]*4,
                fill=[0]*4, anchor=[0]*2, repeat=[0]*2, extend=0, mode=0)
    if l['prep'] != 0 or l['width'] <= 0 or l['height'] <= 0:
        return base
    x, y = l['x'], l['y']
    rx, ry = l['repeatx'], l['repeaty']
    width, height = l['width'], l['height']
    repeats = [width, height]
    if rx == 3:
        if width <= 20:
            x, repeats[0] = 0, 20
        else:
            rx = 0
    if ry == 3:
        if height <= 20:
            y, repeats[1] = 0, 20
        else:
            ry = 0
    if l['fixed'] and not transformed and c['flags'] & 4:
        clip = [0, 0, 40, 40]
    dest = [x, y, width, height]
    fill = [clip[0] if rx else x, clip[1] if ry else y,
            clip[2] if rx else width, clip[3] if ry else height]
    base.update(dest=dest, fill=intersection(fill, clip), anchor=[x, y],
                repeat=repeats, extend=(3 if ry and rx else 2 if ry else 1 if rx else 0),
                mode=l['mode'])
    return base


def oracle(c, repaired=True):
    alpha, result = c['initial'], 0
    events, prepout = [], None
    if c['mode']:
        l = c['layers'][0]
        p = preparation(c, l, l['clip'])
        prepout = [int(p['ready']), int(p['transformed']), *p['dest'], *p['fill'], *p['anchor'], *p['repeat']]
        return dict(alpha=alpha, result=l['prep'], events=['prepare:0'], preparation=prepout)
    theme = c['env'] & 1 and c['env'] & 2
    images = bool(c['mask'] or c['env'] & 8)
    if theme or not images:
        return dict(alpha=alpha, result=0, events=[], preparation=None)
    indices = reversed(range(len(c['layers']))) if c['selected'] < 0 else [c['selected']]
    for i in indices:
        l = c['layers'][i]
        clip = [0, 0, 40, 40] if c['custom'] else l['clip']
        dirty = intersection(clip, [0, 0, 40 if c['dirty'] else 0, 40])
        p = preparation(c, l, clip)
        events.append(f'prepare:{i}')
        result = combine(result, l['prep'])
        if empty(dirty) or (not c['custom'] and not l['dirty']):
            continue
        op = c['op'] if c['selected'] >= 0 else (
            (0 if i == len(c['layers'])-1 else l['op']) if c['mask'] else l['blend'])
        if not empty(p['fill']):
            events.append(f'draw:{i}:{op}')
            alpha = compose(op, l['alpha'] * c['opacity'], alpha)
            result = combine(result, l['draw'])
        elif repaired and c['mask'] and p['ready'] and op in (1, 2):
            events.append('clear:' + ','.join(map(str, c['target'])))
            alpha = F(0)
    return dict(alpha=alpha, result=result, events=events, preparation=prepout)


def discrepancies(c, row, repaired=True):
    expected = oracle(c, repaired)
    events = []
    for event in row['trace']:
        if event.startswith(('prepare:', 'clear:')):
            events.append(event)
        elif event.startswith('draw:'):
            events.append(':'.join(event.split(':')[:3]))
    errors = {}
    for key in ['result', 'preparation']:
        if row[key] != expected[key]:
            errors[key] = [row[key], expected[key]]
    if F(str(row['alpha'])) != expected['alpha']:
        errors['alpha'] = [row['alpha'], str(expected['alpha'])]
    if events != expected['events']:
        errors['events'] = [events, expected['events']]
    if row['matrix'] != c['matrix'] or row['op'] != 0:
        errors['restoration'] = [row['matrix'], row['op']]
    for i, event in enumerate(row['trace']):
        if event.startswith('clear:'):
            if row['trace'][i-2:i] != ['identity:1,0,0,1,0,0', 'get-rect']:
                errors['clear-order'] = row['trace'][max(0, i-2):i+1]
            restored = ('identity:' if c['matrix'] == [1, 0, 0, 1, 0, 0] else 'restore-transform:')
            restored += ','.join(map(str, c['matrix']))
            if row['trace'][i+1:i+2] != [restored]:
                errors['immediate-restoration'] = [row['trace'][i+1:i+2], restored]
        if event.startswith('renderer:'):
            flags = ((1 if c['flags'] & 2 else 0) + (2 if c['flags'] & 4 else 0)
                     + (4 if c['flags'] & 16 else 0)
                     + (8 if c['env'] & 64 and not c['env'] & 32 else 0))
            if int(event.split(':')[2]) != flags:
                errors['renderer-flags'] = [event, flags]
        if event.startswith('draw:'):
            parts = event.split(':')
            index = int(parts[1]); l = c['layers'][index]
            clip = [0, 0, 40, 40] if c['custom'] else l['clip']
            p = preparation(c, l, clip)
            dirty = intersection(clip, [0, 0, 40 if c['dirty'] else 0, 40])
            expected_arguments = [p['dest'], p['fill'], p['anchor'], dirty,
                                  p['repeat'], [p['mode']], [p['extend']], c['matrix']]
            actual_arguments = [[int(x) for x in part.split(',')] for part in parts[3:]]
            if actual_arguments != expected_arguments:
                errors['draw-arguments'] = [actual_arguments, expected_arguments]
    return errors
