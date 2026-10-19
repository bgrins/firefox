import random
from support_b import corpus


def generate():
    cases=corpus.generate()
    case,face=corpus.case,corpus.face
    for requested_weight in (31999,32000,32001,38399,38400,38401,64000):
        for target in (0,1,25600):
            for op in (9,12):
                for mask in range(1,16):
                    fs=[face(25600 if i&2 else 0,weightLo=44800 if i&1 else 25600,weightHi=44800 if i&1 else 25600) for i in range(4) if mask&(1<<i)]
                    cases.append(case(f'simple-slots:{op}:{mask}:{requested_weight}:{target}',fs,target,operation=op,weight=requested_weight))
    for op in (9,12):
        for name,fs in [
            ('same-nonnormal-width',[face(0,widthLo=6300,widthHi=6300),face(25600,widthLo=6300,widthHi=6300)]),
            ('oblique',[face(0),face(1)]),
            ('varying-weight',[face(0,weightLo=25600,weightHi=44800),face(25600)]),
            ('varying-width',[face(0,widthLo=6200,widthHi=6400),face(25600)]),
            ('one-range',[face(1,23040)]),
            ('more-than-four',[face(0) for _ in range(5)])]:
            cases.append(case(f'simple-boundary:{op}:{name}',fs,operation=op))
    rng=random.Random(0xA20261018)
    for n in range(240):
        fs=[]
        for _ in range(rng.randint(1,8)):
            lo,hi=sorted([rng.randint(-23040,23040),rng.randint(-23040,23040)])
            if rng.randrange(4)==0:lo=hi=rng.choice([0,25600,1,2816,3584])
            f=face(lo,hi,coverage=rng.randrange(2),skip=rng.randrange(2),ready=rng.randrange(2),color=rng.randrange(2),known=rng.randrange(2),present=rng.choice([0,1]),size=rng.choice([0,0,0,8,17,20,22,25]))
            f[2:4]=sorted(rng.choices([64,25599,25600,25601,32000,38399,38400,64000],k=2))
            f[4:6]=sorted(rng.choices([0,1,6399,6400,6401,64000],k=2))
            fs.append(f)
        for op in (1,2,3,4,5,6,7,10,11):
            flags=rng.choice([0,0,0,4,12,16,32,128,256,512,1024,2048,4096,16388])
            cases.append(case(f'provider-random:{n}:{op}',fs,target=rng.choice([0,1,-1,2816,3584,25600,30000]),operation=op,allow=rng.randrange(2),presentation=rng.randrange(5),weight=rng.choice([64,25600,32000,38400,64000]),width=rng.choice([0,6399,6400,6401,64000]),flags=flags))
    for op in range(1,6):
        cases.append(case(f'mutation-width-priority:{op}',[face(25600,widthLo=6401,widthHi=6401),face(0,widthLo=6402,widthHi=6402)],target=0,operation=op,width=6401))
        cases.append(case(f'mutation-style-priority:{op}',[face(0,weightLo=64000,weightHi=64000),face(1)],target=0,operation=op))
        cases.append(case(f'mutation-float-key:{op}',[face(0,weightLo=25601,weightHi=25601,widthLo=6401,widthHi=6401),face(0,widthLo=6401,widthHi=6401)],target=0,operation=op))
        cases.append(case(f'mutation-weights-overlap:{op}',[face(0,weightLo=64000,weightHi=64000),face(0)],target=0,operation=op))
    cases.append(case('adapter-abi',[],operation=13))
    for i,c in enumerate(cases):c['id']=i;c.pop('expected',None)
    return cases
