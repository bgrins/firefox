import itertools

def generate():
    events=[]; ident=0
    def root(epoch,zoom,form,value,size=16):
        events.append(dict(event="ROOT",doc=1,element=10,epoch=epoch,zoom=zoom,size=size,form=form,value=value))
        if epoch==1:
            read(0,0,0,0.5,zoom)
            read(1,0,0,1,1)
        events.append(dict(event="PUBLISH"))
    def read(role,unit,base,coefficient,zoom,form=0,value=28,size=18,pc=1,diagnostic=False,call=0):
        nonlocal ident
        ident+=1
        events.append(dict(event="READ",id=ident,role=role,unit=unit,base=base,coefficient=coefficient,
          owner=10010 if role==0 else 10020,zoom=zoom,parentOwner=10011,parentZoom=1,
          size=16 if role==1 else size,form=0 if role==1 else form,value=19 if role==1 else value,
          parentSize=20,parentForm=0,parentValue=24,initialSize=16,initialForm=0,initialValue=19,
          pc=pc,diagnostic=diagnostic,call=call))
    epoch=0
    for zoom,(form,value) in itertools.product([0.5,1,2,4],[(0,12),(0,20),(1,1.25),(3,1.25)]):
        epoch+=1;root(epoch,zoom,form,value)
        for role,base,coefficient in itertools.product([0,1,2],[0,1],[0.5,1,1.5,2]):
            for consumer_zoom in ([zoom] if role==0 else [1] if role==1 else [0.5,1,2,4]):
                read(role,0,base,coefficient,consumer_zoom)
        for unit,role,base in itertools.product(range(1,12),[0,1,2],[0,1]):
            read(role,unit,base,1.5,zoom if role==0 else 1)
    for zoom in [1,2,0.5,1]:
        epoch+=1;root(epoch,zoom,0,20)
        for role in [0,2]:read(role,0,0,1,zoom if role==0 else 2)
        events.append(dict(event="FOREIGN",value=73))
        read(2,0,0,1,2)
    epoch+=1;root(epoch,2,0,20)
    for role,unit in itertools.product([0,1,2],[0,1]):
        read(role,unit,1,1.5,1 if role==1 else 2,call=1)
    for parent_form in [1,3]:
        read(0,0,1,1.5,2)
        events[-1].update(parentForm=parent_form,parentValue=1.25)
    epoch+=1;root(epoch,2,0,24)
    for base in [0,1]:
        read(0,0,base,0.5,2)
        events[-1].update(initialValue=24)
    for pc in [0,1]:
        epoch+=1;root(epoch,2,2,0)
        for role,base in itertools.product([0,1,2],[0,1]):
            read(role,0,base,1,2 if role==0 else 1,pc=pc,diagnostic=True)
    for z in [1.1,0.7,1.3]:
        epoch+=1;root(epoch,z,0,13.37,size=17.25)
        for role,base in itertools.product([0,2],[0,1]):
            read(role,0,base,0.7,z if role==0 else 1.3,diagnostic=True)
    epoch+=1;root(epoch,2,0,20)
    read(3,0,0,1,2,diagnostic=True)
    read(3,0,1,1,2,diagnostic=True)
    return events

def protocol(events):
    lines=[]
    for e in events:
        if e["event"]=="ROOT":keys=["doc","element","epoch","zoom","size","form","value"]
        elif e["event"]=="READ":keys=["id","role","unit","base","coefficient","owner","zoom","parentOwner","parentZoom","size","form","value","parentSize","parentForm","parentValue","initialSize","initialForm","initialValue","pc","call"]
        elif e["event"]=="FOREIGN":keys=["value"]
        else:keys=[]
        lines.append(" ".join([e["event"]]+[str(e[k]) for k in keys]))
    return "\n".join(lines)+"\n"
