import hashlib,re
from collections import Counter

def rows(s):
 pat=r'Row \{ key: (\d+), value: (\d+), important: (true|false) \}'
 found=[(int(a),int(b),c=='true') for a,b,c in re.findall(pat,s)]
 canonical='['+', '.join('Row { key: %d, value: %d, important: %s }'%(a,b,str(c).lower()) for a,b,c in found)+']'
 assert s==canonical,('row syntax',s)
 return found

def bit(s):
 assert s in ('0','1'),('binary field',s)
 return s=='1'

def bits(s):
 assert re.fullmatch(r'\[(?:(?:true|false)(?:, (?:true|false))*)?\]',s),('bits syntax',s)
 return [] if s=='[]' else [x=='true' for x in s[1:-1].split(', ')]

def ids(s,kind,limit):
 if kind=='longhand':
  pat=r'\{(?:LonghandId\(\d+\)(?:, LonghandId\(\d+\))*)?\}'
  values=list(map(int,re.findall(r'LonghandId\((\d+)\)',s)))
  canonical='{'+', '.join('LonghandId(%d)'%x for x in values)+'}'
 else:
  pat=r'\{(?:\d+(?:, \d+)*)?\}'
  values=[] if s=='{}' else list(map(int,re.findall(r'\d+',s)))
  canonical='{'+', '.join(map(str,values))+'}'
 assert re.fullmatch(pat,s) and s==canonical,('set syntax',s)
 assert values==sorted(set(values)) and all(0<=x<limit for x in values),('set domain',s)
 return set(values)

def longhand_list(s):
 values=list(map(int,re.findall(r'LonghandId\((\d+)\)',s)))
 assert s=='['+', '.join('LonghandId(%d)'%x for x in values)+']'
 return values

def roster(providers):
 meta=providers['longhands'];byname={x['name']:x['id'] for x in meta};n=len(meta)
 a,b,c,d,u=[byname[x] for x in ['padding-top','padding-block-start','color','direction','unicode-bidi']];x=n+7
 def seed(es):return [(k,2000+v,i) for k,v,i in es]
 def all_actions(profile,v,imp):
  return [(k,v if v<6 else 1017,imp) for k in providers['all'] if meta[k]['content'] and (not meta[k]['pref'] or profile==0 or profile==2 and k%2==0)]
 out=[]
 for profile in range(3):
  for v in range(7):
   for imp in [False,True]:
    for order in range(4):
     es=[[],[(a,1,not imp),(b,2,not imp)],[(b,1,not imp),(a,2,not imp)],[(a,1,not imp),(x,3,True),(c,2,False),(b,2,imp),(d,4,True),(u,5,False)]][order]
     suffix=f'{profile}-{v}-{str(imp).lower()}-{order}';actions=all_actions(profile,v,imp)
     out.append(('ROW','all-'+suffix,seed(es),actions))
     out.append(('ROW','all-repeat-'+suffix,None,actions))
 for pair in [[a,b],[b,a]]:
  for oldimp in [False,True]:
   for newimp in [False,True]:
    for value in [1,2]:
     name=f'single-{pair}-{str(oldimp).lower()}-{str(newimp).lower()}-{value}'
     out.append(('ROW',name,seed([(pair[0],1,oldimp),(x,8,True),(pair[1],1,oldimp)]),[(a,2000+value,newimp)]))
 max_size=max(len(v) for k,v in providers['shorthands'].items() if k!='all')
 for idx,(name,sub) in enumerate(providers['shorthands'].items()):
  if len(sub)>max_size:continue
  out.append(('ROW',f'ordinary-shorthand-{idx}',seed([(a,1,True),(b,2,False),(c,3,True),(x,4,False)]),[(k,2009,False) for k in sub]))
  out.append(('REMOVE',str(idx),None,sub))
 for imp in [False,True]:out.append(('EXTEND',str(imp).lower(),seed([(a,1,True),(b,2,False),(x,3,True)]),all_actions(0,0,imp)))
 state=0x91745
 def rand():
  nonlocal state
  state=(state*6364136223846793005+1)&((1<<64)-1)
  return state>>32
 for case in range(500):
  pool=[a,b,c,x,d,u,byname['margin-left'],byname['margin-inline-end'],byname['padding-right'],byname['padding-inline-start']]
  for i in range(len(pool)-1,0,-1):
   j=rand()%(i+1);pool[i],pool[j]=pool[j],pool[i]
  count=rand()%(len(pool)+1)
  es=[(k,rand()%3,rand()%2==0) for k in pool[:count]]
  for step in range(5):
   k=pool[rand()%len(pool)];v=rand()%3;imp=rand()%2==0
   out.append(('ROW',f'sequence-{case}-{step}',seed(es) if step==0 else None,[(k,2000+v,imp)]))
 assert len(out)==3042
 return out

def verify(text,providers,variant,execution_exit):
 meta=providers['longhands'];expected_roster=roster(providers)
 def opposite(a,b):
  if a>=len(meta) or b>=len(meta):return False
  x,y=meta[a],meta[b]
  return x['group'] is not None and x['group']==y['group'] and x['logical']!=y['logical']
 def setter(state,new):
  old=next((i for i,x in enumerate(state) if x[0]==new[0]),None)
  if old is None:return state+[new]
  if any(opposite(new[0],x[0]) for x in state[old+1:]):return state[:old]+state[old+1:]+[new]
  return state[:old]+[new]+state[old+1:]
 assert text.endswith('\n')
 lines=text.splitlines();assert 0<len(lines)<=len(expected_roster)
 summaries=[];previous=None
 for index,line in enumerate(lines):
  f=line.split('\t');kind,name=f[:2]
  wanted_kind,wanted_name,initial,wanted_actions=expected_roster[index]
  assert (kind,name)==(wanted_kind,wanted_name),('roster',index,kind,name,wanted_name)
  assert len(f)==(12 if kind=='ROW' else 6),('field count',index,len(f))
  claimed=bit(f[2])
  if kind=='ROW':
   native_gate=bit(f[3]);reported_changed=bit(f[4])
   before,actual,retained_expected,actions=map(rows,f[5:9])
   assert actions==wanted_actions,('actions',name)
   expected=before;changed=False
   for action in actions:
    new=setter(expected,action);changed|=new!=expected;expected=new
   assert expected==retained_expected and changed==reported_changed
   raw_bits=bits(f[9]);membership=ids(f[10],'longhand',len(meta))
   membership|={len(meta)+k for k in ids(f[11],'custom',65536)}
   consistent=(raw_bits==[x[2] for x in actual] and membership=={x[0] for x in actual} and len(actual)==len(membership))
   good=actual==expected and native_gate==changed and consistent
   differences={'state':actual!=expected,'gate':native_gate!=changed,'representation':not consistent}
  elif kind=='REMOVE':
   before,actual=map(rows,f[3:5]);removed=longhand_list(f[5]);assert removed==wanted_actions
   expected=[x for x in before if x[0] not in set(removed)];good=actual==expected;differences={'state':not good}
  elif kind=='EXTEND':
   before,actual,actions=map(rows,f[3:6]);assert actions==wanted_actions
   expected=before
   for new in actions:
    if any(x[0]==new[0] and x[2] and not new[2] for x in expected):continue
    expected=[x for x in expected if x[0]!=new[0]]+[new]
   good=actual==expected;differences={'state':not good}
  else:raise AssertionError(kind)
  assert before==(previous if initial is None else initial),('initial/carry state',name)
  assert claimed==good,(kind,name,claimed,good)
  previous=actual
  summaries.append({'kind':kind,'name':name,'pass':good,'differences':differences,'raw_sha256':hashlib.sha256(line.encode()).hexdigest()})
 if execution_exit==42:
  assert variant in ['mutant_move_bits','mutant_membership']
  assert len(lines)<len(expected_roster) and summaries[-1]['differences'].get('representation')
  assert all(not r['differences'].get('representation') for r in summaries[:-1])
 else:assert execution_exit==0 and len(lines)==len(expected_roster)
 return {'rows':len(summaries),'counts':dict(Counter(f"{r['kind']}:{'pass' if r['pass'] else 'fail'}" for r in summaries)),'failures':[r for r in summaries if not r['pass']]}
