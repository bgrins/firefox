#!/usr/bin/env python3
import hashlib,json,pathlib,shutil,subprocess,tempfile
R=pathlib.Path(__file__).resolve().parent
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
f=json.loads((R/'FREEZE.json').read_text())
assert H(R/'INPUTS.json')==f['inputs_sha256']
for p,h in json.loads((R/'INPUTS.json').read_text()).items():
 assert H(R/p)==h,p
worker='layout/style/FontFaceSetWorkerImpl.cpp'
with tempfile.TemporaryDirectory(prefix='fontface-prerequisite-') as d:
 d=pathlib.Path(d)
 shutil.copytree(R/'original',d,dirs_exist_ok=True)
 shutil.copyfile(R/'evidence/worker-removal/original-FontFaceSetWorkerImpl.cpp',d/worker)
 for reverse in [False,True]:
  args=['patch','--batch','--fuzz=0','-p1','-d',str(d),'-i',str(R/'standalone-native-with-rebuild.patch')]
  if reverse:args.append('-R')
  result=subprocess.run(args,capture_output=True,text=True)
  assert result.returncode==0,result.stdout+result.stderr
  assert 'fuzz' not in result.stdout.lower()
  tree=R/('original' if reverse else 'candidate')
  for p in tree.rglob('*'):
   if p.is_file():assert (d/p.relative_to(tree)).read_bytes()==p.read_bytes(),str(p)
  w='original' if reverse else 'candidate'
  assert (d/worker).read_bytes()==(R/f'evidence/worker-removal/{w}-FontFaceSetWorkerImpl.cpp').read_bytes()
subprocess.run(['node','--check',str(R/'fontface-loaded-descriptor-retirement.any.js')],check=True)
print(json.dumps({'status':'PASS','files_authenticated':len(json.loads((R/'INPUTS.json').read_text())), 'exact_native_files':17,'apply_reverse':True,'browser_probe':'UNEXECUTED','whole_upstream_tree':'NOT_VERIFIED'}))
