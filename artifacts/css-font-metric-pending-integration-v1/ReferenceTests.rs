#[test]
fn pending_primary_cannot_select_fallback_or_advance() {
 let mut c=Context::default();let mut t=AttributeTracker::default();c.map.vars.insert("a".into(),unresolved());
 let mut w=ReferenceWalk::new(&root(vec![reference("a",Some("fallback")),reference("sibling",None)]));
 let a=target(next(&mut w,&mut c,&mut t,None));assert_eq!(a,VarType::Custom("a".into()));
 for _ in 0..4 {assert_eq!(target(next(&mut w,&mut c,&mut t,Some((a.clone(),ReferenceReadiness::ComputationPending)))),a);}
 c.map.vars.insert("a".into(),computed("20px"));
 assert_eq!(target(next(&mut w,&mut c,&mut t,Some((a,ReferenceReadiness::Ready)))),VarType::Custom("sibling".into()));
 assert!(matches!(next(&mut w,&mut c,&mut t,Some((VarType::Custom("sibling".into()),ReferenceReadiness::Ready))),ReferenceWalkStep::Complete));
}

#[test]
fn fallback_queue_keeps_original_sibling_then_lifo_order() {
 let mut c=Context::default();let mut t=AttributeTracker::default();let mut w=ReferenceWalk::new(&root(vec![reference("a",Some("b")),reference("c",Some("d"))]));
 let mut names=Vec::new();let mut response=None;
 loop {match next(&mut w,&mut c,&mut t,response.take()) {ReferenceWalkStep::Link(v)=>{names.push(v.clone());response=Some((v,ReferenceReadiness::Ready));},ReferenceWalkStep::Complete=>break,_=>panic!()}}
 assert_eq!(names,vec!["a","c","d","b"].into_iter().map(|n|VarType::Custom(n.into())).collect::<Vec<_>>());
 assert_eq!(w.flags,ReferenceFlags(3));
}

#[test]
fn typed_attribute_is_loaded_once_across_pending_replies() {
 let mut c=Context::default();let mut t=AttributeTracker::default();t.raw.insert("data".into(),unresolved());
 let mut r=reference("data",Some("fallback"));r.substitution_kind=SubstitutionFunctionKind::Attr;r.attribute_data=AttrData{namespace:Some("length".into()),typed:true,valid_non_type:false};
 let mut w=ReferenceWalk::new(&root(vec![r]));let key=target(next(&mut w,&mut c,&mut t,None));assert_eq!(t.loads,1);
 for _ in 0..4 {assert_eq!(target(next(&mut w,&mut c,&mut t,Some((key.clone(),ReferenceReadiness::ComputationPending)))),key);}
 assert_eq!(t.loads,1);c.map.attrs.insert(("data".into(),"length".into()),computed("20px"));
 assert!(matches!(next(&mut w,&mut c,&mut t,Some((key,ReferenceReadiness::Ready))),ReferenceWalkStep::Complete));assert_eq!(t.loads,1);
}

#[test]
fn wrong_reply_retains_cursor_and_settled_cycle_visits_fallback() {
 let mut c=Context::default();let mut t=AttributeTracker::default();c.map.vars.insert("a".into(),unresolved());
 let mut w=ReferenceWalk::new(&root(vec![reference("a",Some("b"))]));let a=target(next(&mut w,&mut c,&mut t,None));
 assert!(matches!(next(&mut w,&mut c,&mut t,Some((VarType::Custom("wrong".into()),ReferenceReadiness::Ready))),ReferenceWalkStep::WrongReply));
 assert_eq!(target(next(&mut w,&mut c,&mut t,None)),a);
 c.map.vars.remove("a");
 assert_eq!(target(next(&mut w,&mut c,&mut t,Some((a,ReferenceReadiness::SemanticCycle)))),VarType::Custom("b".into()));
}

#[test]
fn invalid_typed_primary_visits_fallback_after_ready_only() {
 let mut c=Context::default();let mut t=AttributeTracker::default();t.raw.insert("data".into(),computed("bad"));let mut r=reference("data",Some("b"));r.substitution_kind=SubstitutionFunctionKind::Attr;r.attribute_data=AttrData{namespace:Some("length".into()),typed:true,valid_non_type:false};let mut w=ReferenceWalk::new(&root(vec![r]));let a=target(next(&mut w,&mut c,&mut t,None));
 assert_eq!(target(next(&mut w,&mut c,&mut t,Some((a.clone(),ReferenceReadiness::ComputationPending)))),a);
 assert_eq!(target(next(&mut w,&mut c,&mut t,Some((a,ReferenceReadiness::Ready)))),VarType::Custom("b".into()));
}
