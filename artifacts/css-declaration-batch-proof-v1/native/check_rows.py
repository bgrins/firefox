import re

def natural(s):
 assert re.fullmatch(r'0|[1-9][0-9]*',s),('natural',s)
 return int(s)
def boolean(s):
 assert s in ('0','1'),('boolean',s)
 return int(s)
def entries(s):
 if not s:return []
 out=[]
 for item in s.split(','):
  fields=item.split(':');assert len(fields)==3
  out.append((natural(fields[0]),natural(fields[1]),boolean(fields[2])))
 return out
def bits(s):
 assert re.fullmatch('[01]*',s),('bits',s)
 return list(map(int,s))
def identities(s):
 out=[] if not s else list(map(natural,s.split(',')))
 assert out==sorted(set(out)),('set',s)
 return out
def plans(s):
 out=[]
 if not s:return out
 for item in s.split(','):
  assert re.fullmatch(r'[NA]|[RM](0|[1-9][0-9]*)',item),('plan',item)
  out.append((item[0],None if len(item)==1 else natural(item[1:])))
 return out

def roster(provider):
 keys={r['name']:r['id'] for r in provider['longhands']}
 p,q,r,s,l,c,d=[keys[x] for x in ['padding-top','padding-right','padding-bottom','padding-left','padding-block-start','color','direction']];x=len(keys)+7
 padding=provider['shorthands']['padding'];assert set(padding)=={p,q,r,s}
 for imp in (0,1):
  cases=[
   ('two-removals-rank',[(c,1,1-imp),(p,2,imp),(q,3,1-imp),(l,4,imp),(d,5,1-imp),(x,6,1)],[p,q,c,d]),
   ('rank-before-after',[(c,1,imp),(p,2,1-imp),(d,3,imp),(q,4,1-imp),(l,5,imp),(x,6,0)],[d,p,c,q]),
   ('padding-provider',[(r,1,1-imp),(c,2,imp),(p,3,imp),(q,4,1-imp),(l,5,imp),(x,6,1)],padding),
   ('replacement-only',[(c,1,1-imp),(d,2,imp),(x,3,0)],[d,c,x]),
   ('absent-only',[(l,1,imp),(x,2,1-imp)],[p,q,c]),
   ('no-op',[(p,9,imp),(q,9,imp),(c,9,imp)],[q,c,p]),
   ('move-unchanged',[(p,9,imp),(q,9,imp),(l,9,1-imp),(c,9,imp)],[p,q,c]),
   ('empty-source',[(p,1,imp),(l,2,1-imp)],[]),
   ('empty-destination',[],padding)]
  for name,seed,actions in cases:
   yield name+'-'+str(bool(imp)).lower(),[(k,2000+v,i) for k,v,i in seed],[(k,2009,imp) for k in actions]

def opposite(provider,a,b):
 rows=provider['longhands']
 if a>=len(rows) or b>=len(rows):return False
 a,b=rows[a],rows[b]
 return a['group'] is not None and a['group']==b['group'] and a['logical']!=b['logical']

def independent_step(provider,before,new):
 # Forward CSSOM setter, without inspecting any emitted/native update plan.
 for n,old in enumerate(before):
  if old[0]==new[0]:
   if any(opposite(provider,new[0],other[0]) for other in before[n+1:]):return before[:n]+before[n+1:]+[new]
   return before[:n]+[new]+before[n+1:]
 return before+[new]

def independent_plan(provider,before,new):
 # Initial source plan is checked separately from the sequential outcome oracle.
 for n,old in enumerate(before):
  if old[0]==new[0]:
   if any(opposite(provider,new[0],x[0]) for x in before[n+1:]):return ('M',n)
   return ('N',None) if old==new else ('R',n)
 return ('A',None)

def verify(text,provider,variant):
 assert text.endswith('\n')
 lines=text.splitlines();cases=list(roster(provider));assert len(lines)==len(cases)==18
 failures=[];branches={x:0 for x in 'NARM'};panics=0
 for line,(name,before,actions) in zip(lines,cases,strict=True):
  f=line.split('\t');assert len(f)==15 and f[:2]==['ROW',name],('field/roster',f[:2])
  gate,newcount,removal,completed=boolean(f[2]),natural(f[3]),boolean(f[4]),boolean(f[5])
  actualbefore=entries(f[6]);beforebits=bits(f[7]);beforeset=identities(f[8]);actualactions=entries(f[9]);initialplans=plans(f[10]);actual=entries(f[11]);actualbits=bits(f[12]);actualset=identities(f[13]);endplans=plans(f[14])
  assert actualbefore==before and actualactions==actions
  assert beforebits==[x[2] for x in before] and beforeset==sorted(x[0] for x in before)
  assert len(set(x[0] for x in before))==len(before) and len(set(x[0] for x in actions))==len(actions)
  assert not any(opposite(provider,a[0],b[0]) for a in actions for b in actions)
  expectedplans=[independent_plan(provider,before,a) for a in actions]
  assert initialplans==expectedplans
  assert gate==any(p[0]!='N' for p in expectedplans)
  assert newcount==sum(p[0]=='A' for p in expectedplans) and removal==any(p[0]=='M' for p in expectedplans)
  for kind,_ in expectedplans:branches[kind]+=1
  expected=before
  for action in actions:expected=independent_step(provider,expected,action)
  consistent=(actualbits==[x[2] for x in actual] and len(actualbits)==len(actual) and actualset==sorted(set(x[0] for x in actual)) and len(actualset)==len(actual))
  correct=bool(completed) and actual==expected and consistent and endplans==([] if gate else initialplans)
  if not completed:panics+=1
  if not correct:failures.append({'name':name,'completed':bool(completed),'expected':expected,'actual':actual,'bits':actualbits,'ids':actualset,'representation':consistent})
 if variant in ('candidate','original'):assert not failures,(variant,failures)
 else:assert failures,(variant,'no semantic witness')
 return {'rows':len(lines),'branches':branches,'panics':panics,'failures':failures}
