import json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'development-build/full'
records=[]
def run(name,args):
 result=subprocess.run(list(map(str,args)),capture_output=True,text=True,timeout=120)
 (OUT/(name+'.log')).write_text(result.stdout+result.stderr)
 records.append({'name':name,'args':list(map(str,args)),'exit':result.returncode});(OUT/'context-build-commands.json').write_text(json.dumps(records,indent=2)+'\n')
 print(name,result.returncode,flush=True)
 if result.returncode:raise SystemExit(result.returncode)
run('extract-context',[sys.executable,ROOT/'native/extract-context.py'])
commands=json.loads((OUT/'commands.json').read_text())
for flavor in ['original','candidate','standalone']:
 args=next(r['args']for r in commands if r['name']=='range-'+flavor)
 args=[a.replace('/range-'+flavor,'/context-'+flavor)for a in args]
 run('compile-context-'+flavor,args)
