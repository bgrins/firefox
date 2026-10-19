import math
import struct
from cases import bits


def unbits(n):return struct.unpack('d',struct.pack('Q',n))[0]


def helper(x,w,m,candidate):
    if candidate and w==0:return x
    y=x+m
    return math.ceil(y/w)*w if w>0 else y


class Provider:
    def __init__(self,c,events,begin,atstart,normal=False,display=False,store=None):
        self.c=c;self.events=events;self.begin=begin;self.start=begin if atstart else None
        self.normal=normal;self.display=display;self.store=store;self.cache=None
        self.limit=0;self.position=c['initial'];self.minimum=-1
        self.events.append([5,0,0])
    def width(self):
        c=self.c
        if c['kind']:
            self.events.extend([[22,0,0],[20,0,0],[21,0,0]])
            return c['width']/20*(20+c['letter'])
        return c['width']
    def metric(self):
        if self.minimum<0:
            self.events.append([10,0,0]);self.minimum=self.c['minimum']
        return self.minimum
    def spacing(self,begin,end,ignore=False):
        c=self.c;t=c['tokens'];out=[[0,0] for _ in range(begin,end)]
        if c['flags']&2:return out,False
        before=math.floor(c['letter']*.5+.5) if c['model']==2 else 0
        after=c['letter']-before
        for i in range(begin,end):
            if i!=self.start and before and (i==0 or t[i]!=-1):out[i-begin][0]=before
            if after and (i+1>=len(t) or t[i]!=-1):out[i-begin][1]=after
        present=bool(c['letter'])
        if not ignore and -1 in t:
            w=self.width()
            if w>0:
                self.calculate(begin,end,w)
                if self.cache is not None:
                    for i,value in self.cache['records']:
                        if begin<=i+self.begin<end:out[i+self.begin-begin][1]+=value
                    present=True
        return out,present
    def calculate(self,begin,end,width):
        if self.cache is None:
            if not self.normal and not self.display:return
            if self.display:
                self.events.append([3,0,0]);self.cache=self.store;return
        current_limit=(self.cache['limit'] if self.cache else self.limit)+self.begin
        if current_limit<end:
            for i in range(current_limit,end):
                spacing,_=self.spacing(i,i+1,True);b,a=spacing[0];self.position+=b
                if self.c['tokens'][i]==-1:
                    if self.cache is None:
                        self.cache=dict(limit=0,records=[]);self.events.append([4,0,0])
                    nxt=helper(self.position,width,self.metric(),self.candidate)
                    delta=nxt-self.position
                    self.cache['records'].append([i-self.begin,int(delta+.5) if delta>=0 else int(delta-.5)])
                    self.position=nxt
                else:
                    self.events.append([11,i,i+1]);self.position+=self.c['tokens'][i]
                self.position+=a
            if self.cache is not None:self.cache['limit']=end-self.begin
        if self.cache is None:
            self.events.append([7,0,0]);self.limit=max(self.limit,end-self.begin)


def run(c,candidate):
    if c['mode']==0:
        x,w,m=map(unbits,c['bits']);return dict(id=c['id'],mode=0,bits=bits(helper(x,w,m,candidate)))
    events=[];mode=c['mode'];tokens=c['tokens'];begin,end=c['begin'],c['end']
    if mode in [1,2]:
        state=[c['initial'],0,not bool(c['flags']&8),not bool(c['flags']&8),False]
        ranges=[(begin,end)] if c['split']<0 else [(begin,c['split']),(c['split'],end)]
        for a,b in ranges:
            if mode==2 and c['flags']&16:events.append([2,0,0])
            events.append([1,a,b])
            if c['flags']&1:continue
            p=Provider(c,events,a,state[2 if mode==1 else 3]);p.candidate=candidate
            if mode==1:events.append([6,a,b])
            if c['flags']&2:
                state[0]+=20;state[1]=0
                if mode==2:state[3]=False
                continue
            if mode==1 and c['flags']&4:
                events.append([30,0,0]);state[0]+=max([max(0,x) for x in tokens[a:b]],default=0)
                state[1]=0;state[2]=False;events.append([30,0,0]);continue
            if mode==2:events.append([6,a,b])
            cursor=a;width=None
            while cursor<b:
                stop=cursor
                while stop<b and tokens[stop]!=-1:stop+=1
                if stop>cursor:
                    advance=sum(tokens[cursor:stop])
                    if c['letter']:
                        events.append([11,cursor,stop]);sp,_=p.spacing(cursor,stop)
                        advance=math.ceil(advance+sum(sum(s) for s in sp))
                    state[0]=min((1<<30)-1,state[0]+max(0,advance));state[1]=0
                    state[2 if mode==1 else 3]=False
                if stop<b:
                    sp,_=p.spacing(stop,stop+1);before,after=sp[0]
                    state[0]+=int(before)
                    if width is None or width<0:width=p.width()
                    state[0]=int(helper(state[0],width,p.metric(),candidate)+after)
                    if mode==2:state[3]=False
                cursor=stop+1
        return dict(id=c['id'],mode=mode,state=state,events=events)
    p=Provider(c,events,begin,not bool(c['flags']&8),normal=mode!=6);p.candidate=candidate
    spacing=[[0,0] for _ in range(begin,end)];present=False
    if mode in [6,7,8]:p.calculate(begin,end,c['width'])
    else:
        if mode==4:p.spacing(begin,begin+(end-begin)//2)
        spacing,present=p.spacing(begin,end)
        if mode==4:spacing,present=p.spacing(begin,end)
        if mode==5:
            d=Provider(c,events,begin,False,display=True,store=p.cache);d.candidate=candidate
            spacing,present=d.spacing(begin,end)
    cache=[] if p.cache is None else [p.cache['limit'],0]+p.cache['records']
    return dict(id=c['id'],mode=mode,value=c['initial']+sum(max(0,x) for x in tokens[begin:end])+sum(sum(s) for s in spacing),
                state=[p.position,p.limit,p.minimum,present],spacing=spacing,cache=cache,events=events)
