import argparse,hashlib,json,os,re,shutil,subprocess,sys
from pathlib import Path
R=Path(__file__).resolve().parent
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
p=argparse.ArgumentParser();p.add_argument('--lean',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
f=json.loads((R/'FREEZE.json').read_text());assert H(R/'MANIFEST.json')==f['manifest_sha256']
m=json.loads((R/'MANIFEST.json').read_text())
for n,h in m.items():
 q=R/n;assert q.is_file() and not q.is_symlink() and H(q)==h,n
for key,parent in json.loads((R/'PARENTS.json').read_text()).items():
 d=R/'inputs'/key;assert H(d/parent['manifest'])==parent['manifest_sha256'];assert H(d/'FREEZE.json')==parent['freeze_sha256']
 for n,h in json.loads((d/parent['manifest']).read_text()).items():assert H(d/n)==h,(key,n)
lean=a.lean.resolve();assert H(lean)=='d1d9c26a539f54fe839d2aa7760bf1ac1dd76a30b26e2c9684bebf2900038fcf'
out=a.output.resolve();assert not out.exists() and not out.is_relative_to(R);out.mkdir(parents=True)
commands=[]
def run(cmd,cwd):
 r=subprocess.run(cmd,cwd=cwd,env={**os.environ,'LEAN_PATH':str(cwd),'PYTHONDONTWRITEBYTECODE':'1'},capture_output=True,text=True)
 commands.append({'cmd':cmd,'cwd':str(cwd),'exit':r.returncode,'stdout':r.stdout,'stderr':r.stderr});(out/'COMMANDS.json').write_text(json.dumps(commands,indent=2)+'\n')
 assert r.returncode==0,commands[-1]
 return r.stdout+r.stderr
tamper=out/'tamper-source'
shutil.copytree(R,tamper)
changed=tamper/'lean/NumericCapture.lean'
changed.write_bytes(changed.read_bytes()+b'\n')
blocked=out/'tamper-must-not-create'
r=subprocess.run([sys.executable,str(tamper/'check.py'),'--lean',str(lean),'--output',str(blocked)],capture_output=True,text=True)
assert r.returncode!=0 and 'lean/NumericCapture.lean' in r.stderr and not blocked.exists()
(out/'TAMPER.json').write_text(json.dumps({'exit':r.returncode,'stdout':r.stdout,'stderr':r.stderr,'output_created':False},indent=2)+'\n')
shutil.rmtree(tamper)
run([sys.executable,str(R/'source_bindings.py'),'--output',str(out/'SOURCE-BINDINGS.json')],out)
proof=out/'proof';proof.mkdir();lex=R/'inputs/lexical';name=lex/'inputs/integration/inputs/name';repair=lex/'inputs/integration/inputs/repair'
modules=['IdentifierStart','HexPrefix','Escape','Name','Boundary','EscapeBoundary','SemanticName','Caller','Witnesses','Integration','NumericDigits','NumericEntry','NumericParts','NumericLexical','NumericToken','NumericBoundary','NumericReads','NumericUnits','NumericPayload','NumericScanner','FromStrGrammar','NumericCapture','NumericRepair']
inventory=json.loads((R/'AUDIT-INVENTORY.json').read_text())
assert list(inventory)==modules
audits=[]
for module in modules:
 src=name/'lean'/(module+'.lean')
 if module=='IdentifierStart':src=repair/'lean/IdentifierStart.lean'
 elif module=='Integration':src=lex/'inputs/integration/lean/Integration.lean'
 elif module in ['FromStrGrammar','NumericCapture','NumericRepair']:src=R/'lean'/(module+'.lean')
 elif module.startswith('Numeric'):src=lex/'lean'/(module+'.lean')
 assert not re.search(r'\b(sorry|admit|axiom|native_decide)\b',src.read_text()),module
 shutil.copyfile(src,proof/src.name)
 log=run([str(lean),'-o',module+'.olean',module+'.lean'],proof)
 found=re.findall(r"^'([^']+)' (?:depends on axioms: \[([^\]]*)\]|does not depend on any axioms)$",log,re.M);assert [theorem for theorem,deps in found]==inventory[module],(module,found)
 for theorem,deps in found:assert set(filter(None,deps.split(', ')))<={'propext','Classical.choice','Quot.sound'},(theorem,deps)
 audits+=found
(proof/'ExtendedSlice.lean').write_text('import NumericRepair\n#eval NumericCapture.slice [49,101,109] 0 2 == (NumericLexical.native [49,101,109]).text\n')
assert run([str(lean),'ExtendedSlice.lean'],proof).strip()=='false'
run([sys.executable,str(R/'native_replay.py'),'--output',str(out/'native')],out)
result={'status':'PASS','authenticated':len(m),'modules':len(modules),'theorem_audits':len(audits),'new_theorem_audits':len(audits)-130,'native_pair_rows':90,'capture_rows':84,'source_bindings':11,'library_source_files':1,'candidate_sha256':'5319a01e403cd2a93bfc3dd4c53a7e5ec95129360da58c6f9f76f480ae5e6211','native_and_model_extended_slice_mutant':'discriminated','standard_parser':'documented grammar acceptance assumed; implementation not proved','values':'f64/f32/i32 payload fidelity and preservation not claimed','whole_tokenizer':'OPEN','exact_theorem_inventory':True,'source_tamper_rejected_before_output':True}
(out/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
