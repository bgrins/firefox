import sys
assert sys.flags.isolated and sys.flags.no_site
import argparse,json,os,shutil,subprocess
from pathlib import Path
R=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args()
out=a.output.resolve();assert not out.is_relative_to(R);out.mkdir(parents=True,exist_ok=False)
records=[]
for name in ['native_change','provider_change','shadow_module','extra_empty_directory','fifo','symlink','duplicate_json_key','duplicate_path','escape_path']:
 capsule=out/name;shutil.copytree(R,capsule)
 if name=='native_change':
  q=capsule/'native/facade.rs';q.write_text(q.read_text()+'\n')
 elif name=='provider_change':
  q=capsule/'evidence/provider/data.py';q.write_text(q.read_text()+'\n')
 elif name=='shadow_module':(capsule/'json.py').write_text('raise RuntimeError("shadow module executed")\n')
 elif name=='extra_empty_directory':(capsule/'unexpected').mkdir()
 elif name=='fifo':os.mkfifo(capsule/'unexpected-fifo')
 elif name=='symlink':(capsule/'unexpected-link').symlink_to('README.md')
 else:
  q=capsule/'MANIFEST.json';data=json.loads(q.read_text())
  if name=='duplicate_json_key':q.write_text(q.read_text().replace('"path":','"path": "duplicate", "path":',1))
  elif name=='duplicate_path':q.write_text(json.dumps(data+[data[0]]))
  else:data[0]['path']='../outside';q.write_text(json.dumps(data))
 result=subprocess.run([sys.executable,'-I','-S',str(capsule/'check.py')],capture_output=True,text=True)
 assert result.returncode!=0 and 'AssertionError' in result.stderr and 'shadow module executed' not in result.stderr,(name,result)
 records.append({'name':name,'rejected':True})
 # Keep diagnostics but not duplicate capsules or special filesystem objects.
 (out/f'{name}.stderr').write_text(result.stderr)
 shutil.rmtree(capsule)
(out/'RESULT.json').write_text(json.dumps(records,indent=2)+'\n')
print(json.dumps(records))
