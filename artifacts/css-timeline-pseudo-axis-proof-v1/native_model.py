"""Native-shaped provider execution, separately implemented from oracle.py."""

class Model:
    def __init__(self,w,variant):
        self.w=w;self.es={e[0]:e for e in w['elements']};self.fs={f[0]:f for f in w['frames']};self.trace=[];self.variant=variant
    def q(self,id,op,result,arg=0):
        self.trace.append([id,op,arg,int(result)]);return result
    def primary(self,e):return self.q(e,1,self.es[e][1])
    def owner(self,e):return self.q(e,12,2000)
    def root(self):return self.q(2000,19,self.w['root'])
    def scrolling(self):return self.q(2000,18,self.w['scrolling'])
    def shell(self):return self.q(2000,11,2001 if self.w['shell'] else 0)
    def rootframe(self):return self.q(2001,17,self.w['root_frame'])
    def pseudo(self,e,p):return self.q(e,2,self.es[e][6+p] if p else e,p)
    def parentframe(self,f):return self.q(f,3,self.fs[f][1])
    def pair(self,e):
        kind=self.es[e][2]
        if 1<=kind<=6:return self.q(e,14,self.es[e][3]),kind
        if kind==7:self.owner(e);return self.root(),kind
        return e,0
    def nearest(self,e,p):
        if not self.primary(e):return 0,0
        subject=self.pseudo(e,p)
        if not subject:return 0,0
        self.owner(subject);root=self.scrolling()
        if root==subject:return root,0
        sf=self.primary(subject)
        if not sf:return 0,0
        curr=self.parentframe(sf)
        while curr:
            content=self.q(curr,15,self.fs[curr][2])
            if not content or not self.q(content,13,self.es[content][4]):
                curr=self.parentframe(curr);continue
            if content==root:break
            if self.q(curr,4,self.fs[curr][3]):return self.pair(content)
            curr=self.parentframe(curr)
        return root,0
    def source(self):
        t,h,p=self.w['type'],self.w['host'],self.w['pseudo']
        if t==3:return h,p
        if t==2:return self.nearest(h,p)
        if t in [0,4]:return h,p
        self.owner(h);return self.scrolling(),0
    def resolved(self,h,p,root):
        if not h:return 0
        if root:return self.rootframe() if self.owner(h) and self.shell() else 0
        e=self.pseudo(h,p)
        if not e:return 0
        f=self.primary(e)
        self.owner(e)
        if self.root()==e:
            shell=self.q(f,9,2001 if self.fs[f][13] else 0) if f else 0
            if not shell:self.owner(e);shell=self.shell()
            rf=self.rootframe() if shell else 0
            if rf:f=rf
        return self.q(f,16,self.fs[f][4]) if f else 0
    def snapshot(self):
        h,p=self.source();root=False
        if h:self.owner(h);root=self.scrolling()==h
        snap=[h,p,int(root),0,-1,0,-1,0]
        if not h or not self.primary(h):return snap
        f=self.resolved(h,p,root)
        if not f:return snap
        if self.variant=='original':
            assert self.primary(h)
            mode=self.q(self.primary(h),5,self.fs[self.es[h][1]][5],self.fs[self.es[h][1]][14])
        else:mode=self.q(f,5,self.fs[f][5],self.fs[f][14])
        axis=0 if self.w['axis']==2 or (not mode and self.w['axis']==1) or (mode and self.w['axis']==0) else 1
        available=bool(self.q(f,6,self.fs[f][6])&(1<<axis))
        self.q(f,7,self.fs[f][12],self.fs[f][11])
        apz=False
        if self.q(0,21,self.w['apz']):
            if not self.q(h,20,self.es[h][5]):apz=bool(self.q(h,22,self.es[h][6]))
        return [h,p,int(root),1,axis,int(available),self.fs[f][11+axis],int(apz)]
    def sample(self,old,subscribers):
        snap=self.snapshot();cache=None
        if snap[3] and snap[5]:
            f=self.resolved(snap[0],snap[1],snap[2]);assert f
            data=self.fs[f];self.q(f,8,data[8],data[7]);self.q(f,10,data[10],data[9])
            axis=snap[4];cache=[data[7+axis],data[9+axis]]
            if old is None or cache[1]!=old[1]:
                for j in range(subscribers):self.q(3000+j,23,0);self.q(3000+j,24,0)
        exposed=self.source()[0]
        value=None if cache is None else abs(cache[0])/cache[1]
        return dict(snapshot=snap,raw_axis_style=[snap[4],snap[6]] if snap[3] else [0,0],exposed=exposed,cache=cache,data=None if cache is None else [cache[0],0,cache[1]],changed=int(cache!=old),duration=None if value is None else value*100000,percent=None if value is None else value*100,fallback=None if value is None else value*100000,trace=self.trace)

def run(c,variant):
    out=[];old=None
    for i,w in enumerate(c['worlds']):
        row=Model(w,variant).sample(old,c['subscribers']);row.update(case=c['id'],sample=i);out.append(row);old=row['cache']
    return out
