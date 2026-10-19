from fractions import Fraction
from support_b import oracle as ranks

FALLBACKS = ((1,2,3),(0,3,2),(3,0,1),(2,1,0))


def minimum_filter(items, coordinates):
    result = list(items)
    for axis in range(4):
        if result:
            minimum = min(coordinates(x)[axis] for x in result)
            result = [x for x in result if coordinates(x)[axis] == minimum]
    return result


class World:
    def __init__(self, case, variant, gtk=False, sizes=(16,48)):
        self.c, self.variant, self.gtk, self.sizes = case, variant, gtk, sizes
        self.fs, self.flags = case['faces'], case['flags']
        self.events, self.counters = [], [0,0,0]
        self.ids = list(range(len(self.fs)))
        if self.flags & 256 and len(self.ids)>1: self.ids[-1]=0
        self.target = 3584 if case['target']==30000 else case['target']
        self.tuple = variant in ('A','AB')
        self.inc = None
        self.best = None
        self.coords = [ranks.coordinates(case,f,variant) for f in self.fs]

    def event(self, kind, ident): self.events.append(f'{kind}:{ident}')

    def score(self, i, narrow=False, mismatch=False, log=False):
        if log:
            for kind in ('width','style','weight'): self.event(kind,i)
        coords = self.coords[i]
        if self.tuple: return (int(mismatch),)+coords
        value = coords[0]*100000000+coords[1]*10000+coords[2]
        if narrow: value = ranks.float32(value)
        if mismatch:
            value += 1000000000000
            if narrow: value = ranks.float32(value)
        return value

    def add_mismatch(self, score, narrow=False):
        if self.tuple: return (1,)+score[1:]
        return ranks.float32(score+1000000000000) if narrow else score+1000000000000

    def better(self, a, b):
        if b is None: return True
        if self.tuple: return minimum_filter([0,1],lambda i:(a,b)[i])==[0]
        return a < b

    def winners(self, ids):
        if self.tuple: return minimum_filter(ids,lambda i:(0,)+self.coords[i])
        best = min((self.score(i) for i in ids), default=None)
        return [i for i in ids if self.score(i)==best]

    def presented(self, i, score, narrow=False):
        if not self.c['presentation']: return score
        self.event('font',i)
        if not self.fs[i][8]: return None
        self.event('color',i)
        if bool(self.fs[i][9]) != (self.c['presentation']>=3):
            score = self.add_mismatch(score,narrow)
        return score

    def update_named(self, i, score):
        take = self.better(score,self.inc)
        if not take and score==self.inc:
            self.event('name',i); self.event('name',self.best)
            take = i<self.best if self.flags&128 else i>self.best
        if take: self.best,self.inc=i,score

    def simple_slots(self, ids, shared=False):
        if not shared:
            if len(ids)>4 or not ids: return False, ids
            if len(ids)==1: return True, ids
            self.event('width',ids[0])
            first = self.fs[ids[0]][4:6]
            if first[0]!=first[1]: return False,ids
        elif not 2<=len(ids)<=4: return False,ids
        slots = [None]*4
        for i in ids:
            f=self.fs[i]
            if not shared:
                self.event('width',i)
                if f[4:6]!=first or f[0] not in (0,25600): return False,ids
                self.event('weight',i)
                if f[2]!=f[3]: return False,ids
                self.event('style',i)
                if f[0]!=f[1]: return False,ids
                self.event('weight',i)
            elif f[0]!=f[1] or f[2]!=f[3] or f[4]!=f[5] or f[4]!=6400:
                return False,ids
            slot = int(f[2]>=38400)+2*int(f[0]!=0)
            if slots[slot] is not None: return False,ids
            slots[slot]=i
        return True,slots

    def select_simple(self, ids, shared=False, published=False):
        want = int(self.c['weight']>32000 if shared else self.c['weight']>=38400)+2*int(self.target!=0)
        for slot in (want,)+FALLBACKS[want]:
            i=ids[slot]
            if shared:
                self.event('pointer',-1 if published else i if i is not None else -1)
                if i is not None:
                    self.event('descriptor',i)
                    if self.fs[i][11]: return [i]
            elif i is not None: return [i]
        return []

    def family_styles(self, ids=None, shared=False, simple=False, published=False, family=100):
        ids=self.ids if ids is None else ids
        if shared:
            self.event('initialized',family)
            if self.flags&1: return []
            self.event('faces',family)
            if self.flags&2: return []
            if published: self.event('pointer',-1)
            if len(ids)==1:
                i=ids[0];self.event('pointer',-1 if published else i)
                self.event('descriptor',i)
                selected=[i] if self.fs[i][11] else []
            elif simple:
                selected=self.select_simple(ids,True,published)
            else:
                available=[]
                for i in ids:
                    self.event('pointer',-1 if published else i)
                    if published or self.fs[i][12]!=2: available.append(i)
                selected=self.winners(available)
        else:
            if len(ids)==1: return list(ids)
            if simple: return self.select_simple(ids)
            order=list(reversed(ids))
            for i in order: self.score(i,log=True)
            selected=self.winners(order)
            selected=[i for k,i in enumerate(selected) if not k or i!=selected[k-1]]
        if shared and self.gtk:
            candidates=[i for i in selected if self.fs[i][13] and abs(self.fs[i][13]-20)*5<=self.fs[i][13]]
            size=self.fs[min(candidates,key=lambda i:abs(self.fs[i][13]-20))][13] if candidates else 0
            if any(self.fs[i][13] for i in selected): selected=[i for i in selected if self.fs[i][13]==size]
        return selected

    def search_unshared(self, ids=None, family=100, covered=None, initialized=None):
        ids=self.ids if ids is None else ids
        initialized=not(self.flags&32) if initialized is None else initialized
        covered=not(self.flags&16) if covered is None else covered
        if not initialized:self.event('readmaps',family)
        self.event('map',family)
        if not covered:return
        for i in reversed(ids):
            self.event('char',i)
            if not self.fs[i][6]:continue
            score=self.presented(i,self.score(i,narrow=True,log=True),True)
            if score is not None:self.update_named(i,score)

    def find_char(self, ids=None, family=100, covered=None, initialized=None):
        ids=self.ids if ids is None else ids
        initialized=not(self.flags&32) if initialized is None else initialized
        covered=not(self.flags&16) if covered is None else covered
        if initialized:
            self.event('map',family)
            if not covered:return
        candidates=self.family_styles(ids)
        found=None; score=None
        for i in candidates:
            self.event('skip',i)
            if self.fs[i][7]:continue
            self.counters[1]+=1;self.event('char',i)
            if not self.fs[i][6]:continue
            self.counters[0]+=1;found=i;score=self.score(i,narrow=True,log=True)
            actual=self.presented(i,score,True)
            if actual is None:continue
            score=actual;break
        if found is None and (self.target!=0 or self.c['weight']!=25600 or self.c['width']!=6400):
            incumbent,best=self.inc,self.best
            self.inc=self.best=None
            self.search_unshared(ids,family,covered,initialized)
            found,score=self.best,self.inc
            self.inc,self.best=incumbent,best
        if found is not None:self.update_named(found,score)

    def search_shared(self, ids=None, family=100, separate=False):
        ids=self.ids if ids is None else ids
        mapid=ids[0] if separate else 100
        self.event('pointer',mapid)
        hasmap=True if separate else not(self.flags&4)
        if not hasmap:
            self.event('initialize',family)
            if self.flags&8:return
            self.event('pointer',mapid);hasmap=not(self.flags&16384)
        if hasmap:
            self.event('map',mapid)
            if (not self.fs[ids[0]][6]) if separate else bool(self.flags&16):return
        self.event('faces',family)
        if not separate and self.flags&2:return
        loaded=0
        for i in ids:
            self.event('pointer',i)
            if not separate and self.fs[i][12]==2:continue
            self.event('descriptor',i)
            self.event('pointer',i)
            known=self.fs[i][10]
            if known:
                loaded+=1;self.event('map',i)
                if not self.fs[i][6]:continue
            score=self.score(i)
            if not self.better(score,self.inc):continue
            self.event('entry',i)
            if not self.fs[i][12]:continue
            if not known:
                self.event('char',i)
                if not self.fs[i][6]:continue
            actual=self.presented(i,score)
            if actual is None or not self.better(actual,self.inc):continue
            self.best,self.inc=i,actual
        if not hasmap and loaded==len(ids):self.event('setupmap',family)

    def global_fallback(self, shared=False, separate=False):
        if self.flags&512:
            self.event('platform',0)
            if self.fs:
                self.event('visible',100);self.event('font',0)
                if self.fs[0][8]:
                    if not self.c['presentation']:return [0]
                    self.event('color',0)
                    if bool(self.fs[0][9])==(self.c['presentation']>=3):return [0]
        if not(shared and self.flags&4096):
            families=[[i] for i in range(len(self.fs))] if separate else [self.ids]
            for index,ids in enumerate(families):
                family=100+index;self.event('visible',family)
                if separate and index==0 and self.flags&1024:continue
                if shared and separate and index==0 and self.flags&2048:
                    self.event('async',index);continue
                if shared:self.search_shared(ids,family,separate)
                else:self.find_char(ids,family,True if separate else None,True if separate else None)
                if self.inc==((0,0,0,0) if self.tuple else 0):break
        self.counters[2]=0 if shared else self.counters[1]
        self.counters[:2]=[0,0]
        if self.best is not None:
            self.event('font',self.best)
            if self.fs[self.best][8]:return [self.best]
        return []

    def run(self):
        op=self.c['operation']; selected=[]
        if op==1:selected=self.family_styles()
        elif op==2:selected=self.family_styles(shared=True,simple=bool(self.flags&64))
        elif op==3:self.search_unshared()
        elif op==4:self.search_shared()
        elif op==5:self.find_char()
        elif op in (6,7,10,11):selected=self.global_fallback(op in (7,11),op in (10,11))
        elif op==8:selected=[3584,14]
        elif op==9:
            simple,ids=self.simple_slots(self.ids)
            selected=[int(simple)]+self.family_styles(ids,simple=simple)
        elif op==12:
            simple,ids=self.simple_slots(list(range(len(self.fs))),True)
            self.event('allocate',len(ids)*self.sizes[0]);self.event('pointer',-1)
            for i in ids:
                if i is not None:
                    self.event('allocate',self.sizes[1]);self.event('pointer',-1)
                    self.event('construct-face',i);self.event('setmap',i)
            selected=[int(simple)]+self.family_styles(ids,True,simple,True)
        elif op==13:selected=list(self.sizes)
        if 3<=op<=5 and self.best is not None:selected=[self.best]
        return dict(id=self.c['id'],scores=[int(x[1]*256) for x in self.coords],selected=selected,counters=self.counters,events=self.events)


def expected(case,variant,gtk=False,sizes=(16,48)):
    return World(case,variant,gtk,sizes).run()
