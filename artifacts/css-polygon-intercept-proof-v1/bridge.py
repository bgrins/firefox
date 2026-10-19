import hashlib
import itertools
import json
import random
import re
from pathlib import Path

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[1]
BINDING = json.loads((BASE/'BINDING-v1.json').read_text())
MIN, MAX = -(1 << 31), (1 << 31) - 1
M, D = (1 << 30) - 1, (1 << 31) - 2


def sha(value):
    return hashlib.sha256(value.encode() if isinstance(value,str) else value).hexdigest()


def block(source, marker):
    if source.count(marker) != 1:
        raise ValueError('ambiguous source marker: ' + marker)
    start = source.index(marker)
    opening = source.index('{',start)
    depth, end = 1, opening+1
    while depth:
        depth += (source[end]=='{')-(source[end]=='}')
        end += 1
    return source[start:end]


def validate(candidate):
    new, old = BINDING['candidate_return'], BINDING['original_return']
    if candidate.count(new) != 1:
        raise ValueError('candidate expression changed')
    original = candidate.replace(new,old,1)
    if sha(original) != BINDING['before_sha256']:
        raise ValueError('source changed outside sole return expression')
    if sha(candidate) != BINDING['candidate_sha256']:
        raise ValueError('candidate identity changed')
    return original


def snippets(candidate, helper):
    original = validate(candidate)
    if sha(helper) != BINDING['helper_file_sha256']:
        raise ValueError('helper source identity changed')
    marker = 'nscoord nsFloatManager::PolygonShapeInfo::XInterceptAtY('
    return {'candidate.inc':block(candidate,marker),'original.inc':block(original,marker),
            'helper.inc':block(helper,'inline nscoord NSCoordMulDiv(')}


def source(candidate, helper):
    items = snippets(candidate,helper)
    alias = re.search(r'^using nscoord = int32_t;$',helper,re.M)
    if not alias:
        raise ValueError('nscoord type changed')
    declaration = '''struct nsFloatManager {
  struct PolygonShapeInfo {
    static nscoord XInterceptAtY(const nscoord, const nsPoint&, const nsPoint&);
  };
};'''
    return '\n'.join([(BASE/'prefix.cpp').read_text(),alias[0],
        'struct nsPoint { nscoord x; nscoord y; };',declaration,items['helper.inc'],
        items['candidate.inc'],'namespace before {',declaration,items['original.inc'],'}',
        (BASE/'suffix.cpp').read_text()])


def expected(row):
    x1,y1,x2,y2,y = row
    require_domain(row)
    product, denominator = (y-y1)*(x2-x1), y2-y1
    magnitude, _remainder = divmod(abs(product),denominator)
    return x1 + (-magnitude if product<0 else magnitude)


def require_domain(row):
    x1,y1,x2,y2,y = row
    if not (all(MIN<=v<=MAX for v in row) and y1<y2 and y1<=y<=y2
            and y2-y1<=D and -D<=x2-x1<=D):
        raise ValueError('fixture violates reviewed domain')


def old_defined(row):
    x1,y1,x2,y2,y=row
    return MIN <= (y-y1)*(x2-x1) <= MAX


def fixtures():
    cases = set()
    for x1,x2,y1,y2 in itertools.product(range(-4,5),repeat=4):
        if y1<y2:
            cases.update((x1,y1,x2,y2,y) for y in range(y1,y2+1))
    for x1,x2 in itertools.product([-M,-1,0,1,M],repeat=2):
        for y in [-M,-M+1,-1,0,1,M-1,M]:
            cases.add((x1,-M,x2,M,y))
    for row in [(0,0,600000,600000,12000),(5,0,4,2,1),
                (MIN,MIN,MIN+D,MIN+D,MIN+D-1),(MAX-D,MAX-D,MAX,MAX,MAX-1)]:
        cases.add(row)
    rng = random.Random(202610189)
    for _ in range(12000):
        x1,x2,y1,y2=[rng.randint(-M,M) for _ in range(4)]
        y1,y2=sorted((y1,y2))
        if y1==y2:
            continue
        tx=rng.randint(MIN-min(x1,x2),MAX-max(x1,x2))
        ty=rng.randint(MIN-y1,MAX-y2)
        y=rng.randint(y1,y2)
        cases.add((x1+tx,y1+ty,x2+tx,y2+ty,y+ty))
        if len(cases)%7==0:
            cases.add((x1+tx,y1+ty,x2+tx,y2+ty,y1+ty))
            cases.add((x1+tx,y1+ty,x2+tx,y2+ty,y2+ty))
    result=sorted(cases)
    for row in result:
        value=expected(row)
        if not min(row[0],row[2]) <= value <= max(row[0],row[2]):
            raise ValueError('oracle containment failure')
    return result
