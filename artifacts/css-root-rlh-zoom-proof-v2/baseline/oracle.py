import math
import struct
from fractions import Fraction

def f(x):return struct.unpack("f",struct.pack("f",float(x)))[0]
def bits(x):return struct.unpack("I",struct.pack("f",f(x)))[0]
def mul(a,b):return f(f(a)*f(b))
def div(a,b):return f(f(a)/f(b))
def font(owner,z,size,kind,value):
    size=mul(size,z)
    if kind==0:value=mul(value,z)
    elif kind==3:value=mul(size,value);kind=0
    return dict(owner=owner,size=size,kind=kind,value=f(value),em=int(mul(size,60)),internal=60,external=120)
def app_units(value):
    scaled=mul(value,60)
    if scaled>=f((1<<30)-1):return (1<<30)-1
    if scaled<=f(-((1<<30)-1)):return -((1<<30)-1)
    return int(f(scaled+0.5)) if scaled>=0 else int(f(scaled-0.5))

def observe(events,variant="candidate",mutant=0):
    cache=0.0; used=False; foreign=64.0; foreign_used=False; pc=True; publishes=0
    rows=[];root=None;version=0
    for e in events:
        trace=[]
        def event(kind,owner,a=0,b=0):trace.append([kind,owner,bits(a),bits(b)])
        def get_font(p,base=0):event(2 if base==0 else 3,p['owner']);return p
        def zoom(value,z):event(30,0,value,z);return value if z==1 else mul(value,z)
        def unzoom(value,z):event(32,0,value,z);return value if z==1 else div(value,z)
        def height(p):
            event(20,p['owner'],0 if p['kind']==2 else p['value'],p['size'])
            if p['kind']==0:au=app_units(p['value'])
            elif p['kind']==1:au=app_units(mul(p['size'],p['value']))
            elif pc:
                event(21,p['owner'],1,p['size'])
                au=p['em']+p['internal']+p['external']
            else:au=app_units(mul(p['size'],f(1.2)))
            event(22,p['owner'],au)
            return div(f(au),60)
        if e['event']=='ROOT':
            version=e['epoch'];root=dict(owner=e['doc']*10000+e['element'],zoom=f(e['zoom']))
            root['font']=font(root['owner'],root['zoom'],e['size'],e['form'],e['value'])
            rows.append(dict(event='root',version=version,owner=root['owner'],cache_bits=bits(cache),used=used))
        elif e['event']=='PUBLISH':
            if mutant!=7 or publishes==0:
                value=height(get_font(root['font']))
                cache=value if mutant==3 else unzoom(value,root['zoom'])
                event(41,root['owner'],cache)
            publishes+=1
            rows.append(dict(event='publish',version=version,owner=root['owner'],cache_bits=bits(cache),used=used,trace=trace))
        elif e['event']=='FOREIGN':
            foreign=f(e['value']);rows.append(dict(event='foreign',cache_bits=bits(cache)))
        elif e['event']=='READ':
            pc=bool(e['pc']);role=e['role'];base=e['base'];unit=e['unit'];coef=f(e['coefficient'])
            owner=root['owner'] if role in [0,3] else e['owner']
            z=root['zoom'] if role in [0,3] else f(e['zoom'])
            cur=root['font'] if role in [0,3] else font(owner,z,e['size'],e['form'],e['value'])
            par=font(e['parentOwner'],f(e['parentZoom']),e['parentSize'],e['parentForm'],e['parentValue'])
            ini=font(10000,1,e['initialSize'],e['initialForm'],e['initialValue'])
            local=div(z,e['parentZoom']);flags=1;fd=ld=0
            fontbase=0 if e.get("call",0)==1 else base
            selected=par if fontbase else cur
            get_font(selected,fontbase);event(1,selected['owner'],selected['size'])
            ref_size=zoom(selected['size'],local) if fontbase else selected['size']
            if fontbase:zoom(selected['size'],local)
            def builder_height():
                nonlocal flags
                selected=cur if base==0 or mutant==5 else par
                get_font(selected,0 if base==0 or mutant==5 else 1)
                if selected['kind']==2:flags |= 2 if base==0 else 4
                val=height(selected)
                return zoom(val,local) if base and mutant!=10 else val
            device_owner=20010 if mutant==6 and role==2 and unit==0 else root['owner']
            if unit==0:
                if role in [0,3]:
                    value=height(get_font(ini)) if mutant==4 else builder_height()
                    if variant=='original' or mutant==1:value=zoom(value,z)
                elif role==1:
                    value=zoom(height(get_font(ini)),z)
                else:
                    val=foreign if mutant==6 else cache
                    event(40,device_owner,val)
                    if mutant==6:foreign_used=True
                    else:used=True
                    value=val if mutant==2 else zoom(val,z)
            elif unit==1:
                if role==1:value=height(get_font(ini))
                else:
                    value=builder_height()
                    if base==0:ld=bits(value)
            elif unit in [2,3]:
                if unit==3 and role==2:
                    event(4,root['owner'],16);value=zoom(16,z)
                else:value=ref_size
                if unit==2 and base==0:fd=bits(ref_size)
            else:
                root_unit=unit in [5,7,9,11]
                if root_unit and role==2:
                    event(4,root['owner'],16);value=zoom(16,z)
                else:
                    get_font(selected,base)
                    metric_flag=1 if unit in [6,7] else 2 if unit in [10,11] else 0
                    event(5,selected['owner'],metric_flag)
                    value=8.0
            factor=1.0 if mutant==8 else coef
            event(31,0,value,factor);value=mul(value,factor)
            if mutant==9:event(31,0,value,coef);value=mul(value,coef)
            exposed=unzoom(value,z)
            rows.append(dict(event='read',id=e['id'],version=version,owner=owner,provider_device=device_owner,
              scaled_bits=bits(value),exposed_bits=bits(exposed),cpp_bits=bits(div(value,z)),cache_bits=bits(cache),
              used=foreign_used if mutant==6 and role==2 and unit==0 else used,flags=flags,font_dependency=fd,lh_dependency=ld,trace=trace))
        else:raise ValueError(e)
    return rows

def semantic_expectations(events):
    root=None;latest=None;results={}
    for e in events:
        if e['event']=='ROOT':
            root=e
            value=Fraction(str(e['value']))
            root_sem=Fraction(str(e['size']))*value if e['form'] in [1,3] else value
        elif e['event']=='PUBLISH':latest=root_sem
        elif e['event']=='READ' and e['unit']==0 and not e['diagnostic']:
            if root['form']==2:continue
            if e['role']==0:
                base=root_sem if e['base']==0 else Fraction(str(e['parentValue']))*(Fraction(str(e['parentSize'])) if e['parentForm'] in [1,3] else 1)
            elif e['role']==1:base=Fraction(str(e['initialValue']))
            else:base=latest
            results[e['id']]=base*Fraction(str(e['coefficient']))
    return results
