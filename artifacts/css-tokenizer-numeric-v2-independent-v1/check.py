import argparse
import hashlib
import json
from pathlib import Path
import subprocess
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--benchmark',action='store_true');a=p.parse_args()
R=Path(__file__).resolve().parent;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
f=json.loads((R/'FREEZE.json').read_text());assert sha(R/'MANIFEST.json')==f['manifest_sha256']
m=json.loads((R/'MANIFEST.json').read_text())
for n,h in m.items():assert (R/n).is_file() and not (R/n).is_symlink() and sha(R/n)==h,n
assert sha(R/'numeric-candidate.rs')=='4900531c70d9e034e02e2a002c569858843ce6e43f20f835b24be01128d04fb9'
new=(R/'numeric-candidate.rs').read_text();old=(R/'v1-numeric-candidate.rs').read_text()
for name in ['benchmark.rs','challenge.rs']:
 s=(R/('v1-'+name)).read_text();assert s.count(old)==1;s=s.replace(old,new)
 s=s.replace("struct Parser<'a> {",'#[derive(Clone, Copy)]\nstruct SourcePosition(usize);\nimpl SourcePosition { fn byte_index(&self) -> usize { self.0 } }\nstruct Parser<\'a> {')
 s=s.replace('fn position(&self) -> usize { self.position }','fn position(&self) -> SourcePosition { SourcePosition(self.position) }')
 s=s.replace("fn slice_from(&self, start: usize) -> &'a str { &self.input[start..self.position] }","fn slice_from(&self, start: SourcePosition) -> &'a str { &self.input[start.0..self.position] }")
 assert s==(R/name).read_text(),name
 for file in ['original-tokenizer.rs','candidate-tokenizer.rs']:
  text=(R/file).read_text();start=text.index('fn consume_numeric');end=text.index('\n#[inline]',start);assert text[start:end] in s
text=(R/'candidate-tokenizer.rs').read_text();start=text.index('fn consume_numeric');end=text.index('\n#[inline]',start);assert text[start:end]==new
tool=json.loads((R/'TOOLCHAIN.json').read_text());rustc=Path(tool['rustc_path']);assert sha(rustc)==tool['rustc_sha256']
assert subprocess.check_output([str(rustc),'--version','--verbose'],text=True)==tool['version']
out=a.output.resolve();assert not out.exists();out.mkdir(parents=True);commands=[]
def run(args):
 r=subprocess.run(args,capture_output=True,text=True);commands.append(dict(args=args,exit=r.returncode,stdout=r.stdout,stderr=r.stderr));(out/'commands.json').write_text(json.dumps(commands,indent=2)+'\n');assert r.returncode==0,r.stdout+r.stderr;return r
run([str(rustc),'--edition=2021','-O',str(R/'challenge.rs'),'-o',str(out/'challenge')]);r=run([str(out/'challenge')]);assert 'PASS 504 independent' in r.stdout
if a.benchmark:
 run([str(rustc),'--edition=2021','-O',str(R/'benchmark.rs'),'-o',str(out/'benchmark')]);r=run([str(out/'benchmark')]);assert len(r.stdout.splitlines())==54;(out/'benchmark.txt').write_text(r.stdout)
result=dict(authenticated=len(m),challenge=504,body='exact draft 4900531c...',benchmark='executed' if a.benchmark else 'retained timings authenticated',status='benchmark checkpoint only; final v2 review pending')
(out/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(result)
