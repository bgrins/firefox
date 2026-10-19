from pathlib import Path
import argparse,hashlib,json,shutil,subprocess,sys,os
assert sys.flags.isolated and sys.flags.no_site
SAFE_ENV={k:v for k,v in os.environ.items()if not k.startswith(("PYTHON","LEAN_"))}
R=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--olean',type=Path,required=True);a=p.parse_args();out=a.output.resolve();out.mkdir(parents=True,exist_ok=False);commands=[]
def run(args,log,expected=0):
 cmd=[sys.executable,'-I','-S',*map(str,args)];r=subprocess.run(cmd,capture_output=True,text=True,env=SAFE_ENV);(out/log).write_text(r.stdout+r.stderr);commands.append({'command':cmd,'exit':r.returncode,'log':log});assert (r.returncode==0)if expected==0 else(r.returncode!=0),(log,r.stdout+r.stderr)
raw=[]
for mode,flags in [('debug',[]),('release',['--release']),('fast-release',['--fast','--release'])]:
 run([R/'native/build.py','--output',out/mode,*flags],mode+'-build.log')
 run([R/'native/compare.py','--native',out/mode,'--output',out/(mode+'-reference')],mode+'-reference.log')
 raw.append((out/mode/'raw.txt').read_bytes())
assert raw[0]==raw[1]==raw[2]
run([R/'native/model_compare.py','--native',out/'fast-release/raw.txt','--output',out/'model','--olean',a.olean], 'model.log')
mutants=[]
for m in json.loads((R/'MUTATIONS.json').read_text()):
 d=out/('mutation-'+m['id']);run([R/'native/build.py','--output',d,'--mutation',m['id']],m['id']+'-build.log')
 run([R/'native/compare.py','--native',d,'--output',d/'comparison'],m['id']+'-rejection.log',1)
 differences=json.loads((d/'comparison/COMPARISON.json').read_text())['unexpected_differences'];assert differences
 mutants.append({'id':m['id'],'compiled':True,'unexpected_differences':len(differences)})
# Challenge both the allowed rollback tuple and an unrelated Function token.
rows=raw[0].decode().splitlines();targets=[]
for i,line in enumerate(rows):
 f=line.split('|')
 if f[2]=='function':
  name=bytes.fromhex(f[3]).decode().lower()
  if name=='url' and not any(k=='quoted'for k,_ in targets):targets.append(('quoted',i))
  if name!='url' and not any(k=='other'for k,_ in targets):targets.append(('other',i))
assert len(targets)==2
for kind,i in targets:
 d=out/('comparator-corruption-'+kind);d.mkdir();changed=rows[:];f=changed[i].split('|');f[4]=str(int(f[4])+1);changed[i]='|'.join(f);(d/'raw.txt').write_text('\n'.join(changed)+'\n')
 run([R/'native/compare.py','--native',d,'--output',d/'comparison'],'comparator-corruption-'+kind+'.log',1)
 assert json.loads((d/'comparison/COMPARISON.json').read_text())['unexpected_differences']
receipt={'status':'PASS','cases':57,'modes':['debug','release','fast_match_byte release'],'raw_sha256':hashlib.sha256(raw[0]).hexdigest(),'native_mutants':mutants,'comparator_corruptions':[k for k,_ in targets],'commands':commands};(out/'CHECK.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({k:v for k,v in receipt.items()if k!='commands'}))
