import hashlib,json,sys
from pathlib import Path
R=Path(__file__).resolve().parent.parent
S=R/'evidence/all-order'
n={'__file__':str(S/'native/build.py'),'__name__':'authenticated_reuse'}
exec(compile((S/'native/build.py').read_text(),str(S/'native/build.py'),'exec'),n)

def build(out):
 out.mkdir(parents=True,exist_ok=False)
 meta,providers=n['provider']()
 (out/'PROVIDERS.json').write_text(json.dumps(providers,indent=2)+'\n')
 for variant in ['original','candidate','mutant_ascending','mutant_rank_omitted','mutant_rank_plus','mutant_remove_bits','mutant_replace_bits']:
  body,records=n['extract']('original' if variant=='original' else 'candidate')
  updates=n['item'](body,'pub fn update(')
  boundary=updates.index('        self.declarations.reserve(updates.new_count);')
  prefix=updates[:boundary];ordinary=updates[boundary:]
  mutations=[]
  def change(old,new):
   nonlocal ordinary
   assert ordinary.count(old)==1,(variant,old)
   ordinary=ordinary.replace(old,new)
   mutations.append({'old':old,'new':new})
  if variant=='mutant_ascending':change('                .rev()\n','')
  if variant=='mutant_rank_omitted':change('pos: update.pos - removed_count,','pos: update.pos,')
  if variant=='mutant_rank_plus':change('pos: update.pos - removed_count,','pos: update.pos + removed_count,')
  if variant=='mutant_remove_bits':change('                    self.declarations_importance.remove(update.pos);\n','')
  if variant=='mutant_replace_bits':change('                    self.declarations_importance.set(pos, important);','                    self.declarations_importance.set(pos, !important);')
  assert body.count(updates)==1
  body=body.replace(updates,prefix+ordinary)
  facade=(S/'native/facade.rs').read_text()
  src=facade+meta+body+(R/'native/driver.rs').read_text()
  (out/f'{variant}.rs').write_text(src)
  (out/f'{variant}-extraction.json').write_text(json.dumps(records,indent=2)+'\n')
  (out/f'{variant}-mutation.json').write_text(json.dumps(mutations,indent=2)+'\n')
 old=n['item']((S/'evidence/declaration_block.original.rs').read_text(),'pub fn update(')
 new=n['item']((S/'evidence/declaration_block.candidate.rs').read_text(),'pub fn update(')
 marker='        self.declarations.reserve(updates.new_count);'
 assert old[old.index(marker):]==new[new.index(marker):]
 (out/'BINDING.json').write_text(json.dumps({'ordinary_update_body_identical':True,'ordinary_update_sha256':hashlib.sha256(new[new.index(marker):].encode()).hexdigest(),'original_complete_items':len(n['extract']('original')[1]),'candidate_complete_items':len(n['extract']('candidate')[1])},indent=2)+'\n')
if __name__=='__main__':build(Path(sys.argv[1]))
