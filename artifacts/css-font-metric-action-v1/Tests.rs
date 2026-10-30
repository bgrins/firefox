#[test]
fn literal_action_publishes_before_owner_resumes(){
 with_context(&[PropertyDeclaration::Value(700)],|c,t|{
  assert_eq!(c.enqueue_action(paused_frame(),Some(PrioritaryPropertyId::FontWeight)),VisitResult::ComputationPending(0));
  let action=c.pending_metric_action().unwrap();let before=snapshot(c);
  assert!(matches!(c.perform_metric_action(&action,t),MetricActionProgress::GeneratedPrerequisite(PrioritaryPropertyId::Appearance)));
  assert_eq!(snapshot(c),before);assert!(!c.priority_completion.complete.contains(PrioritaryPropertyId::FontWeight));
  assert_eq!(c.poll_checkpoint(),VisitResult::ComputationPending(0));
  complete_literal_appearance(c,t);
  assert!(matches!(c.perform_metric_action(&action,t),MetricActionProgress::Published(PrioritaryPropertyId::FontWeight)));
  assert!(c.priority_completion.complete.contains(PrioritaryPropertyId::FontWeight));
  assert_eq!(c.poll_checkpoint(),VisitResult::Complete);
  assert_eq!(c.cascade.publications.len(),2);
  assert!(matches!(c.cascade.publications.last(),Some(PropertyDeclaration::Value(700))));
  assert_eq!(c.cascade.fixups,2);assert_eq!(c.cascade.substitutions.get(),0);
  assert_eq!(c.stack,before.0);assert_eq!(snapshot(c).1,before.1);
  assert!(matches!(c.var_info[0].publication,NodePublication::Pending(())));
  assert!(matches!(c.perform_metric_action(&action,t),MetricActionProgress::WrongAction));
  assert_eq!(c.cascade.publications.len(),2);
 });
}
#[test]
fn foreign_or_tampered_action_does_not_consume_work(){
 with_context(&[PropertyDeclaration::Value(700)],|c,t|{
  c.enqueue_action(paused_frame(),Some(PrioritaryPropertyId::FontWeight));let action=c.pending_metric_action().unwrap();
  let before=snapshot(c);
  let mut foreign=action.clone();foreign.identity=Arc::new(());
  assert!(matches!(c.perform_metric_action(&foreign,t),MetricActionProgress::WrongAction));
  foreign=action.clone();foreign.root=VarType::Custom("other".into());
  assert!(matches!(c.perform_metric_action(&foreign,t),MetricActionProgress::WrongAction));
  foreign=action.clone();foreign.owner=VarType::Custom("other".into());
  assert!(matches!(c.perform_metric_action(&foreign,t),MetricActionProgress::WrongAction));
  foreign=action.clone();foreign.index=usize::MAX;
  assert!(matches!(c.perform_metric_action(&foreign,t),MetricActionProgress::WrongAction));
  foreign=action.clone();foreign.prerequisite=PrioritaryPropertyId::FontWidth;
  assert!(matches!(c.perform_metric_action(&foreign,t),MetricActionProgress::WrongAction));
  assert_eq!(snapshot(c),before);assert!(!c.priority_completion.claimed.contains(PrioritaryPropertyId::FontWeight));
 });
}
#[test]
fn references_remain_foreign_work_without_a_forged_ready_reply(){
 let value=var(PropertyDeclaration::Value(700));
 with_context(&[value],|c,t|{
  complete_literal_appearance(c,t);c.enqueue_action(paused_frame(),Some(PrioritaryPropertyId::FontWeight));let action=c.pending_metric_action().unwrap();let before=snapshot(c);
  let first=match c.perform_metric_action(&action,t){MetricActionProgress::References(id,value)=>{assert_eq!(id,PrioritaryPropertyId::FontWeight);value},_=>panic!("needs actual semantic readiness")};
  let second=match c.perform_metric_action(&action,t){MetricActionProgress::References(_,value)=>value,_=>panic!("must still wait")};
  assert!(Arc::ptr_eq(&first,&second));assert_eq!(snapshot(c),before);assert!(c.pending_metric_action().is_some());
  assert!(!c.priority_completion.complete.contains(PrioritaryPropertyId::FontWeight));
 });
}
#[test]
fn invalidation_and_unsupported_actions_keep_owner_suspended(){
 with_context(&[PropertyDeclaration::Value(700)],|c,t|{
  complete_literal_appearance(c,t);c.cascade.seen.longhands.insert(PrioritaryPropertyId::FontWeight);
  c.enqueue_action(paused_frame(),Some(PrioritaryPropertyId::FontWeight));let action=c.pending_metric_action().unwrap();let before=snapshot(c);
  assert!(matches!(c.perform_metric_action(&action,t),MetricActionProgress::Invalidated));assert_eq!(snapshot(c),before);
  assert_eq!(c.poll_checkpoint(),VisitResult::ComputationPending(0));
 });
 with_context(&[],|c,t|{
  c.enqueue_action(paused_frame(),Some(PrioritaryPropertyId::Appearance));let action=c.pending_metric_action().unwrap();let before=snapshot(c);
  assert!(matches!(c.perform_metric_action(&action,t),MetricActionProgress::Unsupported));assert_eq!(snapshot(c),before);
  assert!(!c.priority_completion.claimed.contains(PrioritaryPropertyId::Appearance));
 });
}
#[test]
fn completion_is_not_inferred_from_the_old_ensured_bit(){
 with_context(&[PropertyDeclaration::Value(700)],|c,t|{
  complete_literal_appearance(c,t);c.cascade.ensured_prioritary.insert(PrioritaryPropertyId::FontWeight);
  c.enqueue_action(paused_frame(),Some(PrioritaryPropertyId::FontWeight));let action=c.pending_metric_action().unwrap();
  assert!(matches!(c.perform_metric_action(&action,t),MetricActionProgress::Invalidated));
  assert!(!c.priority_completion.complete.contains(PrioritaryPropertyId::FontWeight));assert!(c.pending_metric_action().is_some());
 });
}

#[test]
fn settled_completion_avoids_republication_and_stale_context_rejects(){
 with_context(&[PropertyDeclaration::Value(700)],|c,t|{
  complete_literal_appearance(c,t);
  c.enqueue_action(paused_frame(),Some(PrioritaryPropertyId::FontWeight));let action=c.pending_metric_action().unwrap();
  assert!(matches!(c.perform_metric_action(&action,t),MetricActionProgress::Published(_)));
  c.frames.clear();c.enqueue_action(paused_frame(),Some(PrioritaryPropertyId::FontWeight));
  let action=c.pending_metric_action().unwrap();let before=snapshot(c);
  assert!(matches!(c.perform_metric_action(&action,t),MetricActionProgress::AlreadyComplete));assert_eq!(snapshot(c),before);
 });
 with_context(&[PropertyDeclaration::Value(700)],|c,t|{
  c.enqueue_action(paused_frame(),Some(PrioritaryPropertyId::FontWeight));let action=c.pending_metric_action().unwrap();
  c.frames[0].phase=FramePhase::Other;
  assert!(matches!(c.perform_metric_action(&action,t),MetricActionProgress::WrongAction));assert!(c.cascade.publications.is_empty());
 });
}
