import copy
AUTO=(1<<30)-1
LOW=-(AUTO//2)
HIGH=LOW+AUTO

def edge(r,axis):return r[axis]+r[axis+2]
def empty(r):return r[2]<=0 or r[3]<=0

def union(rects):
    result=[0,0,0,0]
    for r in rects:
        if empty(result):result=r[:]
        elif not empty(r):
            x=min(result[0],r[0]);y=min(result[1],r[1])
            right=max(edge(result,0),edge(r,0));bottom=max(edge(result,1),edge(r,1))
            if right-x>AUTO:x=max(x,LOW)
            if bottom-y>AUTO:y=max(y,LOW)
            result=[x,y,min(AUTO,right-x),min(AUTO,bottom-y)]
    return rects[0][:] if empty(result) else result

def deflate(r,m):
    return [r[0]+m[3],r[1]+m[0],max(0,r[2]-m[3]-m[1]),max(0,r[3]-m[0]-m[2])]

def normal(c):return c['normal'] if c['has_normal'] else c['position']
def mode_ends(raw):
    vertical=raw%2==1;reverse=raw//2%2==1;lr=raw//4%2==1
    return ((not reverse) if not vertical else lr, True if not vertical else not reverse)

def limits(c,variant,ignore=False):
    unbounded=[LOW,LOW,AUTO,AUTO]
    if not c['has_offsets']:return [unbounded[:],unbounded[:]]
    borders=[c['border']];margins=[c['margin']]
    if c['extra']:borders.append(c['continuation_border']);margins.append(c['continuation_margin'])
    border=union(borders);margin=union(margins)
    if c['cb_kind']==1:
        contain=deflate(c['overflow'],c['padding']);contain[0]+=c['transform'][0];contain[1]+=c['transform'][1]
        rawmode=c['scroll_mode']
    else:contain=c['containing'][:];rawmode=c['cb_mode']
    marginDelta=[border[1]-margin[1],edge(margin,0)-edge(border,0),edge(margin,1)-edge(border,1),border[0]-margin[0]]
    contain=deflate(deflate(contain,marginDelta),[0,border[2],border[3],0])
    shift=[c['position'][j]-border[j] for j in range(2)]
    contain[0]+=shift[0];contain[1]+=shift[1]
    sizes=c['fixed_size'] if c['viewport'] else c['size']
    bounds=[]
    auto=variant in ['auto-only','combined'];writing=variant in ['writing-only','combined']
    ends=mode_ends(rawmode) if writing else (not bool(c['direction']),True)
    for j,(near,far) in enumerate([(c['offsets'][3],c['offsets'][1]),(c['offsets'][0],c['offsets'][2])]):
        hasNear=near!=AUTO;hasFar=far!=AUTO
        a=0 if not hasNear else near;b=0 if not hasFar else far
        if (hasNear or hasFar) if auto else (hasNear and hasFar):
            if ends[j]:b=min(b,sizes[j]-a-border[j+2])
            else:a=min(a,sizes[j]-b-border[j+2])
        origin=(0 if ignore else c['scroll'][j])+c['padding'][3 if j==0 else 0]-c['parent_offset'][j]+shift[j]
        bounds.append([origin+a if hasNear else LOW,origin+sizes[j]-b-border[j+2] if hasFar else HIGH])
    return [[bounds[0][0],bounds[1][0],bounds[0][1]-bounds[0][0],bounds[1][1]-bounds[1][0]],contain]

def position(c,l):
    stick,contain=l
    return [min(max(normal(c)[j],min(stick[j],edge(contain,j))),max(edge(stick,j),contain[j])) for j in range(2)]

def ranges(c,variant,j):
    near,far=(c['offsets'][3],c['offsets'][1]) if j==0 else (c['offsets'][0],c['offsets'][2])
    if not c['has_offsets'] or near==far==AUTO:return [None,None]
    stick,contain=limits(c,variant,True);n=normal(c)[j]
    first=None if near==AUTO else [n-stick[j],max(0,edge(contain,j)-n)]
    last=None if far==AUTO else [n-edge(stick,j),max(0,n-contain[j])]
    if first and last and last[0]>first[0]:return [None,None]
    return [first,last]

def scroll_ranges(c,l):
    stick,contain=l;n=normal(c);outer=[LOW,LOW,HIGH,HIGH];inner=outer[:]
    for j in range(2):
        if edge(stick,j)!=HIGH:outer[j]=contain[j]-edge(stick,j);inner[j]=n[j]-edge(stick,j)
        if stick[j]!=LOW:inner[j+2]=n[j]-stick[j];outer[j+2]=edge(contain,j)-stick[j]
    inner=[max(inner[0],outer[0]),max(inner[1],outer[1]),min(inner[2],outer[2]),min(inner[3],outer[3])]
    if inner[2]<inner[0] or inner[3]<inner[1]:inner[2:]=inner[:2]
    if inner[2]<=inner[0] or inner[3]<=inner[1]:
        for j in range(2):
            width=min(outer[j+2]-outer[j],inner[j+2]-inner[j])
            left=max(outer[j],inner[j]);newLeft=min(left+width,outer[j+2])-width
            inner[j]=newLeft;inner[j+2]=newLeft+width
    return outer,inner

def move_frame(c,target):
    delta=[target[j]-c['position'][j] for j in range(2)]
    for key in ['border','margin']:
        for j in range(2):c[key][j]+=delta[j]
    c['position']=target


def timeline(c,variant,axis,subject_continuation=False):
    start,end=ranges(c,variant,axis)
    if not start and not end:return None
    startAt,startMax=start or [0,0];endAt,endMax=end or [0,0]
    shift=(c['continuation_position'][axis]-c['continuation_normal'][axis]) if subject_continuation else c['position'][axis]-normal(c)[axis]
    result=[shift,startAt,startMax,endAt,endMax]
    for x in [endAt-1,endAt,endAt+1,startAt-1,startAt,startAt+1]:
        early=x-endMax if endMax and x<=endAt else x+startMax if startMax and x>startAt else x
        late=x-endMax if endMax and x<endAt else x+startMax if startMax and x>=startAt else x
        result.extend([early,late])
    return result

def observe(case,variant):
    c=copy.deepcopy(case);current=limits(c,variant);ignoring=limits(c,variant,True)
    before=position(c,current);zero=position(c,ignoring)
    out=dict(id=c['id'],original_offsets=c['offsets'][:],current=current,ignoring=ignoring,
        position=before,zero=zero,translation=[zero[j]-normal(c)[j] for j in range(2)],
        range_x=ranges(c,variant,0),range_y=ranges(c,variant,1))
    out['outer'],out['inner']=scroll_ranges(c,current)
    if c['action']==2:
        c['offsets']=c['resolved'][:];c['has_offsets']=1
    if c['has_normal']:
        target=position(c,limits(c,variant));delta=[target[j]-c['normal'][j] for j in range(2)]
        move_frame(c,target)
        if c['extra']:c['continuation_position']=[c['continuation_normal'][j]+delta[j] for j in range(2)]
        if c['extra']:
            # The continuation's geometry follows its own position change.
            shift=[c['continuation_position'][j]-case['continuation_position'][j] for j in range(2)]
            for k in ['continuation_border','continuation_margin']:
                for j in range(2):c[k][j]+=shift[j]
    out.update(first_after=c['position'],continuation_after=c['continuation_position'],
        after_computation=position(c,limits(c,variant)),offsets_after=c['offsets'],has_offsets_after=bool(c['has_offsets']))
    out.update(timeline_x=timeline(c,variant,0,c['extra']),timeline_y=timeline(c,variant,1,c['extra']),
        timeline_no_container=None,timeline_no_sticky=None,
        timeline_multiple=timeline(c,variant,1) if c['cb_kind']==1 else None)
    return out


def expected_trace(case,variant):
    c=copy.deepcopy(case)
    out=[]
    def limits_trace():
        out.append(404)
        if not c['has_offsets']:return
        out.extend([204,1140])
        if c['cb_kind']==2:out.append(203)
        out.append(1001 if c['cb_kind']==1 else 1121)
        out.append(1142)
        if not c['viewport']:out.append(700)
        if variant in ['writing-only','combined']:out.append(301 if c['cb_kind']==1 else 302)
    def range_trace(axis):
        out.append(404)
        pair=(c['offsets'][3],c['offsets'][1]) if axis==0 else (c['offsets'][0],c['offsets'][2])
        if c['has_offsets'] and pair!=(AUTO,AUTO):limits_trace()
    for _ in range(5):limits_trace()
    range_trace(0);range_trace(1);limits_trace()
    if c['action']!=0:
        out.append(800)
        if c['action']==2:
            out.append(905)
            if not c['viewport']:out.append(700)
            for side in [3,1,0,2]:
                out.append(100+side)
                if c['resolved'][side]!=AUTO:out.append(950)
            out.append(504)
            c['offsets']=c['resolved'][:];c['has_offsets']=1
    if c['has_normal']:
        limits_trace();out.append(604)
        if c['extra']:out.append(605)
    if c['action']!=0:
        if not(c['action']==2 and c['cb_kind']==1):
            out.append(811 if c['cb_kind']==1 else 813 if c['cb_kind']==2 else 812)
        out.append(899)
    limits_trace()
    for axis in [0,1]:
        out.append(907);range_trace(axis)
    out.append(907)
    if c['cb_kind']==1:range_trace(1)
    else:out.append(907)
    return out
