from pathlib import Path
import argparse,hashlib,json,subprocess,tempfile,shutil,re
R=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def verify():
 entries=json.loads((R/'INPUTS.json').read_text())
 for name,digest in entries.items():assert sha(R/name)==digest,name
 assert set(entries)=={str(p.relative_to(R)) for p in R.rglob('*') if p.is_file()}-{'INPUTS.json','FREEZE.json'}
 assert sha(R/'INPUTS.json')==json.loads((R/'FREEZE.json').read_text())['inputs_sha256']
 for item in json.loads((R/'EXTRACTIONS.json').read_text()):
  source=(R/'source/third_party/rust/cssparser/src'/item['source']).read_text();body=source[item['start']:item['end']]
  assert hashlib.sha256(body.encode()).hexdigest()==item['sha256']
  assert body in (R/'consumer-witness.rs').read_text()
  assert body in (R/'searchfox'/(item['source']+'.txt')).read_text()
 for name in ['string-comment-controls.html','known-badstring-recovery.html']:
  code='\n'.join(re.findall(r'<script[^>]*>(.*?)</script>',(R/name).read_text(),re.S))
  p=subprocess.run(['node','--check'],input=code,text=True,capture_output=True);assert p.returncode==0,p.stderr
 return len(entries)
def replay(out):
 out.mkdir(parents=True,exist_ok=False);records=[]
 def command(cmd):
  p=subprocess.run(cmd,capture_output=True,text=True);log=out/(str(len(records))+'.log');log.write_text(p.stdout+p.stderr);records.append(dict(command=cmd,status=p.returncode,log=log.name,sha256=sha(log)));assert p.returncode==0,p.stderr
  return p
 with tempfile.TemporaryDirectory(prefix='css-string-comment-') as tmp:
  root=Path(tmp);shutil.copytree(R,root/'capsule');copy=root/'capsule';command(['python3',str(copy/'generate.py')])
  for name in ['consumer-witness.rs','CASES.json','EXTRACTIONS.json']:assert (copy/name).read_bytes()==(R/name).read_bytes()
  command(['rustc','--version','--verbose'])
  for mode,flags in [('debug',[]),('release',['-O'])]:
   binary=root/mode;command(['rustc','--edition=2021',*flags,str(copy/'consumer-witness.rs'),'-o',str(binary)]);p=command([str(binary)]);assert 'PASS strings=298 comments=348 total=646' in p.stdout
 (out/'REPLAY.json').write_text(json.dumps(dict(status='PASS',commands=records),indent=2)+'\n')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--run',action='store_true');p.add_argument('--output',type=Path);a=p.parse_args();n=verify()
 if a.run:assert a.output;replay(a.output.resolve())
 print(f'PASS {n} authenticated entries; 27 complete source bindings; probe syntax'+('; fresh debug/release646 cases' if a.run else ''))
