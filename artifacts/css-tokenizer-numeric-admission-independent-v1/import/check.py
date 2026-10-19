import argparse,hashlib,json,os,re,shutil,subprocess,sys
from pathlib import Path
R=Path(__file__).resolve().parent
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
p=argparse.ArgumentParser();p.add_argument('--lean',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
f=json.loads((R/'FREEZE.json').read_text());assert H(R/'MANIFEST.json')==f['manifest_sha256']
m=json.loads((R/'MANIFEST.json').read_text())
for n,h in m.items():
 q=R/n;assert q.is_file() and not q.is_symlink() and H(q)==h,n
for name,meta in json.loads((R/'PARENTS.json').read_text()).items():
 d=R/'inputs'/name
 assert H(d/meta['manifest'])==meta['manifest_sha256']
 assert H(d/'FREEZE.json')==meta['freeze_sha256']
 for n,h in json.loads((d/meta['manifest']).read_text()).items():assert H(d/n)==h,(name,n)
lean=a.lean.resolve();assert H(lean)=='d1d9c26a539f54fe839d2aa7760bf1ac1dd76a30b26e2c9684bebf2900038fcf'
out=a.output.resolve();assert not out.exists();out.mkdir(parents=True)
commands=[]
def run(cmd,cwd):
 r=subprocess.run(cmd,cwd=cwd,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1','LEAN_PATH':str(cwd)},capture_output=True,text=True)
 commands.append({'cmd':cmd,'cwd':str(cwd),'exit':r.returncode,'stdout':r.stdout,'stderr':r.stderr})
 (out/'COMMANDS.json').write_text(json.dumps(commands,indent=2)+'\n')
 assert r.returncode==0,commands[-1]
 return r.stdout+r.stderr
run([sys.executable,str(R/'source_bindings.py'),'--output',str(out/'SOURCE-BINDINGS.json')],out)
proof=out/'proof';proof.mkdir()
name=R/'inputs/integration/inputs/name'
repair=R/'inputs/integration/inputs/repair'
modules=['IdentifierStart','HexPrefix','Escape','Name','Boundary','EscapeBoundary','SemanticName','Caller','Witnesses','Integration','NumericDigits','NumericEntry','NumericParts','NumericLexical','NumericToken','NumericBoundary','NumericReads','NumericUnits','NumericPayload','NumericScanner']
audits=[]
for module in modules:
 src=name/'lean'/(module+'.lean')
 if module=='IdentifierStart':src=repair/'lean/IdentifierStart.lean'
 elif module=='Integration':src=R/'inputs/integration/lean/Integration.lean'
 elif module.startswith('Numeric'):src=R/'lean'/(module+'.lean')
 assert not re.search(r'\b(sorry|admit|axiom|native_decide)\b',src.read_text()),module
 shutil.copyfile(src,proof/src.name)
 log=run([str(lean),'-o',module+'.olean',module+'.lean'],proof)
 found=re.findall(r"^'([^']+)' (?:depends on axioms: \[([^\]]*)\]|does not depend on any axioms)$",log,re.M)
 assert found,module
 for theorem,deps in found:assert set(filter(None,deps.split(', ')))<={'propext','Classical.choice','Quot.sound'},(theorem,deps)
 audits+=found
run([sys.executable,str(R/'native/build.py'),'--output',str(out/'native')],out)
run([sys.executable,str(R/'native/lean_observations.py'),'--lean',str(lean),'--modules',str(proof),'--native',str(out/'native/OBSERVATIONS.tsv')],out)
run([sys.executable,str(R/'native/mutations.py'),'--baseline',str(out/'native'),'--modules',str(proof),'--lean',str(lean),'--output',str(out/'mutants')],out)
result={'status':'PASS','authenticated':len(m),'modules':len(modules),'theorem_audits':len(audits),'native_cases':90,'native_to_lean_rows':81,'native_semantic_mutants':4,'lean_semantic_mutants':4,'complete_source_definitions':16,'arithmetic':'original payload loss retained; no exact-real/IEEE/FromStr theorem','whole_tokenizer':'OPEN','ownership':'native name projection; no independent ownership semantics','native_admission':'codec, usize, metadata normal completion, allocation, compiler/core/string contracts remain explicit'}
(out/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
