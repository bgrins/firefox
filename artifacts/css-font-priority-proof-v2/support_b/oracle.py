import struct
from fractions import Fraction

PIVOT = 2816
ITALIC = 25600


def phase_visit(lo, hi, phases):
    for phase, (start, end, direction) in enumerate(phases):
        left, right = max(lo, min(start, end)), min(hi, max(start, end))
        if left <= right:
            angle = left if direction == 1 else right
            return phase, abs(angle - start)
    raise ValueError('range outside oracle domain')


def interval_visit(lo, hi, target, threshold=PIVOT):
    assert 0 < lo <= hi <= 23040 and 0 < target <= 23040
    if target >= threshold:
        phases = [(target, 23040, 1), (target, 1, -1)]
    else:
        phases = [(target, 1, -1), (target, 23040, 1)]
    return phase_visit(lo, hi, phases)


def spec_style(lo, hi, target):
    if target == ITALIC and 0 < lo <= hi <= 23040:
        return phase_visit(lo, hi, [(PIVOT, 23040, 1), (PIVOT, 1, -1)])
    if 0 < lo <= hi <= 23040 and 0 < target <= 23040:
        return interval_visit(lo, hi, target)
    if -23040 <= lo <= hi < 0 and -23040 <= target < 0:
        return interval_visit(-hi, -lo, -target)
    raise ValueError('cross-kind policy excluded')


def legacy_style(lo, hi, target, allow, threshold):
    if target in (lo, hi): return 0
    if target == 0:
        if ITALIC in (lo, hi): return 179200
        return lo if lo >= 0 else 0 if hi >= 0 else 51200 - hi
    if target == ITALIC:
        aim, bad = (threshold, 0) if allow else (0, 102400)
        if lo >= aim: return bad + lo - aim + 256
        if hi >= aim: return bad + 256
        return bad + (25600 if hi > 0 else 76800) + aim - hi
    if ITALIC in (lo, hi): return 179200
    if target >= threshold:
        if lo >= target: return lo - target
        if hi >= target: return 0
        return (25600 if hi > 0 else 76800) + target - hi
    if target <= -threshold:
        if hi <= target: return target - hi
        if lo <= target: return 0
        return (25600 if lo < 0 else 76800) + lo - target
    if target >= 0:
        if lo > target: return 25600 + lo - target
        if hi >= target: return 0
        return target - hi if hi > 0 else 76800 + target - hi
    if hi < target: return 25600 + target - hi
    if lo <= target: return 0
    return lo - target if lo < 0 else 76800 + lo - target


def width_distance(lo, hi, target):
    if lo <= target <= hi: return Fraction(0)
    distance = lo - target if target < lo else target - hi
    penalty = (target < lo) == (target <= 6400)
    return Fraction(distance, 64) + 1000 * penalty


def weight_distance(lo, hi, target):
    if lo <= target <= hi: return Fraction(0)
    if target < lo:
        penalty = 0 if target > 32000 or 25600 <= target and lo <= 32000 else 600
        return Fraction(lo-target,64)+penalty
    penalty = 0 if target < 25600 else 100 if target <= 32000 else 600
    return Fraction(target-hi,64)+penalty


def float32(x):
    return struct.unpack('f',struct.pack('f',float(x)))[0]


def coordinates(case, face, variant):
    target=3584 if case['target']==30000 else case['target']
    lo,hi,wl,wh,xl,xh=face[:6]
    return (width_distance(xl,xh,case['width']),
            Fraction(legacy_style(lo,hi,target,case['allow'],2816 if variant in ('B','AB') else 3584),256),
            weight_distance(wl,wh,case['weight']))


def key(case, face, variant, fallback=False):
    coords=coordinates(case,face,variant)
    mismatch=bool(case['presentation'] and bool(face[9]) != (case['presentation']>=3)) if fallback else False
    if variant in ('A','AB'): return (int(mismatch),)+coords
    value=coords[0]*100000000+coords[1]*10000+coords[2]+int(mismatch)*1000000000000
    return float32(value) if case['operation'] in (3,5,6,10) else value


def successive_filter(ids, value):
    result=list(ids)
    for coordinate in range(4):
        if result:
            best=min(value(i)[coordinate] for i in result)
            result=[i for i in result if value(i)[coordinate]==best]
    return result


def selected(case,variant,gtk=False):
    faces=case['faces'];op=case['operation'];flags=case['flags'];count=len(faces)
    if op==0:return []
    if op==8:return [3584,14]
    if op in (9,12): return case['expected']
    if op in (6,7,10,11): return case['expected'][variant] if isinstance(case['expected'],dict) else case['expected']
    ids=list(range(count))
    if flags&256 and count>1: ids[-1]=0
    if op in (1,5): ids.reverse()
    if op==2:
        if flags&3: return []
        ids=[i for i in ids if faces[i][12]!=2]
        if count==1 and not faces[0][11]: return []
        if flags&64: return case['expected']
    if op in (1,2,5):
        if variant in ('A','AB'):
            ids=successive_filter(ids,lambda i:(0,)+coordinates(case,faces[i],variant))
        elif ids:
            best=min(key(case,faces[i],variant) for i in ids)
            ids=[i for i in ids if key(case,faces[i],variant)==best]
        if op in (1,5): ids=[i for j,i in enumerate(ids) if not j or i!=ids[j-1]]
        if op==2 and gtk and any(faces[i][13] for i in ids):
            sizes=[faces[i][13] for i in ids if faces[i][13] and abs(faces[i][13]-20)*5<=faces[i][13]]
            size=min(sizes,key=lambda s:abs(s-20)) if sizes else 0
            ids=[i for i in ids if faces[i][13]==size]
        if op in (1,2):return ids
    if flags&16 or op==4 and (flags&2 or flags&4 and flags&8):return []
    if op==3: ids=list(reversed(ids))
    if op==4: ids=[i for i in ids if faces[i][12]!=2]
    if op==5:
        matches=[i for i in ids if not faces[i][7] and faces[i][6]]
        if matches:
            for i in matches:
                if not case['presentation'] or faces[i][8]:return [i]
            return [matches[-1]]
        target=3584 if case['target']==30000 else case['target']
        if target==0 and case['weight']==25600 and case['width']==6400:return []
        ids=list(reversed(range(count)))
    ids=[i for i in ids if faces[i][6] and (op!=4 or faces[i][12]) and (not case['presentation'] or faces[i][8])]
    if not ids:return []
    if variant in ('A','AB'):
        best=successive_filter(ids,lambda i:key(case,faces[i],variant,True))
    else:
        score=min(key(case,faces[i],variant,True) for i in ids)
        best=[i for i in ids if key(case,faces[i],variant,True)==score]
    if op==4:return [best[0]]
    return [min(best) if flags&128 else max(best)]
