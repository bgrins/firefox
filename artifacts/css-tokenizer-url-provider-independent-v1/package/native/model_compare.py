from pathlib import Path
import argparse,json,hashlib,subprocess,os
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--native',type=Path,required=True);p.add_argument('--olean',type=Path,required=True);a=p.parse_args();out=a.output.resolve();out.mkdir(parents=True,exist_ok=False)
tool=json.loads((ROOT/'TOOLCHAIN.json').read_text());lean=Path(tool['lean']);assert hashlib.sha256(lean.read_bytes()).hexdigest()==tool['lean_sha256']
cases=json.loads((ROOT/'CASES.json').read_text());cmd=[str(lean),'--run',str(ROOT/'lean/Driver.lean')]
r=subprocess.run(cmd,input=''.join(x['input'].encode().hex()+'\n'for x in cases),text=True,capture_output=True,env={**{k:v for k,v in os.environ.items()if not k.startswith(("PYTHON","LEAN_"))},'LEAN_PATH':str(a.olean.resolve())});(out/'MODEL.txt').write_text(r.stdout);(out/'STDERR.txt').write_text(r.stderr);assert r.returncode==0,r.stdout+r.stderr
raw=[x.split('|')for x in a.native.read_text().splitlines()];actual={}
for f in raw:
 if f[1]=='0':actual[(f[0],'first')]=f
 elif f[2] in ['string','bad-string']:actual[(f[0],'string')]=f
matched=[]
for line in r.stdout.splitlines():
 f=line.split('|');key=(f[0],f[1]);target=actual.pop(key);expected=target[:];expected[1]=f[1]
 assert f==expected[:9],(f,expected)
 matched.append(key)
assert not actual,actual
receipt={'cases':len(cases),'first_tokens':sum(k=='first'for _,k in matched),'delegated_strings':sum(k=='string'for _,k in matched),'fields':['kind','payload including raw BadUrl','byte offset','line','UTF16 column','pending block','function observer'],'command':cmd,'native_sha256':hashlib.sha256(a.native.read_bytes()).hexdigest(),'model_sha256':hashlib.sha256(r.stdout.encode()).hexdigest(),'status':'PASS','scope':'Fixed native-to-Lean observations; not universal source/compiler refinement or public cache-history proof.'}
(out/'CHECK.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
