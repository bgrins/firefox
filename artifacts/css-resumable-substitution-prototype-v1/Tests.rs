fn value(css:&str)->VariableValue {
    VariableValue::parse(&mut Parser::new(css),None,&UrlExtraData).unwrap()
}
fn put(map:&mut FxHashMap<Name,ComputedRegisteredValue>,name:&str,css:&str,taint:bool) {
    map.insert(name.strip_prefix("--").unwrap_or(name).into(),ComputedRegisteredValue{value:value(css),attr_tainted:taint});
}
fn normalize(result:Result<SubstitutionResult<'_>,()>)->Result<(String,Vec<(usize,usize)>),()> {
    result.map(|r|(r.css.into_owned(),r.attr_taint.0.iter().map(|r|(r.start,r.end)).collect()))
}
fn drain(mut machine:ResumableSubstitution,functions:&ComputedSubstitutionFunctions,stylist:&Stylist,tracker:&mut AttributeTracker,pause:bool)->Result<(String,Vec<(usize,usize)>),()> {
    let mut poll=machine.poll(None);
    loop {match poll {
        SubstitutionPoll::Lookup(request)=>{
            if pause {
                for _ in 0..3 {
                    let again=machine.poll(Some(SubstitutionLookupReply{identity:request.identity.clone(),value:SubstitutionLookupValue::Pending}));
                    let SubstitutionPoll::Lookup(again)=again else {panic!("pending advanced")};
                    assert!(std::ptr::eq(again.identity.as_ref(),request.identity.as_ref()));
                }
            }
            poll=machine.poll(Some(request.read_current(functions,stylist,tracker)));
        },
        SubstitutionPoll::Complete(result)=>{
            assert!(matches!(machine.poll(None),SubstitutionPoll::Finished));
            return normalize(result);
        },
        _=>panic!("unexpected poll"),
    }}
}
fn compare(css:&str,functions:&ComputedSubstitutionFunctions,stylist:&Stylist,attrs:&[(String,String)],container:bool) {
    let v=value(css);
    let mut old_tracker=AttributeTracker{values:attrs.iter().cloned().collect(),queries:Vec::new()};
    let old=normalize(substitute(&v,Some("font-size"),functions,stylist,&computed::Context{in_container_query:container},&mut old_tracker));
    for pause in [false,true] {
        let mut tracker=AttributeTracker{values:attrs.iter().cloned().collect(),queries:Vec::new()};
        let new=drain(ResumableSubstitution::new(v.clone(),Some("font-size"),container),functions,stylist,&mut tracker,pause);
        assert_eq!(old,new,"{css}");assert_eq!(old_tracker.queries,tracker.queries,"query trace {css}");
    }
}

#[test]
fn complete_var_env_fallback_and_empty_equivalence() {
    let mut f=ComputedSubstitutionFunctions::default();
    for (name,css) in [("--a","foo"),("--b","bar"),("--empty",""),("--nested","var(--a)var(--missing, var(--b))")] {put(&mut f.vars,name,css,false)}
    assert_eq!(drain(ResumableSubstitution::new(value("var(--nested)"),None,false),&f,&Stylist::default(),&mut AttributeTracker::default(),true),Ok(("foo/**/bar".into(),vec![])));
    let mut s=Stylist::default();s.device.values.insert("test".into(),value("12px"));
    for css in ["var(--a)","var(--a)var(--empty)var(--b)","var(--nested)","env(test)","env(absent,var(--a))","var(--missing,)","var(--missing)","x var(--a) y env(test) z","var(--a,attr(unused raw-string))"] {compare(css,&f,&s,&[],false)}
}

#[test]
fn attr_forms_and_taint_equivalence() {
    let mut f=ComputedSubstitutionFunctions::default();put(&mut f.attrs,"length","20px",false);
    let attrs=vec![("text".into(),"a\"b".into()),("n".into()," 2.5 ".into()),("length".into(),"20px".into()),("bad".into(),"no".into())];
    for css in ["attr(text)","attr(missing)","attr(missing, fallback)","attr(text raw-string)","attr(n px)","attr(n %)","attr(n number)","attr(bad px,7px)","attr(text unknown,9px)","attr(length type(<length>))","attr(length type(<number>),8)","a attr(n px)var(--missing,attr(text)) z"] {compare(css,&f,&Stylist::default(),&attrs,false)}
    compare("attr(length type(<length>))",&ComputedSubstitutionFunctions::default(),&Stylist::default(),&attrs,true);
}

#[test]
fn typed_attribute_raw_query_is_not_repeated() {
    let mut f=ComputedSubstitutionFunctions::default();put(&mut f.attrs,"length","20px",false);
    let s=Stylist::default();let mut t=AttributeTracker::default();t.values.insert("length".into(),"20px".into());
    let mut m=ResumableSubstitution::new(value("attr(length type(<length>))"),None,false);
    let SubstitutionPoll::Lookup(raw)=m.poll(None) else {panic!()};assert_eq!(raw.kind,SubstitutionLookupKind::RawAttribute);
    let SubstitutionPoll::Lookup(cache)=m.poll(Some(raw.read_current(&f,&s,&mut t))) else {panic!()};assert_eq!(cache.kind,SubstitutionLookupKind::TypedAttribute);
    assert_eq!(t.queries.len(),1);t.values.remove("length");
    for _ in 0..4 {assert!(matches!(m.poll(Some(SubstitutionLookupReply{identity:cache.identity.clone(),value:SubstitutionLookupValue::Pending})),SubstitutionPoll::Lookup(_)));}
    let SubstitutionPoll::Complete(result)=m.poll(Some(cache.read_current(&f,&s,&mut t))) else {panic!()};
    assert_eq!(normalize(result),Ok(("20px".into(),vec![(0,4)])));assert_eq!(t.queries.len(),1);
}

#[test]
fn prefix_pause_preserves_output_and_does_not_choose_fallback() {
    let mut f=ComputedSubstitutionFunctions::default();let s=Stylist::default();let mut t=AttributeTracker::default();
    t.values.insert("prefix".into(),"old".into());t.values.insert("fallback".into(),"wrong".into());
    let mut m=ResumableSubstitution::new(value("attr(prefix raw-string) var(--later,attr(fallback raw-string))"),None,false);
    let SubstitutionPoll::Lookup(prefix)=m.poll(None) else {panic!()};
    let SubstitutionPoll::Lookup(later)=m.poll(Some(prefix.read_current(&f,&s,&mut t))) else {panic!()};
    assert_eq!(later.name,"later");assert_eq!(t.queries.len(),1);
    for _ in 0..4 {assert!(matches!(m.poll(None),SubstitutionPoll::Lookup(_)));}
    t.values.insert("prefix".into(),"changed".into());put(&mut f.vars,"--later","20px",false);
    let SubstitutionPoll::Complete(result)=m.poll(Some(later.read_current(&f,&s,&mut t))) else {panic!()};
    assert_eq!(normalize(result),Ok(("\"old\" 20px".into(),vec![(0,5)])));assert_eq!(t.queries.len(),1);
}

#[test]
fn alias_cycle_and_invalid_fallback_match_old() {
    let mut f=ComputedSubstitutionFunctions::default();put(&mut f.vars,"--a","var(--b,red)",false);put(&mut f.vars,"--b","var(--a,blue)",true);
    compare("var(--a)",&f,&Stylist::default(),&[],false);
    assert_eq!(drain(ResumableSubstitution::new(value("var(--a)"),None,false),&f,&Stylist::default(),&mut AttributeTracker::default(),true),Ok(("blue".into(),vec![(0,4)])));
    put(&mut f.vars,"--a","var(--b)",false);put(&mut f.vars,"--b","var(--a)",false);
    compare("var(--a,green)",&f,&Stylist::default(),&[],false);
}

#[test]
fn reply_identity_and_kind_are_checked_without_advancing() {
    let mut m=ResumableSubstitution::new(value("var(--a)"),None,false);
    let SubstitutionPoll::Lookup(r)=m.poll(None) else {panic!()};
    assert!(matches!(m.poll(Some(SubstitutionLookupReply{identity:Arc::new(()),value:SubstitutionLookupValue::Invalid})),SubstitutionPoll::WrongReply));
    assert!(matches!(m.poll(Some(SubstitutionLookupReply{identity:r.identity.clone(),value:SubstitutionLookupValue::Attribute(None)})),SubstitutionPoll::WrongReply));
    assert!(matches!(m.poll(Some(SubstitutionLookupReply{identity:r.identity.clone(),value:SubstitutionLookupValue::Value(value("var(--b)"),false)})),SubstitutionPoll::WrongReply));
    let SubstitutionPoll::Complete(result)=m.poll(Some(SubstitutionLookupReply{identity:r.identity,value:SubstitutionLookupValue::Value(value("20px"),false)})) else {panic!()};
    assert_eq!(normalize(result),Ok(("20px".into(),vec![])));
}

#[test]
fn unknown_namespace_never_queries_attribute() {
    let mut v=value("attr(text,ok)");v.references.refs[0].attribute_data.namespace=ParsedNamespace::Unknown;
    let mut t=AttributeTracker::default();let result=drain(ResumableSubstitution::new(v,None,false),&ComputedSubstitutionFunctions::default(),&Stylist::default(),&mut t,true);
    assert_eq!(result,Ok(("ok".into(),vec![])));assert!(t.queries.is_empty());
}

#[test]
fn output_limit_and_single_reference_shortcut_match_old() {
    let mut f=ComputedSubstitutionFunctions::default();put(&mut f.vars,"--large",&"a".repeat(1024*1024+1),false);
    compare("var(--large)var(--large)",&f,&Stylist::default(),&[],false);
    assert!(drain(ResumableSubstitution::new(value("var(--large)var(--large)"),None,false),&f,&Stylist::default(),&mut AttributeTracker::default(),true).is_err());
    put(&mut f.vars,"--large",&"a".repeat(2*1024*1024+1),true);
    compare("var(--large)",&f,&Stylist::default(),&[],false);
}

#[test]
fn environment_snapshot_is_retained_across_later_pause() {
    let mut f=ComputedSubstitutionFunctions::default();let mut s=Stylist::default();let mut t=AttributeTracker::default();
    s.device.values.insert("test".into(),value("12px"));
    let mut m=ResumableSubstitution::new(value("env(test) var(--later)"),None,false);
    let SubstitutionPoll::Lookup(env)=m.poll(None) else {panic!()};
    let SubstitutionPoll::Lookup(later)=m.poll(Some(env.read_current(&f,&s,&mut t))) else {panic!()};
    s.device.values.insert("test".into(),value("99px"));assert!(matches!(m.poll(None),SubstitutionPoll::Lookup(_)));
    put(&mut f.vars,"--later","20px",false);
    let SubstitutionPoll::Complete(result)=m.poll(Some(later.read_current(&f,&s,&mut t))) else {panic!()};
    assert_eq!(normalize(result),Ok(("12px 20px".into(),vec![])));
}

#[test]
fn alias_snapshot_survives_provider_map_mutation() {
    let mut f=ComputedSubstitutionFunctions::default();put(&mut f.vars,"--a","var(--b)",false);
    let s=Stylist::default();let mut t=AttributeTracker::default();
    let mut m=ResumableSubstitution::new(value("var(--a)"),None,false);
    let SubstitutionPoll::Lookup(a)=m.poll(None) else {panic!()};
    let SubstitutionPoll::Lookup(b)=m.poll(Some(a.read_current(&f,&s,&mut t))) else {panic!()};
    assert_eq!(b.name,"b");put(&mut f.vars,"--a","wrong",false);
    for _ in 0..3 {assert!(matches!(m.poll(None),SubstitutionPoll::Lookup(_)));}
    put(&mut f.vars,"--b","20px",false);
    let SubstitutionPoll::Complete(result)=m.poll(Some(b.read_current(&f,&s,&mut t))) else {panic!()};
    assert_eq!(normalize(result),Ok(("20px".into(),vec![])));
}

#[test]
fn settled_invalid_alone_selects_attribute_fallback() {
    let f=ComputedSubstitutionFunctions::default();let s=Stylist::default();let mut t=AttributeTracker::default();t.values.insert("fallback".into(),"chosen".into());
    let mut m=ResumableSubstitution::new(value("var(--missing,attr(fallback raw-string))"),None,false);
    let SubstitutionPoll::Lookup(primary)=m.poll(None) else {panic!()};
    assert!(matches!(m.poll(Some(SubstitutionLookupReply{identity:primary.identity.clone(),value:SubstitutionLookupValue::Pending})),SubstitutionPoll::Lookup(_)));assert!(t.queries.is_empty());
    let SubstitutionPoll::Lookup(fallback)=m.poll(Some(SubstitutionLookupReply{identity:primary.identity,value:SubstitutionLookupValue::Invalid})) else {panic!()};
    assert_eq!(fallback.kind,SubstitutionLookupKind::RawAttribute);
    let SubstitutionPoll::Complete(result)=m.poll(Some(fallback.read_current(&f,&s,&mut t))) else {panic!()};
    assert_eq!(normalize(result),Ok(("\"chosen\"".into(),vec![(0,8)])));assert_eq!(t.queries,vec![":fallback"]);
}

#[test]
fn exact_token_separator_and_taint_offsets() {
    let mut f=ComputedSubstitutionFunctions::default();put(&mut f.vars,"--a","foo",false);put(&mut f.vars,"--b","bar",false);
    let mut t=AttributeTracker::default();t.values.insert("n".into(),"2".into());
    let result=drain(ResumableSubstitution::new(value("var(--a)attr(n px)var(--b)"),None,false),&f,&Stylist::default(),&mut t,true);
    assert_eq!(result,Ok(("foo/**/2px/**/bar".into(),vec![(7,10)])));
}
