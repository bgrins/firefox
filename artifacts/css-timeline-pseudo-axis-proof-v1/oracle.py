"""Independent graph relation and per-sample output; no native traces."""

def selected(w):
    es={e[0]:e for e in w['elements']};fs={f[0]:f for f in w['frames']}
    def pair(id):
        e=es[id]
        return (w['root'],7) if e[2]==7 else (e[3],e[2]) if e[2] else (id,0)
    t,h,p=w['type'],w['host'],w['pseudo']
    if t in [0,3,4]:return h,p
    if t==1:return w['scrolling'],0
    if not es[h][1]:return 0,0
    subject=h if not p else es[h][6+p]
    if not subject:return 0,0
    if subject==w['scrolling']:return subject,0
    if not es[subject][1]:return 0,0
    chain=[];cur=fs[es[subject][1]][1];seen=set()
    while cur:
        assert cur not in seen;seen.add(cur);chain.append(fs[cur]);cur=fs[cur][1]
    eligible=[]
    for f in chain:
        if not f[2] or not es[f[2]][4]:continue
        if f[2]==w['scrolling']:break
        if f[3]:eligible.append(f)
    return pair(eligible[0][2]) if eligible else (w['scrolling'],0)

def resolve(w,source):
    es={e[0]:e for e in w['elements']};fs={f[0]:f for f in w['frames']}
    h,p=source
    if not h:return 0
    if h==w['scrolling']:return w['root_frame'] if w['shell'] else 0
    element=h if not p else es[h][6+p]
    if not element:return 0
    primary=es[element][1]
    if element==w['root']:
        shell=fs[primary][13] if primary else 0
        if not shell:shell=w['shell']
        if shell and w['root_frame']:primary=w['root_frame']
    return fs[primary][4] if primary else 0

def observe(w,variant):
    es={e[0]:e for e in w['elements']};fs={f[0]:f for f in w['frames']}
    source=selected(w);h,p=source
    active=bool(h and es[h][1] and resolve(w,source))
    if not active:return [h,p,int(bool(h and h==w['scrolling'])),0,-1,0,-1,0],None
    f=fs[resolve(w,source)]
    vertical=fs[es[h][1]][5] if variant=='original' else f[5]
    dimensions={0:0 if vertical else 1,1:1 if vertical else 0,2:0,3:1}
    axis=dimensions[w['axis']]
    available=bool(f[6]&(1<<axis))
    snapshot=[h,p,int(h==w['scrolling']),1,axis,int(available),f[11+axis],int(bool(w['apz'] and not es[h][5] and es[h][6]))]
    cache=[f[7+axis],f[9+axis]] if available else None
    return snapshot,cache

def run(c,variant):
    old=None;out=[]
    for i,w in enumerate(c['worlds']):
        snapshot,cache=observe(w,variant)
        notifications=[]
        if cache is not None and (old is None or old[1]!=cache[1]):
            notifications=[[3000+j,op,0,0] for j in range(c['subscribers']) for op in [23,24]]
        value=None if cache is None else abs(cache[0])/cache[1]
        out.append(dict(case=c['id'],sample=i,snapshot=snapshot,raw_axis_style=[snapshot[4],snapshot[6]] if snapshot[3] else [0,0],exposed=selected(w)[0],cache=cache,
                        data=None if cache is None else [cache[0],0,cache[1]],changed=int(cache!=old),
                        duration=None if value is None else value*100000,
                        percent=None if value is None else value*100,
                        fallback=None if value is None else value*100000,notifications=notifications))
        old=cache
    return out
