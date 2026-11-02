fn selected(name:&str,fallback:Option<&str>)->PropertyDeclaration {
 PropertyDeclaration::WithVariables(VariableDeclaration{longhand:LonghandId::FontWeight,value:Arc::new(UnparsedValue{result:Box::new(PropertyDeclaration::Value(999)),variable_value:VariableValue{css:"selected".into(),references:References{refs:vec![reference(name,fallback)],flags:ReferenceFlags::VAR},url_data:UrlExtraData}})})
}
fn with_graph(values:&[PropertyDeclaration],priorities:&[CascadePriority],f:impl FnOnce(&mut Context,&mut AttributeTracker)){
 let mut decls=declarations(values,priorities);decls.prioritary_positions=[DeclarationPosition{most_important:DeclarationIndex::MAX};11];
 for id in [PrioritaryPropertyId::FontWeight,PrioritaryPropertyId::LineHeight] {
 let indices:Vec<_>=values.iter().enumerate().filter(|(_,v)|v.id()==PropertyDeclarationId::Longhand(id.to_longhand())).map(|(i,_)|i).collect();
 decls.prioritary_positions[id as usize].most_important=indices.first().map_or(DeclarationIndex::MAX,|i|*i as u16);
 for (position,index) in indices.iter().enumerate(){decls.longhand_declarations[*index].next_index=indices.get(position+1).copied().unwrap_or(0) as u16;}
 }
 let mut cascade=Cascade::default();cascade.priority_completion_flags=Some(RuleCascadeFlags(0));
 for id in [PrioritaryPropertyId::Appearance,PrioritaryPropertyId::FontWidth,PrioritaryPropertyId::FontStyle,PrioritaryPropertyId::FontSizeAdjust,PrioritaryPropertyId::Direction,PrioritaryPropertyId::WritingMode,PrioritaryPropertyId::TextOrientation] {cascade.completed_prioritary.insert(id);}
 let mut stylist=Stylist::default();for name in ["metric","size","nested","cycle","lh"]{stylist.registered.insert(name.into(),PropertyDescriptors{syntax:Some(Syntax{components:vec![]})});}
 let mut computed=computed::Context::default();let mut cache=ShorthandsWithPropertyReferencesCache;let mut tracker=AttributeTracker::default();
 computed.builder.substitution_functions.vars.insert("metric".into(),variable("1ch",vec![],ReferenceFlags::FONT_UNITS|ReferenceFlags::FONT_METRICS));
 computed.builder.substitution_functions.vars.insert("size".into(),variable("1em",vec![],ReferenceFlags::FONT_UNITS));
 computed.builder.substitution_functions.vars.insert("alias".into(),variable("alias",vec![reference("size",None)],ReferenceFlags::VAR));
 let mut priority_completion=PriorityCompletion::default();
 let mut c=Context{count:0,index_map:OrderIndexMap::default(),non_custom_index_map:Default::default(),var_info:vec![],stack:vec![],frames:vec![],frame_root:None,frame_reply:None,stylist:&stylist,computed_context:&mut computed,decls:&decls,font_preparation:None,completed_font_inputs:LonghandSet::default(),font_completion_flags:Some(RuleCascadeFlags(0)),metric_action:None,metric_references:None,priority_completion:&mut priority_completion,metric_drain:MetricDrain::new(&decls),cascade:&mut cascade,cache:&mut cache};
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

#[test]fn generated_line_height_wait_retains_claim_without_ordinary_application(){
 let values=[selected("lh",None),PropertyDeclaration::Synthesis(LonghandId::LineHeight,20)];
 with_graph(&values,&[priority(2,2,2,0),priority(2,2,2,0)],|c,t|{
  let flags=ReferenceFlags::from_unit(NoCalcLength::LH);
  c.map_mut().vars.insert("lh".into(),variable("1lh",vec![],flags));
  let action=pause(c,t,"metric");assert!(matches!(finish(c,t,&action),MetricActionProgress::References(_, _)));
  for id in [PrioritaryPropertyId::FontWeight,PrioritaryPropertyId::LineHeight] {assert!(!c.cascade.ensured_prioritary.contains(id));assert!(!c.cascade.seen.longhands.contains(id.to_longhand()));}
  assert!(c.cascade.publications.is_empty());assert_eq!(c.cascade.substitutions.get(),0);
  assert!(c.priority_completion.claimed.contains(PrioritaryPropertyId::FontWeight));assert!(c.priority_completion.active.is_empty());
  let index=c.non_custom_index_map[SingleNonCustomReference::LhUnits].unwrap();assert!(matches!(c.var_info[index].publication,NodePublication::Pending(ClosedValue::Prioritary(_))));
  assert_eq!(c.frames.last().unwrap().index,index);assert!(matches!(c.frames.last().unwrap().phase,FramePhase::Publish));
  assert!(c.metric_drain.continuations[0].1.waiting.is_some());assert!(c.map().vars["lh"].as_universal().is_some());
  let before=waiting_snapshot(c);for _ in 0..3 {assert!(matches!(finish(c,t,&action),MetricActionProgress::References(_, _)));assert_eq!(waiting_snapshot(c),before);assert!(c.priority_completion.active.is_empty());}
 });
}
#[test]fn ordinary_claim_and_active_checks_precede_old_ensured_fastpath(){
 with_graph(&[PropertyDeclaration::Value(700)],&[priority(2,2,2,0)],|c,t|{
  let id=PrioritaryPropertyId::FontWeight;c.cascade.ensured_prioritary.insert(id);
  c.priority_completion.claimed.insert(id);
  assert_eq!(c.cascade.ensure_prioritary_property(c.computed_context,c.decls,c.cache,t,id,c.priority_completion,true),ComputationStatus::Pending);
  c.priority_completion.claimed.remove(id);c.priority_completion.active.insert(id);
  assert_eq!(c.cascade.ensure_prioritary_property(c.computed_context,c.decls,c.cache,t,id,c.priority_completion,true),ComputationStatus::Pending);
  assert!(c.cascade.publications.is_empty());assert_eq!(c.cascade.substitutions.get(),0);
 });
}
#[test]fn ordinary_success_publishes_once_without_claims(){
 with_graph(&[PropertyDeclaration::Value(700)],&[priority(2,2,2,0)],|c,t|{
  for _ in 0..3 {assert_eq!(c.cascade.ensure_prioritary_property(c.computed_context,c.decls,c.cache,t,PrioritaryPropertyId::FontWeight,c.priority_completion,true),ComputationStatus::Ready);}
  assert!(matches!(c.cascade.publications.as_slice(),[PropertyDeclaration::Value(700)]));assert_eq!(c.cascade.fixups,1);assert!(c.priority_completion.active.is_empty());assert!(c.priority_completion.complete.contains(PrioritaryPropertyId::FontWeight));
 });
}
#[test]fn partial_generated_prerequisites_are_not_reapplied_on_pending_resume(){
 let values=[PropertyDeclaration::Value(700),PropertyDeclaration::Synthesis(LonghandId::LineHeight,20)];
 with_graph(&values,&[priority(2,2,2,0),priority(2,2,2,0)],|c,t|{
  c.priority_completion.claimed.insert(PrioritaryPropertyId::FontStyle);
  assert_eq!(c.cascade.ensure_prioritary_property(c.computed_context,c.decls,c.cache,t,PrioritaryPropertyId::LineHeight,c.priority_completion,true),ComputationStatus::Pending);
  assert!(c.cascade.ensured_prioritary.contains(PrioritaryPropertyId::FontWeight));assert!(!c.cascade.ensured_prioritary.contains(PrioritaryPropertyId::LineHeight));assert_eq!(c.cascade.publications.len(),1);
  assert!(c.priority_completion.active.is_empty());
  // Standalone ledger test: release its manually acquired claim; no retained metric action exists.
  c.priority_completion.claimed.remove(PrioritaryPropertyId::FontStyle);
  for _ in 0..2 {assert_eq!(c.cascade.ensure_prioritary_property(c.computed_context,c.decls,c.cache,t,PrioritaryPropertyId::LineHeight,c.priority_completion,true),ComputationStatus::Ready);}
  assert_eq!(c.cascade.publications.len(),2);assert!(matches!(c.cascade.publications[0],PropertyDeclaration::Value(700)));assert!(matches!(c.cascade.publications[1],PropertyDeclaration::Synthesis(LonghandId::LineHeight,20)));assert!(c.priority_completion.active.is_empty());
 });
}
fn dynamic_attr(id:LonghandId,name:&str,fallback:Option<&str>,value:u16)->PropertyDeclaration {
 let mut r=reference(name,None);r.substitution_kind=SubstitutionFunctionKind::Attr;
 r.attribute_data=AttrData{namespace:Some("n".into()),typed:true,valid_non_type:false,expected_consumer:Some(id)};
 r.fallback=fallback.map(|css|Box::new(VariableValue{css:css.into(),..Default::default()}));
 PropertyDeclaration::WithVariables(VariableDeclaration{longhand:id,value:Arc::new(UnparsedValue{result:Box::new(PropertyDeclaration::Synthesis(id,value)),variable_value:VariableValue{css:"dynamic-attr".into(),references:References{refs:vec![r],flags:ReferenceFlags::ATTR},url_data:UrlExtraData}})})
}
fn with_dynamic(values:&[PropertyDeclaration],priorities:&[CascadePriority],f:impl FnOnce(&mut Context,&mut AttributeTracker)) {
 let mut decls=declarations(values,priorities);decls.prioritary_positions.fill(DeclarationPosition{most_important:DeclarationIndex::MAX});
 for index in (0..values.len()).rev() {
  let PropertyDeclarationId::Longhand(id)=values[index].id();let priority_id=PrioritaryPropertyId::from_longhand(id).unwrap();
  let old=decls.prioritary_positions[priority_id as usize].most_important;
  decls.longhand_declarations[index].next_index=if old==DeclarationIndex::MAX{0}else{old};
  decls.prioritary_positions[priority_id as usize].most_important=index as DeclarationIndex;
 }
 let mut cascade=Cascade::default();let mut stylist=Stylist::default();stylist.registered.insert("len".into(),PropertyDescriptors{syntax:Some(Syntax{components:vec![]})});
 let mut computed=computed::Context::default();computed.builder.substitution_functions.vars.insert("len".into(),variable("1em",vec![],ReferenceFlags::from_unit("em")));
 let mut cache=ShorthandsWithPropertyReferencesCache;let mut tracker=AttributeTracker::default();let mut ledger=PriorityCompletion::default();
 let mut c=Context{count:0,index_map:OrderIndexMap::default(),non_custom_index_map:Default::default(),var_info:vec![],stack:vec![],frames:vec![],frame_root:None,frame_reply:None,stylist:&stylist,computed_context:&mut computed,decls:&decls,font_preparation:None,completed_font_inputs:LonghandSet::default(),font_completion_flags:None,metric_action:None,metric_references:None,priority_completion:&mut ledger,metric_drain:MetricDrain::new(&decls),cascade:&mut cascade,cache:&mut cache};f(&mut c,&mut tracker);
}
#[test] fn reached_literal_and_missing_typed_attrs_publish_and_certify_once() {
 for (id,missing,text) in [(LonghandId::Appearance,false,"20"),(LonghandId::Appearance,true,"20"),(LonghandId::FontFamily,false,"monospace")] {
  let values=[dynamic_attr(id,"data",Some("20"),42),PropertyDeclaration::Synthesis(LonghandId::FontSize,20)];
  with_dynamic(&values,&[priority(2,2,2,0);2],|c,t|{
   if !missing {t.raw.insert("data".into(),variable(text,vec![],ReferenceFlags::empty()));}
   let action=pause(c,t,"len");let target=PrioritaryPropertyId::from_longhand(id).unwrap();
   assert!(action.prerequisite.same_as(FontTarget::Metric(target)));
   assert!(!c.cascade.ensured_prioritary.contains(target));assert!(!c.cascade.seen.longhands.contains(id));assert_eq!(c.cascade.substitutions.get(),0);
   assert!(matches!(finish(c,t,&action),MetricActionProgress::Published(_)));
   assert!(c.priority_completion.complete.contains(target));assert_eq!(c.cascade.substitutions.get(),1);
   assert!(matches!(c.poll_root(VarType::Custom("len".into()),&Default::default(),t,&mut font_publication_demand),VisitResult::Complete));
   assert!(c.cascade.completed_prioritary.contains(PrioritaryPropertyId::FontSize));
   assert_eq!(c.cascade.publications.iter().filter(|x|matches!(x,PropertyDeclaration::Synthesis(p,42) if *p==id)).count(),1);
   assert_eq!(c.cascade.substitutions.get(),1);c.reset();
  });
 }
}
#[test] fn raw_attr_len_waits_before_appearance_application_or_ensured() {
 let values=[dynamic_attr(LonghandId::Appearance,"data",Some("20"),42),PropertyDeclaration::Synthesis(LonghandId::FontSize,20)];
 with_dynamic(&values,&[priority(2,2,2,0);2],|c,t|{
  let raw=variable("raw",vec![reference("len",None)],ReferenceFlags::VAR);
  t.raw.insert("data".into(),raw.clone());c.map_mut().attrs.insert(("data".into(),"n".into()),raw);
  let action=pause(c,t,"len");let flags=c.computed_context.included_cascade_flags;
  assert!(matches!(finish(c,t,&action),MetricActionProgress::References(_, _)));
  assert!(!c.cascade.ensured_prioritary.contains(PrioritaryPropertyId::Appearance));assert!(!c.cascade.seen.longhands.contains(LonghandId::Appearance));
  assert!(c.cascade.publications.is_empty());assert_eq!(c.cascade.substitutions.get(),0);assert_eq!(c.computed_context.included_cascade_flags,flags);
  assert!(c.priority_completion.active.is_empty());assert!(c.priority_completion.claimed.contains(PrioritaryPropertyId::Appearance));
  let before=waiting_snapshot(c);for _ in 0..2{assert!(matches!(finish(c,t,&action),MetricActionProgress::References(_, _)));assert_eq!(before,waiting_snapshot(c));}
 });
}
#[test] fn dynamic_rollback_owns_next_arc_and_skips_losing_declaration() {
 let values=[dynamic_attr(LonghandId::Appearance,"first",None,42),dynamic_attr(LonghandId::Appearance,"loser",None,43),dynamic_attr(LonghandId::Appearance,"last",None,44),PropertyDeclaration::Synthesis(LonghandId::FontSize,20)];
 with_dynamic(&values,&[priority(2,2,2,0),priority(2,1,1,0),priority(1,1,1,0),priority(2,2,2,0)],|c,t|{
  t.raw.insert("first".into(),variable("revert",vec![],ReferenceFlags::empty()));t.raw.insert("last".into(),variable("20",vec![],ReferenceFlags::empty()));
  let action=pause(c,t,"len");let first=c.perform_metric_action(&action,t);let MetricActionProgress::References(_,first_arc)=first else {panic!()};
  assert!(matches!(finish(c,t,&action),MetricActionProgress::Published(_)));
  assert_eq!(c.cascade.substitutions.get(),2);assert_eq!(t.loads,2);assert!(c.visited(&VarType::Attr("loser".into(),"n".into())).is_none());
  assert!(matches!(c.cascade.publications.as_slice(),[PropertyDeclaration::SynthesisWide(LonghandId::Appearance,_),PropertyDeclaration::Synthesis(LonghandId::Appearance,44)]));
  assert!(matches!(c.metric_drain.poll(c.cascade,c.computed_context,c.cache,t,c.priority_completion,Some((LonghandId::Appearance,first_arc))),MetricDrainStep::WrongReply));
 });
}
#[test] fn ordinary_final_caller_can_keep_legacy_dynamic_path() {
 let values=[dynamic_attr(LonghandId::Appearance,"data",None,42)];
 with_dynamic(&values,&[priority(2,2,2,0)],|c,t|{
  assert_eq!(c.count,0);assert!(c.frame_root.is_none());
  for _ in 0..2{c.cascade.finish_ordinary(c.computed_context,c.decls,c.cache,t,c.priority_completion);}
  assert_eq!(c.count,0);assert!(c.frame_root.is_none());
  assert_eq!(c.cascade.publications.len(),1);assert_eq!(c.cascade.substitutions.get(),1);
  assert!(!c.priority_completion.complete.contains(PrioritaryPropertyId::Appearance));
 });
}
#[test] fn prepare_status_propagates_through_shared_ordinary_ledger() {
 let mut ledger=PriorityCompletion::default();let mut visited=Vec::new();
 let status=ledger.ensure_ordinary(PrioritaryPropertyId::FontSize,&mut |id|{
  visited.push(id.to_longhand());if id.to_longhand()==LonghandId::Appearance{ComputationStatus::Prepare(LonghandId::Appearance)}else{ComputationStatus::Ready}
 });
 assert_eq!(status,ComputationStatus::Prepare(LonghandId::Appearance));assert!(ledger.active.is_empty());
 assert!(!ledger.complete.contains(PrioritaryPropertyId::Appearance));assert!(!visited.contains(&LonghandId::FontSize));
}
#[test] fn appearance_flag_change_does_not_certify_old_context() {
 let values=[dynamic_attr(LonghandId::Appearance,"data",None,999),PropertyDeclaration::Synthesis(LonghandId::FontSize,20)];
 with_dynamic(&values,&[priority(2,2,2,0);2],|c,t|{
  t.raw.insert("data".into(),variable("20",vec![],ReferenceFlags::empty()));let action=pause(c,t,"len");
  assert!(matches!(finish(c,t,&action),MetricActionProgress::Invalidated));
  assert!(!c.cascade.completed_prioritary.contains(PrioritaryPropertyId::Appearance));assert!(!c.priority_completion.complete.contains(PrioritaryPropertyId::Appearance));
  assert!(matches!(finish(c,t,&action),MetricActionProgress::Invalidated));assert_eq!(c.cascade.substitutions.get(),1);assert_eq!(c.cascade.publications.len(),1);
 });
}
#[test] fn literal_winner_does_not_evaluate_dynamic_loser() {
 let values=[PropertyDeclaration::Synthesis(LonghandId::Appearance,42),dynamic_attr(LonghandId::Appearance,"loser",None,43),PropertyDeclaration::Synthesis(LonghandId::FontSize,20)];
 with_dynamic(&values,&[priority(2,2,2,0),priority(1,1,1,0),priority(2,2,2,0)],|c,t|{
  let action=pause(c,t,"len");assert!(matches!(finish(c,t,&action),MetricActionProgress::Published(_)));
  assert_eq!(t.loads,0);assert_eq!(c.cascade.substitutions.get(),0);
  assert!(matches!(c.cascade.publications.as_slice(),[PropertyDeclaration::Synthesis(LonghandId::Appearance,42)]));
 });
}
#[test] fn rollback_next_wait_rejects_previous_arc_before_consumption() {
 let values=[dynamic_attr(LonghandId::Appearance,"first",None,42),dynamic_attr(LonghandId::Appearance,"last",None,44),PropertyDeclaration::Synthesis(LonghandId::FontSize,20)];
 with_dynamic(&values,&[priority(2,2,2,0),priority(1,1,1,0),priority(2,2,2,0)],|c,t|{
  t.raw.insert("first".into(),variable("revert",vec![],ReferenceFlags::empty()));
  t.raw.insert("last".into(),variable("raw",vec![reference("len",None)],ReferenceFlags::VAR));
  let action=pause(c,t,"len");let MetricActionProgress::References(_,old)=c.perform_metric_action(&action,t) else {panic!()};
  let MetricActionProgress::References(_,new)=finish(c,t,&action) else {panic!()};
  assert!(!Arc::ptr_eq(&old,&new));assert_eq!(c.cascade.substitutions.get(),1);
  let before=waiting_snapshot(c);
  assert!(matches!(c.metric_drain.poll(c.cascade,c.computed_context,c.cache,t,c.priority_completion,Some((LonghandId::Appearance,old))),MetricDrainStep::WrongReply));
  assert_eq!(before,waiting_snapshot(c));assert_eq!(c.cascade.substitutions.get(),1);assert!(c.cascade.publications.is_empty());
 });
}
