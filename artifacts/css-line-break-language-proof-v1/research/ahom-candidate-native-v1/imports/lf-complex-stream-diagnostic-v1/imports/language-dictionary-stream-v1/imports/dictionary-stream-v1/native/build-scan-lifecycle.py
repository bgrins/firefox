import json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'development-build/full';records=[]
def run(name,args):
 r=subprocess.run(list(map(str,args)),capture_output=True,text=True,timeout=180);(OUT/(name+'.log')).write_text(r.stdout+r.stderr);records.append({'name':name,'args':list(map(str,args)),'exit':r.returncode});(OUT/'scan-lifecycle-build-commands.json').write_text(json.dumps(records,indent=2)+'\n');print(name,r.returncode,flush=True)
 if r.returncode:raise SystemExit(r.returncode)
run('extract-scan-lifecycle',[sys.executable,ROOT/'native/extract-scan-lifecycle.py'])
commands=json.loads((OUT/'commands.json').read_text())
for flavor in ['original','candidate','standalone']:
 args=next(r['args']for r in commands if r['name']=='range-'+flavor);args=[a.replace('/range-'+flavor,'/scan-lifecycle-'+flavor)for a in args];run('compile-scan-lifecycle-'+flavor,args)
