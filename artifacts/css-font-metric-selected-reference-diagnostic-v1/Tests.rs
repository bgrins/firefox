fn selected(name:&str,fallback:Option<&str>)->PropertyDeclaration {
 PropertyDeclaration::WithVariables(VariableDeclaration{longhand:LonghandId::FontWeight,value:Arc::new(UnparsedValue{result:Box::new(PropertyDeclaration::Value(999)),variable_value:VariableValue{css:"selected".into(),references:References{refs:vec![reference(name,fallback)],flags:ReferenceFlags::VAR},url_data:UrlExtraData}})})
}
fn with_graph(values:&[PropertyDeclaration],priorities:&[CascadePriority],f:impl FnOnce(&mut Context,&mut AttributeTracker)){
 let mut decls=declarations(values,priorities);decls.prioritary_positions=[DeclarationPosition{most_important:DeclarationIndex::MAX};11];
 decls.prioritary_positions[PrioritaryPropertyId::FontWeight as usize].most_important=0;
 let mut cascade=Cascade::default();cascade.priority_completion_flags=Some(RuleCascadeFlags(0));
 for id in [PrioritaryPropertyId::Appearance,PrioritaryPropertyId::FontWidth,PrioritaryPropertyId::FontStyle,PrioritaryPropertyId::FontSizeAdjust,PrioritaryPropertyId::Direction,PrioritaryPropertyId::WritingMode,PrioritaryPropertyId::TextOrientation] {cascade.completed_prioritary.insert(id);}
 let mut stylist=Stylist::default();for name in ["metric","size","nested","cycle"]{stylist.registered.insert(name.into(),PropertyDescriptors{syntax:Some(Syntax{components:vec![]})});}
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
#[test]fn actual_unvisited_size_alias_computes_before_selected_publication(){
 with_graph(&[selected("alias",None)],&[priority(2,2,2,0)],|c,t|{
  let action=pause(c,t,"metric");assert!(c.visited(&VarType::Custom("size".into())).is_none());assert!(c.visited(&VarType::Custom("alias".into())).is_none());
  let root=c.frame_root.clone();let owner_low=c.frames.last().unwrap().lowlink;let count=c.count;
  assert!(matches!(finish(c,t,&action),MetricActionProgress::Published(FontTarget::Metric(_))));
  assert_eq!(c.frame_root,root);assert_eq!(c.frames.len(),1);assert_eq!(c.frames[0].lowlink,owner_low);assert!(c.count>count);
  assert_eq!(c.map().vars["size"].css,"20");assert_eq!(c.map().vars["alias"].css,"20");
  assert!(matches!(c.cascade.publications.as_slice(),[PropertyDeclaration::Value(700)]));assert_eq!(c.cascade.substitutions.get(),1);
  assert!(matches!(finish(c,t,&action),MetricActionProgress::WrongAction));assert_eq!(c.cascade.publications.len(),1);
  assert!(matches!(c.poll_root(VarType::Custom("metric".into()),&Default::default(),t,&mut font_publication_demand),VisitResult::Complete));c.reset();
 });
}
#[test]fn foreign_open_ancestor_does_not_merge_or_select_fallback(){
 for indirect in [false,true] {with_graph(&[selected(if indirect{"bridge"}else{"outer"},Some("fallback"))],&[priority(2,2,2,0)],|c,t|{
  c.map_mut().vars.insert("outer".into(),variable("outer",vec![reference("metric",None)],ReferenceFlags::VAR));
  c.map_mut().vars.insert("fallback".into(),computed("20"));
  c.map_mut().vars.insert("bridge".into(),variable("bridge",vec![reference("outer",Some("fallback"))],ReferenceFlags::VAR));
  let action=pause(c,t,"outer");let outer=c.index_map.var["outer"];let before=c.var_info[outer].lowlink;
  assert!(matches!(finish(c,t,&action),MetricActionProgress::References(_, _)));
  assert_eq!(c.var_info[outer].lowlink,before);assert!(matches!(c.visited(&VarType::Custom("outer".into())),Some(VisitResult::SemanticOpen(_))));
  assert!(c.map().vars["outer"].as_universal().is_some());assert!(c.cascade.publications.is_empty());assert_eq!(c.cascade.substitutions.get(),0);
  if indirect {let child=c.frames.last().unwrap();assert_eq!(child.lowlink,child.index);assert!(child.waiting.is_some());}
  let snapshot=waiting_snapshot(c);for _ in 0..3 {assert!(matches!(finish(c,t,&action),MetricActionProgress::References(_, _)));assert_eq!(waiting_snapshot(c),snapshot);}
  assert!(Arc::ptr_eq(&action.identity,&c.pending_metric_action().unwrap().identity));
 });}
}
#[test]fn nested_metric_pending_never_replaces_outer_action(){
 with_graph(&[selected("nested",None)],&[priority(2,2,2,0)],|c,t|{
  c.map_mut().vars.insert("nested".into(),variable("1ch",vec![],ReferenceFlags::FONT_UNITS|ReferenceFlags::FONT_METRICS));
  let action=pause(c,t,"metric");assert!(matches!(finish(c,t,&action),MetricActionProgress::References(_, _)));
  assert!(matches!(c.visited(&VarType::Custom("nested".into())),Some(VisitResult::ComputationPending(_))));
  assert!(Arc::ptr_eq(&action.identity,&c.pending_metric_action().unwrap().identity));
  let snapshot=waiting_snapshot(c);assert!(matches!(finish(c,t,&action),MetricActionProgress::References(_, _)));assert_eq!(waiting_snapshot(c),snapshot);assert_eq!(c.metric_drain.continuations.len(),1);
 });
}
#[test]fn internal_css_cycle_settles_then_used_fallback_resumes(){
 with_graph(&[selected("cycle",Some("alias"))],&[priority(2,2,2,0)],|c,t|{
  c.map_mut().vars.insert("cycle".into(),variable("cycle",vec![reference("cycle",None)],ReferenceFlags::VAR));
  let action=pause(c,t,"metric");assert!(matches!(finish(c,t,&action),MetricActionProgress::Published(_)));
  assert_eq!(c.visited(&VarType::Custom("cycle".into())),Some(VisitResult::CycleSettled));assert!(!c.map().vars.contains_key("cycle"));
  assert!(matches!(c.cascade.publications.as_slice(),[PropertyDeclaration::Value(700)]));
 });
}
#[test]fn rollback_retains_owned_selection_and_walks_next_arc_once(){
 let values=[selected("reverter",None),selected("forbidden",None),selected("alias",None)];
 with_graph(&values,&[priority(2,2,2,0),priority(2,1,1,0),priority(1,1,1,0)],|c,t|{
  c.map_mut().vars.insert("reverter".into(),computed("revert"));
  let action=pause(c,t,"metric");assert!(matches!(finish(c,t,&action),MetricActionProgress::Published(_)));
  assert_eq!(c.cascade.substitutions.get(),2);assert!(c.visited(&VarType::Custom("forbidden".into())).is_none());
  assert!(matches!(c.cascade.publications.as_slice(),[PropertyDeclaration::Wide(CSSWideKeyword::Revert(_)),PropertyDeclaration::Value(700)]));
 });
}
#[test]fn stale_action_or_flags_cannot_consume_pending_references(){
 with_graph(&[selected("nested",None)],&[priority(2,2,2,0)],|c,t|{
  c.map_mut().vars.insert("nested".into(),variable("1ch",vec![],ReferenceFlags::FONT_UNITS|ReferenceFlags::FONT_METRICS));
  let action=pause(c,t,"metric");assert!(matches!(finish(c,t,&action),MetricActionProgress::References(_, _)));
  let snapshot=waiting_snapshot(c);let mut wrong=action.clone();wrong.identity=Arc::new(());
  assert!(matches!(finish(c,t,&wrong),MetricActionProgress::WrongAction));assert_eq!(waiting_snapshot(c),snapshot);
  c.computed_context.included_cascade_flags=RuleCascadeFlags(1);
  assert!(matches!(finish(c,t,&action),MetricActionProgress::WrongAction));assert_eq!(waiting_snapshot(c),snapshot);
 });
}

#[test]fn saved_foreign_reply_is_preserved_before_receive(){
 with_graph(&[selected("bridge",Some("fallback"))],&[priority(2,2,2,0)],|c,t|{
  c.map_mut().vars.insert("outer".into(),variable("outer",vec![reference("metric",None)],ReferenceFlags::VAR));
  c.map_mut().vars.insert("bridge".into(),variable("bridge",vec![reference("outer",None)],ReferenceFlags::VAR));
  c.map_mut().vars.insert("fallback".into(),computed("20"));
  let action=pause(c,t,"outer");assert!(matches!(finish(c,t,&action),MetricActionProgress::References(_, _)));
  let outer=c.index_map.var["outer"];c.frame_reply=Some((VarType::Custom("outer".into()),VisitResult::SemanticOpen(outer)));
  let snapshot=waiting_snapshot(c);
  for _ in 0..2 {assert!(matches!(finish(c,t,&action),MetricActionProgress::References(_, _)));assert_eq!(waiting_snapshot(c),snapshot);}
 });
}
#[test]fn child_flags_change_invalidates_before_selected_publication(){
 with_graph(&[selected("alias",None)],&[priority(2,2,2,0)],|c,t|{
  c.map_mut().vars.insert("size".into(),variable("flags:1em",vec![],ReferenceFlags::FONT_UNITS));
  let action=pause(c,t,"metric");assert!(matches!(finish(c,t,&action),MetricActionProgress::WrongAction));
  assert_eq!(c.computed_context.included_cascade_flags,RuleCascadeFlags(1));assert!(c.cascade.publications.is_empty());assert_eq!(c.cascade.substitutions.get(),0);
  assert!(c.metric_references.as_ref().unwrap().complete);assert!(c.metric_drain.continuations[0].1.waiting.is_some());
 });
}
#[test]fn typed_attr_walk_uses_selected_longhand_and_child_value(){
 let mut reference=reference("data-weight",Some("fallback"));reference.substitution_kind=SubstitutionFunctionKind::Attr;
 reference.attribute_data=AttrData{namespace:Some("n".into()),typed:true,valid_non_type:false,expected_consumer:Some(LonghandId::FontWeight)};
 let value=PropertyDeclaration::WithVariables(VariableDeclaration{longhand:LonghandId::FontWeight,value:Arc::new(UnparsedValue{result:Box::new(PropertyDeclaration::Value(999)),variable_value:VariableValue{css:"selected".into(),references:References{refs:vec![reference],flags:ReferenceFlags::ATTR},url_data:UrlExtraData}})});
 with_graph(&[value],&[priority(2,2,2,0)],|c,t|{
  c.map_mut().vars.insert("other".into(),computed("10"));
  c.map_mut().vars.insert("fallback".into(),variable("fallback",vec![self::reference("other",None)],ReferenceFlags::VAR));
  t.raw.insert("data-weight".into(),variable("attribute",vec![self::reference("alias",None)],ReferenceFlags::VAR));
  let action=pause(c,t,"metric");assert!(matches!(finish(c,t,&action),MetricActionProgress::Published(_)));
  assert_eq!(t.loads,1);assert!(c.visited(&VarType::Custom("fallback".into())).is_none());assert_eq!(c.map().attrs[&("data-weight".into(),"n".into())].css,"20");
  assert!(matches!(c.cascade.publications.as_slice(),[PropertyDeclaration::Value(700)]));
  assert_eq!(c.cascade.substitutions.get(),1);
 });
}

#[test] fn diagnostic_reads_saved_progress_without_advancing_or_publishing() {
 with_graph(&[selected("nested",None)],&[priority(2,2,2,0)],|c,t|{
  c.map_mut().vars.insert("nested".into(),variable("1ch",vec![],ReferenceFlags::FONT_UNITS|ReferenceFlags::FONT_METRICS));
  let action=pause(c,t,"metric");let progress=finish(c,t,&action);
  assert!(matches!(progress,MetricActionProgress::References(_, _)));
  let before=waiting_snapshot(c);let root=c.frame_root.clone();let count=c.count;
  let token=Arc::as_ptr(&c.metric_action.as_ref().unwrap().identity);
  let raw=Arc::as_ptr(&c.metric_references.as_ref().unwrap().value);
  let mut output=Vec::new();
  c.write_metric_diagnostic(&mut output,VisitResult::ComputationPending(action.index),Some(&progress));
  let output=String::from_utf8(output).unwrap();
  assert!(output.contains("progress=references"));assert!(output.contains("frame="));assert!(output.contains("readiness=ComputationPending"));assert!(output.contains("references action="));
  assert_eq!(before,waiting_snapshot(c));assert_eq!(root,c.frame_root);assert_eq!(count,c.count);
  assert_eq!(token,Arc::as_ptr(&c.metric_action.as_ref().unwrap().identity));assert_eq!(raw,Arc::as_ptr(&c.metric_references.as_ref().unwrap().value));
  assert!(c.cascade.publications.is_empty());assert_eq!(c.cascade.substitutions.get(),0);
 });
}
#[test] fn diagnostic_no_action_and_failed_output_leave_state_untouched() {
 struct Failed;
 impl std::io::Write for Failed {
  fn write(&mut self,_:&[u8])->std::io::Result<usize>{Err(std::io::Error::other("closed"))}
  fn flush(&mut self)->std::io::Result<()>{Ok(())}
 }
 with_graph(&[selected("alias",None)],&[priority(2,2,2,0)],|c,t|{
  let action=pause(c,t,"metric");let before=waiting_snapshot(c);
  let mut output=Vec::new();c.write_metric_diagnostic(&mut output,VisitResult::ComputationPending(action.index),None);
  assert!(String::from_utf8(output).unwrap().contains("progress=not-driven"));
  c.write_metric_diagnostic(&mut Failed,VisitResult::ComputationPending(action.index),None);
  assert_eq!(before,waiting_snapshot(c));assert!(c.cascade.publications.is_empty());
 });
}

#[test] fn actual_terminal_condition_does_not_log_success() {
 with_graph(&[selected("alias",None)],&[priority(2,2,2,0)],|c,_|{
  let mut output=Vec::new();
  terminal_snapshot(c,&mut output,VisitResult::Complete,None);
  terminal_snapshot(c,&mut output,VisitResult::CycleSettled,None);
  assert!(output.is_empty());
  terminal_snapshot(c,&mut output,VisitResult::ComputationPending(0),None);
  assert!(!output.is_empty());
 });
}

#[test] fn diagnostic_includes_pending_node_beyond_prefix_limit() {
 with_graph(&[selected("alias",None)],&[priority(2,2,2,0)],|c,_|{
  for index in 0..20 { c.var_info.push(VarInfo{var:None,lowlink:index,publication:NodePublication::SemanticOpen}); }
  let mut output=Vec::new();
  c.write_metric_diagnostic(&mut output,VisitResult::ComputationPending(19),None);
  assert!(String::from_utf8(output).unwrap().contains("pending_node=19"));
 });
}
