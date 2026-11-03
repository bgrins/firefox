fn child_source(css: &str, url: u8) -> VariableValue {
    VariableValue::parse(&mut Parser::new(css), None, &UrlExtraData(url)).unwrap()
}
fn child_drive(engine: &mut ResumableSubstitution, context: &mut LookupContext, tracker: &mut AttributeTracker) -> Result<SubstitutionResult<'static>, ()> {
    let mut reply = None;
    loop {
        match engine.poll(reply.take()) {
            SubstitutionPoll::Lookup(request) => {
                let value = context.owned_lookup_value(&request, tracker).unwrap().expect("test child inputs complete");
                reply = Some(SubstitutionLookupReply { identity: request.identity, value });
            }
            SubstitutionPoll::Complete(result) => return result,
            _ => panic!("unexpected child reply"),
        }
    }
}
fn child_run(css: &str, url: u8, context: &mut LookupContext, tracker: &mut AttributeTracker) -> Result<SubstitutionResult<'static>, ()> {
    child_drive(&mut ResumableSubstitution::new(child_source(css, url), None, false), context, tracker)
}
#[test]
fn independent_url_attempts_keep_env_primary_and_fallback_distinct() {
    let mut context = LookupContext::new();
    context.stylist.device.contextual.insert(("metric".into(), 1), child_source("7px", 1));
    let mut tracker = AttributeTracker::default();
    tracker.values.insert("a".into(), "env(metric, 1px)".into());
    for (url, expected) in [(0,"1px"),(1,"7px"),(0,"1px"),(1,"7px")] {
        let result = child_run("attr(a type(<length>))", url, &mut context, &mut tracker).unwrap();
        assert_eq!(result.css, expected);
        assert_eq!(result.attr_taint.0.as_slice(), &[AttrTaintedRange{start:0,end:3}]);
    }
    assert_eq!(tracker.queries.len(), 1);
    assert!(context.functions.attrs.is_empty());
}
#[test]
fn marked_attribute_body_cannot_be_laundered_by_inner_fallback() {
    let mut context = LookupContext::new();let mut tracker = AttributeTracker::default();
    tracker.values.insert("a".into(), "attr(a type(<length>), 2px)".into());
    assert_eq!(child_run("attr(a type(<length>), 9px)", 0, &mut context, &mut tracker).unwrap().css, "9px");
    assert!(child_run("attr(a type(<length>))", 0, &mut context, &mut tracker).is_err());
    tracker.values.insert("b".into(), "7px".into());
    assert_eq!(child_run("attr(a type(<length>), attr(b type(<length>)))", 0, &mut context, &mut tracker).unwrap().css, "7px");
}
#[test]
fn every_participating_attribute_stays_marked_until_its_body_finishes() {
    let mut context = LookupContext::new();let mut tracker = AttributeTracker::default();
    tracker.values.insert("a".into(), "attr(b type(<length>), 4px)".into());
    tracker.values.insert("b".into(), "attr(a type(<length>), 3px)".into());
    assert_eq!(child_run("attr(a type(<length>), 9px)", 0, &mut context, &mut tracker).unwrap().css, "9px");
}
#[test]
fn context_local_cycle_does_not_poison_independent_primary_context() {
    for order in [[0,1],[1,0]] {
        let mut context = LookupContext::new();let mut tracker = AttributeTracker::default();
        context.stylist.device.contextual.insert(("metric".into(),1), child_source("7px",1));
        tracker.values.insert("a".into(), "env(metric, attr(a type(<length>), 2px))".into());
        for url in order {
            assert_eq!(child_run("attr(a type(<length>), 9px)",url,&mut context,&mut tracker).unwrap().css, if url==1 {"7px"} else {"9px"});
        }
        assert_eq!(tracker.queries.len(),1);
    }
}
#[test]
fn child_pending_retains_raw_snapshot_guard_and_exact_request() {
    let mut context=LookupContext::new();let mut tracker=AttributeTracker::default();
    tracker.values.insert("a".into(),"var(--ready, attr(fallback type(<length>)))".into());
    context.lookup_bindings.pending.insert("ready".into());
    let mut engine=ResumableSubstitution::new(tokens("attr(a type(<length>), 9px)"),None,false);
    let mut reply=None;
    let waiting=loop {
        let SubstitutionPoll::Lookup(request)=engine.poll(reply.take()) else {panic!("premature finish")};
        match context.owned_lookup_value(&request,&mut tracker).unwrap() {
            Some(value)=>reply=Some(SubstitutionLookupReply{identity:request.identity,value}),
            None=>break request,
        }
    };
    assert_eq!(waiting.name,"ready");assert_eq!(engine.guards.len(),1);
    assert!(Arc::ptr_eq(waiting.attribute_attempt.as_ref().unwrap(),&engine.guards[0].identity));
    for _ in 0..3 {
        let SubstitutionPoll::Lookup(again)=engine.poll(Some(SubstitutionLookupReply{identity:waiting.identity.clone(),value:SubstitutionLookupValue::Pending})) else {panic!("pending became fallback")};
        assert!(Arc::ptr_eq(&again.identity,&waiting.identity));
    }
    assert_eq!(tracker.queries.len(),1);
    tracker.values.insert("a".into(),"30px".into());
    context.lookup_bindings.pending.clear();
    context.lookup_bindings.values.insert("ready".into(),Some(ComputedRegisteredValue{value:tokens("20px"),attr_tainted:false}));
    let result=child_drive(&mut engine,&mut context,&mut tracker).unwrap();
    assert_eq!(result.css,"20px");assert!(engine.guards.is_empty());assert_eq!(tracker.queries.len(),1);
}
#[test]
fn child_wrong_url_reply_is_not_consumed() {
    let mut engine=ResumableSubstitution::new(child_source("attr(a type(<length>))",2),None,false);
    let SubstitutionPoll::Lookup(raw)=engine.poll(None) else {panic!()};
    let SubstitutionPoll::Lookup(typed)=engine.poll(Some(SubstitutionLookupReply{identity:raw.identity,value:SubstitutionLookupValue::Attribute(Some("20px".into()))})) else {panic!()};
    assert!(matches!(engine.poll(Some(SubstitutionLookupReply{identity:typed.identity.clone(),value:SubstitutionLookupValue::AttributeSource(child_source("20px",1))})),SubstitutionPoll::WrongReply));
    let SubstitutionPoll::Complete(Ok(result))=engine.poll(Some(SubstitutionLookupReply{identity:typed.identity,value:SubstitutionLookupValue::AttributeSource(child_source("20px",2))})) else {panic!()};
    assert_eq!(result.css,"20px");
}
#[test]
fn thousands_of_attribute_children_use_iterative_frames_on_small_thread_stack() {
    std::thread::Builder::new().stack_size(256*1024).spawn(|| {
        let mut context=LookupContext::new();let mut tracker=AttributeTracker::default();
        for i in 0..4096 {tracker.values.insert(format!("a{i}"),if i==4095 {"20px".into()} else {format!("attr(a{} type(<length>))",i+1)});}
        assert_eq!(child_run("attr(a0 type(<length>))",0,&mut context,&mut tracker).unwrap().css,"20px");
        assert_eq!(tracker.queries.len(),4096);
    }).unwrap().join().unwrap();
}
#[test]
fn child_result_preserves_utf8_separator_and_taint_offsets() {
    let mut context=LookupContext::new();let mut tracker=AttributeTracker::default();
    tracker.values.insert("a".into(),"var(--size)".into());
    context.lookup_bindings.values.insert("size".into(),Some(ComputedRegisteredValue{value:tokens("2px"),attr_tainted:false}));
    let result=child_run("é attr(a type(<length>))foo",0,&mut context,&mut tracker).unwrap();
    assert_eq!(result.css,"é 2px/**/foo");
    assert_eq!(result.attr_taint.0.as_slice(),&[AttrTaintedRange{start:3,end:6}]);
}
#[test]
fn expanded_child_still_enforces_existing_output_limit() {
    let mut context=LookupContext::new();let mut tracker=AttributeTracker::default();
    tracker.values.insert("a".into(),"var(--big) var(--big)".into());
    context.lookup_bindings.values.insert("big".into(),Some(ComputedRegisteredValue{value:tokens(&"a".repeat(1024*1024)),attr_tainted:false}));
    assert_eq!(child_run("attr(a type(*), 9px)",0,&mut context,&mut tracker).unwrap().css,"9px");
}

#[test]
fn unscoped_graph_cycle_is_not_css_invalid_and_active_graph_is_pending() {
    let mut context=LookupContext::new();let mut tracker=AttributeTracker::default();
    tracker.values.insert("a".into(),"20px".into());
    let typed=request(SubstitutionLookupKind::TypedAttribute,"a",0);
    context.nodes.insert(VarType::Attr("a".into(),String::new()),VisitResult::CycleSettled);
    assert!(context.owned_lookup_value(&typed,&mut tracker).is_err());
    context.nodes.insert(VarType::Attr("a".into(),String::new()),VisitResult::SemanticOpen(0));
    assert!(matches!(context.owned_lookup_value(&typed,&mut tracker),Ok(None)));
    assert!(tracker.queries.is_empty());
}
#[test]
fn completed_custom_default_is_authoritative_but_cannot_clear_active_attribute_marks() {
    let mut context=LookupContext::new();let mut tracker=AttributeTracker::default();
    context.lookup_bindings.values.insert("b".into(),Some(ComputedRegisteredValue{value:tokens("8px"),attr_tainted:false}));
    context.nodes.insert(VarType::Custom("b".into()),VisitResult::CycleSettled);
    tracker.values.insert("a".into(),"attr(a type(<length>), var(--b))".into());
    tracker.values.insert("other".into(),"var(--b)".into());
    assert_eq!(child_run("attr(a type(<length>), 9px)",0,&mut context,&mut tracker).unwrap().css,"9px");
    assert_eq!(child_run("attr(other type(<length>))",0,&mut context,&mut tracker).unwrap().css,"8px");
    assert_eq!(context.lookup_bindings.values["b"].as_ref().unwrap().value.css,"8px");
}
