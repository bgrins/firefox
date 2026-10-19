import copy
import math
import struct
from fractions import Fraction


def numeric(v):
    return format(v, '.17g')


def f32(x):
    return struct.unpack('f',struct.pack('f',x))[0]


def specified(frames):
    return [(f['offset'],f['easing'],f['composite'],[(p[0],p[1],p[3]) for p in f['properties']]) for f in frames]


def derive(frames, context):
    ordinary=[i for i,f in enumerate(frames) if f['offset'] is None or f['offset'][0]==0]
    anchors={j:Fraction(frames[i]['offset'][1]) for j,i in enumerate(ordinary) if frames[i]['offset'] is not None}
    if ordinary:
        anchors.setdefault(0,Fraction(0 if len(ordinary)>1 else 1))
        anchors.setdefault(len(ordinary)-1,Fraction(1))
    answer=[None]*len(frames)
    for j,i in enumerate(ordinary):
        if j in anchors:answer[i]=frames[i]['offset'][1] if frames[i]['offset'] is not None else float(anchors[j]);continue
        a=max(k for k in anchors if k<j);b=min(k for k in anchors if k>j)
        answer[i]=float((anchors[a]*(b-j)+anchors[b]*(j-a))/(b-a))
    for i,f in enumerate(frames):
        if f['offset'] is None or f['offset'][0]==0:continue
        if not context['active'] or context['view']<=0 or not context['resolved']:continue
        p=Fraction(f['offset'][1]);value=Fraction(context['start'])+Fraction(context['delta'])*p
        width=Fraction(context['last'])-Fraction(context['first'])
        if width:answer[i]=float((value-Fraction(context['first']))/width)
    return answer


def segments(frames, default, style):
    grouped={}
    if style['fail']:return []
    for f in frames:
        if f['computed'] is None:continue
        for pid,name,allocation,value in f['properties']:
            key=(pid,name)
            v=None if value is None else value*style['scale']
            grouped.setdefault(key,[]).append((f32(f['computed']),v,f['easing'],default if f['composite']==3 else f['composite']))
    result=[]
    order={0:2,1:0,2:1,3:3,4:4}
    for key,entries in sorted(grouped.items(),key=lambda p:(order[p[0][0]],p[0][1])):
        groups=[]
        for entry in sorted(entries,key=lambda e:e[0]):
            if not groups or groups[-1][0][0]!=entry[0]:groups.append([])
            groups[-1].append(entry)
        built=[]
        def connect(a,b):return [a[0],b[0],a[1],b[1],a[2],a[3],b[3]]
        first,last=groups[0][0],groups[-1][-1]
        if first[0]>0:built.append([0,first[0],None,first[1],-1,0,first[3]])
        for i,g in enumerate(groups):
            if g[0][0] in (0,1) and len(g)>1:built.append(connect(g[0],g[-1]))
            if i+1<len(groups):built.append(connect(g[-1],groups[i+1][0]))
        if last[0]<1:built.append([last[0],1,last[1],None,last[2],last[3],0])
        result.append([*key,False,built])
    return result


class Oracle:
    def __init__(self):self.step=0
    def event(self,s):self.trace.append(s)
    def comparator_trace(self,left,right):
        if len(left)!=len(right):return
        for a,b in zip(left,right):
            if (a['offset'],a['easing'],a['composite'])!=(b['offset'],b['easing'],b['composite']):return
            if len(a['properties'])!=len(b['properties']):return
            for x,y in zip(a['properties'],b['properties']):
                if x[:2]!=y[:2]:return
                if x[2]==y[2]:continue
                if x[2]<0 or y[2]<0:return
                self.event(f'declaration-equals:{x[2]}:{y[2]}')
                if x[3]!=y[3]:return
    def context(self):return dict(self.env,active=self.animation and self.env['view']>=0)
    def map_trace(self,f):
        c=self.context()
        if not c['active'] or c['view']<=0:return
        self.event('timeline-map:'+str(f['offset'][0])+':'+numeric(f['offset'][1]))
        if c['resolved']:self.event('attachment-range')
    def update(self):
        self.event('update');self.event('build')
        properties=[]
        if self.target:
            self.event('ordinary-keyframes');self.event('computed-values');self.event('pres-context')
            if not self.style['fail']:
                for f in self.frames:
                    for pid,name,alloc,value in f['properties']:self.event(f'computed-value:{pid}:{alloc}')
            properties=segments(self.frames,self.default,self.style)
        equivalent=lambda ps:[[p[0],p[1],p[3]] for p in ps]
        changed=equivalent(properties)!=equivalent(self.properties)
        self.event('base-styles')
        base=[] if self.target else copy.deepcopy(self.base)
        if self.target:self.event('pres-context')
        needed=[]
        for pid,name,running,segs in properties:
            if any(s[2] is None or s[3] is None or s[5]!=0 or s[6]!=0 for s in segs):base.append([pid,name,self.style['base']]);needed.append(pid)
        if needed:self.event('base-context')
        for pid in needed:self.event(f'base-value:{pid}')
        base.sort(key=lambda p:(p[0],p[1]))
        basechanged=any(p not in self.base for p in base);self.base=base
        if not changed:
            if basechanged:self.event('restyle')
            return
        running={p[0] for p in self.properties if p[2]}
        self.properties=properties;self.event('effect-set');self.cumulative=0
        for p in self.properties:
            p[2]=p[0] in running;self.event(f'cumulative:{p[0]}');self.cumulative+=1
        self.event('cascade-dirty')
        if self.animation:self.event('effect-updated')
        self.event('restyle')
    def refresh(self):
        self.event('refresh')
        if not self.ranged:return
        derived=derive(self.frames,self.context());changed=False
        for i,f in enumerate(self.frames):
            if f['offset'] is None or f['offset'][0]==0:continue
            self.map_trace(f)
            changed|=f['computed']!=derived[i];f['computed']=derived[i]
        if changed and self.target:
            self.event('target-style')
            if self.style_on:self.update()
    def get(self, failure=0):
        self.event('get');result=[]
        if failure==1:self.event('error:1');return result,1
        if self.animation and self.env['view']>=0:self.refresh()
        self.event('style-data');self.event('ordinary-keyframes')
        for f in self.frames:
            offset=None
            if f['offset'] is not None:
                kind,v=f['offset']
                if kind==0:offset=v
                else:self.event('range-name');self.event('percent-unit');offset=[str(kind),v*100]
            easing='linear' if f['easing'] in (-1,0) else 'ease' if f['easing']==1 else 'steps(2)'
            obj=dict(offset=offset,computed=f['computed'],easing=easing,composite=f['composite'],properties=[],offsetNegativeZero=isinstance(offset,(int,float)) and offset==0 and math.copysign(1,offset)<0,computedNegativeZero=f['computed'] is not None and f['computed']==0 and math.copysign(1,f['computed'])<0)
            self.event('dictionary')
            if failure==2:self.event('error:2');return result,2
            for pid,name,alloc,value in f['properties']:
                text=''
                if alloc>=0:self.event(f'serialize:{alloc}');text=numeric(value)
                else:
                    for p,n,v in self.base:
                        if (p,n)==(pid,name):self.event('serialize-base');text=numeric(v);break
                key=['opacity','cssFloat','cssOffset','width','--'+name][pid]
                self.event('js-string')
                if failure==3:self.event('error:2');return result,2
                self.event('define:'+key)
                if failure==4:self.event('error:2');return result,2
                obj['properties'].append([key,text])
            result.append(obj)
        return result,0
    def apply(self, action):
        self.trace=[];op=action['op'];getter=[];error=0
        if op=='RESET':
            self.target=action['target'];self.style_on=action['style'];self.animation=action['animation'];self.relevant=action['relevant'];self.env=copy.deepcopy(action['env']);self.style=dict(base=action['base'],scale=action['scale'],fail=action['fail']);self.default=action['default'];self.frames=[];self.ranged=0;self.properties=[];self.base=[];self.cumulative=0
        elif op=='SET':
            self.event('process')
            if action['error']:self.event('error:3');error=3
            else:
                self.event('target-style');frames=copy.deepcopy(action['frames']);self.comparator_trace(frames,self.frames)
                if specified(frames)!=specified(self.frames):
                    self.frames=frames;self.event('compute');derived=derive(frames,self.context());self.ranged=0
                    for i,f in enumerate(frames):
                        f['computed']=derived[i]
                        if f['offset'] is not None and f['offset'][0]!=0:self.ranged=1;self.map_trace(f)
                    if self.animation and self.relevant:self.event('notify')
                    if self.target and self.style_on:self.update()
        elif op=='DEFAULT':
            if self.default!=action['value']:
                self.default=action['value']
                if self.animation and self.relevant:self.event('notify')
                if self.target:
                    self.event('target-style')
                    if self.style_on:self.update()
        elif op=='GET':getter,error=self.get(action['failure'])
        elif op=='CONTEXT':self.env=copy.deepcopy(action['env']);getter,error=self.get()
        elif op=='INVALIDATE':
            self.style.update(base=action['base'],scale=action['scale']);self.target=action['target'];self.style_on=action['style']
        elif op=='STYLE':self.style.update(base=action['base'],scale=action['scale']);self.update()
        elif op=='RUNNING':
            for p in self.properties:p[2]=True
        else:raise AssertionError(op)
        answer=dict(step=self.step,op=op,error=error,frames=self.frames,range=self.ranged,default=self.default,properties=self.properties,base=self.base,cumulative=self.cumulative,getter=getter,trace=self.trace);self.step+=1
        answer=copy.deepcopy(answer)
        for f in answer['frames']:
            f['offsetNegativeZero']=f['offset'] is not None and f['offset'][1]==0 and math.copysign(1,f['offset'][1])<0
            f['computedNegativeZero']=f['computed'] is not None and f['computed']==0 and math.copysign(1,f['computed'])<0
        return answer
