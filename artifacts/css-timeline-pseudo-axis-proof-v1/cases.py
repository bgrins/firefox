from copy import deepcopy
from itertools import product

def base():
    return dict(type=3, host=2, pseudo=1, axis=1, root=1, scrolling=1,
                shell=1, root_frame=1001, apz=0,
                elements=[
                    [1,1002,0,0,1,0,1,0,0,0,0,0,0,0],
                    [2,1003,0,1,1,0,1,3,4,0,0,0,0,0],
                    [3,1004,1,2,1,0,1,0,0,0,0,0,0,0],
                    [4,1005,2,2,1,0,1,0,0,0,0,0,0,0],
                    [5,1008,0,2,1,0,1,0,0,0,0,0,0,0],
                    [6,0,0,0,0,0,0,0,0,0,0,0,0,0]],
                frames=[
                    [1001,0,1,1,1001,0,3,7,-11,100,200,2,3,1,0],
                    [1002,1001,1,0,1001,1,0,0,0,0,0,0,0,1,0],
                    [1003,1002,2,1,1006,0,0,0,0,0,0,0,0,1,0],
                    [1004,1003,3,1,1007,1,0,0,0,0,0,0,0,1,0],
                    [1005,1003,4,1,1007,1,0,0,0,0,0,0,0,1,0],
                    [1006,1002,2,1,1006,0,3,13,-17,120,240,2,3,1,0],
                    [1007,1003,3,1,1007,1,2,0,-25,0,100,3,2,1,0],
                    [1008,1004,5,0,0,0,0,0,0,0,0,0,0,1,0],
                    [1009,1003,6,0,0,0,0,0,0,0,0,0,0,1,0],
                    [1010,1003,0,0,0,0,0,0,0,0,0,0,0,1,0]])

def frame(w,id): return next(x for x in w['frames'] if x[0]==id)
def element(w,id): return next(x for x in w['elements'] if x[0]==id)

def cases():
    result=[]
    def add(label, worlds, subscribers=2):
        for w in worlds:
            after=deepcopy(frame(w,1007));after[0]=1012;after[2]=4;after[4]=1012
            w['frames'].append(after)
            if frame(w,1005)[4]==1007:frame(w,1005)[4]=1012
            if w['pseudo']==2 and frame(w,1005)[4]==1011:frame(w,1011)[2]=4
        result.append(dict(id=len(result),label=label,worlds=worlds,subscribers=subscribers))
    for typ,pseudo,hostwm,pseudowm,scrollwm,axis,available in product(range(5),range(3),range(2),range(2),range(2),range(4),range(4)):
        w=base();w.update(type=typ,pseudo=pseudo,axis=axis)
        if typ==2: w['host']=5;w['pseudo']=0
        frame(w,1003)[5]=hostwm
        for id in [1004,1005]:frame(w,id)[5]=pseudowm
        for id in [1001,1006,1007]:
            f=frame(w,id);f[5]=scrollwm;f[6]=available
            f[7:11]=[24 if available&1 else 0,-35 if available&2 else 0,96 if available&1 else 0,140 if available&2 else 0]
        add('product', [w],len(result)%3)
    for axis in range(4):
      for pseudo in [1,2]:
        w=base();w.update(axis=axis,pseudo=pseudo)
        variations={}
        for name in ['provided-null','nearest-root-subject','nearest-no-parent','missing-host','missing-host-primary','missing-pseudo','missing-pseudo-frame','non-scroll-target','missing-shell','missing-root-frame','root','quirks','root-pseudo','nearest-no-principal','nearest-no-pseudo','nearest-no-pseudo-frame','nearest-no-eligible','nearest-non-element','nearest-empty-content','nearest-pseudo','fieldset','apz-disabled','apz-displayport','apz-no-displayport']:
            v=deepcopy(w)
            if name=='provided-null':v.update(type=0,host=0,pseudo=0)
            elif name=='nearest-root-subject':v.update(type=2,host=1,pseudo=0)
            elif name=='nearest-no-parent':v.update(type=2,host=5,pseudo=0);frame(v,1008)[1]=0
            elif name=='missing-host':v['host']=0
            elif name=='missing-host-primary':element(v,2)[1]=0
            elif name=='missing-pseudo':element(v,2)[6+pseudo]=0
            elif name=='missing-pseudo-frame':element(v,2+pseudo)[1]=0
            elif name=='non-scroll-target':frame(v,1003+pseudo)[4]=0
            elif name=='missing-shell':v.update(type=1,shell=0)
            elif name=='missing-root-frame':v.update(type=1,root_frame=0)
            elif name=='root':v.update(type=1)
            elif name=='quirks':v.update(type=1,scrolling=2)
            elif name=='root-pseudo':v.update(scrolling=2)
            elif name=='nearest-no-principal':v.update(type=2);element(v,2)[1]=0
            elif name=='nearest-no-pseudo':v.update(type=2);element(v,2)[6+pseudo]=0
            elif name=='nearest-no-pseudo-frame':v.update(type=2);element(v,2+pseudo)[1]=0
            elif name=='nearest-no-eligible':v.update(type=2,host=5,pseudo=0);frame(v,1004)[3]=0;frame(v,1003)[3]=0
            elif name=='nearest-non-element':v.update(type=2,host=5,pseudo=0);frame(v,1008)[1]=1009
            elif name=='nearest-empty-content':v.update(type=2,host=5,pseudo=0);frame(v,1008)[1]=1010
            elif name=='nearest-pseudo':v.update(type=2,host=5,pseudo=0)
            elif name=='fieldset':v.update(type=0,pseudo=0)
            elif name.startswith('apz-'):
                v['apz']=1;element(v,2)[5]=int(name=='apz-disabled');element(v,2)[6]=int(name=='apz-displayport')
            variations[name]=v
            add(name,[deepcopy(w),v,deepcopy(w)])
        hostchange=deepcopy(w);frame(hostchange,1003)[5]=1
        pseudochange=deepcopy(w);frame(pseudochange,1007)[5]=0
        position=deepcopy(w);frame(position,1007)[8]=-70
        extent=deepcopy(w);frame(extent,1007)[10]=210
        swap=deepcopy(w);frame(swap,1007)[6:11]=[1,33,0,132,0]
        unavailable=deepcopy(w);frame(unavailable,1007)[6:11]=[0,0,0,0,0]
        replacement=deepcopy(w);new=deepcopy(frame(replacement,1007));new[0]=1011;new[4]=1011;new[8]=-50;replacement['frames'].append(new);frame(replacement,1003+pseudo)[4]=1011
        same=deepcopy(replacement);frame(same,1011)[8]=frame(w,1007)[8]
        axischange=deepcopy(w);axischange['axis']=(axis+1)%4
        sourcechange=deepcopy(w);sourcechange.update(type=1,pseudo=0)
        reverse=deepcopy(w)
        for f in reverse['frames']:f[14]=1;f[7]=-f[7];f[8]=-f[8]
        for name,v in [('same-data-generation',same),('axis-replacement',axischange),('source-replacement',sourcechange),('direction-reversal',reverse),('host-change',hostchange),('scroll-mode-change',pseudochange),('position-change',position),('extent-change',extent),('axis-availability-change',swap),('unavailable',unavailable),('frame-replacement',replacement)]:
            add(name,[deepcopy(w),v,deepcopy(w),deepcopy(w)],3)
    for pos,extent in [(0,1),(1,2),(-1,2),(1,3),(-2,3),(2147483647,2147483647),(-2147483647,2147483647),(1,2147483647)]:
        w=base();frame(w,1007)[8]=pos;frame(w,1007)[10]=extent;add('numeric',[w],1)
    for kind in range(1,8):
        w=base();w.update(type=2,host=5,pseudo=0)
        element(w,3)[2]=kind;element(w,2)[7]=0;element(w,2)[6+kind]=3
        add('pseudo-pair-kind',[w],0)
    for primary_shell,document_shell,root_frame in product(range(2),range(2),[0,1001]):
        w=base();w.update(type=0,host=1,pseudo=0,scrolling=2,shell=document_shell,root_frame=root_frame)
        frame(w,1002)[13]=primary_shell
        add('root-element-provider',[w])
    for axis in range(4):
        w=base();w['axis']=axis;frame(w,1007)[6:11]=[0,0,-25,80,100]
        add('diagnostic-inconsistent-availability',[w])
    w=base();frame(w,1007)[8]=200;add('diagnostic-out-of-range',[w])
    return result

def encode(corpus):
    lines=[str(len(corpus))]
    for c in corpus:
        lines.append(f"{c['id']} {len(c['worlds'])} {c['subscribers']}")
        for w in c['worlds']:
            lines.append(' '.join(str(w[k]) for k in ['type','host','pseudo','axis','root','scrolling','shell','root_frame','apz'])+f" {len(w['elements'])} {len(w['frames'])}")
            lines.extend(' '.join(map(str,row)) for row in w['elements'])
            lines.extend(' '.join(map(str,row)) for row in w['frames'])
    return '\n'.join(lines)+'\n'
