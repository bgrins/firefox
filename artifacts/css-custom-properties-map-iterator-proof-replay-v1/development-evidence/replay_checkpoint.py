import hashlib,json,os,subprocess,sys
from pathlib import Path
assert sys.flags.isolated and sys.flags.no_site
r=Path(__file__).resolve().parent.parent/'css-custom-properties-map-iterator-proof-v1'
d=Path(__file__).resolve().parent
t=json.loads((r/'TOOLCHAIN.json').read_text()); assert hashlib.sha256(Path(t['lean']).read_bytes()).hexdigest()==t['lean_sha256']
env={k:v for k,v in os.environ.items() if not k.startswith(('LEAN_','PYTHON'))};env['LEAN_PATH']=str(d)
for m in ['Iterator','Contracts']:
 p=subprocess.run([t['lean'],'-o',str(d/(m+'.olean')),str(r/'lean'/(m+'.lean'))],env=env,text=True,capture_output=True)
 (d/(m+'-checkpoint.log')).write_text(p.stdout+p.stderr)
 print(m,p.returncode)
 assert p.returncode==0,p.stdout+p.stderr
