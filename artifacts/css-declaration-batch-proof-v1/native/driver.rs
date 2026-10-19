fn key(name:&str)->usize{META.iter().position(|x|x.name==name).unwrap()}
fn plain(id:usize,v:u16)->PropertyDeclaration{if id<META.len(){PropertyDeclaration::Ordinary(LonghandId(id),v)}else{PropertyDeclaration::Custom((id-META.len())as u16,v)}}
fn importance(x:bool)->Importance{if x{Importance::Important}else{Importance::Normal}}
fn state(b:&PropertyDeclarationBlock)->String{b.declarations.iter().enumerate().map(|(i,d)|format!("{}:{}:{}",d.id().key(),d.payload(),usize::from(b.declarations_importance.get(i).copied().unwrap_or(false)))).collect::<Vec<_>>().join(",")}
fn rawbits(b:&PropertyDeclarationBlock)->String{b.declarations_importance.iter().map(|x|if x{'1'}else{'0'}).collect()}
fn rawset(b:&PropertyDeclarationBlock)->String{b.property_ids.longhands.0.iter().map(|x|x.0).chain(b.property_ids.custom.iter().map(|x|META.len()+usize::from(*x))).map(|x|x.to_string()).collect::<Vec<_>>().join(",")}
fn plans(u:&SourcePropertyDeclarationUpdate)->String{u.updates.iter().map(|p|match p{DeclarationUpdate::None=>"N".into(),DeclarationUpdate::Append=>"A".into(),DeclarationUpdate::UpdateInPlace{pos}=>format!("R{pos}"),DeclarationUpdate::AppendAndRemove{pos}=>format!("M{pos}")}).collect::<Vec<_>>().join(",")}
fn source_rows(source:&SourcePropertyDeclaration,imp:bool)->String{source.declarations.iter().map(|d|format!("{}:{}:{}",d.id().key(),d.payload(),usize::from(imp))).collect::<Vec<_>>().join(",")}
fn call(name:&str,entries:&[(usize,u16,bool)],actionids:&[usize],value:u16,imp:bool){
 let mut block=PropertyDeclarationBlock::new();
 for &(k,v,i) in entries{block.push(plain(k,v),importance(i));}
 let before=state(&block);let beforebits=rawbits(&block);let beforeset=rawset(&block);
 let mut source=SourcePropertyDeclaration::default();for id in actionids{source.push(plain(*id,value));}
 let actions=source_rows(&source,imp);let mut updates=SourcePropertyDeclarationUpdate::default();
 let gate=block.prepare_for_update(&source,importance(imp),&mut updates);let initialplans=plans(&updates);let newcount=updates.new_count;let removal=updates.any_removal;
 let result=std::panic::catch_unwind(std::panic::AssertUnwindSafe(||{if gate{block.update(source.drain(),importance(imp),&mut updates);}}));
 let endplans=plans(&updates);
 println!("ROW\t{name}\t{}\t{}\t{}\t{}\t{before}\t{beforebits}\t{beforeset}\t{actions}\t{initialplans}\t{}\t{}\t{}\t{endplans}",usize::from(gate),newcount,usize::from(removal),usize::from(result.is_ok()),state(&block),rawbits(&block),rawset(&block));
}
fn main(){
 std::panic::set_hook(Box::new(|_|{}));
 let p=key("padding-top");let q=key("padding-right");let r=key("padding-bottom");let s=key("padding-left");let l=key("padding-block-start");let c=key("color");let d=key("direction");let x=META.len()+7;
 let padding=SHORTHANDS.iter().find(|ids|ids.len()==4&&ids.iter().any(|k|k.0==p)&&ids.iter().any(|k|k.0==q)&&ids.iter().any(|k|k.0==r)&&ids.iter().any(|k|k.0==s)).unwrap().iter().map(|k|k.0).collect::<Vec<_>>();
 for imp in [false,true]{
  let cases:Vec<(&str,Vec<(usize,u16,bool)>,Vec<usize>,u16)>=vec![
   ("two-removals-rank",vec![(c,1,!imp),(p,2,imp),(q,3,!imp),(l,4,imp),(d,5,!imp),(x,6,true)],vec![p,q,c,d],9),
   ("rank-before-after",vec![(c,1,imp),(p,2,!imp),(d,3,imp),(q,4,!imp),(l,5,imp),(x,6,false)],vec![d,p,c,q],9),
   ("padding-provider",vec![(r,1,!imp),(c,2,imp),(p,3,imp),(q,4,!imp),(l,5,imp),(x,6,true)],padding.clone(),9),
   ("replacement-only",vec![(c,1,!imp),(d,2,imp),(x,3,false)],vec![d,c,x],9),
   ("absent-only",vec![(l,1,imp),(x,2,!imp)],vec![p,q,c],9),
   ("no-op",vec![(p,9,imp),(q,9,imp),(c,9,imp)],vec![q,c,p],9),
   ("move-unchanged",vec![(p,9,imp),(q,9,imp),(l,9,!imp),(c,9,imp)],vec![p,q,c],9),
   ("empty-source",vec![(p,1,imp),(l,2,!imp)],vec![],9),
   ("empty-destination",vec![],padding.clone(),9),
  ];
  for (name,entries,actions,v) in cases{call(&format!("{name}-{imp}"),&entries,&actions,v,imp);}
 }
}
