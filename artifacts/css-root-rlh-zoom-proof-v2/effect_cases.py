import itertools

def generate():
    events = []
    ident = 0
    seeds = [0, 1, 2, 4, 7, 8, 0x80000000, 0x80000006]
    conditions = [(None, None), (0, 0), (13.25, 29.5), (13.25, None)]
    for current in range(4):
        value = 20 if current == 0 else 1.25
        events.append(dict(event='ROOT', doc=1, element=10, epoch=current + 1,
                           zoom=2, size=16, form=current, value=value))
        events.append(dict(event='PUBLISH'))
        for role, base, parent, flags, deps in itertools.product(range(3), range(2), range(4), seeds, conditions):
            ident += 1
            events.append(dict(event='READ', id=ident, role=role, unit=0, base=base,
                coefficient=1.5, owner=10020, zoom=1 if role == 1 else 4,
                parentOwner=10011, parentZoom=1, size=16, form=current, value=value,
                parentSize=20, parentForm=parent, parentValue=24 if parent == 0 else 1.25,
                initialSize=16, initialForm=current, initialValue=19 if current == 0 else 1.25,
                pc=1, call=0, diagnostic=current == 2 or parent == 2,
                flags=flags, fontDependency=deps[0], lineHeightDependency=deps[1]))
    return events

def protocol(events, base_protocol):
    lines = base_protocol(events).splitlines()
    for i, event in enumerate(events):
        if event['event'] == 'READ':
            values = [event['flags']]
            for key in ['fontDependency', 'lineHeightDependency']:
                values.extend([int(event[key] is not None), event[key] or 0])
            lines[i] += ' ' + ' '.join(map(str, values))
    return '\n'.join(lines) + '\n'
