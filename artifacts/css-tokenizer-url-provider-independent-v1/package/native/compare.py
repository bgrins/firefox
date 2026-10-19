from pathlib import Path
import argparse,json,runpy
tokens=runpy.run_path(str(Path(__file__).with_name("reference.py")))["tokens"]
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--native',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
cases=json.loads((ROOT/'CASES.json').read_text());rows={i:[]for i in range(len(cases))}
for line in (a.native/'raw.txt').read_text().splitlines():
 row,index,kind,value,pos,ln,col,pending,seen,url,source_map=line.split('|');rows[int(row)].append({'kind':kind,'value':bytes.fromhex(value).decode(),'position':int(pos),'line':int(ln),'column':int(col),'pending':pending=='true','seen':seen=='true','url':url,'source_map':source_map})
checks=[];differences=[];intentional=[]
for index,case in enumerate(cases):
 expected=tokens(case['input']);actual=rows[index]
 if len(expected)!=len(actual):differences.append({'index':index,'reason':'token count','native':actual,'reference':expected});continue
 for n,(got,want)in enumerate(zip(actual,expected)):
  fields=['kind','position','line','column','pending','seen']
  if want['value']is not None:fields.append('value')
  # Only the independently derived quoted-url rollback endpoint is admitted.
  locations=['position','line','column']
  if any(got[f]!=want[f] for f in locations):
   delegation=want.get('quoted_url_delegation')
   admitted=(got['kind']==want['kind']=='function' and delegation is not None
             and all(got[f]==delegation[f] for f in locations))
   if admitted:
    intentional.append({'index':index,'token':n,'native':got,'reference':want,'classification':'exact quoted-url rollback endpoint before subsequent whitespace/string'})
    fields=[f for f in fields if f not in locations]
  changed=[f for f in fields if got[f]!=want[f]]
  if got['url']!='none' or got['source_map']!='none':changed.append('comment observer unexpectedly changed')
  if changed:differences.append({'index':index,'token':n,'fields':changed,'native':got,'reference':want})
 checks.append({'index':index,'tokens':len(actual)})
a.output.mkdir(parents=True,exist_ok=False);(a.output/'COMPARISON.json').write_text(json.dumps({'cases':len(cases),'tokens':sum(len(r)for r in rows.values()),'intentional_intermediate_cursor_differences':intentional,'unexpected_differences':differences,'checks':checks},indent=2,ensure_ascii=False)+'\n');print('cases',len(cases),'intentional cursor differences',len(intentional),'unexpected',len(differences));assert not differences
