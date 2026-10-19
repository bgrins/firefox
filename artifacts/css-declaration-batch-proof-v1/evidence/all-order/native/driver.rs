#[derive(Clone,Debug,PartialEq,Eq)]
struct Row{key:usize,value:u32,important:bool}
fn rows(b:&PropertyDeclarationBlock)->Vec<Row>{b.declaration_importance_iter().map(|(d,p)|Row{key:d.id().key(),value:d.payload(),important:p.important()}).collect()}
fn opposite(a:usize,b:usize)->bool{if a>=META.len()||b>=META.len(){return false}let a=&META[a];let b=&META[b];a.group.is_some()&&a.group==b.group&&a.logical!=b.logical}
fn spec_set(mut old:Vec<Row>,new:Row)->Vec<Row>{
 if let Some(i)=old.iter().position(|d|d.key==new.key){
  if old[i+1..].iter().any(|d|opposite(new.key,d.key)){old.remove(i);old.push(new);}else{old[i]=new;}
 }else{old.push(new)}old
}
fn spec_push(mut old:Vec<Row>,new:Row)->Vec<Row>{
 if old.iter().any(|d|d.key==new.key&&d.important&&!new.important){return old}
 old.retain(|d|d.key!=new.key);old.push(new);old
}
fn invariant(b:&PropertyDeclarationBlock)->bool{
 if b.declarations.len()!=b.declarations_importance.len(){return false}
 let r=rows(b);let keys:BTreeSet<_>=r.iter().map(|x|x.key).collect();if keys.len()!=r.len(){return false}
 let actual:BTreeSet<_>=b.property_ids.longhands.0.iter().map(|x|x.0).chain(b.property_ids.custom.iter().map(|x|META.len()+usize::from(*x))).collect();if keys!=actual{return false}
 for d in &b.declarations{let Some((g,p))=b.get(d.id()) else{return false};if g!=d||p.important()!=r.iter().find(|x|x.key==d.id().key()).unwrap().important{return false}}
 true
}
fn oracle_all(all:&AllShorthand,i:bool)->Vec<Row>{
 let payload=match all{AllShorthand::NotSet=>return vec![],AllShorthand::CSSWideKeyword(k)=>*k as u32,AllShorthand::WithVariables(v)=>1000+u32::from(v.0)};
 ALL_IDS.iter().filter(|id|{let m=&META[id.0];m.content&&(!m.pref||match PREF_PROFILE.load(Ordering::Relaxed){0=>true,1=>false,_=>id.0%2==0})}).map(|id|Row{key:id.0,value:payload,important:i}).collect()
}
fn key(name:&str)->usize{META.iter().position(|x|x.name==name).unwrap()}
fn plain(k:usize,v:u16)->PropertyDeclaration{if k<META.len(){PropertyDeclaration::Ordinary(LonghandId(k),v)}else{PropertyDeclaration::Custom((k-META.len())as u16,v)}}
fn wide(k:usize,v:CSSWideKeyword)->PropertyDeclaration{PropertyDeclaration::css_wide_keyword(LonghandId(k),v)}
fn importance(v:bool)->Importance{if v{Importance::Important}else{Importance::Normal}}
fn seed(entries:&[(usize,u16,bool)])->PropertyDeclarationBlock{let mut b=PropertyDeclarationBlock::new();for &(k,v,i) in entries{b.push(plain(k,v),importance(i));}assert!(invariant(&b));b}
fn expansion(all:&AllShorthand)->Vec<PropertyDeclaration>{all.declarations().collect()}
fn row(d:&PropertyDeclaration,i:bool)->Row{Row{key:d.id().key(),value:d.payload(),important:i}}
fn call(name:&str,b:&mut PropertyDeclarationBlock,mut source:SourcePropertyDeclaration,i:bool){
 let before=rows(b);let mut actions:Vec<_>=source.declarations.iter().cloned().collect();actions.extend(expansion(&source.all_shorthand));
 let mut oracle:Vec<_>=source.declarations.iter().map(|d|row(d,i)).collect();oracle.extend(oracle_all(&source.all_shorthand,i));assert_eq!(actions.iter().map(|d|row(d,i)).collect::<Vec<_>>(),oracle);
 let mut expected=before.clone();let mut changed=false;for d in &oracle{let next=spec_set(expected.clone(),d.clone());changed|=next!=expected;expected=next;}
 let mut updates=SourcePropertyDeclarationUpdate::default();let gate=b.prepare_for_update(&source,importance(i),&mut updates);
 if gate{b.update(source.drain(),importance(i),&mut updates);}
 let consistent=invariant(b);let actual=rows(b);let ok=actual==expected&&gate==changed&&consistent;
 println!("ROW\t{name}\t{}\t{}\t{}\t{:?}\t{:?}\t{:?}\t{:?}\t{:?}\t{:?}\t{:?}",usize::from(ok),usize::from(gate),usize::from(changed),before,actual,expected,oracle,b.declarations_importance.0,b.property_ids.longhands.0,b.property_ids.custom);
 if !consistent{std::process::exit(42)}
}
fn all_source(v:u8)->SourcePropertyDeclaration{SourcePropertyDeclaration{declarations:vec![],all_shorthand:match v{0=>AllShorthand::CSSWideKeyword(CSSWideKeyword::Initial),1=>AllShorthand::CSSWideKeyword(CSSWideKeyword::Inherit),2=>AllShorthand::CSSWideKeyword(CSSWideKeyword::Unset),3=>AllShorthand::CSSWideKeyword(CSSWideKeyword::Revert),4=>AllShorthand::CSSWideKeyword(CSSWideKeyword::RevertLayer),5=>AllShorthand::CSSWideKeyword(CSSWideKeyword::RevertRule),_=>AllShorthand::WithVariables(Arc::new(UnparsedValue(17)))}}}
fn main(){
 let a=key("padding-top");let b=key("padding-block-start");let c=key("color");let d=key("direction");let u=key("unicode-bidi");let x=META.len()+7;
 for profile in 0..3{PREF_PROFILE.store(profile,Ordering::Relaxed);
  for v in 0..7{for imp in [false,true]{for order in 0..4{
   let entries=match order{0=>vec![],1=>vec![(a,1,!imp),(b,2,!imp)],2=>vec![(b,1,!imp),(a,2,!imp)],_=>vec![(a,1,!imp),(x,3,true),(c,2,false),(b,2,imp),(d,4,true),(u,5,false)]};
   let mut block=seed(&entries);call(&format!("all-{profile}-{v}-{imp}-{order}"),&mut block,all_source(v),imp);
   call(&format!("all-repeat-{profile}-{v}-{imp}-{order}"),&mut block,all_source(v),imp);
  }}}
 }
 PREF_PROFILE.store(0,Ordering::Relaxed);
 for ids in [[a,b],[b,a]]{for oldimp in [false,true]{for newimp in [false,true]{for value in [1,2]{
  let mut block=seed(&[(ids[0],1,oldimp),(x,8,true),(ids[1],1,oldimp)]);
  call(&format!("single-{:?}-{oldimp}-{newimp}-{value}",ids),&mut block,SourcePropertyDeclaration::with_one(plain(a,value)),newimp);
 }}}}
 for (idx,sub) in SHORTHANDS.iter().enumerate(){if sub.len()>property_counts::MAX_SHORTHAND_EXPANDED{continue}
  let mut block=seed(&[(a,1,true),(b,2,false),(c,3,true),(x,4,false)]);
  let mut source=SourcePropertyDeclaration::default();for id in sub.iter().copied(){source.push(plain(id.0,9));}
  call(&format!("ordinary-shorthand-{idx}"),&mut block,source,false);
  let prior=rows(&block);let property=PropertyId::Shorthand(ShorthandId::Selected(idx));let mut expected=prior.clone();expected.retain(|r|!sub.iter().any(|id|id.0==r.key));
  if let Some(first)=block.first_declaration_to_remove(&property){block.remove_property(&property,first);}
  assert!(invariant(&block));println!("REMOVE\t{idx}\t{}\t{:?}\t{:?}\t{:?}",usize::from(rows(&block)==expected),prior,rows(&block),sub);
 }
 for imp in [false,true]{let mut block=seed(&[(a,1,true),(b,2,false),(x,3,true)]);let old=rows(&block);let src=all_source(0);let actions=oracle_all(&src.all_shorthand,imp);let mut expected=old.clone();for decl in &actions{expected=spec_push(expected,decl.clone());}let mut src=src;block.extend(src.drain(),importance(imp));assert!(invariant(&block));println!("EXTEND\t{imp}\t{}\t{:?}\t{:?}\t{:?}",usize::from(rows(&block)==expected),old,rows(&block),actions);}
 let mut state:u64=0x91745;for case in 0..500{let mut rand=||{state=state.wrapping_mul(6364136223846793005).wrapping_add(1);(state>>32)as usize};let mut pool=vec![a,b,c,x,d,u,key("margin-left"),key("margin-inline-end"),key("padding-right"),key("padding-inline-start")];for i in (1..pool.len()).rev(){let j=rand()%(i+1);pool.swap(i,j);}let len=rand()%(pool.len()+1);let entries:Vec<_>=pool[..len].iter().map(|k|(*k,(rand()%3)as u16,rand()%2==0)).collect();let mut block=seed(&entries);for step in 0..5{let id=pool[rand()%pool.len()];let v=(rand()%3)as u16;let imp=rand()%2==0;call(&format!("sequence-{case}-{step}"),&mut block,SourcePropertyDeclaration::with_one(plain(id,v)),imp);}}
}
