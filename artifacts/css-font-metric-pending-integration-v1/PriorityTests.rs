#[test]
fn ordinary_generated_pending_never_completes_parent() {
    let mut completion=PriorityCompletion::default();
    let mut calls=Vec::new();
    assert_eq!(completion.ensure_ordinary(PrioritaryPropertyId::FontWeight,&mut |id| {
        calls.push(id); ComputationStatus::Pending
    }),ComputationStatus::Pending);
    assert_eq!(calls,vec![PrioritaryPropertyId::Appearance]);
    assert!(!completion.complete.contains(PrioritaryPropertyId::Appearance));
    assert!(!completion.complete.contains(PrioritaryPropertyId::FontWeight));
    calls.clear();
    assert_eq!(completion.ensure_ordinary(PrioritaryPropertyId::FontWeight,&mut |id| {
        calls.push(id); ComputationStatus::Ready
    }),ComputationStatus::Ready);
    assert_eq!(calls,vec![PrioritaryPropertyId::Appearance,PrioritaryPropertyId::FontWeight]);
    completion.ensure_ordinary(PrioritaryPropertyId::FontWeight,&mut |_|panic!("reapplication"));
}

#[test]
fn active_is_pending_and_not_semantic_cycle_policy() {
    let mut completion=PriorityCompletion::default();
    completion.active.insert(PrioritaryPropertyId::Appearance);
    assert_eq!(completion.ensure_ordinary(PrioritaryPropertyId::FontWeight,&mut |_|panic!("premature application")),ComputationStatus::Pending);
    assert!(completion.active.contains(PrioritaryPropertyId::Appearance));
    assert!(!completion.active.contains(PrioritaryPropertyId::FontWeight));
    assert!(!completion.complete.contains(PrioritaryPropertyId::FontWeight));
}

#[test]
fn prerequisite_changes_flags_before_selection_and_retains_rollback() {
    let values=[var(PropertyDeclaration::Wide(CSSWideKeyword::Revert(RevertKind::Layer))),var(PropertyDeclaration::Value(999)),var(PropertyDeclaration::Value(700))];
    let priorities=[priority(2,2,2,1),priority(2,2,1,1),priority(1,1,1,1)];
    let decls=declarations(&values,&priorities);let mut c=Cascade::default();let mut cx=computed::Context::default();let mut cache=ShorthandsWithPropertyReferencesCache;let mut attrs=AttributeTracker;
    let mut completion=PriorityCompletion::default();let mut work=MetricDrain::new(&decls);work.request(PrioritaryPropertyId::FontWeight,&mut completion).unwrap();
    assert!(matches!(work.poll(&mut c,&mut cx,&mut cache,&mut attrs,&mut completion,None),MetricDrainStep::Prerequisite(PrioritaryPropertyId::Appearance)));
    assert!(work.continuations.is_empty());
    completion.ensure_ordinary(PrioritaryPropertyId::Appearance,&mut |_|{cx.included_cascade_flags=RuleCascadeFlags(1);ComputationStatus::Ready});
    let MetricDrainStep::References(id,first)=work.poll(&mut c,&mut cx,&mut cache,&mut attrs,&mut completion,None) else {panic!()};
    let MetricDrainStep::References(_,second)=work.poll(&mut c,&mut cx,&mut cache,&mut attrs,&mut completion,Some((id,first))) else {panic!()};
    for _ in 0..3 {assert!(matches!(work.poll(&mut c,&mut cx,&mut cache,&mut attrs,&mut completion,None),MetricDrainStep::References(..)));}
    assert_eq!(c.substitutions.get(),1);assert!(c.publications.is_empty());assert!(!completion.complete.contains(PrioritaryPropertyId::FontWeight));
    assert!(matches!(work.poll(&mut c,&mut cx,&mut cache,&mut attrs,&mut completion,Some((id,second))),MetricDrainStep::Published(PrioritaryPropertyId::FontWeight)));
    assert_eq!(c.substitutions.get(),2);assert_eq!(c.publications.len(),2);assert!(matches!(c.publications[1],PropertyDeclaration::Value(700)));
    assert!(completion.complete.contains(PrioritaryPropertyId::FontWeight));
    assert!(matches!(work.poll(&mut c,&mut cx,&mut cache,&mut attrs,&mut completion,None),MetricDrainStep::Complete));
}

#[test]
fn pending_first_request_does_not_starve_other_metric_property() {
    let values=[var(PropertyDeclaration::Value(700))];let priorities=[priority(2,2,2,0)];let mut decls=declarations(&values,&priorities);
    decls.prioritary_positions[PrioritaryPropertyId::Direction as usize].most_important=DeclarationIndex::MAX;
    let mut c=Cascade::default();let mut cx=computed::Context::default();let mut cache=ShorthandsWithPropertyReferencesCache;let mut attrs=AttributeTracker;let mut completion=PriorityCompletion::default();
    let mut work=MetricDrain::new(&decls);work.request(PrioritaryPropertyId::FontWeight,&mut completion).unwrap();work.request(PrioritaryPropertyId::Direction,&mut completion).unwrap();
    assert!(matches!(work.poll(&mut c,&mut cx,&mut cache,&mut attrs,&mut completion,None),MetricDrainStep::Prerequisite(PrioritaryPropertyId::Appearance)));
    assert!(matches!(work.poll(&mut c,&mut cx,&mut cache,&mut attrs,&mut completion,None),MetricDrainStep::Published(PrioritaryPropertyId::Direction)));
    assert!(completion.complete.contains(PrioritaryPropertyId::Direction));assert!(!completion.complete.contains(PrioritaryPropertyId::FontWeight));
}

#[test]
fn wrong_consumer_reply_and_withdrawn_prerequisite_cannot_publish() {
    let values=[var(PropertyDeclaration::Value(700))];let priorities=[priority(2,2,2,0)];let decls=declarations(&values,&priorities);
    let mut c=Cascade::default();let mut cx=computed::Context::default();let mut cache=ShorthandsWithPropertyReferencesCache;let mut attrs=AttributeTracker;let mut completion=PriorityCompletion::default();
    completion.ensure_ordinary(PrioritaryPropertyId::Appearance,&mut |_|ComputationStatus::Ready);
    let mut work=MetricDrain::new(&decls);work.request(PrioritaryPropertyId::FontWeight,&mut completion).unwrap();
    let MetricDrainStep::References(id,value)=work.poll(&mut c,&mut cx,&mut cache,&mut attrs,&mut completion,None) else {panic!()};
    assert!(matches!(work.poll(&mut c,&mut cx,&mut cache,&mut attrs,&mut completion,Some((PrioritaryPropertyId::FontWidth,value.clone()))),MetricDrainStep::WrongReply));
    completion.complete.remove(PrioritaryPropertyId::Appearance);
    assert!(matches!(work.poll(&mut c,&mut cx,&mut cache,&mut attrs,&mut completion,Some((id,value))),MetricDrainStep::Invalidated(PrioritaryPropertyId::FontWeight)));
    assert_eq!(c.substitutions.get(),0);assert!(c.publications.is_empty());
}

#[test]
fn selected_owner_blocks_ordinary_application_and_accepts_prior_completion() {
    let values=[var(PropertyDeclaration::Value(700))];let priorities=[priority(2,2,2,0)];let decls=declarations(&values,&priorities);
    let mut c=Cascade::default();let mut cx=computed::Context::default();let mut cache=ShorthandsWithPropertyReferencesCache;let mut attrs=AttributeTracker;let mut completion=PriorityCompletion::default();
    completion.ensure_ordinary(PrioritaryPropertyId::Appearance,&mut |_|ComputationStatus::Ready);
    let mut work=MetricDrain::new(&decls);work.request(PrioritaryPropertyId::FontWeight,&mut completion).unwrap();
    let MetricDrainStep::References(id,value)=work.poll(&mut c,&mut cx,&mut cache,&mut attrs,&mut completion,None) else {panic!()};
    let mut rival=MetricDrain::new(&decls);assert!(rival.request(PrioritaryPropertyId::FontWeight,&mut completion).is_err());
    assert_eq!(completion.ensure_ordinary(PrioritaryPropertyId::FontWeight,&mut |_|panic!("second owner")),ComputationStatus::Pending);
    assert!(matches!(work.poll(&mut c,&mut cx,&mut cache,&mut attrs,&mut completion,Some((id,value))),MetricDrainStep::Published(PrioritaryPropertyId::FontWeight)));
    assert_eq!(completion.ensure_ordinary(PrioritaryPropertyId::FontWeight,&mut |_|panic!("reapplication")),ComputationStatus::Ready);
    let mut second=MetricDrain::new(&decls);second.request(PrioritaryPropertyId::FontWeight,&mut completion).unwrap();
    assert!(matches!(second.poll(&mut c,&mut cx,&mut cache,&mut attrs,&mut completion,None),MetricDrainStep::Complete));
    assert_eq!(c.substitutions.get(),1);assert_eq!(c.publications.len(),1);
}
