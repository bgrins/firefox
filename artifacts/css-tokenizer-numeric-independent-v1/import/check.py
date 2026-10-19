from pathlib import Path
import argparse,hashlib,json,shutil,subprocess,tempfile
from decimal import Decimal
R=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def verify():
 manifest=json.loads((R/'INPUTS.json').read_text())
 for name,digest in manifest.items():
  assert sha(R/name)==digest,name
 assert set(manifest)=={str(p.relative_to(R)) for p in R.rglob('*') if p.is_file()}-{'INPUTS.json','FREEZE.json'}
 freeze=json.loads((R/'FREEZE.json').read_text());assert sha(R/'INPUTS.json')==freeze['inputs_sha256']
 for folder in ['original','candidate']:
  base=R/folder/'third_party/rust/cssparser'
  assert json.loads((base/'.cargo-checksum.json').read_text())['files']['src/tokenizer.rs']==sha(base/'src/tokenizer.rs')
  source=(base/'src/tokenizer.rs').read_text();a=source.index('fn consume_numeric');b=source.index('\n#[inline]',a)
  assert source[a:b]==(R/('numeric-before.rs' if folder=='original' else 'numeric-candidate.rs')).read_text()
 before=json.loads((R/'original/third_party/rust/cssparser/.cargo-checksum.json').read_text());after=json.loads((R/'candidate/third_party/rust/cssparser/.cargo-checksum.json').read_text())
 before['files']['src/tokenizer.rs']=after['files']['src/tokenizer.rs'];assert before==after
 for row in json.loads((R/'DECIMAL.json').read_text()): assert Decimal(row['number'])==Decimal(row['expected'])
 return len(manifest)
def run(out):
 out.mkdir(parents=True,exist_ok=False);receipts=[]
 def command(args,cwd=None,expect=0):
  p=subprocess.run(args,cwd=cwd,text=True,capture_output=True)
  n=len(receipts);log=out/f'{n:02d}.log';log.write_text(p.stdout+p.stderr)
  receipts.append(dict(command=args,cwd=str(cwd) if cwd else None,status=p.returncode,log=log.name,sha256=sha(log)))
  assert (p.returncode==0) if expect==0 else (p.returncode!=0),(args,p.stdout,p.stderr)
  return p
 with tempfile.TemporaryDirectory(prefix='css-numeric-') as tmp:
  t=Path(tmp);copy=t/'capsule';shutil.copytree(R,copy)
  command(['python3',str(copy/'make_witness.py')])
  assert (copy/'numeric-comparison.rs').read_bytes()==(R/'numeric-comparison.rs').read_bytes()
  assert (copy/'CASES.json').read_bytes()==(R/'CASES.json').read_bytes()
  tree=t/'apply';shutil.copytree(R/'original',tree)
  command(['patch','--batch','--fuzz=0','-p1','-i',str(R/'native-candidate.patch')],tree)
  for p in (R/'candidate').rglob('*'):
   if p.is_file(): assert (tree/p.relative_to(R/'candidate')).read_bytes()==p.read_bytes()
  command(['patch','--batch','--fuzz=0','-R','-p1','-i',str(R/'native-candidate.patch')],tree)
  for p in (R/'original').rglob('*'):
   if p.is_file(): assert (tree/p.relative_to(R/'original')).read_bytes()==p.read_bytes()
  command(['rustc','--version','--verbose'])
  for mode,flags in [('debug',[]),('release',['-O'])]:
   binary=t/mode
   command(['rustc','--edition=2021',*flags,str(R/'numeric-comparison.rs'),'-o',str(binary)])
   result=command([str(binary)]);assert 'PASS total=852 changed=300 unchanged=552' in result.stdout
  source=(R/'numeric-comparison.rs').read_text();prefix,body=source.split('mod candidate {',1)
  mutants={
   'final-nonfinite-only':body.replace('if needs_reparse {','if !value.is_finite() {'),
   'no-fraction-subnormal':body.replace('needs_reparse |= factor < f64::MIN_POSITIVE;','needs_reparse |= false;'),
   'no-exponent-subnormal':body.replace('needs_reparse |= !factor.is_normal();','needs_reparse |= !factor.is_finite();'),
  }
  for name,mutant in mutants.items():
   assert mutant!=body
   path=t/(name+'.rs');path.write_text(prefix+'mod candidate {'+mutant)
   binary=t/name;command(['rustc','--edition=2021','-O',str(path),'-o',str(binary)])
   failed=command([str(binary)],expect=1)
   assert 'reference case' in failed.stderr and 'assertion' in failed.stderr
 (out/'REPLAY.json').write_text(json.dumps({'status':'PASS','source_sha256':sha(R/'numeric-comparison.rs'),'commands':receipts},indent=2)+'\n')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--run',action='store_true');p.add_argument('--output',type=Path);args=p.parse_args()
 n=verify()
 if args.run:
  assert args.output;run(args.output.resolve())
 print(f'PASS {n} authenticated entries'+(' plus source binding, patch apply/reverse, debug/release and three semantic mutants' if args.run else ''))
