from fractions import Fraction as F

Q = 1073741823

def nearest_even(x):
    k = x.numerator // x.denominator
    r = x - k
    return k if r < F(1, 2) or (r == F(1, 2) and k % 2 == 0) else k + 1

def ieee(x, precision):
    x = F(x)
    if not x:
        return x
    a = abs(x)
    exponent = a.numerator.bit_length() - a.denominator.bit_length()
    if a < F(2) ** exponent:
        exponent -= 1
    unit = F(2) ** (exponent + 1 - precision)
    return nearest_even(x / unit) * unit

def floor_half(x):
    x += F(1, 2)
    return x.numerator // x.denominator

def constrain(start, size):
    end = F(min(Q, max(-Q, start + size)))
    start = F(min(Q, max(-Q, start)))
    size = end - start
    if size > Q:
        start += (size - Q) / 2
        size = F(Q)
    return start, size

def pipeline(x, width, factor, route):
    f32 = lambda v: ieee(v, 24)
    f64 = lambda v: ieee(v, 53)
    px, pw = f32(f32(x) / factor), f32(f32(width) / factor)
    if route:
        sx, sw = constrain(f32(px * factor), f32(pw * factor))
        ax, aw = floor_half(sx), floor_half(sw)
        if not width:
            aw = 0
    else:
        ax, aw = x, width
    multiplier = f64(F(65536, 60))
    begin = F(floor_half(f64(f64(ax * multiplier) + F(1, 2)) - F(1, 2)), 65536)
    end = F(floor_half(f64(f64((ax + aw) * multiplier) + F(1, 2)) - F(1, 2)), 65536)
    dx, dw = f32(begin), f32(f64(end - begin))
    right = max(dx, f64(dx + dw))
    return [ax, aw, float(px), float(pw), float(begin), float(end),
            float(dx), float(dw), float(right)]

CASES = [(6000-w, w, f, r)
         for w in [0, 7200, 7208, 8168, 7864324, 8388488, 8389448, 16777217]
         for f in [30, 60, 120] for r in [0, 1]]
CASES += [(0, 1, 60, 0), (-1, 1, 60, 0), (-Q, Q, 60, 1),
          (Q-60, 120, 60, 1), (-Q, 2*Q, 60, 1)]
