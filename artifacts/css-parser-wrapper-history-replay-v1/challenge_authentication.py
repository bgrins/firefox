from pathlib import Path
import argparse,hashlib,json,os,shutil,subprocess,sys
assert sys.flags.isolated and sys.flags.no_site
p=argparse.ArgumentParser();p.add_argument('--capsule',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();r=a.capsule.resolve();out=a.output.resolve();out.mkdir(parents=True,exist_ok=False)
assert hashlib.sha256((r/'MANIFEST.json').read_bytes()).hexdigest()=='5f00da8cda2a48e4e9e0e34cfaa68f75ca97f9bc64890465283cd7ba6d253e20'
assert hashlib.sha256((r/'check.py').read_bytes()).hexdigest()=='8958afc0475c9ee10c0758ed587946ebea053e288dca0883a2c032920a59e5c2'
m=json.loads((r/'MANIFEST.json').read_text());assert all(hashlib.sha256((r/f).read_bytes()).hexdigest()==h for f,h in m.items())
rows=[]
for case in ['alter-helper','extra-file','extra-directory','symlink','duplicate-seal-key','shadow-json','not-isolated']:
 d=out/case;d.mkdir();src=d/'capsule';shutil.copytree(r,src)
 if case=='alter-helper':
  q=src/'native/check.py';q.write_text(q.read_text()+'\nraise RuntimeError("must not execute")\n')
 elif case=='extra-file':(src/'unexpected').write_text('unlisted')
 elif case=='extra-directory':(src/'unexpected-directory').mkdir()
 elif case=='symlink':(src/'unexpected-link').symlink_to(src/'REPORT.md')
 elif case=='duplicate-seal-key':
  q=src/'FREEZE.json';s=q.read_text();q.write_text(s.replace('{','{"inputs":0,',1))
 elif case=='shadow-json':(src/'json.py').write_text('raise RuntimeError("SHADOW_EXECUTED")\n')
 target=d/'should-not-exist';cmd=[sys.executable,*([] if case=='not-isolated' else ['-I','-S']),str(src/'check.py'),'--run','--output',str(target)]
 env={k:v for k,v in os.environ.items() if not k.startswith(('PYTHON','LEAN_'))};v=subprocess.run(cmd,capture_output=True,text=True,env=env);log=v.stdout+v.stderr;(d/'result.log').write_text(log)
 assert v.returncode!=0 and not target.exists(),case
 assert 'SHADOW_EXECUTED' not in log,case
 rows.append({'case':case,'command':cmd,'exit':v.returncode,'output_created':False,'log_sha256':hashlib.sha256(log.encode()).hexdigest()})
(out/'CHECK.json').write_text(json.dumps({'status':'PASS','rejections':rows},indent=2)+'\n');print('PASS',len(rows),'pre-execution authentication challenges')
