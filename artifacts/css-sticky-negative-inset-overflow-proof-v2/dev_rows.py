import sys
sys.dont_write_bytecode=True
import importlib.util,json,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;cap=r/'capsule';out=r/sys.argv[1];out.mkdir()
spec=importlib.util.spec_from_file_location('core',cap/'core.py');c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)
t=json.loads((cap/'TOOLCHAIN.json').read_text());rows=c.cases()
for v in ['combined-after','standalone-after']:
 p=out/(v+'.lean');p.write_text(c.lean_source(rows,v));z=subprocess.run([t['lean'],'--run',str(p)],env={'PATH':'/usr/bin:/bin','LEAN_PATH':str(r/'development-lean-v13')},capture_output=True,text=True);(out/(v+'.stdout')).write_text(z.stdout);(out/(v+'.stderr')).write_text(z.stderr);print(v,z.returncode,flush=True)
 if z.returncode:continue
 got=[json.loads(x) for x in z.stdout.splitlines()];fail=[]
 for row,result in zip(rows,got):
  exp=c.expected(row,v)
  for key in result:
   if key in exp and result[key]!=exp[key]:fail.append([row['id'],key,result[key],exp[key]])
 (out/(v+'-compare.json')).write_text(json.dumps({'rows':len(got),'fail':fail,'safe':sum(x['safe'] for x in got),'debug':sum(x['debug'] for x in got),'old_safe':sum(x['old_safe'] for x in got)},indent=2))
