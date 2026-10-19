import sys
assert sys.flags.isolated and sys.flags.no_site
import argparse,json,shutil,subprocess
from pathlib import Path
R=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args()
out=a.output.resolve();assert not out.exists() and not out.is_relative_to(R);out.mkdir(parents=True)
results=[]
for case in ['changed_model','shadow_module']:
    source=out/case;shutil.copytree(R,source)
    if case=='changed_model':
        f=source/'lean/NativeRemoval.lean';f.write_text(f.read_text()+'\n-- altered input\n')
    else:(source/'json.py').write_text('raise SystemExit(88)\n')
    dest=out/(case+'-output')
    p=subprocess.run([sys.executable,'-I','-S',str(source/'check.py'),'--output',str(dest)],capture_output=True,text=True)
    assert p.returncode not in (0,88) and 'AssertionError' in p.stderr and not dest.exists()
    results.append({'case':case,'rejected_before_output':True,'exit':p.returncode})
    shutil.rmtree(source)
(out/'RESULT.json').write_text(json.dumps(results,indent=2)+'\n')
print(json.dumps(results))
