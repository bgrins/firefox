import sys,importlib.util,itertools,copy,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent

def module(name):
    spec=importlib.util.spec_from_file_location(name,ROOT/'native'/(name+'.py'))
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
corpus=module('corpus');oracle=module('oracle')
M=corpus.AUTO
MODES=['horizontal','verticalRl','verticalLr','sidewaysRl','sidewaysLr']
ORIENTATIONS=['mixed','upright','sideways']

def cases():
    rows=[]
    for mode,rtl,orientation,axis,mask in itertools.product(range(5),range(2),range(3),range(2),range(4)):
        row=corpus.base('mode-mask',axis,200,-20 if mask&1 else None,10 if mask&2 else None,160,
            corpus.mode_flags(corpus.MODES[mode],rtl,orientation),39,rtl)
        row.update(mode=mode,orientation=orientation,rtl=rtl)
        rows.append(row)
    for kind,offsets,extra in itertools.product(range(3),range(2),range(2)):
        row=corpus.base('provider-path',1,200,None,20,160,13,18)
        row.update(cb_kind=kind,has_offsets=offsets,extra=extra,mode=2,orientation=0,rtl=0)
        row['padding']=[3,5,7,11];row['parent_offset']=[7,-9];row['transform']=[-11,13]
        row['continuation_position']=[0,280];row['continuation_normal']=[0,280]
        row['continuation_border']=[0,280,20,120];row['continuation_margin']=[0,275,20,130]
        rows.append(row)
    for nx,ny in [(-200,50),(50,-200),(-200,-200),(0,0),(90,90),(700,50),(50,700),(700,700)]:
        row=corpus.base('clamp-branch',0,10,0,0,0)
        row.update(border=[0,0,10,10],margin=[0,0,10,10],containing=[0,0,500,500],position=[0,0],normal=[nx,ny],offsets=[0,0,0,0],resolved=[0,0,0,0],mode=0,orientation=0,rtl=0)
        rows.append(row)
    for size in [60,600,12000]:
      for val in [-M,-M+6000,-700000000,-1000000]:
        row=corpus.base('negative-wide',1,size,val,val,0)
        row.update(border=[0,12000,600,size],margin=[0,12000,600,size],containing=[0,0,60000,60000],position=[0,12000],normal=[0,12000],size=[6000,6000],mode=0,orientation=0,rtl=0)
        rows.append(row)
    for i,r in enumerate(rows):r['id']=i
    return rows

def prepared(c):
    borders=[c['border']];margins=[c['margin']]
    if c['extra']:borders.append(c['continuation_border']);margins.append(c['continuation_margin'])
    b=oracle.union(borders);m=oracle.union(margins)
    if c['cb_kind']==1:
        cb=oracle.deflate(c['overflow'],c['padding'])
        cb[0]+=c['transform'][0];cb[1]+=c['transform'][1]
    else:cb=c['containing'][:]
    return b,m,cb

def expected(c,v):
    cur=oracle.limits(c,v);ign=oracle.limits(c,v,True)
    zero=oracle.position(c,ign,v)
    def convert(l):
        s,k=l;return [[s[0],s[1],s[0]+s[2],s[1]+s[3]],k]
    out=dict(id=c['id'],original_offsets=c['offsets'],current=convert(cur),ignoring=convert(ign),
        position=oracle.position(c,cur,v),zero=zero,translation=[zero[j]-oracle.normal(c)[j] for j in range(2)],
        range_x=oracle.ranges(c,v,0),range_y=oracle.ranges(c,v,1))
    out['outer'],out['inner']=oracle.scroll_ranges(c,cur)
    out['trace']=expected_trace(c,v)
    return out

def lean_int(x):return '('+str(x)+')'
def lean_bool(x):return 'true' if x else 'false'
def lean_frame(c,v):
    b,m,cb=prepared(c);axes=[]
    for j,(n,f) in enumerate([(c['offsets'][3],c['offsets'][1]),(c['offsets'][0],c['offsets'][2])]):
        option=lambda x:'none' if x==M else 'some '+lean_int(x)
        fields=[f'⟨{b[j]},{b[j+2]}⟩',f'⟨{m[j]},{m[j+2]}⟩',f'⟨{cb[j]},{cb[j+2]}⟩',
            lean_int(c['position'][j]),lean_int(oracle.normal(c)[j]),lean_int((c['fixed_size'] if c['viewport'] else c['size'])[j]),
            lean_int(c['padding'][3 if j==0 else 0]),lean_int(c['parent_offset'][j]),lean_int(c['scroll'][j]),f'⟨{option(n)},{option(f)}⟩']
        axes.append('⟨'+','.join(fields)+'⟩')
    return '⟨⟨'+','.join(axes+[lean_bool(c['has_offsets']),'.'+MODES[c['mode']],lean_bool(c['rtl']),'.'+ORIENTATIONS[c['orientation']]])+'⟩,'+lean_bool(v.startswith('combined'))+'⟩'

def lean_source(rows,v):
    prefix=(ROOT/'lean/Rows.lean').read_text()
    body='\ndef main : IO Unit := do\n  let out ← IO.getStdout\n'
    for c in rows:body+='  out.putStrLn ((row '+str(c['id'])+' '+lean_frame(c,v)+' '+lean_preparation(c)+').compress)\n'
    return prefix+body

def lean_preparation(c):
    _,_,cb=prepared(c)
    interval=lambda a,j:'⟨'+str(a[j])+','+str(a[j+2])+'⟩'
    return '⟨'+','.join([lean_bool(c['cb_kind']==1),interval(c['overflow'],0),interval(c['overflow'],1),
        *[lean_int(c['padding'][j]) for j in [3,1,0,2]],interval(cb,0),interval(cb,1),
        interval(c['containing'],0),interval(c['containing'],1)])+'⟩'

def negative_cases():
    c=corpus.base('retained-clamp-overflow',1,600,-M,7000-M,0)
    c.update(border=[0,12000,6000,600],margin=[0,12000,6000,600],containing=[0,0,12000,60000],
      position=[0,12000],normal=[0,12000],size=[6000,6000],offsets=[-M,0,7000-M,0],resolved=[-M,0,7000-M,0],mode=0,orientation=0,rtl=0,id=10000)
    return [c]

def expected_trace(c,v):
    result=[];modern=v.startswith('combined')
    def limits():
        result.append(404)
        if not c['has_offsets']:return
        result.extend([204,1140])
        if c['cb_kind']==2:result.append(203)
        result.extend([1001 if c['cb_kind']==1 else 1121,1142])
        if not c['viewport']:result.append(700)
        if modern:result.append(301 if c['cb_kind']==1 else 302)
    limits();limits()
    for _ in range(3):
        limits()
        if modern:result.append(404)
    for a,b in [(3,1),(0,2)]:
        result.append(404)
        if c['has_offsets'] and (c['offsets'][a]!=M or c['offsets'][b]!=M):limits()
    limits()
    return result
