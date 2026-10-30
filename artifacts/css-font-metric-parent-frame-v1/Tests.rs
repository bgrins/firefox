#[derive(Debug,Eq,PartialEq)]struct Outcome{events:Vec<String>,values:Vec<(String,String,bool)>,attrs:usize}
fn execute(vars:Vec<(&str,Value)>,root:&str,eager:bool,pause:bool,attrs:HashMap<Name,Value>)->Outcome{
 let mut stylist=Stylist::default();let mut computed=ComputedContext::default();
 for (name,value) in vars {if !name.starts_with('u'){stylist.registered.insert(name.into(),PropertyDescriptors{syntax:Some(Syntax{components:vec![]})});}computed.builder.substitution_functions.vars.insert(name.into(),value);}
 let mut tracker=AttributeTracker{raw:attrs,..Default::default()};let refs=NonCustomPropertyReferences::default();
 let mut context=Context::new(&stylist,&mut computed);let var=VarType::Custom(root.into());
 if eager {assert!(matches!(traverse(var,&refs,&mut context,&mut tracker),VisitResult::Complete|VisitResult::CycleSettled));}
 else {
  let mut paused=HashSet::new();let mut count=0;
  loop {
   count+=1;assert!(count<100);
   let result=context.poll_root(var.clone(),&refs,&mut tracker,&mut |v| !pause || !paused.insert(format!("{v:?}")));
   if matches!(result,VisitResult::Complete|VisitResult::CycleSettled){break;}
   assert!(matches!(result,VisitResult::ComputationPending(_)));
   assert_eq!(context.frame_root.as_ref(),Some(&var));assert!(!context.frames.is_empty());
  }
 }
 context.reset();drop(context);
 let mut values:Vec<_>=computed.builder.substitution_functions.vars.into_iter().map(|(n,v)|(n,v.css,v.universal.is_some())).collect();values.sort();
 Outcome{events:computed.events,values,attrs:tracker.loads}
}
#[test]
fn all_three_node_dags_match_recursive_eager_before_and_after_suspension(){
 for mask in 0..8 {
  let mut graph=vec![];
  for i in 0..3 {let mut refs=vec![];for j in i+1..3 {let bit=match(i,j){(0,1)=>0,(0,2)=>1,_=>2};if mask&(1<<bit)!=0 {refs.push(reference(&format!("x{j}"),None));}}
   graph.push((format!("x{i}"),variable(&format!("v{i}"),refs,ReferenceFlags::VAR|ReferenceFlags::FONT)));
  }
  let input=|| graph.iter().map(|(n,v)|(n.as_str(),v.clone())).collect();
  let reference=execute(input(),"x0",true,false,HashMap::new());
  assert_eq!(reference,execute(input(),"x0",false,false,HashMap::new()),"eager mask {mask}");
  assert_eq!(reference,execute(input(),"x0",false,true,HashMap::new()),"suspended mask {mask}");
 }
}
#[test]
fn selected_preparation_and_fallback_order_are_retained(){
 let graph=vec![
  ("root",variable("color-root",vec![reference("missing",Some("u1")),reference("other-missing",Some("x2"))],ReferenceFlags::VAR|ReferenceFlags::COLOR_SCHEME)),
  ("u1",variable("alias",vec![reference("x3",None)],ReferenceFlags::VAR)),
  ("x2",variable("v2",vec![],ReferenceFlags::FONT)),
  ("x3",variable("v3",vec![],ReferenceFlags::FONT)),
 ];
 let expected=execute(graph.clone(),"root",true,false,HashMap::new());
 assert_eq!(expected,execute(graph.clone(),"root",false,false,HashMap::new()));
 assert_eq!(expected,execute(graph,"root",false,true,HashMap::new()));
 assert_eq!(expected.events.iter().filter(|e|*e=="prepare:root").count(),1);
 assert_eq!(expected.events.iter().filter(|e|*e=="prepared:root").count(),1);
}
#[test]
fn active_semantic_cycles_are_not_settled_certificates(){
 for graph in [
  vec![("root",variable("self",vec![reference("root",None)],ReferenceFlags::VAR))],
  vec![("root",variable("root",vec![reference("child",None)],ReferenceFlags::VAR)),("child",variable("child",vec![reference("root",Some("tail"))],ReferenceFlags::VAR)),("tail",variable("tail",vec![],ReferenceFlags::FONT))],
 ] {
  let expected=execute(graph.clone(),"root",true,false,HashMap::new());
  assert_eq!(expected,execute(graph.clone(),"root",false,false,HashMap::new()));
  assert_eq!(expected,execute(graph,"root",false,true,HashMap::new()));
 }
}
#[test]
fn attribute_fetch_and_parent_reference_cursor_survive_pause(){
 let mut attr=reference("data",None);attr.substitution_kind=SubstitutionFunctionKind::Attr;attr.attribute_data=AttrData{namespace:Some("ns".into()),typed:true,valid_non_type:true};
 let graph=vec![("root",variable("root",vec![attr],ReferenceFlags::ATTR)),("child",variable("child",vec![],ReferenceFlags::FONT))];
 let attrs=HashMap::from([("data".into(),variable("attribute",vec![reference("child",None)],ReferenceFlags::VAR))]);
 let expected=execute(graph.clone(),"root",true,false,attrs.clone());
 assert_eq!(expected.attrs,1);assert_eq!(expected,execute(graph,"root",false,true,attrs));
}
#[test]
fn post_pop_pending_keeps_parent_cursor_and_rejects_root_reset(){
 let mut stylist=Stylist::default();for n in ["root","child"]{stylist.registered.insert(n.into(),PropertyDescriptors{syntax:Some(Syntax{components:vec![]})});}
 let mut computed=ComputedContext::default();computed.builder.substitution_functions.vars=HashMap::from([
  ("root".into(),variable("root",vec![reference("child",None)],ReferenceFlags::VAR)),
  ("child".into(),variable("child",vec![],ReferenceFlags::FONT)),
 ]);
 let mut c=Context::new(&stylist,&mut computed);let mut tracker=AttributeTracker::default();let refs=NonCustomPropertyReferences::default();let root=VarType::Custom("root".into());
 for _ in 0..2 {
  assert!(matches!(c.poll_root(root.clone(),&refs,&mut tracker,&mut |_|false),VisitResult::ComputationPending(_)));
  assert!(c.computed_context.events.is_empty());
  assert_eq!(c.frames.len(),3);
  assert_eq!(c.frames[0].lowlink,0);
  assert_eq!(c.frames[0].walk.as_ref().unwrap().current.as_ref().unwrap().1,0);
 }
 assert!(std::panic::catch_unwind(std::panic::AssertUnwindSafe(||c.reset())).is_err());
 assert!(std::panic::catch_unwind(std::panic::AssertUnwindSafe(||c.poll_root(VarType::Custom("other".into()),&refs,&mut tracker,&mut |_|true))).is_err());
 assert!(matches!(c.poll_root(root,&refs,&mut tracker,&mut |_|true),VisitResult::Complete));
 assert!(c.frames.is_empty()&&c.frame_root.is_none());c.reset();
}
#[test]
fn multiple_unit_links_and_line_height_order_match_eager(){
 let graph=vec![("root",variable("color-metric",vec![],ReferenceFlags::FONT|ReferenceFlags::LH|ReferenceFlags::COLOR_SCHEME))];
 let expected=execute(graph.clone(),"root",true,false,HashMap::new());
 assert_eq!(expected,execute(graph.clone(),"root",false,false,HashMap::new()));
 assert_eq!(expected,execute(graph,"root",false,true,HashMap::new()));
}
#[test]
fn reply_identity_and_semantic_open_certificate_are_explicit(){
 let mut stylist=Stylist::default();stylist.registered.insert("root".into(),PropertyDescriptors{syntax:Some(Syntax{components:vec![]})});
 let mut computed=ComputedContext::default();computed.builder.substitution_functions.vars.insert("root".into(),variable("root",vec![reference("root",None)],ReferenceFlags::VAR));
 let mut c=Context::new(&stylist,&mut computed);let mut tracker=AttributeTracker::default();let root=VarType::Custom("root".into());
 let mut frame=match start_frame(root.clone(),&mut c,&mut tracker){Ok(f)=>f,Err(_)=>panic!("frame")};
 frame.link(root.clone(),LinkPurpose::Reference);
 assert!(!frame.receive(VarType::Custom("other".into()),VisitResult::SemanticOpen(0),&c));
 assert!(!frame.receive(root.clone(),VisitResult::ComputationPending(0),&c));
 assert!(frame.waiting.is_some()&&frame.reference_reply.is_none());
 assert!(frame.receive(root,VisitResult::SemanticOpen(0),&c));
 assert!(matches!(frame.reference_reply,Some((_,ReferenceReadiness::SemanticOpen))));
 assert!(frame.self_ref);
}
