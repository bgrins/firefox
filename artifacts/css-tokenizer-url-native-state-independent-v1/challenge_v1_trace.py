from pathlib import Path
import argparse,json,subprocess,sys,hashlib
p=argparse.ArgumentParser();p.add_argument('--package',type=Path,required=True);p.add_argument('--raw',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
a.output.mkdir(parents=True,exist_ok=False)
raw=a.raw.read_text();lines=raw.splitlines();step=next(i for i,s in enumerate(lines) if s.split('|')[1]=='step')
mutations={'missing-helper':lines[:step]+lines[step+1:], 'unknown-event':lines+['0|unrecognized|ignored'], 'duplicate-helper':lines[:step]+[lines[step]]+lines[step:], 'extra-helper-field':lines[:step]+[lines[step]+'|ignored']+lines[step+1:]}
steps=[i for i,s in enumerate(lines) if s.split('|')[1]=='step']
pair=next((a,b)for a,b in zip(steps,steps[1:])if lines[a].split('|')[0]==lines[b].split('|')[0]);reordered=lines.copy();reordered[pair[0]],reordered[pair[1]]=reordered[pair[1]],reordered[pair[0]];mutations['reordered-helpers']=reordered
records=[]
for name,changed in mutations.items():
 path=a.output/(name+'.txt');path.write_text('\n'.join(changed)+'\n');receipt=a.output/(name+'.json')
 cmd=[sys.executable,'-I','-S','-B',str(a.package/'native/check_states.py'),'--cases',str(a.package/'CASES.json'),'--raw',str(path),'--output',str(receipt)]
 r=subprocess.run(cmd,capture_output=True,text=True)
 records.append({'name':name,'command':cmd,'exit':r.returncode,'stdout':r.stdout,'stderr':r.stderr,'raw_sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
 assert r.returncode==0,(name,r.stderr)
(a.output/'FINDINGS.json').write_text(json.dumps({'verdict':'BLOCKER','reason':'All five invalid traces accepted by sealed v1 comparator','records':records},indent=2)+'\n')
