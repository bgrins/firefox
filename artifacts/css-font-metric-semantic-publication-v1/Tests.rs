#[test]
fn retains_payload_until_ready_and_does_not_publish_twice() {
    let mut state = NodePublication::SemanticOpen;
    state.close(Box::new(23));
    assert_eq!(state.readiness(), NodeReadiness::ComputationPending);
    for _ in 0..2 { assert!(state.take_ready(false).is_none()); }
    assert!(!state.can_retire());
    assert_eq!(*state.take_ready(true).unwrap(),23);
    assert_eq!(state.readiness(),NodeReadiness::ComputationPending);
    assert!(!state.can_retire());
    state.finish(); assert!(state.can_retire());
    assert!(std::panic::catch_unwind(std::panic::AssertUnwindSafe(||state.take_ready(true))).is_err());
}
#[test]
fn actual_publication_routes_preserve_payload_and_reentrant_status() {
    let mut output=Observations::default(); let mut c=Context::new(&mut output);
    let a=c.insert(VarType::Custom(1)); let b=c.insert(VarType::Attr(2,4)); let d=c.insert(VarType::NonCustom(1));
    c.stack.clear(); for row in &mut c.var_info {row.var.take();}
    c.var_info[a].publication.close(ClosedValue::Prepared(1,PreparedCustomValue(41)));
    c.var_info[b].publication.close(ClosedValue::Substitute(VarType::Attr(2,4),Arc::new(ComputedPropertyValue(52))));
    c.var_info[d].publication.close(ClosedValue::Prioritary(1));
    assert_eq!(c.visited(&VarType::Custom(1)),Some(VisitResult::ComputationPending(a)));
    assert_eq!(c.visited(&VarType::Attr(2,4)),Some(VisitResult::ComputationPending(b)));
    c.publish_closed(a,&mut ());c.publish_closed(b,&mut ());c.publish_closed(d,&mut ());
    assert_eq!(c.computed_context.applied,vec![(1,None,41),(2,Some(4),52),(101,None,1)]);
    assert_eq!(c.visited(&VarType::Custom(1)),Some(VisitResult::Complete));
    c.reset(); assert!(c.var_info.is_empty());
}
#[test]
fn reset_rejects_closed_pending_and_applying() {
    let mut output=Observations::default();let mut c=Context::new(&mut output);
    let i=c.insert(VarType::Custom(1));c.stack.clear();c.var_info[i].var.take();
    c.var_info[i].publication.close(ClosedValue::Prepared(1,PreparedCustomValue(41)));
    assert!(std::panic::catch_unwind(std::panic::AssertUnwindSafe(||c.reset())).is_err());
    assert_eq!(c.count,1);
    c.var_info[i].publication.take_ready(true).unwrap();
    assert!(std::panic::catch_unwind(std::panic::AssertUnwindSafe(||c.reset())).is_err());
    c.var_info[i].publication.finish();c.reset();
}
#[test]
fn component_cycle_certificate_follows_all_map_outcomes() {
    let mut output=Observations::default();let mut c=Context::new(&mut output);
    let root=VarType::Custom(1);c.insert(root.clone());c.insert(VarType::Attr(2,4));
    assert_eq!(pop_component(&mut c,0,root,false),VisitResult::CycleSettled);
    assert_eq!(c.computed_context.cycle_steps.len(),2);
    assert!(c.computed_context.cycle_steps.iter().flatten().all(|r|*r!=NodeReadiness::CycleSettled));
    assert!(c.computed_context.cycle_steps.last().unwrap().iter().all(|r|*r==NodeReadiness::ComputationPending));
    assert_eq!(c.visited(&VarType::Custom(1)),Some(VisitResult::CycleSettled));
    assert_eq!(c.visited(&VarType::Attr(2,4)),Some(VisitResult::CycleSettled));
    c.reset();
}
#[test]
fn semantic_indices_do_not_encode_scheduling_waits() {
    assert_eq!(link_result(VisitResult::SemanticOpen(5)),Some(5));
    assert_eq!(link_result(VisitResult::Complete),None);
    assert_eq!(link_result(VisitResult::CycleSettled),None);
    assert!(std::panic::catch_unwind(||link_result(VisitResult::ComputationPending(5))).is_err());
}
