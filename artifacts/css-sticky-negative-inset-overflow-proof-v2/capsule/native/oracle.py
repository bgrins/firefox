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
    auto=writing=variant.startswith('combined')
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

def position(c,l,variant):
    stick,contain=l
    out=normal(c)[:]
    for j,(n,f) in enumerate([(c['offsets'][3],c['offsets'][1]),(c['offsets'][0],c['offsets'][2])]):
        modern=variant.startswith('combined')
        if not modern or (c['has_offsets'] and n!=AUTO):out[j]=max(out[j],min(stick[j],edge(contain,j)))
        if not modern or (c['has_offsets'] and f!=AUTO):out[j]=min(out[j],max(edge(stick,j),contain[j]))
    return out

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

