import argparse,hashlib,json,os,subprocess,tempfile
from pathlib import Path
P=Path(__file__).resolve().parent
ROOT=P.parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();out=a.output.resolve();out.mkdir(exist_ok=False)
 inputs=json.loads((P/'INPUTS.json').read_text());lean=ROOT/inputs['lean'];assert sha(lean)==inputs['lean_sha256'];assert sha(P/'CountTransport.lean')==inputs['module_sha256']
 refs=json.loads((P/'REFERENCES.json').read_text())
 for name in ['SOURCE-PINS.json','SOURCE-EXCERPTS.json']:
  assert (P/name).read_bytes()==(ROOT/'artifacts/css-subgrid-positive-count-audit-v2'/name).read_bytes()
 for path,h in refs.items():
  manifest=ROOT/path;assert sha(manifest)==h
  for rel,digest in json.loads(manifest.read_text()).items():assert sha(manifest.parent/rel)==digest
 with tempfile.TemporaryDirectory(prefix='subgrid-count-model-') as t:
  t=Path(t);(t/'CountTransport.lean').write_bytes((P/'CountTransport.lean').read_bytes())
  env={**os.environ,'LEAN_NUM_THREADS':'2'}
  result=subprocess.run([str(lean),'CountTransport.lean'],cwd=t,env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=60)
  (out/'lean.log').write_text(result.stdout)
  assert result.returncode==0,result.stdout
  names=['addCap_correct','mulCap_correct','cache_correct','remaining_capacity_preserved','signed_transport_safe']
  assert len(result.stdout.splitlines())==len(names)
  for name in names:assert "'SubgridCountTransport."+name+"' depends on axioms: [propext, Classical.choice, Quot.sound]" in result.stdout
  assert not list(t.glob('*.olean'))
 check={'status':'PASS','lean_exit':0,'threads':2,'named_general_results':names,'anonymous_checked_examples':8,'new_canonical_registrations':0,'source_refinement_proved':False,'temporary_outputs_removed':True,'references_authenticated':len(refs)}
 (out/'CHECK.json').write_text(json.dumps(check,indent=2)+'\n');print(json.dumps(check,indent=2))
if __name__=='__main__':main()
