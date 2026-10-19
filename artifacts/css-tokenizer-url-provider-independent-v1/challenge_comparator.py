import argparse,json,pathlib,subprocess
p=argparse.ArgumentParser();p.add_argument('--package',type=pathlib.Path,required=True);p.add_argument('--native',type=pathlib.Path,required=True);p.add_argument('--output',type=pathlib.Path,required=True);a=p.parse_args()
a.output.mkdir(parents=True,exist_ok=False)
lines=(a.native/'raw.txt').read_text().splitlines();cases=json.loads((a.package/'CASES.json').read_text());records=[]
choices=[]
for label,predicate,column in [
 ('non-url-function-cursor',lambda raw:raw.startswith('urlx('),4),
 ('quoted-url-wrong-cursor',lambda raw:raw.startswith('url(  '),4),
 ('quoted-url-wrong-line',lambda raw:raw.startswith('url(  '),5),
 ('quoted-url-wrong-column',lambda raw:raw.startswith('url(  '),6),
]:
 row=next(i for i,c in enumerate(cases) if predicate(c['input']))
 line=next(i for i,s in enumerate(lines) if s.split('|')[:2]==[str(row),'0'])
 fields=lines[line].split('|');assert fields[2]=='function';fields[column]=str(int(fields[column])+997)
 changed=lines[:];changed[line]='|'.join(fields)
 root=a.output/label;root.mkdir();(root/'raw.txt').write_text('\n'.join(changed)+'\n')
 cmd=['python3','-I','-S','-B',str(a.package/'native/compare.py'),'--native',str(root),'--output',str(root/'comparison')]
 r=subprocess.run(cmd,capture_output=True,text=True)
 records.append({'label':label,'command':cmd,'exit':r.returncode,'stdout':r.stdout,'stderr':r.stderr})
 assert r.returncode!=0,label
 receipt=json.loads((root/'comparison/COMPARISON.json').read_text())
 assert receipt['unexpected_differences'],label
(a.output/'CHECK.json').write_text(json.dumps({'result':'PASS','rejected':len(records),'records':records},indent=2)+'\n')
