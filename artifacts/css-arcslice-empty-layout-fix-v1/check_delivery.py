from pathlib import Path
import json,subprocess,tempfile
P=Path(__file__).resolve().parent;ROOT=P.parents[1];roles=json.loads((P/'DELIVERY-ROLES.json').read_text());records=[]
for variant,rows in roles.items():
 with tempfile.TemporaryDirectory(prefix='arcslice-empty-delivery-',dir='/private/tmp') as temp:
  tree=Path(temp)
  for path,row in rows.items():
   f=tree/path;f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes((ROOT/row['base_capture']).read_bytes())
  for reverse in [False,True]:
   cmd=['patch','--batch','--fuzz=0','-p1','-i',str(P/variant/'delivery.patch')]+(['-R'] if reverse else [])
   r=subprocess.run(cmd,cwd=tree,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT);assert r.returncode==0 and 'fuzz' not in r.stdout.lower() and 'offset' not in r.stdout.lower()
   for path,row in rows.items():assert (tree/path).read_bytes()==(ROOT/row[('base' if reverse else 'candidate')+'_capture']).read_bytes()
   records.append({'variant':variant,'reverse':reverse,'exit':r.returncode,'output':r.stdout})
 assert not tree.exists()
result={'success':True,'records':records,'scratch_removed':True};(P/'DELIVERY.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
