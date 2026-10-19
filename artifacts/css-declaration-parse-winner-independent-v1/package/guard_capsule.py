import sys
assert sys.flags.isolated and sys.flags.no_site
import argparse,json,os,shutil,subprocess,hashlib
from pathlib import Path
R=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args()
out=a.output.resolve();assert not out.is_relative_to(R);out.mkdir(parents=True,exist_ok=False)
results=[]
for case in ['module_shadow','package_shadow','modified_executor','empty_directory','fifo','symlink','duplicate_key','path_escape','output_inside']:
 d=out/case;shutil.copytree(R,d)
 if case=='module_shadow':(d/'json.py').write_text('raise SystemExit(88)\n')
 elif case=='package_shadow':(d/'json').mkdir();(d/'json/__init__.py').write_text('raise SystemExit(88)\n')
 elif case=='modified_executor':(d/'replay.py').write_text('raise SystemExit(88)\n')
 elif case=='empty_directory':(d/'extra').mkdir()
 elif case=='fifo':os.mkfifo(d/'fifo')
 elif case=='symlink':(d/'check-link.py').symlink_to(d/'check.py')
 elif case=='duplicate_key':
  m=(d/'MANIFEST.json').read_text();key=next(iter(json.loads(m)));(d/'MANIFEST.json').write_text('{'+json.dumps(key)+':"duplicate",'+m[1:])
 elif case=='path_escape':
  m=json.loads((d/'MANIFEST.json').read_text());m['../outside.py']='0'*64;(d/'MANIFEST.json').write_text(json.dumps(m))
 command=[sys.executable,'-I','-S',str(d/'check.py')]
 if case=='output_inside':command+=['--output',str(d/'untrusted-output')]
 run=subprocess.run(command,capture_output=True,text=True)
 assert run.returncode not in (0,88),(case,run.returncode)
 assert 'AssertionError' in run.stderr,(case,run.stderr)
 results.append({'case':case,'rejected_before_local_execution':True,'exit':run.returncode})
 shutil.rmtree(d)
(out/'RESULT.json').write_text(json.dumps(results,indent=2)+'\n')
print(json.dumps({'tamper_controls':len(results)}))
