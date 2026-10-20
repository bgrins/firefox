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

def cases():
    rows=[]
    for axis,size,pair,scroll in itertools.product(['vertical','horizontal-ltr','horizontal-rtl'],[60,80,200],[(None,-20),(None,0),(None,20),(0,20),(20,None),(None,None)],[0,160,260,400]):
        start,end=pair;label=lambda v:'auto' if v is None else str(v)
        name=f'{axis}, size {size}, start {label(start)}, end {label(end)}, scroll {scroll}'
        rtl=axis=='horizontal-rtl';near,far=(end,start) if rtl else pair
        row=base(name,1 if axis=='vertical' else 0,size,near,far,scroll,18 if rtl else 0,direction=int(rtl))
        row.update(historical=True,suite='A');rows.append(row)
    for mode,rtl,child,axis,size,pair,scroll in itertools.product(MODES,[0,1],['horizontal-tb/ltr','vertical-rl/rtl','sideways-lr/ltr'],['x','y'],[70,200],[(0,0),(20,10),(-20,10)],[0,180,400]):
        near,far=pair;direction='rtl' if rtl else 'ltr'
        name=f'{mode}/{direction}, child {child}, {axis}, size {size}, insets {near}/{far}, scroll {scroll}'
        childMode,childDir=child.split('/')
        row=base(name,0 if axis=='x' else 1,size,near,far,scroll,mode_flags(mode,rtl),mode_flags(childMode,childDir=='rtl'),rtl)
        row.update(historical=True,suite='B');rows.append(row)
    expected=json.loads((ROOT/'inputs/ORACLE-ROWS.json').read_text())
    if [(x['suite'],x['name']) for x in rows] != [(x['test'],x['name']) for x in expected]:raise RuntimeError('historical identity')
    for mode,rtl,orientation,axis,mask,size in itertools.product(MODES,[0,1],range(3),[0,1],range(4),[0,80,200]):
        near=-20 if mask&1 else None;far=10 if mask&2 else None
        row=base(f'mixed-{len(rows)}',axis,size,near,far,180,mode_flags(mode,rtl,orientation),mode_flags('sideways-lr',not rtl),rtl)
        rows.append(row)
    for kind,normal,computed,action,extra in itertools.product(range(3),[0,1],[0,1],range(3),[0,1]):
        row=base(f'entry-{len(rows)}',1,200,None,20,160,1,39)
        row.update(cb_kind=kind,has_normal=normal,has_offsets=computed,action=action,extra=extra)
        row['continuation_position']=[0,280];row['continuation_normal']=[0,280]
        row['continuation_border']=[0,280,20,120];row['continuation_margin']=[0,275,20,130]
        row['padding']=[3,5,7,11];row['parent_offset']=[7,-9];row['transform']=[-11,13]
        row['viewport']=1;row['fixed_size']=[90,110];row['resolved']=[0,AUTO,10,AUTO]
        rows.append(row)
    rng=random.Random(502603)
    for i in range(128):
        row=base(f'geometry-{i}',i%2,rng.choice([0,1,40,200,700]),rng.choice([None,-50,0,20]),rng.choice([None,-30,0,40]),rng.randint(-500,700),mode_flags(MODES[i%5],i%2),mode_flags(MODES[(i+1)%5],(i+1)%2),i%2)
        row['containing']=[rng.randint(-100,100),rng.randint(-100,100),rng.choice([0,30,600]),rng.choice([0,20,600])]
        row['margin']=[row['border'][0]-10,row['border'][1]+5,row['border'][2]+30,row['border'][3]-10]
        row['parent_offset']=[rng.randint(-20,20),rng.randint(-20,20)]
        rows.append(row)
    for nx,ny in [(-200,50),(50,-200),(-200,-200),(0,0),(90,90),(700,50),(50,700),(700,700)]:
        row=base(f'absolute-cross-axis-{nx}-{ny}',0,10,0,0,0)
        row.update(border=[0,0,10,10],margin=[0,0,10,10],containing=[0,0,500,500],
                   position=[0,0],normal=[nx,ny],offsets=[0,0,0,0],resolved=[0,0,0,0])
        rows.append(row)
    for index,row in enumerate(rows):
        row['id']=index
        row['units_per_css_pixel']=60 if row['historical'] else None
        if row['historical']:
            for key in ARRAYS:
                row[key]=[value if value==AUTO else value*60 for value in row[key]]
    return rows

SCALARS=['id','action','cb_kind','cb_mode','child_mode','scroll_mode','direction','has_offsets','has_normal','viewport','extra']
ARRAYS=['border','margin','containing','overflow','padding','size','fixed_size','scroll','position','normal','parent_offset','transform','offsets','resolved','continuation_position','continuation_normal','continuation_border','continuation_margin']
def input_text(rows):
    return ''.join(' '.join(str(n) for n in [*[r[k] for k in SCALARS],*[v for k in ARRAYS for v in r[k]]])+'\n' for r in rows)
