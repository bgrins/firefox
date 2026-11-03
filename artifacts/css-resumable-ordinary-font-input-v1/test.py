import hashlib,json,subprocess,tempfile,shutil
from pathlib import Path
HERE=Path(__file__).resolve().parent
s=(HERE/'candidate/servo/components/style/properties/cascade.rs').read_text()
def block(needle):
 a=s.index(needle);b=s.index('{',a);depth=1;i=b+1
 while depth:
  depth+=(s[i]=='{')-(s[i]=='}');i+=1
 return s[a:i]
predicate=block('fn is_retained_font_input(')
action=block('fn perform_font_input_action(')
code=(HERE/'ActionTests.rs').read_text().replace('// EXACT-PREDICATE',predicate).replace('// EXACT-ACTION',action)
(HERE/'ACTION-EXTRACTED.rs').write_text(code)
variants={'positive':code,'no_completion_ledger':code.replace('self.completed_font_inputs.insert(longhand);',''),'drop_retained_state':code.replace('self.font_preparation = Some(state);',''),'allow_wrong_reply':code.replace('reference.as_ref().is_some_and(|(id, _)| *id != longhand)','false'),'allow_wrong_target':code.replace('state.longhand != longhand','false'),'replay_completed_input':code.replace('if self.completed_font_inputs.contains(longhand) {','if false {')}
scratch=Path(tempfile.mkdtemp(prefix='css-ordinary-input-actions-',dir='/private/tmp'));results=[]
try:
 for name,text in variants.items():
  source=scratch/(name+'.rs');source.write_text(text);binary=scratch/name
  compiled=subprocess.run(['rustc','--edition=2024','--test',str(source),'-o',str(binary)],capture_output=True,text=True)
  assert compiled.returncode==0,(name,compiled.stderr)
  run=subprocess.run([str(binary),'--test-threads=1'],capture_output=True,text=True)
  results.append({'variant':name,'compile_exit':compiled.returncode,'exit':run.returncode,'stdout':run.stdout,'stderr':run.stderr})
  assert run.returncode==(0 if name=='positive' else 101),name
finally:shutil.rmtree(scratch)
(HERE/'ACTION-CHECK.json').write_text(json.dumps({'results':results,'extracted_function_sha256':{'predicate':hashlib.sha256(predicate.encode()).hexdigest(),'action':hashlib.sha256(action.encode()).hexdigest()},'scratch':str(scratch),'scratch_removed':not scratch.exists(),'scope':'Actual action-controller body and admission predicate. Selector/provider/native apply are scripted doubles; no native effect/readset correctness claim.'},indent=2)+'\n')
print(json.dumps({'positive_tests':5,'compiled_negative_controls':5,'scratch_removed':not scratch.exists()}))
