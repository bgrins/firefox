import itertools, json, random
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
AUTO=(1<<30)-1
MODES=['horizontal-tb','vertical-rl','vertical-lr','sideways-rl','sideways-lr']
MODE_FLAGS={'horizontal-tb':(0,18),'vertical-rl':(1,19),'vertical-lr':(13,31),'sideways-rl':(33,51),'sideways-lr':(39,53)}

def mode_flags(mode,rtl,orientation=0):
    raw=MODE_FLAGS[mode][rtl]
    if mode in ['vertical-rl','vertical-lr']:
        if orientation==1:return MODE_FLAGS[mode][0]+128
        if orientation==2:return raw+64
    return raw

def base(name,axis,size,near,far,scroll,mode=0,child=0,direction=0):
    border=[200,0,size,20] if axis==0 else [0,200,20,size]
    offsets=[AUTO]*4
    offsets[3 if axis==0 else 0]=AUTO if near is None else near
    offsets[1 if axis==0 else 2]=AUTO if far is None else far
    return dict(name=name,historical=False,axis=axis,action=0,cb_kind=0,cb_mode=mode,
        child_mode=child,scroll_mode=mode,direction=direction,has_offsets=1,has_normal=1,
        viewport=0,extra=0,border=border,margin=border[:],containing=[0,0,600,600],
        overflow=[0,0,600,600],padding=[0,0,0,0],size=[100,100],fixed_size=[100,100],
        scroll=[scroll,0] if axis==0 else [0,scroll],position=border[:2],normal=border[:2],
        parent_offset=[0,0],transform=[0,0],offsets=offsets,resolved=offsets[:],
        continuation_position=[13,17],continuation_normal=[13,17],
        continuation_border=[13,17,0,0],continuation_margin=[13,17,0,0])


SCALARS=['id','action','cb_kind','cb_mode','child_mode','scroll_mode','direction','has_offsets','has_normal','viewport','extra']
ARRAYS=['border','margin','containing','overflow','padding','size','fixed_size','scroll','position','normal','parent_offset','transform','offsets','resolved','continuation_position','continuation_normal','continuation_border','continuation_margin']
def input_text(rows):
    return ''.join(' '.join(str(n) for n in [*[r[k] for k in SCALARS],*[v for k in ARRAYS for v in r[k]]])+'\n' for r in rows)
