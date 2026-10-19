from fractions import Fraction as Q
import struct

def bits(value):
    return struct.unpack('I', struct.pack('f', value))[0]

def expected_effect(event, mutation=0):
    seed = event['flags']
    selected_normal = event['role'] == 0 and (event['form'] if event['base'] == 0 else event['parentForm']) == 2
    added = (2 if event['base'] == 0 else 4) if selected_normal else 0
    if mutation == 1:
        flags = seed | added
    elif mutation == 2:
        flags = seed | 1
    elif mutation == 3:
        flags = 1 | added
    else:
        flags = seed | 1 | added
    return dict(flags=flags, font_present=event['fontDependency'] is not None,
        lh_present=event['lineHeightDependency'] is not None,
        font_dependency=bits(event['fontDependency'] or 0),
        lh_dependency=bits(event['lineHeightDependency'] or 0))

def semantic(event, root, original=False):
    def line(tag, size, value, zoom):
        if tag == 0:
            return Q(value)
        if tag in [1, 3]:
            return Q(size) * Q(value)
        assert event['pc'] == 1
        return Q(size) + Q(3) / zoom
    current = line(root['form'], root['size'], root['value'], Q(root['zoom']))
    parent = line(event['parentForm'], event['parentSize'], event['parentValue'], Q(event['parentZoom']))
    initial = line(event['initialForm'], event['initialSize'], event['initialValue'], Q(1))
    role = event['role']
    value = (current if event['base'] == 0 else parent) if role == 0 else initial if role == 1 else current
    zoom = Q(root['zoom']) if role == 0 else Q(event['zoom'])
    if original and role == 0:
        value *= zoom
    exposed = value * Q(event['coefficient'])
    return exposed * zoom, exposed
