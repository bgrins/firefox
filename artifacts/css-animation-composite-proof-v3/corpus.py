import copy
import itertools
import random


def env(view=0,resolved=1,start=0,delta=1,first=0,last=1):return dict(view=view,resolved=resolved,start=start,delta=delta,first=first,last=last)
def reset(target=1,style=1,animation=1,relevant=1,context=None,default=0,base=10,scale=1,fail=0):return dict(op='RESET',target=target,style=style,animation=animation,relevant=relevant,env=context or env(),default=default,base=base,scale=scale,fail=fail)
def frame(offset=None,easing=-1,composite=3,properties=None,computed=99):return dict(offset=offset,easing=easing,composite=composite,properties=properties or [],computed=computed)
def setter(frames,error=0):return dict(op='SET',frames=copy.deepcopy(frames),error=error)
def get(failure=0):return dict(op='GET',failure=failure)
def prop(pid=0,allocation=0,value=20,name=''):return [pid,name,allocation,value if allocation>=0 else None]


def corpus():
    cases=[]
    def add(name,actions):cases.append(dict(name=name,actions=actions))
    for a,b,target,style,animation,relevant in itertools.product(range(4),range(4),range(2),range(2),range(2),range(2)):
        frames=[frame([0,0],composite=a),frame([0,1],composite=a)]
        changed=copy.deepcopy(frames);changed[0]['composite']=b
        add(f'enum-{a}-{b}-{target}-{style}-{animation}-{relevant}',[reset(target,style,animation,relevant),setter(frames),get(),setter(changed),get(),setter(changed),get()])
    for n in [0,1,2,3,5]:
        for where in range(max(n,1)):
            for field in ['composite','easing','offset','properties','length','order','raw-equal','derived-only']:
                fs=[frame(None,properties=[prop(0,i,i+1)]) for i in range(n)];changed=copy.deepcopy(fs)
                if n:
                    if field=='composite':changed[where]['composite']=1
                    if field=='easing':changed[where]['easing']=1
                    if field=='offset':changed[where]['offset']=[0,where/max(n-1,1)]
                    if field=='properties':changed[where]['properties']=[prop(3,100,30)]
                    if field=='order':changed.reverse()
                    if field=='raw-equal':changed[where]['properties'][0][2]+=1000
                    if field=='derived-only':changed[where]['computed']=-123
                if field=='length':changed.append(frame([0,1]))
                add(f'field-{n}-{where}-{field}',[reset(),setter(fs),get(),dict(op='RUNNING'),setter(changed),get(),setter(changed),get()])
    for offsets in [[],[None],[None,None,None],[None,[0,.5],None],[None,[0,0],[0,0],None],[None,[0,1],[0,1]],[[0,0],[0,.5],[0,.5],[0,1]],[[0,0],[0,0],[0,1],[0,1]],[[0,-0.0],[0,1]],[[2,-1]],[[2,2]],[[2,-1],[2,-1]],[[2,2],[2,2]],[[2,0],[2,.5],None,[2,1]],[[2,0],[3,.5],[4,1]]]:
        for context in [env(),env(-1),env(1),env(1,0),env(1,1,0,1,.25,.75),env(1,1,0,1,.5,.5)]:
            fs=[frame(off,composite=i%4,properties=[prop(i%4,i,10+i),prop(4,i+100,20+i,'x')]) for i,off in enumerate(offsets)]
            add(f'offset-{len(cases)}',[reset(context=context),setter(fs),get(),dict(op='CONTEXT',env=env(1,1,-.5,2,.25,.75)),get(),dict(op='CONTEXT',env=env(1,0)),get(),dict(op='CONTEXT',env=env(1,0)),dict(op='CONTEXT',env=env(1)),get()])
    for composite,default in itertools.product(range(4),range(3)):
        fs=[frame([0,0],composite=composite,properties=[prop(value=20)]),frame([0,1],composite=composite,properties=[prop(allocation=1,value=30)])]
        add(f'default-{composite}-{default}',[reset(),setter(fs),get(),dict(op='DEFAULT',value=default),get(),dict(op='STYLE',base=40,scale=1),dict(op='STYLE',base=40,scale=2),get()])
    for failure in range(5):
        fs=[frame(None,properties=[prop(4,0,2,'x'),prop(2,1,3)]),frame(None,properties=[prop(1,2,4)])]
        add(f'error-{failure}',[reset(),setter(fs),get(failure),setter([frame(composite=1)],1),get()])
    add('null-provider',[reset(),setter([frame([0,0],properties=[prop(allocation=-1)]),frame([0,1],composite=1,properties=[prop(allocation=0,value=20)])]),get(),dict(op='STYLE',base=30,scale=1),get()])
    for composite in range(4):
        for offset in [0,.5,1]:
            fs=[frame([0,offset],composite=composite,properties=[prop(allocation=-1)])]
            add(f'null-existing-and-missing-{composite}-{offset}',[reset(default=1),setter(fs),get(),dict(op='STYLE',base=30,scale=2),get(),setter([frame([0,offset],composite=composite)]),get()])
    for target,style,composite in itertools.product(range(2),range(2),range(4)):
        fs=[frame([0,0],composite=composite,properties=[prop(value=20)]),frame([0,1],composite=composite,properties=[prop(allocation=1,value=30)])]
        add(f'pending-cache-{target}-{style}-{composite}',[reset(),setter(fs),get(),dict(op='INVALIDATE',base=30,scale=2,target=target,style=style),setter(fs),get(),dict(op='DEFAULT',value=1),get(),dict(op='INVALIDATE',base=30,scale=2,target=1,style=1),dict(op='STYLE',base=30,scale=2),get()])
    fs=[frame([2,.5],composite=1,properties=[prop()])]
    add('pending-offset-missing-timeline',[reset(context=env(1)),setter(fs),dict(op='CONTEXT',env=env(-1)),setter(fs),get(),dict(op='CONTEXT',env=env(1,1,0,1,0,2)),get()])
    add('failed-computation',[reset(fail=1),setter([frame(None,properties=[prop()])]),get(),dict(op='DEFAULT',value=1),get()])
    add('signed-zero',[reset(),setter([frame([0,-0.0])]),get(),setter([frame([0,0.0])]),get(),setter([frame([0,0.0],composite=1)]),get()])
    rng=random.Random(22501)
    for i in range(200):
        n=rng.randrange(1,9);fs=[];allocation=0
        offsets=sorted(rng.choices([0,.25,.5,.75,1],k=n))
        for j in range(n):
            properties=[]
            for pid in rng.sample(range(5),rng.randrange(0,5)):
                properties.append(prop(pid,allocation,rng.randrange(-20,31),'x' if pid==4 else ''));allocation+=1
            fs.append(frame(None if rng.randrange(3)==0 else [0,offsets[j]],rng.randrange(-1,3),rng.randrange(4),properties))
        modified=copy.deepcopy(fs);modified[rng.randrange(n)]['composite']=rng.randrange(4)
        add(f'random-{i}',[reset(default=rng.randrange(3)),setter(fs),get(),setter(modified),get(),dict(op='DEFAULT',value=rng.randrange(3)),get()])
    fs=[frame([0,0],composite=1,properties=[prop(value=20)]),frame([0,1],composite=1,properties=[prop(allocation=1,value=30)])]
    add('ready-equal-default-failure',[reset(),setter(fs),get(),setter(fs),get(),setter([],1),setter(fs),dict(op='DEFAULT',value=2),get(),setter(fs),get()])
    add('diagnostic-undelivered-identical-provider',[reset(),setter(fs),dict(op='INVALIDATE',base=10,scale=1,target=1,style=1),setter(fs),get(),dict(op='STYLE',base=10,scale=1),setter(fs),get()])
    add('ready-after-style-delivery',[reset(),setter(fs),dict(op='INVALIDATE',base=30,scale=2,target=1,style=1),dict(op='STYLE',base=30,scale=2),setter(fs),get()])
    ranged=[frame([2,.5],composite=1,properties=[prop(allocation=-1)])]
    add('ready-offset-then-style-delivery',[reset(context=env(1)),setter(ranged),dict(op='INVALIDATE',base=30,scale=2,target=1,style=0),dict(op='CONTEXT',env=env(1,1,0,1,0,2)),dict(op='STYLE',base=30,scale=2),setter(ranged),get(),dict(op='INVALIDATE',base=30,scale=2,target=1,style=1),dict(op='STYLE',base=30,scale=2),setter(ranged),get()])
    add('ready-absent-target-delivery',[reset(target=0,style=0),setter(fs),dict(op='STYLE',base=10,scale=1),setter(fs),get(),dict(op='INVALIDATE',base=30,scale=2,target=1,style=1),dict(op='STYLE',base=30,scale=2),setter(fs),get()])
    add('ready-missing-timeline-restored',[reset(context=env(1)),setter(ranged),dict(op='CONTEXT',env=env(-1)),dict(op='STYLE',base=30,scale=2),dict(op='CONTEXT',env=env(1,1,0,1,0,2)),setter(ranged),get()])
    add('ready-default-without-style',[reset(style=0),setter(fs),dict(op='DEFAULT',value=2),dict(op='STYLE',base=30,scale=2),setter(fs),dict(op='DEFAULT',value=2),setter(fs),get()])
    add('ready-empty-after-delivery',[reset(),dict(op='STYLE',base=10,scale=1),setter([]),get(),setter([],1),setter([]),get()])
    add('diagnostic-style-delivery-before-offsets',[reset(context=env(1)),setter(ranged),dict(op='CONTEXT',env=env(-1)),dict(op='STYLE',base=30,scale=2),setter(ranged),get(),dict(op='CONTEXT',env=env(1,1,0,1,0,2)),setter(ranged),get()])
    return cases


def encode(action):
    op=action['op'];parts=[op]
    def context(e):return [e[k] for k in ['view','resolved','start','delta','first','last']]
    if op=='RESET':parts += [action[k] for k in ['target','style','animation','relevant']]+context(action['env'])+[action[k] for k in ['default','base','scale','fail']]
    elif op=='SET':
        parts += [action['error'],len(action['frames'])]
        for f in action['frames']:
            parts+=(f['offset'] or [-1,0])+[f['computed'],f['easing'],f['composite'],len(f['properties'])]
            for pid,name,allocation,value in f['properties']:parts += [pid,name or '-',allocation,value or 0]
    elif op=='GET':parts+=[action['failure']]
    elif op=='DEFAULT':parts+=[action['value']]
    elif op=='CONTEXT':parts+=context(action['env'])
    elif op=='INVALIDATE':parts += [action[k] for k in ['base','scale','target','style']]
    elif op=='STYLE':parts += [action['base'],action['scale']]
    return ' '.join(str(x) for x in parts)
