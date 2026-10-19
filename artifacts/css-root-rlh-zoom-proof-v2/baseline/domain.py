import struct
from fractions import Fraction as Q

def q(x): return Q(str(x))
def binary32(x):
    x=Q(x)
    denominator=x.denominator
    assert denominator & (denominator-1)==0,("not dyadic",x)
    n=x.numerator;e=-(denominator.bit_length()-1)
    while n and n%2==0:n//=2;e+=1
    assert abs(n)<2**24 and -126<=e<=100,("outside binary32 profile",x,n,e)
    packed=struct.unpack("f",struct.pack("f",float(x)))[0]
    assert Q(packed)==x,("inexact binary32",x)
    return dict(value=str(x),significand=n,exponent=e)
def provider(size,form,value,z):
    size,value,z=map(q,(size,value,z))
    assert z>0
    sem=size*value if form in (1,3) else value
    scaled_font=size*z
    scaled=scaled_font*value if form in (1,3) else value*z
    au=scaled*60
    assert au.denominator==1 and 0<=au<=1048576,("outside exact app-unit grid",au)
    values=[size,value,z,sem,scaled_font,scaled,au,au+Q(1,2),au/60,scaled/z]
    return sem,scaled,[binary32(v) for v in values]
def admit(events):
    root=None;published=False;admissions=[]
    for e in events:
        if e['event']=='ROOT':root=e;published=False
        elif e['event']=='PUBLISH':published=True
        elif e['event']=='READ' and e['unit']==0 and not e['diagnostic']:
            assert root['form'] in (0,1,3) and e['role'] in (0,1,2)
            assert e['role']!=2 or published
            assert e['owner']//10000==root['doc'] and e['parentOwner']//10000==root['doc']
            rs,rv,rw=provider(root['size'],root['form'],root['value'],root['zoom'])
            ps,pv,pw=provider(e['parentSize'],e['parentForm'],e['parentValue'],e['parentZoom'])
            ins,inv,iw=provider(e['initialSize'],e['initialForm'],e['initialValue'],1)
            z=q(root['zoom'] if e['role']==0 else e['zoom']);c=q(e['coefficient'])
            cs,cv,cw=provider(root['size'] if e['role']==0 else e['size'],root['form'] if e['role']==0 else e['form'],root['value'] if e['role']==0 else e['value'],z)
            sem=(rs if e['base']==0 else ps) if e['role']==0 else ins if e['role']==1 else rs
            extra=[z/q(e['parentZoom']),pv*(z/q(e['parentZoom'])),sem*z,c,sem*z*c,(sem*z*c)/z]
            admissions.append(dict(id=e['id'],rootEpoch=root['epoch'],form=root['form'],role=e['role'],base=e['base'],witnesses=rw+pw+iw+cw+[binary32(v) for v in extra]))
    return admissions

def rejected_domains():
    attempts=[('zero zoom',16,0,20,0),('negative zoom',16,0,20,-1),('non-grid',16,0,Q(1,128),1),('saturation',16,0,2**30,1),('non-dyadic',16,0,Q(1,3),1)]
    output=[]
    for name,size,form,value,z in attempts:
        try:provider(size,form,value,z)
        except AssertionError:output.append(name)
        else:raise AssertionError(('negative domain admitted',name))
    return output
