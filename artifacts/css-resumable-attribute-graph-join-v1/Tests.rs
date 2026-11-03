fn run(c:&mut Context,depth:usize,floor:usize,guard:Option<&Arc<()>>)->VisitResult{c.poll_frames(&NonCustomPropertyReferences,&mut AttributeTracker,&mut|_,_,_|PublicationDemand::Ready,depth,floor,guard)}
fn push(c:&mut Context,n:&str){let f=start_frame(VarType::Custom(n.into()),c,&mut AttributeTracker).unwrap_or_else(|_|panic!());c.frames.push(f);}
#[test]fn child_custom_alias_produces_value_without_changing_parent(){
 let mut c=Context::new();c.add("outer",&[],99);push(&mut c,"outer");c.frame_root=Some(VarType::Custom("outer".into()));c.add("b",&["c"],20);c.add("c",&[],30);push(&mut c,"b");let guard=Arc::new(());
 assert_eq!(run(&mut c,1,1,Some(&guard)),VisitResult::Complete);assert_eq!(c.frames.len(),1);assert_eq!(c.frames[0].var,VarType::Custom("outer".into()));assert_eq!(c.frame_root,Some(VarType::Custom("outer".into())));assert_eq!(c.computed_context.builder.substitution_functions.vars["b"].n,20);assert_eq!(c.published,vec!["c","b"]);assert_eq!(c.stack,vec![0]);
}
#[test]fn reached_attribute_blocks_before_global_cache_or_semantic_reply(){
 let mut c=Context::new();c.add("outer",&[],99);push(&mut c,"outer");c.add("b",&["attr:a"],20);push(&mut c,"b");let guard=Arc::new(());
 assert_eq!(run(&mut c,1,1,Some(&guard)),VisitResult::ComputationPending(1));assert!(c.published.is_empty());assert!(!c.starts.iter().any(|v|matches!(v,VarType::Attr(..))));assert_eq!(c.frames.len(),2);
 c.frame_reply=Some((VarType::Attr("a".into(),String::new()),VisitResult::CycleSettled));
 assert_eq!(run(&mut c,1,1,Some(&guard)),VisitResult::ComputationPending(1));assert!(c.frame_reply.is_some());assert_eq!(c.frames[1].lowlink,1);assert_eq!(c.stack,vec![0,1]);
}
#[test]fn true_child_custom_cycle_uses_actual_cycle_close_and_registered_initial(){
 let mut c=Context::new();c.add("outer",&[],99);push(&mut c,"outer");c.add("b",&["c"],20);c.add("c",&["b"],30);push(&mut c,"b");let guard=Arc::new(());
 assert_eq!(run(&mut c,1,1,Some(&guard)),VisitResult::CycleSettled);assert_eq!(c.stack,vec![0]);assert_eq!(c.frames.len(),1);
 for n in ["b","c"]{assert_eq!(c.computed_context.builder.substitution_functions.vars[n].n,8);assert_eq!(c.published.iter().filter(|p|p.as_str()==n).count(),1);}
}
#[test]fn foreign_open_root_is_pending_not_new_semantic_cycle(){
 let mut c=Context::new();c.add("outer",&[],99);push(&mut c,"outer");c.add("b",&["outer"],20);push(&mut c,"b");let guard=Arc::new(());
 assert_eq!(run(&mut c,1,1,Some(&guard)),VisitResult::ComputationPending(0));assert_eq!(c.frames.len(),2);assert_eq!(c.frames[1].lowlink,1);assert!(c.published.is_empty());assert_eq!(c.stack,vec![0,1]);
}
fn action_lookup(c:&mut Context,n:&str)->MetricLookup{
 c.add("outer",&[],99);push(c,"outer");c.frames[0].phase=FramePhase::Publish;c.var_info[0].publication.close(ClosedValue::Substitute(VarType::Custom("outer".into()),Arc::new(Value{n:99})));
 c.frame_root=Some(VarType::Custom("outer".into()));
 let action=MetricAction{identity:Arc::new(()),root:c.frame_root.clone().unwrap(),owner:c.frame_root.clone().unwrap(),index:0,prerequisite:FontTarget::Metric};c.metric_action=Some(action.clone());
 MetricLookup{action,flags:0,generation:c.lookup_bindings.root.clone(),depth:1,semantic_floor:1,request:SubstitutionLookup{identity:Arc::new(()),attribute_attempt:Some(Arc::new(())),kind:SubstitutionLookupKind::Variable,name:n.into(),namespace:None},longhand:0,value:Arc::new(Value{n:0})}
}
#[test]fn actual_lookup_producer_publishes_child_cycle_initial_with_exact_reply_identity(){
 let mut c=Context::new();c.add("b",&["c"],20);c.add("c",&["b"],30);let state=action_lookup(&mut c,"b");
 assert_eq!(c.resolve_metric_lookup_inner(&state,&NonCustomPropertyReferences,&mut AttributeTracker,&mut|_,_,_|PublicationDemand::Ready),Ok(true));
 let (_,reply)=c.lookup_reply.take().unwrap();assert!(Arc::ptr_eq(&reply.generation,&state.generation));assert!(Arc::ptr_eq(&reply.value,&state.value));let reply=reply.lookup.unwrap();assert!(Arc::ptr_eq(&reply.identity,&state.request.identity));let SubstitutionLookupValue::Value(n)=reply.value;assert_eq!(n,8);assert_eq!(c.frames.len(),1);assert!(c.metric_action.is_some());
}
#[test]fn actual_lookup_producer_checks_generation_then_retains_attribute_frontier(){
 let mut c=Context::new();c.add("b",&["attr:a"],20);let mut state=action_lookup(&mut c,"b");let generation=state.generation.clone();state.generation=Arc::new(());
 let before=c.starts.len();assert_eq!(c.resolve_metric_lookup_inner(&state,&NonCustomPropertyReferences,&mut AttributeTracker,&mut|_,_,_|PublicationDemand::Ready),Err(()));assert_eq!(c.starts.len(),before);
 state.generation=generation;
 for _ in 0..2 {assert_eq!(c.resolve_metric_lookup_inner(&state,&NonCustomPropertyReferences,&mut AttributeTracker,&mut|_,_,_|PublicationDemand::Ready),Ok(false));assert_eq!(c.frames.len(),2);assert!(c.lookup_reply.is_none());}
 assert_eq!(c.starts.iter().filter(|v|**v==VarType::Custom("b".into())).count(),1);assert!(!c.starts.iter().any(|v|matches!(v,VarType::Attr(..))));
}
