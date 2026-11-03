fn tokens(css:&str)->VariableValue {VariableValue::parse(&mut Parser::new(css),None,&UrlExtraData(0)).unwrap()}
fn dynamic(id:LonghandId,css:&str)->PropertyDeclaration{PropertyDeclaration::WithVariables(VariableDeclaration{id,value:Arc::new(UnparsedValue{variable_value:tokens(css),from_shorthand:None})})}
fn declarations<'a>(values:&'a [PropertyDeclaration],levels:&[u8])->Declarations<'a>{Declarations{longhand_declarations:values.iter().enumerate().map(|(i,decl)|Declaration{decl,priority:CascadePriority{level:levels[i],flags:RuleCascadeFlags::empty()},next_index:if i+1<values.len(){(i+1)as DeclarationIndex}else{0}}).collect(),prioritary_positions:[DeclarationPosition{most_important:0};5]}}
fn reference(step:MetricPreparationStep,generation:&Arc<()>)->FontSelectionReply{match step{MetricPreparationStep::References(_,value)=>FontSelectionReply{value,generation:generation.clone(),lookup:None},_=>panic!("expected references")}}
fn lookup(step:MetricPreparationStep)->(Arc<UnparsedValue>,SubstitutionLookup){match step{MetricPreparationStep::Lookup(_,value,request)=>(value,request),_=>panic!("expected lookup")}}
fn answer(value:&Arc<UnparsedValue>,request:&SubstitutionLookup,generation:&Arc<()>,reply:SubstitutionLookupValue)->Option<FontSelectionReply>{Some(FontSelectionReply{value:value.clone(),generation:generation.clone(),lookup:Some(SubstitutionLookupReply{identity:request.identity.clone(),value:reply})})}
fn numeric(state:&MetricPreparation)->f32{match &state.prepared.last().unwrap().declaration{PropertyDeclaration::Number(_,n)=>*n,_=>panic!("not numeric")}}

#[test]
fn actual_caller_retains_pending_without_fallback_parse_or_restarting_effects(){
    PARSES.with(|n|n.set(0));let values=[dynamic(LonghandId::Appearance,"var(--main, var(--fallback))")];let decls=declarations(&values,&[2]);
    let cascade=Cascade::default();let mut context=computed::Context::default();let mut cache=ShorthandsWithPropertyReferencesCache::default();let mut tracker=AttributeTracker::default();let mut state=cascade.begin_font_preparation(&context,&decls,LonghandId::Appearance);let generation=Arc::new(());
    let step=cascade.resume_font_selection(&mut context,&mut cache,&mut tracker,&mut state,None);let reply=reference(step,&generation);
    let (value,request)=lookup(cascade.resume_font_selection(&mut context,&mut cache,&mut tracker,&mut state,Some(reply)));assert_eq!(request.name,"main");
    for _ in 0..3{let (_,again)=lookup(cascade.resume_font_selection(&mut context,&mut cache,&mut tracker,&mut state,answer(&value,&request,&generation,SubstitutionLookupValue::Pending)));assert!(Arc::ptr_eq(&request.identity,&again.identity));}
    assert_eq!(state.cursor,Some(0));assert!(state.prepared.is_empty());assert_eq!(context.rule_cache_conditions.borrow().marks,1);PARSES.with(|n|assert_eq!(n.get(),0));assert!(cache.is_empty());
    let step=cascade.resume_font_selection(&mut context,&mut cache,&mut tracker,&mut state,answer(&value,&request,&generation,SubstitutionLookupValue::Value(tokens("20px"),false)));assert!(matches!(step,MetricPreparationStep::Complete));assert_eq!(numeric(&state),20.0);PARSES.with(|n|assert_eq!(n.get(),1));assert!(state.substitution.is_none());
}

#[test]
fn settled_invalid_uses_actual_fallback_then_shared_parser_once(){
    PARSES.with(|n|n.set(0));let values=[dynamic(LonghandId::FontSize,"var(--missing, 30px)")];let decls=declarations(&values,&[2]);let cascade=Cascade::default();let mut context=computed::Context::default();let mut cache=ShorthandsWithPropertyReferencesCache::default();let mut tracker=AttributeTracker::default();let mut state=cascade.begin_font_preparation(&context,&decls,LonghandId::FontSize);let generation=Arc::new(());
    let reply=reference(cascade.resume_font_selection(&mut context,&mut cache,&mut tracker,&mut state,None),&generation);let(value,request)=lookup(cascade.resume_font_selection(&mut context,&mut cache,&mut tracker,&mut state,Some(reply)));
    assert!(matches!(cascade.resume_font_selection(&mut context,&mut cache,&mut tracker,&mut state,answer(&value,&request,&generation,SubstitutionLookupValue::Invalid)),MetricPreparationStep::Complete));assert_eq!(numeric(&state),30.0);PARSES.with(|n|assert_eq!(n.get(),1));
}

#[test]
fn wrong_raw_arc_and_generation_cannot_complete_selected_entry(){
    let values=[dynamic(LonghandId::FontSize,"var(--size)")];let decls=declarations(&values,&[2]);let cascade=Cascade::default();let mut context=computed::Context::default();let mut cache=ShorthandsWithPropertyReferencesCache::default();let mut tracker=AttributeTracker::default();let mut state=cascade.begin_font_preparation(&context,&decls,LonghandId::FontSize);let generation=Arc::new(());
    let reply=reference(cascade.resume_font_selection(&mut context,&mut cache,&mut tracker,&mut state,None),&generation);let(value,request)=lookup(cascade.resume_font_selection(&mut context,&mut cache,&mut tracker,&mut state,Some(reply)));
    let wrong=Arc::new((*value).clone());assert!(matches!(cascade.resume_font_selection(&mut context,&mut cache,&mut tracker,&mut state,answer(&wrong,&request,&generation,SubstitutionLookupValue::Value(tokens("20px"),false))),MetricPreparationStep::Invalidated));
    assert!(matches!(cascade.resume_font_selection(&mut context,&mut cache,&mut tracker,&mut state,answer(&value,&request,&Arc::new(()),SubstitutionLookupValue::Value(tokens("20px"),false))),MetricPreparationStep::Invalidated));assert!(state.prepared.is_empty());
    let wrong_request=SubstitutionLookupReply{identity:Arc::new(()),value:SubstitutionLookupValue::Value(tokens("20px"),false)};
    assert!(matches!(cascade.resume_font_selection(&mut context,&mut cache,&mut tracker,&mut state,Some(FontSelectionReply{value:value.clone(),generation:generation.clone(),lookup:Some(wrong_request)})),MetricPreparationStep::Invalidated));
}

#[test]
fn dynamic_rollback_retains_its_value_and_skips_ineligible_dynamic_loser(){
    let values=[dynamic(LonghandId::FontSize,"var(--rollback)"),dynamic(LonghandId::FontSize,"var(--loser)"),PropertyDeclaration::Number(LonghandId::FontSize,30.0)];let decls=declarations(&values,&[2,2,1]);let cascade=Cascade::default();let mut context=computed::Context::default();let mut cache=ShorthandsWithPropertyReferencesCache::default();let mut tracker=AttributeTracker::default();let mut state=cascade.begin_font_preparation(&context,&decls,LonghandId::FontSize);let generation=Arc::new(());
    let reply=reference(cascade.resume_font_selection(&mut context,&mut cache,&mut tracker,&mut state,None),&generation);let(value,request)=lookup(cascade.resume_font_selection(&mut context,&mut cache,&mut tracker,&mut state,Some(reply)));
    assert!(matches!(cascade.resume_font_selection(&mut context,&mut cache,&mut tracker,&mut state,answer(&value,&request,&generation,SubstitutionLookupValue::Value(tokens("revert-layer"),false))),MetricPreparationStep::Complete));assert_eq!(state.prepared.len(),2);assert_eq!(numeric(&state),30.0);assert_eq!(state.cursor,Some(2));
}

#[test]
fn typed_attr_raw_query_and_each_url_parse_are_retained_separately(){
    let mut tracker=AttributeTracker::default();tracker.values.insert("size".into(),"20px".into());let name="size".to_string();let ns=String::new();let mut input=CapturedAttributeInput::query(&name,&ns,&mut tracker);
    tracker.values.insert(name.clone(),"30px".into());
    let first=input.parse(&UrlExtraData(1)).unwrap();let second=input.parse(&UrlExtraData(2)).unwrap();let repeated=input.parse(&UrlExtraData(1)).unwrap();assert_eq!(tracker.queries.len(),1);assert_eq!(input.parsed.len(),2);assert_eq!(first.value.css,"20px");assert_eq!(first.value.url_data,UrlExtraData(1));assert_eq!(second.value.url_data,UrlExtraData(2));assert_eq!(repeated.value.url_data,UrlExtraData(1));
    let mut typed_first=CapturedAttributeInput::query(&name,&ns,&mut tracker);typed_first.parse(&UrlExtraData(2)).unwrap();assert_eq!(typed_first.raw.as_deref(),Some("30px"));typed_first.parse(&UrlExtraData(1)).unwrap();assert_eq!(typed_first.parsed.len(),2);
}

#[test]
fn real_engine_typed_attr_pending_keeps_taint_until_shared_parse_tail(){
    PARSES.with(|n|n.set(0));let values=[dynamic(LonghandId::FontSize,"attr(data-size type(<length>), 9px)")];let decls=declarations(&values,&[2]);let cascade=Cascade::default();let mut context=computed::Context::default();let mut cache=ShorthandsWithPropertyReferencesCache::default();let mut tracker=AttributeTracker::default();let mut state=cascade.begin_font_preparation(&context,&decls,LonghandId::FontSize);let generation=Arc::new(());
    let reply=reference(cascade.resume_font_selection(&mut context,&mut cache,&mut tracker,&mut state,None),&generation);let(value,raw)=lookup(cascade.resume_font_selection(&mut context,&mut cache,&mut tracker,&mut state,Some(reply)));assert!(matches!(raw.kind,SubstitutionLookupKind::RawAttribute));
    let(_,typed)=lookup(cascade.resume_font_selection(&mut context,&mut cache,&mut tracker,&mut state,answer(&value,&raw,&generation,SubstitutionLookupValue::Attribute(Some("20px".into())))));assert!(matches!(typed.kind,SubstitutionLookupKind::TypedAttribute));
    let(_,again)=lookup(cascade.resume_font_selection(&mut context,&mut cache,&mut tracker,&mut state,answer(&value,&typed,&generation,SubstitutionLookupValue::Pending)));assert!(Arc::ptr_eq(&typed.identity,&again.identity));PARSES.with(|n|assert_eq!(n.get(),0));
    assert!(matches!(cascade.resume_font_selection(&mut context,&mut cache,&mut tracker,&mut state,answer(&value,&typed,&generation,SubstitutionLookupValue::Value(tokens("20px"),true))),MetricPreparationStep::Complete));assert_eq!(numeric(&state),20.0);LAST_TAINT.with(|v|assert_eq!(*v.borrow(),vec![(0,4)]));
}

fn declaration_key(d:&PropertyDeclaration)->String{match d{PropertyDeclaration::Number(id,n)=>format!("{id:?}:{n}"),PropertyDeclaration::Wide(id,k)=>format!("{id:?}:{k:?}"),_=>panic!("unresolved")}}
#[test]
fn actual_synchronous_and_retained_callers_share_parse_and_cache_results(){
    for css in ["var(--size)","var(--absent, 30px)","var(--empty)","var(--wide)","env(test-size)","attr(data-size type(<length>), 9px)"] {
        let mut functions=ComputedSubstitutionFunctions::default();
        for(name,text)in [("size","20px"),("empty",""),("wide","initial")] {functions.vars.insert(name.into(),ComputedRegisteredValue{value:tokens(text),attr_tainted:false});}
        functions.attrs.insert("data-size".into(),ComputedRegisteredValue{value:tokens("20px"),attr_tainted:true});
        let mut stylist=Stylist::default();stylist.device.values.insert("test-size".into(),tokens("30px"));
        let mut tracker=AttributeTracker::default();tracker.values.insert("data-size".into(),"20px".into());
        let values=[dynamic(LonghandId::FontSize,css)];let PropertyDeclaration::WithVariables(variable)=&values[0] else{unreachable!()};let decls=declarations(&values,&[2]);
        let mut context=computed::Context::default();let mut sync_cache=ShorthandsWithPropertyReferencesCache::default();
        let expected=variable.substitute_variables(&functions,&stylist,&context,&mut sync_cache,&mut tracker).into_owned();
        let cascade=Cascade::default();let mut cache=ShorthandsWithPropertyReferencesCache::default();let mut state=cascade.begin_font_preparation(&context,&decls,LonghandId::FontSize);let generation=Arc::new(());
        let mut reply=None;
        loop {match cascade.resume_font_selection(&mut context,&mut cache,&mut tracker,&mut state,reply.take()) {
            MetricPreparationStep::References(_,value)=>reply=Some(FontSelectionReply{value,generation:generation.clone(),lookup:None}),
            MetricPreparationStep::Lookup(_,value,request)=>reply=Some(FontSelectionReply{value,generation:generation.clone(),lookup:Some(request.read_current(&functions,&stylist,&mut tracker))}),
            MetricPreparationStep::Complete=>break,
            _=>panic!("unexpected readiness"),
        }}
        assert_eq!(declaration_key(&state.prepared.last().unwrap().declaration),declaration_key(&expected),"{css}");
    }
}

#[test]
fn shorthand_cache_is_inserted_only_after_complete_and_requires_source_arc(){
    PARSES.with(|n|n.set(0));let mut declaration=dynamic(LonghandId::FontSize,"var(--size)");
    let PropertyDeclaration::WithVariables(v)=&mut declaration else{unreachable!()};v.value=Arc::new(UnparsedValue{variable_value:tokens("var(--size)"),from_shorthand:Some(ShorthandId::Font)});
    let values=[declaration];let decls=declarations(&values,&[2]);let cascade=Cascade::default();let mut context=computed::Context::default();let mut cache=ShorthandsWithPropertyReferencesCache::default();let mut tracker=AttributeTracker::default();let mut state=cascade.begin_font_preparation(&context,&decls,LonghandId::FontSize);let generation=Arc::new(());
    let reply=reference(cascade.resume_font_selection(&mut context,&mut cache,&mut tracker,&mut state,None),&generation);let(value,request)=lookup(cascade.resume_font_selection(&mut context,&mut cache,&mut tracker,&mut state,Some(reply)));
    lookup(cascade.resume_font_selection(&mut context,&mut cache,&mut tracker,&mut state,answer(&value,&request,&generation,SubstitutionLookupValue::Pending)));assert!(cache.is_empty());
    assert!(matches!(cascade.resume_font_selection(&mut context,&mut cache,&mut tracker,&mut state,answer(&value,&request,&generation,SubstitutionLookupValue::Value(tokens("20px"),false))),MetricPreparationStep::Complete));assert_eq!(cache.len(),1);
    let PropertyDeclaration::WithVariables(v)=&values[0] else{unreachable!()};assert!(v.begin_retained_substitution(&context,&cache).is_err());
    let other=VariableDeclaration{id:v.id,value:Arc::new((*v.value).clone())};assert!(other.begin_retained_substitution(&context,&cache).is_ok());PARSES.with(|n|assert_eq!(n.get(),1));
}

fn request(kind:SubstitutionLookupKind,name:&str,url:u8)->SubstitutionLookup{SubstitutionLookup{guards:Vec::new(),kind,name:name.into(),identity:Arc::new(()),attribute_attempt:None,namespace:Some(String::new()),url_data:UrlExtraData(url)}}
#[test]
fn production_lookup_distinguishes_initial_absence_pending_and_cycle_default(){
    let mut context=LookupContext::new();let mut tracker=AttributeTracker::default();let r=request(SubstitutionLookupKind::Variable,"x",0);
    assert!(matches!(context.owned_lookup_value(&r,&mut tracker),Ok(Some(SubstitutionLookupValue::Invalid))));
    context.lookup_bindings.pending.insert("x".into());assert!(matches!(context.owned_lookup_value(&r,&mut tracker),Ok(None)));
    context.lookup_bindings.pending.clear();context.lookup_bindings.values.insert("x".into(),Some(ComputedRegisteredValue{value:tokens("2px"),attr_tainted:false}));
    context.nodes.insert(VarType::Custom("x".into()),VisitResult::ComputationPending(0));assert!(matches!(context.owned_lookup_value(&r,&mut tracker),Ok(None)));
    context.nodes.insert(VarType::Custom("x".into()),VisitResult::CycleSettled);
    match context.owned_lookup_value(&r,&mut tracker).unwrap().unwrap(){SubstitutionLookupValue::Value(v,_)=>assert_eq!(v.css,"2px"),_=>panic!("registered cycle default")}
}

#[test]
fn production_attribute_lookup_returns_owned_source_per_url_without_global_publication() {
    let mut context=LookupContext::new();let mut tracker=AttributeTracker::default();tracker.values.insert("x".into(),"20px".into());
    let raw=request(SubstitutionLookupKind::RawAttribute,"x",1);
    assert!(matches!(context.owned_lookup_value(&raw,&mut tracker),Ok(Some(SubstitutionLookupValue::Attribute(Some(_))))));
    context.cascade.attribute_value_urls.insert(("x".into(),String::new()),UrlExtraData(3));
    for url in [2,1,2] {
        let typed=request(SubstitutionLookupKind::TypedAttribute,"x",url);
        match context.owned_lookup_value(&typed,&mut tracker).unwrap().unwrap() {
            SubstitutionLookupValue::AttributeSource(value)=>{
                assert_eq!(value.css,"20px");assert_eq!(value.url_data,UrlExtraData(url));
            },_=>panic!("not raw child source"),
        }
    }
    assert_eq!(tracker.queries.len(),1);assert!(context.functions.attrs.is_empty());
    assert_eq!(context.cascade.attribute_inputs[&("x".into(),String::new())].parsed.len(),2);
}

#[test]
fn production_raw_namespace_missing_and_environment_snapshot_keep_distinct_paths(){
    let mut context=LookupContext::new();let mut tracker=AttributeTracker::default();let mut unknown=request(SubstitutionLookupKind::RawAttribute,"x",1);unknown.namespace=None;
    assert!(matches!(context.owned_lookup_value(&unknown,&mut tracker),Ok(Some(SubstitutionLookupValue::Attribute(None)))));assert!(tracker.queries.is_empty());
    let missing=request(SubstitutionLookupKind::RawAttribute,"x",1);assert!(matches!(context.owned_lookup_value(&missing,&mut tracker),Ok(Some(SubstitutionLookupValue::Attribute(None)))));assert_eq!(tracker.queries.len(),1);
    assert!(context.owned_lookup_value(&request(SubstitutionLookupKind::TypedAttribute,"x",1),&mut tracker).is_err());
    context.stylist.device.values.insert("size".into(),tokens("20px"));let env=request(SubstitutionLookupKind::Environment,"size",1);
    context.owned_lookup_value(&env,&mut tracker).unwrap();context.stylist.device.values.insert("size".into(),tokens("30px"));
    match context.owned_lookup_value(&env,&mut tracker).unwrap().unwrap(){SubstitutionLookupValue::Value(v,_)=>assert_eq!(v.css,"20px"),_=>panic!("environment")};
}
