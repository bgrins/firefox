import hashlib,json,sys,types,tomllib
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent

def load(path):
 n={'__file__':str(path),'__name__':'retained_source'}
 exec(compile(path.read_text(),str(path),'exec'),n)
 return n

reader=load(ROOT/'native/rust_reader.py')
def item(source,anchor,start=0):
 a=source.index(anchor,start);ts=reader['tokens'](source[a:]);k=next(i for i,t in enumerate(ts) if t[0]=='{');j=reader['pair'](ts,k)
 return source[a:a+ts[j][2]]

def provider():
 p=ROOT/'evidence/provider'
 t=types.ModuleType('toml');t.loads=tomllib.loads;sys.modules['toml']=t
 c=types.ModuleType('counted_unknown_properties');c.__dict__.update(load(p/'counted_unknown_properties.py'));sys.modules['counted_unknown_properties']=c
 d=load(p/'data.py')['PropertiesData']('gecko')
 groups=sorted(d.logical_groups);ids={x.name:i for i,x in enumerate(d.longhands)}
 rows=[{'id':i,'name':x.name,'group':groups.index(x.logical_group) if x.logical_group else None,'logical':x.logical,'content':x.enabled_in_content(),'pref':bool(x.gecko_pref)} for i,x in enumerate(d.longhands)]
 all_ids=[ids[x.name] for x in d.shorthands_by_name['all'].sub_properties]
 shorthands={s.name:[ids[x.name] for x in s.sub_properties] for s in d.shorthands}
 assert len(all_ids)==len(set(all_ids)) and ids['direction'] not in all_ids and ids['unicode-bidi'] not in all_ids
 out='static META:&[Meta]=&[\n'+''.join('Meta{name:'+json.dumps(r['name'])+',group:'+('None' if r['group'] is None else f"Some({r['group']})")+',logical:'+str(r['logical']).lower()+',content:'+str(r['content']).lower()+',pref:'+str(r['pref']).lower()+'},\n' for r in rows)+'];\n'
 out+='static ALL_IDS:&[LonghandId]=&['+','.join(f'LonghandId({i})' for i in all_ids)+'];\n'
 out+='static SHORTHANDS:&[&[LonghandId]]=&['+','.join('&['+','.join(f'LonghandId({i})' for i in ids)+']' for ids in shorthands.values())+'];\n'
 out+=f'mod property_counts {{pub const ALL_SHORTHAND_EXPANDED:usize={len(all_ids)};pub const MAX_SHORTHAND_EXPANDED:usize={max(len(x) for k,x in shorthands.items() if k!="all")};}}\n'
 return out,{'longhands':rows,'all':all_ids,'shorthands':shorthands,'groups':groups}

def extract(variant):
 source=(ROOT/'evidence'/f'declaration_block.{variant}.rs').read_text()
 props=(ROOT/'evidence/static/evidence/source/servo/components/style/properties/mod.rs').read_text()
 records=[]
 def get(src,anchor,start=0):
  body=item(src,anchor,start);records.append({'source_file':f'evidence/declaration_block.{variant}.rs' if src is source else 'evidence/static/evidence/source/servo/components/style/properties/mod.rs','anchor':anchor,'start':src.index(anchor,start),'sha256':hashlib.sha256(body.encode()).hexdigest(),'body':body});return body
 parts=[]
 for anchor,derive in [('enum DeclarationUpdate','#[derive(Clone,Copy,Debug,Eq,PartialEq)]'),('pub struct SourcePropertyDeclarationUpdate','#[derive(Default)]'),('pub enum Importance','#[derive(Clone,Copy,Debug,Eq,PartialEq,Default)]'),('pub struct PropertyDeclarationIdSet','#[derive(Clone,Debug,Default)]'),('pub struct PropertyDeclarationBlock','')]:
  parts.append(derive+'\n'+get(source,anchor))
 parts.append(get(source,'impl Importance'))
 start=source.index('impl PropertyDeclarationIdSet')
 parts.append('impl PropertyDeclarationIdSet{'+''.join(get(source,'pub fn '+n+'(',start) for n in ['insert','contains','remove','clear','is_empty'])+'}')
 start=source.index('impl PropertyDeclarationBlock')
 names=['len','new','contains','get','declaration_importance_iter','extend','push','prepare_for_update','update','first_declaration_to_remove','remove_declaration_at','clear','remove_property']
 if variant=='candidate':names.insert(7,'declaration_update')
 parts.append('impl PropertyDeclarationBlock{'+''.join(get(source,('fn ' if n in ['remove_declaration_at','declaration_update'] else 'pub fn ')+n+'(',start) for n in names)+'}')
 for anchor in ["pub struct DeclarationImportanceIterator", "impl<'a> DeclarationImportanceIterator", "impl<'a> Iterator for DeclarationImportanceIterator"]:parts.append(get(source,anchor))
 for anchor,derive in [('pub enum CSSWideKeyword','#[derive(Clone,Copy,Debug,PartialEq,Eq)]'),('pub enum AllShorthand','#[derive(Default,Clone,Debug)]'),('impl AllShorthand',''),('pub struct AllShorthandDeclarationIterator',''),("impl<'a> Iterator for AllShorthandDeclarationIterator",''),('pub struct NonCustomPropertyIterator',''),('impl<Item> Iterator for NonCustomPropertyIterator',''),('pub struct SourcePropertyDeclaration {','#[derive(Default)]'),('impl SourcePropertyDeclaration {',''),("pub struct SourcePropertyDeclarationDrain<'a>",'')]:parts.append(derive+'\n'+get(props,anchor))
 return '\n'.join(parts),records

def build(out):
 out.mkdir(parents=True,exist_ok=True)
 old=(ROOT/'evidence/declaration_block.original.rs').read_text();new=(ROOT/'evidence/declaration_block.candidate.rs').read_text()
 a=old.index('.map(|declaration| {',old.index('pub fn prepare_for_update'))+len('.map(|declaration| ')
 b=new.index('{',new.index('fn declaration_update('))
 old_body=item(old,'{',a);new_body=item(new,'{',b)
 assert [t[0] for t in reader['tokens'](old_body)]==[t[0] for t in reader['tokens'](new_body)]
 meta,pr=provider();(out/'PROVIDERS.json').write_text(json.dumps(pr,indent=2)+'\n')
 for variant in ['original','candidate','mutant_legacy_update','mutant_legacy_gate','mutant_no_order','mutant_importance','mutant_move_bits','mutant_membership']:
  body,records=extract('original' if variant=='original' else 'candidate')
  mutations=[]
  def replace_once(old,new):
   nonlocal body
   assert body.count(old)==1,(variant,old,body.count(old))
   body=body.replace(old,new);mutations.append({'old':old,'new':new})
  if variant in ['mutant_legacy_update','mutant_legacy_gate']:
   name='update' if variant=='mutant_legacy_update' else 'prepare_for_update'
   old=(ROOT/'evidence/declaration_block.original.rs').read_text()
   original=item(old,'pub fn '+name+'(')
   candidate=item(body,'pub fn '+name+'(')
   if name=='update':
    a=candidate.index('        if !matches!(drain.all_shorthand');z=candidate.index('        self.declarations.reserve(updates.new_count);')
    oa=original.index('        if !matches!(drain.all_shorthand');oz=original.index('        self.declarations.reserve(updates.new_count);')
   else:
    a=candidate.index('        if !matches!(source_declarations');z=candidate.index('        // Fill `updates`')
    oa=original.index('        if !matches!(source_declarations');oz=original.index('        // Fill `updates`')
   replace_once(candidate,candidate[:a]+original[oa:oz]+candidate[z:])
  elif variant=='mutant_no_order':replace_once('if needs_append {','if false && needs_append {')
  elif variant=='mutant_importance':
   helper=item(body,'pub fn update(');replace_once(helper,helper.replace('self.declarations_importance.set(pos, important);','self.declarations_importance.set(pos, true);',1))
  elif variant=='mutant_move_bits':
   helper=item(body,'pub fn update(');replace_once(helper,helper.replace('self.declarations_importance.remove(pos);','',1))
  elif variant=='mutant_membership':
   helper=item(body,'pub fn update(');replace_once(helper,helper.replace('self.property_ids.insert(decl.id());','',1))
  (out/f'{variant}-mutation.json').write_text(json.dumps(mutations,indent=2)+'\n')
  (out/f'{variant}-extraction.json').write_text(json.dumps(records,indent=2)+'\n')
  src=(ROOT/'native/facade.rs').read_text()+meta+body+(ROOT/'native/driver.rs').read_text()
  (out/f'{variant}.rs').write_text(src)
if __name__=='__main__':build(Path(sys.argv[1]))
