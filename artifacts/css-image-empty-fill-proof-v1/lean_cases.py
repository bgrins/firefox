from fixtures import empty, intersection, preparation


def rat(value):
    return f'({value.numerator}/{value.denominator} : Rat)'


def generate(cases):
    lines = ['import Image', 'set_option maxRecDepth 10000',
        'def emit (id : Nat) (initial : Rat) (layers : List Image.Input) : IO Unit :=',
        '  IO.println s!"{id} {Image.newFold layers initial}"']
    names = ['add', 'subtract', 'intersect', 'exclude']
    boolean = lambda x: 'true' if x else 'false'
    for c in cases:
        inputs = []
        active = not c['mode'] and not (c['env'] & 1 and c['env'] & 2) and (c['mask'] or c['env'] & 8)
        if active:
            for i in reversed(range(len(c['layers']))):
                l = c['layers'][i]
                clip = [0, 0, 40, 40] if c['custom'] else l['clip']
                p = preparation(c, l, clip)
                prep = ('unavailable' if not p['ready'] else
                        'emptySize' if l['width'] <= 0 or l['height'] <= 0 else
                        'clipped' if empty(p['fill']) else 'covered')
                dirty = not empty(intersection(clip, [0, 0, 40 if c['dirty'] else 0, 40]))
                dirty = dirty and (c['custom'] or l['dirty'])
                op = c['op'] if c['selected'] >= 0 else l['op'] if c['mask'] else l['blend']
                fields = [boolean(c['selected'] < 0 or c['selected'] == i), boolean(dirty),
                    boolean(c['mask']), '.' + prep, boolean(c['selected'] < 0),
                    boolean(i == len(c['layers'])-1), '.' + names[op], rat(l['alpha']*c['opacity'])]
                inputs.append('⟨' + ', '.join(fields) + '⟩')
        if c['id'] % 64 == 0:
            lines.append('#eval do')
        lines.append(f"  emit {c['id']} {rat(c['initial'])} [{', '.join(inputs)}]")
    return '\n'.join(lines) + '\n'
