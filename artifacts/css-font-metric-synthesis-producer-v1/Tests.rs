fn flags(unit:&str)->ReferenceFlags {ReferenceFlags::from_unit(unit)}
#[test]
fn concrete_units_alias_joins_and_root_scope(){
 use FontDependencyDemand::*;
 for (unit,expected) in [("em",ComputedSize),("ex",FontMetrics),("cap",FontMetrics),("ch",OrientedMetrics),("ic",OrientedMetrics),("lh",OrientedMetrics),("px",None)] {
  assert_eq!(frame_font_demand(true,flags(unit),false),expected);
  assert_eq!(frame_font_demand(false,flags(unit),false),None);
 }
 assert_eq!(frame_font_demand(true,flags("em")|flags("ch"),false),OrientedMetrics);
 assert_eq!(frame_font_demand(true,flags("rch"),false),None);
 assert_eq!(frame_font_demand(true,flags("em")|flags("rch"),false),ComputedSize);
 assert_eq!(frame_font_demand(true,flags("rch"),true),OrientedMetrics);
}
#[test]
fn size_completion_is_preserved_while_metrics_wait(){
 let mut complete=PrioritaryPropertyIdSet::default();
 assert!(matches!(font_publication_demand(FontDependencyDemand::ComputedSize,&complete,None),PublicationDemand::Unresolved));
 complete.insert(PrioritaryPropertyId::FontSize);
 assert!(matches!(font_publication_demand(FontDependencyDemand::ComputedSize,&complete,Some(LonghandId::FontFeatureSettings)),PublicationDemand::Ready));
 assert!(matches!(font_publication_demand(FontDependencyDemand::FontMetrics,&complete,None),PublicationDemand::Metric(PrioritaryPropertyId::FontWeight)));
 assert!(complete.contains(PrioritaryPropertyId::FontSize));
}
#[test]
fn actual_literal_actions_satisfy_provider_in_order(){
 with_context(&[PropertyDeclaration::Value(700)],|c,t|{
  for id in [PrioritaryPropertyId::Appearance,PrioritaryPropertyId::FontSize] {
   c.cascade.ensure_prioritary_property(c.computed_context,c.metric_drain.declarations,c.cache,t,id);
  }
  c.import_priority_completion();
  let before=c.cascade.publications.len();
  let mut requested=Vec::new();
  loop {
   match font_publication_demand(FontDependencyDemand::OrientedMetrics,&c.priority_completion.complete,None){
    PublicationDemand::Ready=>break,
    PublicationDemand::Metric(id)=>{
     requested.push(id);c.frames.clear();c.enqueue_action(paused_frame(),Some(FontTarget::Metric(id)));
     let action=c.pending_metric_action().unwrap();
     assert!(matches!(c.perform_metric_action(&action,t),MetricActionProgress::Published(FontTarget::Metric(done)) if done==id));
     assert!(matches!(c.var_info[0].publication,NodePublication::Pending(())));
    },
    PublicationDemand::Synthesis(_)=>panic!("unexpected synthesis in priority-only fixture"),
    PublicationDemand::Unresolved=>panic!("literal prerequisites must progress"),
   }
  }
  assert_eq!(requested,vec![PrioritaryPropertyId::FontWeight,PrioritaryPropertyId::FontWidth,PrioritaryPropertyId::FontStyle,PrioritaryPropertyId::FontSizeAdjust,PrioritaryPropertyId::Direction,PrioritaryPropertyId::WritingMode,PrioritaryPropertyId::TextOrientation]);
  assert_eq!(c.cascade.publications.len(),before+7);assert_eq!(c.cascade.substitutions.get(),0);
  assert!(matches!(font_publication_demand(FontDependencyDemand::OrientedMetrics,&c.priority_completion.complete,Some(LonghandId::FontFeatureSettings)),PublicationDemand::Unresolved));
 });
}
#[test]
fn ordinary_early_bit_and_dynamic_application_do_not_certify_completion(){
 with_context(&[PropertyDeclaration::Value(700)],|c,t|{
  c.cascade.ensured_prioritary.insert(PrioritaryPropertyId::Appearance);
  c.cascade.ensure_prioritary_property(c.computed_context,c.metric_drain.declarations,c.cache,t,PrioritaryPropertyId::FontWeight);
  c.import_priority_completion();
  assert!(!c.priority_completion.complete.contains(PrioritaryPropertyId::FontWeight));
 });
 with_context(&[var(PropertyDeclaration::Value(700))],|c,t|{
  c.cascade.ensure_prioritary_property(c.computed_context,c.metric_drain.declarations,c.cache,t,PrioritaryPropertyId::FontSize);
  c.import_priority_completion();
  assert_eq!(c.cascade.substitutions.get(),1);
  assert!(!c.priority_completion.complete.contains(PrioritaryPropertyId::FontSize));
 });
}
#[test]
fn selected_references_suspend_without_forced_metric_readiness(){
 with_context(&[var(PropertyDeclaration::Value(700))],|c,t|{
  complete_literal_appearance(c,t);c.priority_completion.complete.insert(PrioritaryPropertyId::FontSize);
  assert!(matches!(font_publication_demand(FontDependencyDemand::FontMetrics,&c.priority_completion.complete,None),PublicationDemand::Metric(PrioritaryPropertyId::FontWeight)));
  c.enqueue_action(paused_frame(),Some(FontTarget::Metric(PrioritaryPropertyId::FontWeight)));let action=c.pending_metric_action().unwrap();
  assert!(matches!(c.perform_metric_action(&action,t),MetricActionProgress::References(PrioritaryPropertyId::FontWeight,_)));
  assert_eq!(c.cascade.substitutions.get(),0);assert!(!c.priority_completion.complete.contains(PrioritaryPropertyId::FontWeight));
 });
}

#[test]
fn changed_eligibility_invalidates_completion_without_republishing(){
 with_context(&[PropertyDeclaration::Value(700)],|c,t|{
  c.cascade.ensure_prioritary_property(c.computed_context,c.metric_drain.declarations,c.cache,t,PrioritaryPropertyId::FontSize);
  c.import_priority_completion();assert!(c.priority_completion.complete.contains(PrioritaryPropertyId::FontSize));
  let before=c.cascade.publications.len();c.computed_context.included_cascade_flags=RuleCascadeFlags(1);
  c.import_priority_completion();assert!(!c.priority_completion.complete.contains(PrioritaryPropertyId::FontSize));
  assert_eq!(c.cascade.publications.len(),before);
  assert!(matches!(font_publication_demand(FontDependencyDemand::ComputedSize,&c.priority_completion.complete,None),PublicationDemand::Unresolved));
 });
}

#[test]
fn ordinary_ast_preparation_does_not_wait_for_its_own_font_edge(){
 assert!(!preparation_needs_font_inputs(flags("em")|ReferenceFlags::COLOR_SCHEME,false));
 assert!(!preparation_needs_font_inputs(flags("ch")|ReferenceFlags::COLOR_SCHEME,false));
 assert!(preparation_needs_font_inputs(flags("em")|ReferenceFlags::ATTR,false));
 assert!(!preparation_needs_font_inputs(flags("px")|ReferenceFlags::ATTR,false));
 assert!(!preparation_needs_font_inputs(flags("rch")|ReferenceFlags::ATTR,false));
 assert!(preparation_needs_font_inputs(flags("rch")|ReferenceFlags::ATTR,true));
}

fn preparing_frame(extra:ReferenceFlags)->TraversalFrame{
 let mut f=paused_frame();f.phase=FramePhase::Prepare;f.lowlink=0;f.registered=true;f.selected_dependency_eligible=true;f.value=Some(Arc::new(TestValue));f.value_non_custom_refs=flags("em")|ReferenceFlags::COLOR_SCHEME|extra;f
}
#[test]
fn pure_union_ast_then_font_link_then_computation_route(){
 with_context(&[PropertyDeclaration::Value(20)],|c,t|{
  c.stack=vec![0];let mut f=preparing_frame(ReferenceFlags::empty());
  assert!(matches!(f.poll_prepare(c,t,&mut font_publication_demand),FrameStep::Next));
  assert_eq!(c.computed_context.preparations.get(),1);assert_eq!(c.computed_context.computations.get(),0);
  assert!(f.prepared_custom.is_some());assert_eq!(f.unit_links,vec![SingleNonCustomReference::FontUnits]);
  assert!(matches!(f.poll_units(c,t,&mut font_publication_demand),FrameStep::Link(VarType::NonCustom(SingleNonCustomReference::FontUnits))));
  c.cascade.ensure_prioritary_property(c.computed_context,c.decls,c.cache,t,PrioritaryPropertyId::FontSize);
  f.unit_cursor+=1;assert!(matches!(f.poll_units(c,t,&mut font_publication_demand),FrameStep::Next));
  f.phase=FramePhase::Publish;c.var_info[0].publication=NodePublication::Pending(());
  assert!(matches!(f.poll_publication(c,t,&mut font_publication_demand),FrameStep::Complete(VisitResult::Complete)));
  assert_eq!(c.computed_context.preparations.get(),1);assert_eq!(c.computed_context.computations.get(),1);
 });
}
#[test]
fn early_attr_wait_retains_preparation_on_repeated_poll(){
 with_context(&[PropertyDeclaration::Value(20)],|c,t|{
  c.stack=vec![0];let mut f=preparing_frame(ReferenceFlags::ATTR);
  for _ in 0..2 {
   assert!(matches!(f.poll_prepare(c,t,&mut font_publication_demand),FrameStep::Pending(None)));
   assert_eq!(c.computed_context.preparations.get(),0);assert!(f.value_non_custom_refs.contains(ReferenceFlags::COLOR_SCHEME));assert!(f.unit_links.is_empty());
  }
  c.cascade.ensure_prioritary_property(c.computed_context,c.decls,c.cache,t,PrioritaryPropertyId::FontSize);
  assert!(matches!(f.poll_prepare(c,t,&mut font_publication_demand),FrameStep::Next));
  assert_eq!(c.computed_context.preparations.get(),1);assert_eq!(f.unit_links,vec![SingleNonCustomReference::FontUnits]);
 });
}

#[test]
fn selected_synthesis_publications_complete_the_literal_provider_route(){
 let ids=[LonghandId::FontSynthesisWeight,LonghandId::FontSynthesisStyle,LonghandId::FontSynthesisSmallCaps,LonghandId::FontSynthesisPosition];
 let values=ids.map(|id|PropertyDeclaration::Synthesis(id,id as u16));let priorities=[priority(2,2,2,0);4];
 with_synthesis_context(&values,&priorities,|c,t|{
  let before=snapshot(c);let mut applied=Vec::new();
  loop {
   c.import_priority_completion();
   match font_publication_demand(FontDependencyDemand::OrientedMetrics,&c.priority_completion.complete,next_unprepared_font_input(c.decls,&c.completed_font_inputs)){
    PublicationDemand::Synthesis(id)=>{
     c.frames.clear();c.enqueue_action(paused_frame(),Some(FontTarget::Synthesis(id)));let token=c.pending_metric_action().unwrap();
     assert!(matches!(c.perform_metric_action(&token,t),MetricActionProgress::Published(FontTarget::Synthesis(done)) if done==id));applied.push(id);
     assert!(c.font_preparation.is_none());assert!(matches!(c.var_info[0].publication,NodePublication::Pending(())));
     assert!(matches!(c.perform_metric_action(&token,t),MetricActionProgress::WrongAction));
    },
    PublicationDemand::Ready=>break,
    _=>panic!("literal synthesis must progress"),
   }
  }
  assert_eq!(applied,ids);assert_eq!(c.cascade.publications.len(),4);
  for (entry,id) in c.cascade.publications.iter().zip(ids){assert!(matches!(entry,PropertyDeclaration::Synthesis(actual,value) if *actual==id && *value==id as u16));}assert_eq!(c.cascade.fixups,0);assert_eq!(c.cascade.substitutions.get(),0);assert_eq!(c.stack,before.0);
  for id in ids {assert!(c.cascade.seen.longhands.contains(id));assert!(c.completed_font_inputs.contains(id));}
 });
}
#[test]
fn synthesis_cursor_filters_longhands_and_preserves_local_rollback(){
 let id=LonghandId::FontSynthesisWeight;
 let values=[PropertyDeclaration::SynthesisWide(id,CSSWideKeyword::Revert(RevertKind::Layer)),PropertyDeclaration::Synthesis(LonghandId::FontSynthesisStyle,9),synthesis_var(id,PropertyDeclaration::Synthesis(id,800)),PropertyDeclaration::Synthesis(id,700)];
 let priorities=[priority(2,2,2,0),priority(2,2,2,0),priority(2,2,1,0),priority(2,1,1,0)];
 with_synthesis_context(&values,&priorities,|c,t|{
  c.enqueue_action(paused_frame(),Some(FontTarget::Synthesis(id)));let token=c.pending_metric_action().unwrap();
  assert!(matches!(c.perform_metric_action(&token,t),MetricActionProgress::Published(FontTarget::Synthesis(done)) if done==id));
  assert_eq!(c.cascade.substitutions.get(),0);assert_eq!(c.cascade.publications.len(),2);
  assert!(matches!(c.cascade.publications.last(),Some(PropertyDeclaration::Synthesis(done,700)) if *done==id));
  assert!(!c.cascade.seen.longhands.contains(LonghandId::FontSynthesisStyle));
 });
}
#[test]
fn synthesis_variable_wait_retains_exact_selected_arc_without_publication(){
 let id=LonghandId::FontSynthesisWeight;let values=[synthesis_var(id,PropertyDeclaration::Synthesis(id,0))];
 with_synthesis_context(&values,&[priority(2,2,2,0)],|c,t|{
  c.enqueue_action(paused_frame(),Some(FontTarget::Synthesis(id)));let token=c.pending_metric_action().unwrap();
  let first=match c.perform_metric_action(&token,t){MetricActionProgress::References(done,value)=>{assert_eq!(done,id);value},_=>panic!("must wait")};
  let second=match c.perform_metric_action(&token,t){MetricActionProgress::References(_,value)=>value,_=>panic!("must still wait")};
  assert!(Arc::ptr_eq(&first,&second));assert_eq!(c.cascade.substitutions.get(),0);assert!(c.cascade.publications.is_empty());
  assert!(c.font_preparation.is_some());assert!(c.pending_metric_action().is_some());assert!(!c.completed_font_inputs.contains(id));
 });
}
#[test]
fn synthesis_completion_invalidates_after_eligibility_change(){
 let id=LonghandId::FontSynthesisWeight;let values=[PropertyDeclaration::Synthesis(id,0)];
 with_synthesis_context(&values,&[priority(2,2,2,0)],|c,t|{
  c.enqueue_action(paused_frame(),Some(FontTarget::Synthesis(id)));let token=c.pending_metric_action().unwrap();
  assert!(matches!(c.perform_metric_action(&token,t),MetricActionProgress::Published(_)));
  c.computed_context.included_cascade_flags=RuleCascadeFlags(1);c.import_priority_completion();assert!(!c.completed_font_inputs.contains(id));
  c.frames.clear();c.enqueue_action(paused_frame(),Some(FontTarget::Synthesis(id)));let token=c.pending_metric_action().unwrap();
  assert!(matches!(c.perform_metric_action(&token,t),MetricActionProgress::Invalidated));assert_eq!(c.cascade.publications.len(),1);
 });
}

#[test]
fn synthesis_cursor_preserves_full_ordinary_indices_across_priority_sentinel(){
 let id=LonghandId::FontSynthesisWeight;
 let boundary=65_535usize;
 assert_eq!(DeclarationIndex::MAX as usize,boundary);
 for rollback in [false,true] {
  let mut values=vec![PropertyDeclaration::Synthesis(LonghandId::FontSynthesisStyle,9);boundary+2];
  let mut priorities=vec![priority(2,2,2,0);values.len()];
  if rollback {
   values[boundary-1]=PropertyDeclaration::SynthesisWide(id,CSSWideKeyword::Revert(RevertKind::Layer));
   values[boundary]=synthesis_var(id,PropertyDeclaration::Synthesis(id,800));
   values[boundary+1]=PropertyDeclaration::Synthesis(id,700);
   priorities[boundary+1]=priority(2,1,1,0);
  } else { values[boundary]=PropertyDeclaration::Synthesis(id,700); }
  with_synthesis_context(&values,&priorities,|c,t|{
   c.enqueue_action(paused_frame(),Some(FontTarget::Synthesis(id)));
   let token=c.pending_metric_action().unwrap();
   assert!(matches!(c.perform_metric_action(&token,t),MetricActionProgress::Published(FontTarget::Synthesis(done)) if done==id));
   assert_eq!(c.cascade.substitutions.get(),0);
   assert_eq!(c.cascade.publications.len(),if rollback {2} else {1});
   assert!(matches!(c.cascade.publications.last(),Some(PropertyDeclaration::Synthesis(done,700)) if *done==id));
   assert!(c.completed_font_inputs.contains(id));
  });
 }
}
