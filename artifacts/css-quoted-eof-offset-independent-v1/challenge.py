import json, subprocess, sys
from pathlib import Path
root=Path(__file__).resolve().parent
native=Path(sys.argv[1])
out=Path(sys.argv[2]);out.mkdir(exist_ok=False)
cases=[]
for quote in ['"', "'"]:
 for kind,name in [('var','--absent'),('env','absent'),('attr','absent')]:
  for depth in [1,2,3,8,32]:
   for prefix in ['', '  \t', 'var(--first, known), ']:
    for slashes in [0,1,3,5]:
     body='é𐀀 example'
     raw=prefix+'var(--outer, '*(depth-1)+kind+'('+name+', '+quote+body+'\\'*slashes
     suffix=quote+')'*depth
     stored=raw.lstrip()+suffix if not slashes else raw.lstrip()[:-1]+suffix
     expected=('known, ' if prefix.startswith('var') else '')+quote+body+'\\'*max(slashes-1,0)+quote
     cases.append({'css':raw,'stored':stored,'output':expected,'depth':depth})
feed=''.join(c['css'].encode().hex()+'\n' for c in cases)
rows={}
for variant in ['original','candidate','missing-correction-mutant']:
 p=subprocess.run([str(native/variant)],input=feed,text=True,capture_output=True)
 assert p.returncode==0,p.stderr
 rows[variant]=[json.loads(x) for x in p.stdout.splitlines()]
 (out/(variant+'.jsonl')).write_text(p.stdout)
for c,old,new,mut in zip(cases,rows['original'],rows['candidate'],rows['missing-correction-mutant']):
 assert old==mut
 assert new['status']=='OK'
 assert bytes.fromhex(new['css_hex']).decode()==c['stored']
 assert old['css_hex']==new['css_hex']
 assert bytes.fromhex(new['output_hex']).decode()==c['output']
 data=c['stored'].encode()
 for start,end,fb in new['refs']:
  assert 0<=start<=end<=len(data)
  data[:start].decode();data[:end].decode()
  if fb:
   assert start<fb<=end-1
   data[fb:end-1].decode()
 if old['status']=='OK':assert old==new
(out/'CASES.json').write_text(json.dumps(cases,indent=2)+'\n')
result={'cases':len(cases),'candidate_ok':len(rows['candidate']),'original_panics':sum(r['status']=='PANIC' for r in rows['original']),'mutant_matches_original':True,'independent_expectations':'constructed serialized bytes and substitution output; UTF-8 slice boundaries'}
(out/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(result)
