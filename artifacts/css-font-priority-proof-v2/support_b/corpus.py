import json
import random
import re
from pathlib import Path

BASE=Path(__file__).resolve().parent


def face(lo=3072,hi=None,**kw):
    values=[lo,lo if hi is None else hi,25600,25600,6400,6400,1,0,1,0,1,1,1,0]
    fields={'weightLo':2,'weightHi':3,'widthLo':4,'widthHi':5,'coverage':6,'skip':7,'ready':8,'color':9,'known':10,'valid':11,'present':12,'size':13}
    for key,value in kw.items():values[fields[key]]=value
    return values


def case(name,faces=None,target=3072,operation=1,allow=1,presentation=0,weight=25600,width=6400,flags=0,expected=None):
    return dict(name=name,faces=[face()] if faces is None else faces,target=target,operation=operation,allow=allow,presentation=presentation,weight=weight,width=width,flags=flags,expected=expected)


def parse_range(value,kind):
    if kind=='style':
        if value=='normal':return (0,0)
        if value=='italic':return (25600,25600)
        if value=='oblique':return (3584,3584)
        ns=[round(float(x)*256) for x in re.findall(r'(-?[\d.]+)deg',value)]
    else:ns=[round(float(x)*64) for x in value.replace('%','').split()]
    return ns[0],ns[-1]


def generate():
    cases=[]
    for table in ('threshold','lexicographic'):
        rows=json.loads((BASE/'design/wpt-proposals'/f'{table}-cases.json').read_text())
        for row in rows:
            descriptors=[]
            for d in row['faces']:
                lo,hi=parse_range(d['style'],'style');f=face(lo,hi)
                f[2:4]=parse_range(d['weight'],'weight');f[4:6]=parse_range(d['width'],'width');descriptors.append(f)
            request=row['request']
            for reverse in (False,True):
                for op in range(1,6):
                    cases.append(case(f'{table}:{row["name"]}:reverse={reverse}:op={op}',list(reversed(descriptors)) if reverse else descriptors,
                        target=30000 if request['style']=='oblique' else parse_range(request['style'],'style')[0],operation=op,
                        weight=parse_range(request['weight'],'weight')[0],width=parse_range(request['width'],'width')[0]))
    boundary=[-23040,-3584,-3583,-3072,-2817,-2816,-2815,-1,0,1,2815,2816,2817,3072,3583,3584,23040]
    for target in boundary+[25600,30000]:
        for allow in (0,1):
            for i,lo in enumerate(boundary):
                for hi in boundary[i:]:
                    cases.append(case(f'boundary:{target}:{lo}:{hi}:{allow}',[face(lo,hi)],target=target,allow=allow,operation=0))
            cases.append(case(f'italic-face:{target}:{allow}',[face(25600)],target=target,allow=allow,operation=0))
    rng=random.Random(0x112026)
    for n in range(260):
        target=rng.choice([-1,1])*rng.randint(1,23040)
        fs=[]
        for _ in range(rng.randint(2,7)):
            lo,hi=sorted([rng.randint(1,23040),rng.randint(1,23040)])
            if target<0:lo,hi=-hi,-lo
            fs.append(face(lo,hi))
        for op in range(1,6):cases.append(case(f'random-same-sign:{n}:op={op}',fs,target,operation=op))
    for n in range(120):
        fs=[face(*sorted([rng.randint(1,23040),rng.randint(1,23040)])) for _ in range(rng.randint(2,7))]
        for op in range(1,6):
            for allow in (0,1):cases.append(case(f'random-italic:{n}:allow={allow}:op={op}',fs,target=25600,operation=op,allow=allow))
    for n in range(100):
        fs=[]
        for _ in range(rng.randint(2,7)):
            lo,hi=sorted([rng.randint(1,23040),rng.randint(1,23040)])
            f=face(lo,hi)
            f[2:4]=sorted([rng.randint(64,64000),rng.randint(64,64000)])
            f[4:6]=sorted([rng.randint(0,64000),rng.randint(0,64000)])
            fs.append(f)
        for op in range(1,6):cases.append(case(f'random-coordinates:{n}:op={op}',fs,operation=op,weight=rng.randint(64,64000),width=rng.randint(0,64000)))
    for op in range(1,6):
        for name,fs,options in [
            ('tie',[face(),face()],{}),('tie-reverse-name',[face(),face()],{'flags':128}),
            ('duplicate',[face(),face(),face()],{'flags':256}),
            ('improvement-clears-ties',[face(),face(3584),face(3584)],{}),
            ('overlap',[face(2816,3584),face(2560,3584)],{}),
            ('glyph-absent',[face(3584,coverage=0),face(2560)],{}),
            ('skipped',[face(3584,skip=1),face(2560)],{}),
            ('missing-map',[face(3584,known=0),face(2560)],{}),
            ('lazy-missing-glyph',[face(3584,known=0,coverage=0),face(2560)],{}),
            ('failed-font',[face(3584,ready=0),face(2560)],{'presentation':2}),
            ('presentation-mismatch-incumbent',[face(2560,color=1),face(3584,color=0)],{'presentation':2}),
            ('presentation-text',[face(3584,color=1),face(2560,color=0)],{'presentation':1}),
            ('mismatch-only',[face(),face(3584)],{'presentation':2}),
            ('family-no-glyph',[face(),face()],{'flags':16}),
            ('zero-spanning',[face(-256,3584),face(3584)],{'target':0}),
            ('oblique-only',[face(256),face(3072)],{'target':25600,'allow':0}),
            ('exact-italic',[face(2816),face(25600)],{'target':25600}),
            ('normal-legacy-cross-kind',[face(-256),face(25600)],{'target':0}),
            ('last-resort-weight',[face(3072,weightLo=64000,weightHi=64000),face(3072)],{'target':25600,'allow':0}),
        ]:cases.append(case(f'provider:{name}:op={op}',fs,operation=op,**options))
    for name,fs,options in [
        ('uninitialized',[face(),face()],{'flags':1}),
        ('unavailable-faces',[face(),face()],{'flags':2}),
        ('mapped-null',[face(present=2),face()],{}),
        ('invalid-single',[face(valid=0)],{}),
        ('bitmap-nearest',[face(size=20),face(size=23),face()],{}),
        ('bitmap-outside',[face(size=8),face()],{}),
        ('bitmap-none',[face(size=8),face(size=9)],{}),
    ]:cases.append(case(f'shared:{name}',fs,operation=2,**options))
    for flags in (4,12,16388,32):cases.append(case(f'provider-flags:{flags}',[face(),face(3584)],operation=4 if flags!=32 else 3,flags=flags))
    cases.append(case('shared-missing-entry',[face(present=0),face(3584)],operation=4))
    for op in (0,3,4,7,10,11):cases.append(case(f'empty:op={op}',[],operation=op,expected=[]))
    for op in (9,12):
        cases.extend([
            case(f'simple-normal:{op}',[face(0),face(25600)],target=0,operation=op,expected=[1,0]),
            case(f'simple-italic:{op}',[face(0),face(25600)],target=25600,operation=op,expected=[1,1]),
            case(f'range-not-simple:{op}',[face(2816,3072),face(3584)],operation=op,expected=[0,0]),
            case(f'duplicate-slot-not-simple:{op}',[face(0),face(0)],target=0,operation=op,expected=[0,1,0] if op==9 else [0,0,1]),
        ])
    for op in (10,11):
        for name,fs,options,expected in [
            ('zero-stops',[face(),face()],{},[0]),
            ('mismatch-does-not-stop',[face(),face(color=1)],{'presentation':2},[1]),
            ('mismatch-only',[face(),face(3584)],{'presentation':2},{'original':[0],'B':[1],'A':[0],'AB':[0]} if op==10 else [0]),
            ('name-tie',[face(3584),face(3584)],{},[1] if op==10 else [0]),
            ('hidden-first',[face(),face()],{'flags':1024},[1]),
            ('glyph-first-absent',[face(coverage=0),face()],{},[1]),
            ('failed-zero-font',[face(ready=0),face()],{},[]),
        ]:cases.append(case(f'global:{name}:op={op}',fs,operation=op,expected=expected,**options))
    cases.extend([
        case('global-async',[face(),face()],operation=11,flags=2048,expected=[1]),
        case('global-list-unavailable',[face(),face()],operation=11,flags=4096,expected=[]),
        case('platform-shortcut',[face(2560),face()],operation=6,flags=512,expected=[0]),
        case('platform-mismatch-fallthrough',[face(2560),face(color=1)],operation=6,flags=512,presentation=2,expected=[1]),
        case('actual-default-and-roundtrip',[],operation=8),
    ])
    for c in cases:
        if c['presentation']==2:c['presentation']=3
    for op in range(1,6):
        cases.append(case(f'explicit-text:{op}',[face(3584,color=1),face(2560,color=0)],operation=op,presentation=2))
        cases.append(case(f'explicit-emoji:{op}',[face(3584,color=0),face(2560,color=1)],operation=op,presentation=4))
    for i,c in enumerate(cases):c['id']=i
    return cases


def wire(cases):
    return '\n'.join(' '.join(map(str,[c['id'],c['operation'],c['target'],c['allow'],c['presentation'],len(c['faces']),c['weight'],c['width'],c['flags']]+[x for f in c['faces'] for x in f])) for c in cases)+'\n'
