#!/usr/bin/env python3
from pathlib import Path
import argparse,hashlib,json,shutil,subprocess,sys
R=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--output',required=True,type=Path);args=p.parse_args()
out=args.output.resolve();assert not out.exists();out.mkdir(parents=True)
hashfile=lambda q:hashlib.sha256(q.read_bytes()).hexdigest()
freeze=json.loads((R/'FREEZE.json').read_text());assert hashfile(R/'MANIFEST.json')==freeze['manifest_sha256']
manifest=json.loads((R/'MANIFEST.json').read_text())
for name,pin in manifest.items():assert hashfile(R/name)==pin,name

def copy(target):
 target.mkdir()
 for name in list(manifest)+['MANIFEST.json','FREEZE.json']:
  dst=target/name;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(R/name,dst)

relocated=out/'relocated';copy(relocated)
cmd=[sys.executable,str(relocated/'check.py'),'--run','--output',str(out/'replay')]
r=subprocess.run(cmd,cwd=out,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
(out/'relocation.log').write_text(r.stdout);assert r.returncode==0,r.stdout
results=[]
for label,path in [('model','lean/CommentExecution.lean'),('source','source/third_party/rust/cssparser/src/tokenizer.rs'),('fixture','observer-witness.rs'),('manifest','MANIFEST.json')]:
 target=out/('tampered-'+label);copy(target);q=target/path;q.write_bytes(q.read_bytes()+b'\n')
 generated=out/('must-not-exist-'+label)
 command=[sys.executable,str(target/'check.py'),'--run','--output',str(generated)]
 r=subprocess.run(command,cwd=out,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
 (out/('tamper-'+label+'.log')).write_text(r.stdout)
 assert r.returncode!=0 and 'authentication' in r.stdout and not generated.exists(),(label,r.stdout)
 results.append(dict(label=label,path=path,exit=r.returncode,rejected_before_output=True))
(out/'GATES.json').write_text(json.dumps(dict(status='PASS',original_manifest_sha256=hashfile(R/'MANIFEST.json'),original_freeze_sha256=hashfile(R/'FREEZE.json'),relocation_command=cmd,relocation_exit=0,source_only=True,tamper=results),indent=2)+'\n')
print('PASS source-only relocation and four authentication-before-execution tamper gates')
