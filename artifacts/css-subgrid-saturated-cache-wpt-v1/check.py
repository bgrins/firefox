import argparse,hashlib,json,os,re,subprocess,tempfile
from pathlib import Path
P=Path(__file__).resolve().parent
ROOT=P.parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def run(args,cwd,env=None):
 r=subprocess.run(args,cwd=cwd,env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=60)
 assert r.returncode==0,(args,r.stdout)
 return r.stdout

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();out=a.output.resolve();out.mkdir(exist_ok=False)
 for name,h in json.loads((P/'REFERENCES.json').read_text()).items():
  f=ROOT/name;assert sha(f)==h
  for rel,digest in json.loads(f.read_text()).items():assert sha(f.parent/rel)==digest
 controls=json.loads((P/'CONTROL-PINS.json').read_text())
 for name,h in controls['pins'].items():
  if h is not None:assert sha(P/'controls'/name)==h
 control_roster=json.loads(run(['/opt/homebrew/bin/node',str(P/'control-roster.mjs')],P))
 assert control_roster==json.loads((P/'CONTROL-ROSTER.json').read_text())
 pins=json.loads((P/'SOURCE-PINS.json').read_text());proposal=ROOT/'artifacts/css-subgrid-saturated-cache-proposal-v1'
 assert (P/'standalone.patch').read_bytes()==(proposal/'proposal.patch').read_bytes()+(P/'wpt.patch').read_bytes()
 path='testing/web-platform/tests/css/css-grid/subgrid/subgrid-repeat-count-capacity.html'
 html=(P/'subgrid-repeat-count-capacity.html').read_text()
 with tempfile.TemporaryDirectory(prefix='subgrid-landing-check-') as temp:
  temp=Path(temp);js=temp/'fixture.js';script=re.search(r'<script>(.*?)</script>',html,re.S).group(1)
  js.write_text(script);run(['/opt/homebrew/bin/node','--check',str(js)],temp)
  js.write_text('const registered=[];global.test=(fn,name)=>registered.push(name);\n'+script+'\nconsole.log(JSON.stringify(registered));')
  names=json.loads(run(['/opt/homebrew/bin/node',str(js)],temp));expected=[axis+': '+case for axis in ['columns','rows'] for case in ['large exact product','product beyond 32 bits','sum beyond 32 bits']];assert names==expected
  (out/'ROSTER.json').write_text(json.dumps({ '/css/css-grid/subgrid/subgrid-repeat-count-capacity.html':names},indent=2)+'\n')
  repo=temp/'git';repo.mkdir();run(['git','init','-q'],repo)
  for source,h in pins['original'].items():
   data=subprocess.check_output(['git','show',pins['revision']+':'+source],cwd=ROOT);assert hashlib.sha256(data).hexdigest()==h
   target=repo/source;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
  run(['git','apply','--check',str(P/'standalone.patch')],repo);run(['git','apply',str(P/'standalone.patch')],repo)
  for source,h in pins['candidate'].items():assert sha(repo/source)==h
  assert (repo/path).read_bytes()==(P/'subgrid-repeat-count-capacity.html').read_bytes()
  run(['git','apply','--reverse','--check',str(P/'standalone.patch')],repo);run(['git','apply','--reverse',str(P/'standalone.patch')],repo)
  for source,h in pins['original'].items():assert sha(repo/source)==h
  assert not (repo/path).exists()
  lean=ROOT/'artifacts/stylo-bloom-tools/lean-4.35.0-rc4-darwin_aarch64/bin/lean';assert sha(lean)=='d1d9c26a539f54fe839d2aa7760bf1ac1dd76a30b26e2c9684bebf2900038fcf'
  (temp/'Witnesses.lean').write_bytes((P/'Witnesses.lean').read_bytes())
  (out/'lean.log').write_text(run([str(lean),'Witnesses.lean'],temp,{**os.environ,'LEAN_NUM_THREADS':'2'}))
 cases=[('large exact product',2147483647,2,0,['a','b','a']),('product beyond 32 bits',1431655766,3,0,['a','b','c']),('sum beyond 32 bits',2147483647,2,2,['a','b','a'])]
 arithmetic=[]
 for label,count,groups,tail,prefix in cases:
  total=count*groups+tail;low=total%2**32;signed=low if low<2**31 else low-2**32;extra=3-signed
  assert -2**31<=extra<=2**31-1 and signed!=-2**31
  assert total>3
  arithmetic.append({'case':label,'count':count,'groups':groups,'ordinary_tail_groups':tail,'exact_total':total,'narrowed_int32':signed,'modeled_native64_remaining':max(0,extra),'exact_remaining':0,'expected_prefix':prefix,'usize32_product_fits':count*groups<2**32,'usize32_sum_fits':total<2**32})
 (out/'ARITHMETIC.json').write_text(json.dumps(arithmetic,indent=2)+'\n')
 receipt={'status':'PASS_ARTIFACT_ONLY','tests':6,'existing_control_subtests':sum(map(len,control_roster.values())),'existing_reftests':4,'syntax_exit':0,'callbacks_executed':False,'scratch_git_apply_reverse':True,'kernel_checked_examples':4,'new_named_theorems':0,'lean_exit':0,'browser_observed':False,'temporary_products_removed':True,'native_paths_unchanged_from_proposal':3,'landing_path':path}
 (out/'CHECK.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
if __name__=='__main__':main()
