def validate(payload):
 assert payload['compatMode']=='CSS1Compat'
 expected=[(a,b,e) for a in ('x','y') for b in (16,8388600) for e in (0,9)]
 rows=payload['rows']; assert len(rows)==8
 result=[]
 for row,(axis,base,extra) in zip(rows,expected):
  assert (row['axis'],row['base'],row['extra'])==(axis,base,extra)
  assert row['first']==row['repeat']==row['restored']
  matches={}
  for phase in ('first','repeat','recovery','restored'):
   v=row[phase]; padding=0 if phase=='recovery' else extra; size=base+padding
   assert v['parentMatches'] is True and v['content']==base and v['padding']==padding
   assert v['position']=='absolute' and v['boxSizing']=='content-box' and v['transform']=='none' and v['zoom']=='1'
   assert type(v['boxes']) is int and v['boxes']==1
   assert v['hostRect']==[0,0,100,100]
   assert v['rect']==([0,0,size,4] if axis=='x' else [0,0,4,size])
   assert type(v['offset']) is int
   matches[phase]=v['offset']==size
  result.append({'axis':axis,'base':base,'extra':extra,'matched':matches,'observed':row['first']['offset'],'expected':base+extra})
 return {'calibrated':8,'stable':8,'rows':result,'matching':{p:sum(r['matched'][p] for r in result) for p in ('first','repeat','recovery','restored')}}
