fn selected(name:&str,fallback:Option<&str>)->PropertyDeclaration {
 PropertyDeclaration::WithVariables(VariableDeclaration{longhand:LonghandId::FontWeight,value:Arc::new(UnparsedValue{result:Box::new(PropertyDeclaration::Value(999)),variable_value:VariableValue{css:"selected".into(),references:References{refs:vec![reference(name,fallback)],flags:ReferenceFlags::VAR},url_data:UrlExtraData}})})
}
fn with_graph(values:&[PropertyDeclaration],priorities:&[CascadePriority],f:impl FnOnce(&mut Context,&mut AttributeTracker)){
 let mut decls=declarations(values,priorities);decls.prioritary_positions=[DeclarationPosition{most_important:DeclarationIndex::MAX};11];
 decls.prioritary_positions[PrioritaryPropertyId::FontWeight as usize].most_important=0;
 decls.prioritary_positions[PrioritaryPropertyId::LineHeight as usize].most_important=1;
 decls.longhand_declarations[0].next_index=0;decls.longhand_declarations[1].next_index=0;
 let mut cascade=Cascade::default();cascade.priority_completion_flags=Some(RuleCascadeFlags(0));
 for id in [PrioritaryPropertyId::Appearance,PrioritaryPropertyId::FontWidth,PrioritaryPropertyId::FontStyle,PrioritaryPropertyId::FontSizeAdjust,PrioritaryPropertyId::Direction,PrioritaryPropertyId::WritingMode,PrioritaryPropertyId::TextOrientation] {cascade.completed_prioritary.insert(id);}
 let mut stylist=Stylist::default();for name in ["metric","size","nested","cycle","lh"]{stylist.registered.insert(name.into(),PropertyDescriptors{syntax:Some(Syntax{components:vec![]})});}
 let mut computed=computed::Context::default();let mut cache=ShorthandsWithPropertyReferencesCache;let mut tracker=AttributeTracker::default();
 computed.builder.substitution_functions.vars.insert("metric".into(),variable("1ch",vec![],ReferenceFlags::FONT_UNITS|ReferenceFlags::FONT_METRICS));
 computed.builder.substitution_functions.vars.insert("size".into(),variable("1em",vec![],ReferenceFlags::FONT_UNITS));
 computed.builder.substitution_functions.vars.insert("alias".into(),variable("alias",vec![reference("size",None)],ReferenceFlags::VAR));
 let mut c=Context{count:0,index_map:OrderIndexMap::default(),non_custom_index_map:Default::default(),var_info:vec![],stack:vec![],frames:vec![],frame_root:None,frame_reply:None,stylist:&stylist,computed_context:&mut computed,decls:&decls,font_preparation:None,completed_font_inputs:LonghandSet::default(),font_completion_flags:Some(RuleCascadeFlags(0)),metric_action:None,metric_references:None,priority_completion:PriorityCompletion::default(),metric_drain:MetricDrain::new(&decls),cascade:&mut cascade,cache:&mut cache};
 f(&mut c,&mut tracker);
}
fn pause(c:&mut Context,t:&mut AttributeTracker,root:&str)->MetricAction {
 assert!(matches!(c.poll_root(VarType::Custom(root.into()),&Default::default(),t,&mut font_publication_demand),VisitResult::ComputationPending(_)));
 c.pending_metric_action().unwrap()
}
fn finish(c:&mut Context,t:&mut AttributeTracker,action:&MetricAction)->MetricActionProgress {c.drive_metric_action(action,&Default::default(),t,&mut font_publication_demand)}
fn waiting_snapshot(c:&Context)->String {format!("{:?}/{:?}/{:?}/{:?}/{:?}",c.stack,c.frames.iter().map(|f|(&f.var,f.index,f.lowlink,f.self_ref,f.waiting.as_ref().map(|(v,_)|v),f.walk.as_ref().map(|w|(w.current.as_ref().map(|(_,cursor)|*cursor),w.waiting.as_ref(),w.queued.len())))).collect::<Vec<_>>(),c.frame_reply,c.computed_context.events,c.cascade.substitutions.get())}

#[test]fn generated_line_height_reenters_claimed_weight_before_child_value(){
 let values=[selected("lh",None),PropertyDeclaration::Synthesis(LonghandId::LineHeight,20)];
 with_graph(&values,&[priority(2,2,2,0),priority(2,2,2,0)],|c,t|{
  let flags=ReferenceFlags::from_unit(NoCalcLength::LH);
  assert_eq!(flags,ReferenceFlags::FONT_UNITS|ReferenceFlags::LH_UNITS|ReferenceFlags::FONT_METRICS|ReferenceFlags::FONT_ORIENTATION);
  c.map_mut().vars.insert("lh".into(),variable("1lh",vec![],flags));
  let action=pause(c,t,"metric");assert!(!c.cascade.ensured_prioritary.contains(PrioritaryPropertyId::FontWeight));
  let result=finish(c,t,&action);
  println!("action_result={}; ordinary_events={:?}; retained_preparations={}",match &result {MetricActionProgress::References(_,_)=>"References",MetricActionProgress::AlreadyComplete=>"AlreadyComplete",MetricActionProgress::Invalidated=>"Invalidated",MetricActionProgress::Published(_)=>"Published",_=>"other"},c.computed_context.events,c.metric_drain.continuations.len());
  assert!(matches!(result,MetricActionProgress::References(_, _)));
  assert!(c.cascade.ensured_prioritary.contains(PrioritaryPropertyId::FontWeight));assert!(!c.cascade.completed_prioritary.contains(PrioritaryPropertyId::FontWeight));
  assert!(c.priority_completion.claimed.contains(PrioritaryPropertyId::FontWeight));assert_eq!(c.metric_drain.continuations.len(),1);assert!(c.metric_drain.continuations[0].1.waiting.is_some());
  assert!(c.metric_action.is_some());assert!(!c.metric_references.as_ref().unwrap().complete);assert!(c.map().vars["lh"].as_universal().is_some());
  let events=&c.computed_context.events;let early=events.iter().position(|s|s=="ordinary-weight-unresolved:true").unwrap();let literal=events.iter().position(|s|s=="ordinary-line-height:20").unwrap();assert!(early<literal);
  assert!(events.iter().all(|s|!s.starts_with("selected:") && s!="substitute:lh:None"));assert_eq!(c.cascade.substitutions.get(),1);
  println!("events={events:?}; result=References/Pending; ensuredWeight=true; completedWeight=false; retainedWaiting=true");
 });
}
