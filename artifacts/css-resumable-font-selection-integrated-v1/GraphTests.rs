struct Driver{engine:ResumableSubstitution<'static>,request:Option<SubstitutionLookup>,floor:usize}
impl Driver{
 fn new(css:&str,url:u8)->Self{Self{engine:ResumableSubstitution::new(tokens(css,url),None,false),request:None,floor:0}}
 fn poll(&mut self,c:&mut Context,t:&mut AttributeTracker)->Option<Result<String,()>>{
  let mut reply=None;
  for _ in 0..100000{
   if let Some(request)=self.request.as_ref(){
    let mut value=if c.frames.is_empty(){c.owned_lookup_value(request,t).unwrap()}else{None};
    if value.is_none(){
     if c.frames.is_empty(){
      self.floor=c.var_info.len();let target=VarType::Custom(request.name.clone());
      let mut frame=match start_frame(target.clone(),c,t){Ok(f)=>f,Err(VisitResult::ComputationPending(_))=>return None,Err(_)=>panic!("unjoined root")};
      frame.enter_guarded_custom(request.guards.clone(),c);c.frames.push(frame);c.frame_root=Some(target);
     }
     let result=c.poll_frames(&NonCustomPropertyReferences,t,&mut|_,_,_|PublicationDemand::Ready,0,self.floor,request.attribute_attempt.as_ref());
     if !matches!(result,VisitResult::Complete|VisitResult::CycleSettled){return None}
     value=c.owned_lookup_value(request,t).unwrap();
    }
    reply=Some(SubstitutionLookupReply{identity:request.identity.clone(),value:value.unwrap()});self.request=None;
   }
   match self.engine.poll(reply.take()){
    SubstitutionPoll::Lookup(r)=>self.request=Some(r),
    SubstitutionPoll::Complete(v)=>return Some(v.map(|v|v.css.into_owned())),
    _=>panic!("wrong driver state"),
   }
  }panic!("finite test driver exhausted")
 }
}
fn raw(t:&mut AttributeTracker,n:&str,s:&str){t.values.insert(n.into(),s.into());}
fn result(c:&Context,n:&str)->Option<String>{c.lookup_bindings.values.get(n).and_then(|v|v.as_ref()).map(|v|v.value.css.clone())}
#[test]fn reached_attribute_custom_frontier_finishes_with_actual_body_parser(){
 let mut c=Context::new();let mut t=AttributeTracker::default();raw(&mut t,"a","var(--b)");raw(&mut t,"x","20px");c.add("b","attr(x type(<length>))",2,true);
 let mut d=Driver::new("attr(a type(<length>))",1);assert_eq!(d.poll(&mut c,&mut t),Some(Ok("20px".into())));
 assert_eq!(result(&c,"b"),Some("20px".into()));assert_eq!(c.published,vec!["b"]);assert_eq!(t.queries,vec![":a",":x"]);assert_eq!(c.computed_context.computations,vec!["20px"]);
}
#[test]fn cross_url_registered_initial_does_not_clear_ancestor_attribute_mark(){
 let mut c=Context::new();let mut t=AttributeTracker::default();raw(&mut t,"a","var(--b)");c.add("b","attr(a type(<length>), 9px)",2,true);
 let mut d=Driver::new("attr(a type(<length>), 1px)",1);assert_eq!(d.poll(&mut c,&mut t),Some(Ok("1px".into())));
 assert_eq!(result(&c,"b"),Some("8px".into()));assert_eq!(c.published,vec!["b"]);assert_eq!(t.queries.len(),1);
 assert!(matches!(c.var_info[0].publication.readiness(),NodeReadiness::CycleSettled));
 let mut next=Driver::new("attr(a type(<length>), 1px)",2);assert_eq!(next.poll(&mut c,&mut t),Some(Ok("8px".into())));assert_eq!(c.published,vec!["b"]);
}
#[test]fn valid_primary_avoids_unused_self_fallback_for_registered_and_unregistered(){
 for registered in [false,true]{let mut c=Context::new();let mut t=AttributeTracker::default();raw(&mut t,"a","var(--b)");c.add("b","var(--ready,var(--b))",2,registered);c.lookup_bindings.values.insert("ready".into(),Some(ComputedRegisteredValue::universal(Arc::new(tokens("1px",0)))));
 let mut d=Driver::new("attr(a type(<length>))",1);assert_eq!(d.poll(&mut c,&mut t),Some(Ok("1px".into())));assert_eq!(result(&c,"b"),Some("1px".into()));assert!(matches!(c.var_info[0].publication.readiness(),NodeReadiness::Complete));}
}
#[test]fn invalid_primary_reaches_self_fallback_and_settles_registered_default(){
 let mut c=Context::new();let mut t=AttributeTracker::default();raw(&mut t,"a","var(--b)");c.add("b","var(--missing,var(--b))",2,true);
 let mut d=Driver::new("attr(a type(<length>))",1);assert_eq!(d.poll(&mut c,&mut t),Some(Ok("8px".into())));assert!(matches!(c.var_info[0].publication.readiness(),NodeReadiness::CycleSettled));
}
#[test]fn child_local_custom_scc_settles_before_parent_consumption(){
 let mut c=Context::new();let mut t=AttributeTracker::default();raw(&mut t,"a","var(--b)");c.add("b","var(--c)",2,true);c.add("c","var(--b)",3,true);
 let mut d=Driver::new("attr(a type(<length>))",1);assert_eq!(d.poll(&mut c,&mut t),Some(Ok("8px".into())));assert_eq!(result(&c,"b"),Some("8px".into()));assert_eq!(result(&c,"c"),Some("8px".into()));assert_eq!(c.published.len(),2);
}
#[test]fn scheduler_pause_retains_exact_request_and_does_not_select_fallback(){
 let mut c=Context::new();let mut t=AttributeTracker::default();raw(&mut t,"a","var(--b)");raw(&mut t,"x","var(--c,99px)");c.add("b","attr(x type(<length>))",2,true);c.add("c","7px",3,true);c.blocked.insert("c".into());
 let mut d=Driver::new("attr(a type(<length>), 2px)",1);assert_eq!(d.poll(&mut c,&mut t),None);let identity=c.frames[0].guarded_custom.as_ref().unwrap().request.as_ref().unwrap().identity.clone();assert_eq!(t.queries.len(),2);assert!(c.published.is_empty());assert_eq!(d.poll(&mut c,&mut t),None);assert!(Arc::ptr_eq(&identity,&c.frames[0].guarded_custom.as_ref().unwrap().request.as_ref().unwrap().identity));c.blocked.clear();assert_eq!(d.poll(&mut c,&mut t),Some(Ok("7px".into())));assert_eq!(t.queries.len(),2);
}
#[test]fn registered_output_units_remain_pending_until_separate_readiness(){
 let mut c=Context::new();let mut t=AttributeTracker::default();raw(&mut t,"a","var(--b)");raw(&mut t,"x","1em");c.add("b","attr(x type(<length>))",2,true);
 let mut d=Driver::new("attr(a type(<length>))",1);assert_eq!(d.poll(&mut c,&mut t),None);assert!(c.frames[0].value_non_custom_refs.intersects(ReferenceFlags::FONT_UNITS));assert_eq!(c.unit_visits,vec![SingleNonCustomReference::FontUnits]);assert!(matches!(c.frames[0].waiting,Some((VarType::NonCustom(SingleNonCustomReference::FontUnits),LinkPurpose::Unit))));assert!(c.published.is_empty());c.unit_ready=true;assert_eq!(d.poll(&mut c,&mut t),Some(Ok("1em".into())));assert_eq!(t.queries.len(),2);
}
#[test]fn changed_generation_or_flags_cannot_resume_guarded_body(){
 for generation in [false,true]{let mut c=Context::new();let mut t=AttributeTracker::default();raw(&mut t,"a","var(--b)");c.add("b","var(--c)",2,true);c.add("c","7px",2,true);c.blocked.insert("c".into());let mut d=Driver::new("attr(a type(<length>))",1);assert!(d.poll(&mut c,&mut t).is_none());if generation{c.lookup_bindings.root=Arc::new(())}else{c.computed_context.included_cascade_flags=1;c.lookup_bindings.flags=1}c.blocked.clear();assert!(d.poll(&mut c,&mut t).is_none());assert!(!c.published.contains(&"b".into()));}
}
#[test]fn foreign_semantic_root_is_wait_not_cycle_or_fallback(){
 let mut c=Context::new();let mut t=AttributeTracker::default();c.add("outer","4px",0,true);let frame=start_frame(VarType::Custom("outer".into()),&mut c,&mut t).unwrap();drop(frame);raw(&mut t,"a","var(--b)");c.add("b","var(--outer,99px)",2,true);
 let mut d=Driver::new("attr(a type(<length>),2px)",1);assert_eq!(d.poll(&mut c,&mut t),None);assert_eq!(d.poll(&mut c,&mut t),None);assert!(c.published.is_empty());assert!(matches!(c.var_info[0].publication.readiness(),NodeReadiness::SemanticOpen));assert!(!c.frames[0].guarded_custom.as_ref().unwrap().substitution.body_marked());
}
#[test]fn custom_attribute_alternation_is_iterative_on_small_stack(){
 std::thread::Builder::new().stack_size(256*1024).spawn(||{
 let mut c=Context::new();let mut t=AttributeTracker::default();for i in 0..256{raw(&mut t,&format!("a{i}"),&format!("var(--b{i})"));c.add(&format!("b{i}"),&if i==255{"7px".into()}else{format!("attr(a{} type(<length>))",i+1)},0,true);}
 let mut d=Driver::new("attr(a0 type(<length>))",0);assert_eq!(d.poll(&mut c,&mut t),Some(Ok("7px".into())));assert_eq!(c.published.len(),256);assert_eq!(t.queries.len(),256);
 }).unwrap().join().unwrap();
}
#[test]fn actual_metric_lookup_entry_attaches_guards_and_preserves_outer_owner(){
 for recurrent in [false,true]{
 let mut c=Context::new();let mut t=AttributeTracker::default();raw(&mut t,"a","var(--b)");raw(&mut t,"x","20px");c.add("b",if recurrent{"attr(a type(<length>),9px)"}else{"attr(x type(<length>))"},2,true);
 let mut engine=ResumableSubstitution::new(tokens("attr(a type(<length>),1px)",1),None,false);let mut reply=None;
 let request=loop{let SubstitutionPoll::Lookup(r)=engine.poll(reply.take())else{panic!()};if r.kind==SubstitutionLookupKind::Variable{break r}reply=Some(SubstitutionLookupReply{identity:r.identity.clone(),value:c.owned_lookup_value(&r,&mut t).unwrap().unwrap()});};
 let owner=VarType::NonCustom(SingleNonCustomReference::FontUnits);c.var_info.push(VarInfo{var:None,lowlink:0,publication:NodePublication::Pending(ClosedValue::Prioritary(PrioritaryPropertyId))});
 c.frames.push(TraversalFrame{guarded_custom:None,var:owner.clone(),index:0,lowlink:0,self_ref:false,phase:FramePhase::Publish,waiting:None,reference_reply:None,prepared_custom:None,value:None,value_non_custom_refs:ReferenceFlags::empty(),unit_cursor:0,registered:false,unit_links:vec![]});
 let action=MetricAction{identity:Arc::new(()),root:owner.clone(),owner:owner.clone(),index:0,prerequisite:FontTarget::Metric};c.metric_action=Some(action.clone());c.frame_root=Some(owner.clone());
 let raw=Arc::new(tokens("var(--b)",1));let state=MetricLookup{action,flags:0,generation:c.lookup_bindings.root.clone(),depth:1,semantic_floor:1,request,longhand:0,value:raw.clone()};
 assert_eq!(c.resolve_metric_lookup_inner(&state,&NonCustomPropertyReferences,&mut t,&mut|_,_,_|PublicationDemand::Ready),Ok(true));assert_eq!(c.frames.len(),1);assert_eq!(c.frame_root,Some(owner));
 let (_,answer)=c.lookup_reply.take().unwrap();assert!(Arc::ptr_eq(&raw,&answer.value));let SubstitutionPoll::Complete(Ok(value))=engine.poll(answer.lookup)else{panic!()};assert_eq!(value.css,if recurrent{"1px"}else{"20px"});assert_eq!(c.published,vec!["b"]);
 }
}
#[test]fn actual_ordinary_custom_root_enters_guard_before_legacy_attribute_cycle(){
 let mut c=Context::new();let mut t=AttributeTracker::default();raw(&mut t,"a","20px");c.add("b","attr(a type(<length>))",2,true);
 c.indices.insert(VarType::Attr("a".into(),String::new()),0);c.var_info.push(VarInfo{var:None,lowlink:0,publication:NodePublication::CycleSettled});
 assert!(matches!(c.poll_root(VarType::Custom("b".into()),&NonCustomPropertyReferences,&mut t,&mut|_,_,_|PublicationDemand::Ready),VisitResult::Complete));assert_eq!(result(&c,"b"),Some("20px".into()));assert_eq!(c.published,vec!["b"]);assert!(c.frame_root.is_none());
}
#[test]fn actual_ordinary_custom_root_keeps_property_and_attribute_cycle_marks(){
 let mut c=Context::new();let mut t=AttributeTracker::default();raw(&mut t,"a","var(--b)");c.add("b","attr(a type(<length>), 9px)",2,true);
 assert!(matches!(c.poll_root(VarType::Custom("b".into()),&NonCustomPropertyReferences,&mut t,&mut|_,_,_|PublicationDemand::Ready),VisitResult::CycleSettled));assert_eq!(result(&c,"b"),Some("8px".into()));assert_eq!(c.published,vec!["b"]);
}
#[test]fn ordinary_and_custom_property_guard_identities_are_distinct(){
 let custom=SubstitutionGuard::new(SubstitutionGuardKey::Property(PropertyId::Custom("font-size".into())));assert!(!SubstitutionGuard::mark_reentry(&[custom.clone()],&SubstitutionGuardKey::Property(PropertyId::NonCustom(0))));assert!(!custom.marked());
}
