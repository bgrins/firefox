from copy import deepcopy


def marker(side):
    return dict(width=0,intrinsic=0,style=side,overflow=False,block=-1,
                initialized=False,active=False,edge=False)


def packed(m):
    return [int(m[k]) for k in ["width","intrinsic","style","overflow","block",
                               "initialized","active","edge"]]


def markers(ms):
    return packed(ms[0])+packed(ms[1])


def reset(m):
    m.update(overflow=False,block=-1,edge=False)


def rect(start,end):
    return [start,0,end-start,1]


def shrink_start(r,width):
    return [r[0]+width,r[1],max(r[2]-width,0),r[3]]


def shrink_end(r,width):
    return [r[0],r[1],max(r[2]-width,0),r[3]]


def intersect(a,b):
    i,j=max(a[0],b[0]),max(a[1],b[1])
    w,h=min(a[0]+a[2],b[0]+b[2])-i,min(a[1]+a[3],b[1]+b[3])-j
    return [i,j,0,0] if min(w,h)<0 else [i,j,w,h]


def block_style(m,line):
    return line["clamp"] if m["block"]>=0 else None


def has_block(m,line):
    s=block_style(m,line)
    return s is not None and s[0]!=0 and (s[0]!=2 or s[2]!=0)


def needed(m,line):
    return m["overflow"] or has_block(m,line)


def suppressed(m,c,line):
    return not has_block(m,line) if m["block"]>=0 else c["styles"][m["style"]]["kind"]==0


def measure(m,c,line,events):
    if m["initialized"]:return
    block=block_style(m,line)
    normal=c["styles"][m["style"]]
    kind=block[0] if block is not None else normal["kind"]
    if kind==1:
        width=0 if c["ellipsisFailure"] else c["ellipsisWidth"]
        events.append([2,-1,width,int(c["ellipsisFailure"])])
    else:
        assert kind==2
        width=block[1] if block is not None else normal["width"]
        events.append([2,m["block"] if block is not None else m["style"],width,0])
    m.update(width=width,intrinsic=width,initialized=True)


def initial(c):
    ms=[marker(0),marker(1)]
    if c["seed"]:
        for m in ms:
            s=c["styles"][m["style"]]
            width=0 if s["kind"]==0 else (0 if c["ellipsisFailure"] else c["ellipsisWidth"]) if s["kind"]==1 else s["width"]
            m.update(width=width,intrinsic=width,initialized=True)
    return ms


def observations(line,content,inside,ms):
    nodes=line["frames"]
    reachable=[]
    for index,node in enumerate(nodes):
        parent=node["parent"]
        if parent>=0 and (parent not in reachable or nodes[parent]["role"] in [2,3,4]):continue
        reachable.append(index)
    left,right=inside[0],inside[0]+inside[2]
    c0,c1=content[0],content[0]+content[2]
    effects=[]
    for index in reachable:
        f=nodes[index]
        if f["role"] in [3,4] or not f["visible"]:continue
        a,b=f["start"],f["start"]+f["size"]
        ov=[f["overflow"][0]<c0,f["overflow"][1]>c1]
        effect=dict(overflow=ov,hidden=False,inner=None,outer=None,clip=[None,None],visible=False,id=index)
        effects.append(effect)
        if f["role"]==2 and any(m["active"] and o for m,o in zip(ms,ov)):
            effect["hidden"]=True
            continue
        if f["role"] not in [1,2]:continue
        overlap=[max(left-a,0),max(b-right,0)]
        effect["clip"]=[a if overlap[0]>0 else None,b if overlap[1]>0 else None]
        cuts=[v if m["active"] else 0 for v,m in zip(overlap,ms)]
        crossing=(cuts[0]>0 and left<=b) or (cuts[1]>0 and a<=right)
        outside=left>b or a>right
        if crossing:
            if f["role"]==2:effect["hidden"]=True
            elif left<right and f["nonsuppressed"]:
                position=0;clusters=[]
                for advance in f["advances"]:
                    end=position+advance
                    if position>=cuts[0] and end<=f["size"]-cuts[1]:clusters.append((position,end))
                    position=end
                if clusters:
                    effect["inner"]=(a+clusters[0][0] if cuts[0]>0 else a,
                                     a+clusters[-1][1] if cuts[1]>0 else b)
                    effect["visible"]=True
        elif outside:
            if left>b:effect["outer"]=b
            effect["hidden"]=f["role"]==2
        else:
            effect["inner"]=(a,b)
            effect["visible"]=f["role"]==2 or f["nonsuppressed"]
    return effects


def analysis(line,content,inside,ms,alignment,hidden):
    effects=observations(line,content,inside,ms)
    for side in [0,1]:ms[side]["overflow"] |= any(e["overflow"][side] for e in effects)
    hidden.update(e["id"] for e in effects if e["hidden"])
    inners=[e["inner"] for e in effects if e["inner"] is not None]
    if alignment[3]:inners.append((alignment[0],alignment[1]))
    if inners:
        alignment[0]=min(x[0] for x in inners);alignment[1]=max(x[1] for x in inners);alignment[3]=True
    alignment[2]=max([alignment[2]]+[e["outer"] for e in effects if e["outer"] is not None])
    starts=[e["clip"][0] for e in effects if e["clip"][0] is not None]
    ends=[e["clip"][1] for e in effects if e["clip"][1] is not None]
    clips=[max(starts) if starts else 0,min(ends) if ends else 0,bool(starts),bool(ends)]
    return any(e["visible"] for e in effects),clips


def kernel(c,line,ms,events):
    suppress=[suppressed(m,c,line) for m in ms]
    if c["scroll"]:
        pos,low,high=c["scroll"]
        suppress[0] |= pos<=low
        suppress[1] |= pos>=high and not has_block(ms[1],line)
    area=rect(c["start"],c["start"]+c["width"])
    snapping=[True,True]
    if line["floats"]:
        lo,hi=line["floats"]
        if hi<area[0]+area[2]:area[2]=max(0,hi-area[0]);snapping[1]=False
        if lo>area[0]:area=shrink_start(area,lo-area[0]);snapping[0]=False
    analysis_area=area[:]
    if c["snap"]:
        if snapping[0]:analysis_area=shrink_start(analysis_area,-c["units"])
        if snapping[1]:analysis_area=shrink_end(analysis_area,-c["units"])
    wants=[not suppress[0] and line["overflow"][0]<analysis_area[0],
           not suppress[1] and (line["overflow"][1]>analysis_area[0]+analysis_area[2] or has_block(ms[1],line))]
    hidden=set();alignment=[0,0,0,False]
    if not any(wants):return area,hidden,alignment
    for side in [0,1]:ms[side]["active"]=wants[side]
    ms[0]["edge"]=bool(c["scroll"]) and wants[0]
    ms[1]["edge"]=bool(c["scroll"]) and not suppress[1] and line["overflow"][1]>analysis_area[0]+analysis_area[2]
    guesses=wants[:];clipped=[False,False];retry=True;pass_number=0
    for attempt in range(12):
        for side in [0,1]:
            if guesses[side]:measure(ms[side],c,line,events)
        reservation=[m["width"] if m["active"] else 0 for m in ms]
        if all(reservation) and sum(reservation)>analysis_area[2]:reservation[0]=0
        inside=area[:]
        if guesses[0]:inside=shrink_start(inside,reservation[0])
        if guesses[1]:inside=shrink_end(inside,reservation[1])
        visible,clips=analysis(line,analysis_area,inside,ms,alignment,hidden)
        events.append([1,*analysis_area,*inside,*markers(ms),int(visible),
                       *map(int,alignment),*map(int,clips),len(hidden),*sorted(hidden)])
        if not visible and retry:
            alignment[2]=0;alignment[3]=False;hidden.clear();pass_number=0
            eligible=[side for side in [0,1] if needed(ms[side],line) and ms[side]["active"] and not clipped[side]]
            if eligible:
                side=eligible[0]
                available=clips[0]-area[0] if side==0 else area[0]+area[2]-clips[1]
                if clips[2+side] and available>0:
                    assert available<ms[side]["intrinsic"]
                    ms[side]["width"]=available;clipped[side]=True
                else:ms[side]["active"]=False;guesses[side]=False
            else:
                retry=False
                for side in [0,1]:
                    ms[side]["width"]=ms[side]["intrinsic"]
                    ms[side]["active"]=wants[side];guesses[side]=wants[side]
                if needed(ms[1],line) and ms[1]["active"] and has_block(ms[1],line):
                    assert area[0]>alignment[2]
                    ms[1]["width"]=max(ms[1]["intrinsic"]-area[0]+alignment[2],0)
            continue
        observed=[m["active"] and needed(m,line) for m in ms]
        if guesses==observed:break
        guesses=observed;block=ms[1]["block"]
        for m in ms:reset(m)
        ms[1]["block"]=block;hidden.clear()
        assert pass_number==0
        pass_number+=1
        if pass_number==2:break
    else:raise AssertionError("retry bound")
    for side in [0,1]:
        if not wants[side] or not ms[side]["active"]:reset(ms[side])
    return area,hidden,alignment


def process(c,line,number,ms,candidate=True):
    events=[[0,*markers(ms)]]
    if all(s["kind"]==0 for s in c["styles"]) and line["clamp"] is None:
        return events+[[9,*markers(ms)]]
    reset(ms[0])
    if candidate:ms[0]["width"]=ms[0]["intrinsic"]
    ms[0]["active"]=c["styles"][0]["kind"]!=0
    reset(ms[1])
    if candidate:ms[1]["width"]=ms[1]["intrinsic"]
    previous=deepcopy(ms[1]) if line["clamp"] is not None else None
    if previous is not None:ms[1].update(block=number+2,initialized=False)
    ms[1]["active"]=not suppressed(ms[1],c,line)
    area,hidden,alignment=kernel(c,line,ms,events)
    needs=[needed(m,line) for m in ms]
    if any(needs):
        assert not (suppressed(ms[0],c,line) and needs[0])
        assert not (suppressed(ms[1],c,line) and needs[1])
        if all(needs) and sum(m["width"] for m in ms)>area[2]:needs[0]=False
        inside=area[:]
        if needs[0]:inside=shrink_start(inside,ms[0]["width"])
        if needs[1]:inside=shrink_end(inside,ms[1]["width"])
        if alignment[3]:
            if ms[0]["edge"]:alignment[0]=inside[0]
            if ms[1]["edge"]:alignment[1]=inside[0]+inside[2]
            inside=intersect(inside,rect(alignment[0],alignment[1]))
        elif has_block(ms[1],line):inside=rect(alignment[2],alignment[2])
        for list_id in [0,1]:events.append([3,list_id,*inside,*markers(ms),len(hidden),*sorted(hidden)])
        events.append([4,*map(int,needs),number,*inside,*area,*markers(ms)])
        if previous is not None:ms[1]=previous
    return events+[[9,*markers(ms)]]


def run(c,candidate=True):
    ms=initial(c);rows={}
    for number,line in enumerate(c["lines"]):
        fresh=deepcopy(ms)
        for m in fresh:m["width"]=m["intrinsic"];reset(m)
        rows[(c["id"],number,"reuse")]=process(c,line,number,ms,candidate)
        rows[(c["id"],number,"fresh")]=process(c,line,number,fresh,candidate)
    return rows
