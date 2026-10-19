import itertools

SENTINEL = (1 << 30) - 1
MAPPING = [[3,1,0,2],[1,3,0,2],[0,2,1,3],[2,0,1,3],[0,2,3,1],[2,0,3,1]]


def half(value):
    return (abs(value)//2) * (-1 if value < 0 else 1)


def split(axis,residual,tags,values):
    start,end = values
    if tags == [True,True]:
        return [0,residual] if axis == 0 and residual < 0 else [half(residual),residual-half(residual)]
    if tags[0]:
        return [residual,end]
    if tags[1]:
        return [start,residual]
    return [start,end]


def expected(case,version):
    result = list(case['margin'])
    reads = []
    flags = [any(case['inset_auto'][0:2]),any(case['inset_auto'][2:4])]
    for axis in [0,1]:
        sides = slice(2*axis,2*axis+2)
        tags = case['margin_auto'][sides]
        margins = case['margin'][sides]
        offsets = case['offsets'][sides]
        if version == 'candidate' and not any(tags):
            reads.append(0)
            continue
        auto = SENTINEL in offsets or (version == 'candidate' and flags[axis])
        if auto:
            residual = 0
            reads.append(0)
        else:
            raw = case['cb'][axis]-sum(offsets)
            if version == 'original':
                residual = max(0,raw-sum(margins))-case['kid'][axis]
            else:
                residual = max(0,raw)-sum(margins)-case['kid'][axis]
            reads.append(4)
        result[sides] = split(axis,residual,tags,margins)
    physical = [17,19,23,29]
    if case['property']:
        for side,index in enumerate(MAPPING[case['wm']]):
            physical[index] = result[side]
    return ' '.join(map(str,result+result+physical+reads+[1,1,15,int(flags[0]),int(flags[1])]))


def make(wm,axis,cb,kid,offsets,margins,tags,insets,family,prop=True):
    case = {'wm':wm,'property':prop,'cb':[100,100],'kid':[20,20],'offsets':[0,0,0,0],
            'margin':[2,3,2,3],'margin_auto':[False]*4,'inset_auto':[False]*4,'family':family}
    case['cb'][axis] = cb
    case['kid'][axis] = kid
    for key,values in [('offsets',offsets),('margin',margins),('margin_auto',tags),('inset_auto',insets)]:
        case[key][2*axis:2*axis+2] = values
    return case


def fixtures():
    cases = []
    for wm,axis,offsets,insets in itertools.product(range(6),[0,1],[(0,0),(10,30),(40,60),(60,60)],itertools.product([False,True],repeat=2)):
        margins = [([True,True],[0,0])]
        for fixed in [-50,0,150]:
            margins += [([True,False],[0,fixed]),([False,True],[fixed,0]),([False,False],[fixed,fixed+7])]
        for tags,values in margins:
            cases.append(make(wm,axis,100,20,list(offsets),values,tags,list(insets),'bounded'))
    for wm,axis,margin_side,insets in itertools.product(range(6),[0,1],[0,1],[(True,False),(False,True),(True,True)]):
        tags = [margin_side==0,margin_side==1]
        values = [0,-50] if margin_side==0 else [-50,0]
        offsets = [130,0] if insets[0] else [0,130]
        cases.append(make(wm,axis,100,20,offsets,values,tags,list(insets),'numeric-auto-provenance'))
    for wm,axis,side,tags in itertools.product(range(6),[0,1],[0,1],[[True,False],[False,True],[True,True]]):
        offsets = [0,0];offsets[side]=SENTINEL
        values = [0 if tag else -50 for tag in tags]
        cases.append(make(wm,axis,100,20,offsets,values,tags,[False,False],'sentinel'))
    for wm,axis,(cb,kid,offsets) in itertools.product(range(6),[0,1],[(101,20,[0,0]),(100,21,[40,60]),(100,23,[60,60])]):
        cases.append(make(wm,axis,cb,kid,offsets,[0,0],[True,True],[False,False],'odd-split'))
    for wm,axis in itertools.product(range(6),[0,1]):
        cases.append(make(wm,axis,6000,1020000000,[0,0],[1020000000,1020000000],[False,False],[False,False],'large-no-auto'))
        cases.append(make(wm,axis,100,20,[60,60],[13,-7],[False,False],[False,False],'no-property',False))
    for case in cases:
        assert all(not auto or value==0 for auto,value in zip(case['margin_auto'],case['margin']))
        values = [case['wm'],int(case['property'])]+case['cb']+case['kid']+case['offsets']+case['margin']
        values += [int(b) for b in case['margin_auto']+case['inset_auto']]
        case['input'] = ' '.join(map(str,values))
        case['candidate_expected'] = expected(case,'candidate')
        case['original_expected'] = expected(case,'original')
    return cases
