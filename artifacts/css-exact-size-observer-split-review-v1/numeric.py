import json
import math
import struct


def f32(value):
    return struct.unpack('f', struct.pack('f', value))[0]


def rounded_edge(value):
    return math.floor(value * (65536 / 60) + 0.5) / 65536


rows = []
for width in [7208, 7864324, 8388488, 8389448]:
    for edge in [6000, 6006]:
        x = edge - width
        gx = math.floor(f32(f32(f32(x) / 60) * 60) + 0.5)
        gw = math.floor(f32(f32(f32(width) / 60) * 60) + 0.5)
        variants = {}
        for integer_path in [False, True]:
            for double_dom in [False, True]:
                px, pw = (x, width) if integer_path else (gx, gw)
                start = rounded_edge(px)
                size = rounded_edge(px + pw) - start
                if not double_dom:
                    start, size = f32(start), f32(size)
                name = ('both' if double_dom else 'integer-only') if integer_path else ('dom-only' if double_dom else 'baseline')
                variants[name] = start + size
        rows.append({'widthAU': width, 'edgeAU': edge, 'xAU': x,
                     'conditionalGfxRectAU': {'x': gx, 'width': gw},
                     'variants': variants})

print(json.dumps({'scope': 'Conditional scalar float rectangle model plus double/float DOM transport; not a full native matrix or browser trace.', 'rows': rows}, indent=2))
