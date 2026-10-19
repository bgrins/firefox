from pathlib import Path
import argparse,hashlib,json,os,subprocess,sys
assert sys.flags.isolated and sys.flags.no_site
R=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--olean',type=Path,required=True);a=p.parse_args();out=a.output.resolve();out.mkdir(parents=True,exist_ok=False)
env={k:v for k,v in os.environ.items() if not k.startswith(('PYTHON','LEAN_'))}
config=json.loads((R/'TOOLCHAIN.json').read_text());lean=Path(config['lean']);assert hashlib.sha256(lean.read_bytes()).hexdigest()==config['lean_sha256']
commands=[]
def run(cmd,log,localenv=None):
 r=subprocess.run(list(map(str,cmd)),capture_output=True,text=True,env=localenv or env);(out/log).write_text(r.stdout+r.stderr);commands.append({'command':list(map(str,cmd)),'exit':r.returncode,'log':log});return r
cases=json.loads((R/'CASES.json').read_text());keys=[]
for i,c in enumerate(cases):
 keys.append([str(i),'0','init'])
 for j,op in enumerate(c['ops']):
  assert op in ['fetch','stop','save','query'] or op.startswith(('reset:','enable:'))
  keys.append([str(i),str(j+1),op])
r=run([lean,'--run',R/'lean/HistoryDriver.lean'],'model.txt',{**env,'LEAN_PATH':str(a.olean.resolve())});assert r.returncode==0,r.stdout+r.stderr
expected=r.stdout.splitlines()
def grammar(rows):
 assert len(rows)==len(keys),'exact operation roster'
 for row,key in zip(rows,keys):
  f=row.split('|');assert len(f)==11,'exact field arity';assert f[:3]==key,'exact ordered input/operation identity'
grammar(expected)
def compare(rows):
 grammar(rows)
 assert rows==expected,'projected state/result differs from independent Lean execution'
normal=[]
for name,flags in [('debug',[]),('release',['--release'])]:
 r=run([sys.executable,'-I','-S',R/'native/build.py','--output',out/name,*flags],name+'.log');assert r.returncode==0,r.stdout+r.stderr
 rows=(out/name/'raw.txt').read_text().splitlines();compare(rows);normal.append({'mode':name,'rows':len(rows),'sha256':hashlib.sha256((out/name/'raw.txt').read_bytes()).hexdigest()})
mutants=[]
for m in json.loads((R/'MUTATIONS.json').read_text()):
 name='mutant-'+m['id'];r=run([sys.executable,'-I','-S',R/'native/build.py','--output',out/name,'--mutation',m['id']],name+'.log')
 compiled=json.loads((out/name/'COMMANDS.json').read_text());assert all(c['exit']==0 for c in compiled[:-1]),'compile failure is not a semantic mutant'
 assert compiled[-1]['command'][0]==str(out/name/'probe'),'must execute mutant'
 if r.returncode==0:
  rows=(out/name/'raw.txt').read_text().splitlines();grammar(rows)
  differences=[i for i,(x,y) in enumerate(zip(rows,expected)) if x!=y];assert differences,'mutant did not discriminate'
  mutants.append({'id':m['id'],'result':'different projected observations','rows':differences})
 else:
  assert compiled[-1]['exit']!=0,'only runtime rejection admitted'
  mutants.append({'id':m['id'],'result':'native runtime rejection','exit':compiled[-1]['exit']})
corruptions={
 'drop-first':expected[1:],
 'duplicate-first':[expected[0],*expected],
 'unknown-operation':[expected[0].replace('|init|','|unknown|'),*expected[1:]],
 'extra-field':[expected[0]+'|ignored',*expected[1:]],
 'swap-first-two':[expected[1],expected[0],*expected[2:]],
 'observer-none-empty':[expected[0].replace('|none|none|none','|some:|none|none'),*expected[1:]],
}
for name,rows in corruptions.items():
 assert rows!=expected,name
 try:compare(rows)
 except AssertionError:pass
 else:raise AssertionError('accepted corruption '+name)
receipt={'status':'PASS','cases':len(cases),'operation_snapshots':len(expected),'normal':normal,'native_mutants':mutants,'rejected_trace_corruptions':list(corruptions),'commands':commands,'scope':'Complete primary API byte/pending/cache/token/mode/annotation/saved-state projection. Other token payloads and full line metadata are intentionally not projected.'}
(out/'CHECK.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({k:v for k,v in receipt.items() if k!='commands'}))
