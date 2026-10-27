import argparse,hashlib,json,os,subprocess,tempfile
from pathlib import Path
P=Path(__file__).resolve().parent
ROOT=P.parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();out=a.output.resolve();out.mkdir(exist_ok=False)
 inputs=json.loads((P/'INPUTS.json').read_text());lean=ROOT/inputs['lean'];assert sha(lean)==inputs['lean_sha256']
 for name,h in inputs['modules'].items():assert sha(P/name)==h
 for path,h in json.loads((P/'REFERENCES.json').read_text()).items():
  manifest=ROOT/path;assert sha(manifest)==h
  for rel,digest in json.loads(manifest.read_text()).items():assert sha(manifest.parent/rel)==digest
 assert (P/'CountTransport.lean').read_bytes()==(ROOT/'artifacts/css-subgrid-count-transport-model-v1/CountTransport.lean').read_bytes()
 assert sha(P/'PROSPECTIVE.patch')==json.loads((P/'SOURCE-CONTRACT.json').read_text())['snapshot_patch_sha256']
 with tempfile.TemporaryDirectory(prefix='guarded-consumer-replay-') as temp:
  temp=Path(temp)
  for name in inputs['modules']:(temp/name).write_bytes((P/name).read_bytes())
  env={**os.environ,'LEAN_PATH':str(temp),'LEAN_NUM_THREADS':'2'}
  for label,args in [('dependency',['-o','CountTransport.olean','CountTransport.lean']),('companion',['GuardedConsumer.lean'])]:
   r=subprocess.run([str(lean),*args],cwd=temp,env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=60)
   (out/(label+'.log')).write_text(r.stdout);assert r.returncode==0,r.stdout
   assert 'sorryAx' not in r.stdout and all(line.endswith('depends on axioms: [propext, Classical.choice, Quot.sound]') for line in r.stdout.splitlines())
  assert len((out/'dependency.log').read_text().splitlines())==5
  assert (out/'companion.log').read_text()=="'SubgridGuardedConsumer.guarded_transport' depends on axioms: [propext, Classical.choice, Quot.sound]\n"
 receipt={'status':'PASS','lean_exits':[0,0],'threads':2,'new_general_theorems':1,'prior_results_rebuilt_not_new':5,'new_anonymous_examples':8,'canonical_registrations':0,'source_refinement':False,'temporary_products_removed':True}
 (out/'CHECK.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
if __name__=='__main__':main()
