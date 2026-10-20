import sys
if not(sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize):raise RuntimeError('use -I -S')
from pathlib import Path
import json,shutil,subprocess,os
r=Path(__file__).resolve().parent;s=r/'relocated-source';root=r/'guard-work';root.mkdir();rows=[]
def run(label,path,flags,expect=1):
 out=root/(label+'-output');cmd=[sys.executable,*flags,str(path),'--output',str(out),'--help'];p=subprocess.run(cmd,capture_output=True,text=True);row={'case':label,'command':cmd,'exit':p.returncode,'stdout':p.stdout,'stderr':p.stderr,'output_absent':not out.exists()};rows.append(row)
 if (p.returncode==0)!=(expect==0) or out.exists() or 'NESTED_SHADOW_BEFORE_GUARD' in p.stdout+p.stderr:raise RuntimeError(row)
 return row
for entry in ['check.py','compile.py','native/build.py']:
 d=root/entry.replace('/','-');d.mkdir();p=d/'entry.py';shutil.copyfile(s/entry,p)
 for label,flags in [('optimized',['-I','-S','-O']),('double-optimized',['-I','-S','-OO']),('not-isolated',['-S']),('site-enabled',['-I'])]:
  row=run(entry.replace('/','-')+'-'+label,p,flags)
  if 'Require python3 -I -S' not in row['stderr'] and 'use -I -S' not in row['stderr']:raise RuntimeError(row)
 (d/'json.py').write_text('raise RuntimeError("NESTED_SHADOW_BEFORE_GUARD")\n');run(entry.replace('/','-')+'-shadow',p,['-S']);shutil.rmtree(d)
c=root/'capsule';shutil.copytree(s,c)
run('intact-help',c/'check.py',['-I','-S'],0)
for case in ['nested-seal','fifo','empty-directory','directory-symlink','changed-source']:
 p=c/'native/FILES.json' if case=='nested-seal' else c/('pipe' if case=='fifo' else 'extra')
 if case=='nested-seal':p.write_text('unlisted')
 elif case=='fifo':os.mkfifo(p)
 elif case=='empty-directory':p.mkdir()
 elif case=='directory-symlink':p.symlink_to(root,target_is_directory=True)
 else:p=c/'lean/RawRecovery.lean';old=p.read_bytes();p.write_bytes(old+b'\n')
 run(case,c/'check.py',['-I','-S'])
 if case=='changed-source':p.write_bytes(old)
 elif p.is_dir() and not p.is_symlink():p.rmdir()
 else:p.unlink()
shutil.rmtree(c);root.rmdir()
(r/'GUARDS.json').write_text(json.dumps(rows,indent=2)+'\n');print('PASS',len(rows),'independent guard controls')
