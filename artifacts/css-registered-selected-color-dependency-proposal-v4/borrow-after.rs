include!("borrow-common.rs");
enum SubstitutionInput<'a> {
    Unresolved(&'a VariableValue, &'a mut AttributeTracker),
    Prepared(Result<Substitution<'static>, ()>),
}
fn apply(input: SubstitutionInput, context: &mut Context) {
    let substitution = match input {
        SubstitutionInput::Unresolved(value, tracker) =>
            substitute_internal(value, &context.values, context, tracker),
        SubstitutionInput::Prepared(substitution) => substitution,
    };
    let Ok(substitution) = substitution else { context.applied = 0; return; };
    if substitution.css == "inherit" { context.applied = 7; return; }
    let result = (substitution.css.len(), substitution.attr_tainted);
    context.values.clear();
    context.applied = result.0;
    context.tainted = result.1;
}
fn context() -> Context { Context { values: "borrowed-map".into(), applied: 99, tainted: false } }
#[test] fn map_borrow_ends_before_mutation() {
    let mut c = context(); let mut t = AttributeTracker(0);
    let v = VariableValue { css: "map".into() };
    let sub = substitute_internal(&v, &c.values, &c, &mut t).unwrap();
    assert!(matches!(sub.css, Cow::Borrowed(_)));
    assert_eq!(sub.css.as_ptr(), c.values.as_ptr());
    apply(SubstitutionInput::Unresolved(&v, &mut t), &mut c);
    assert_eq!((c.applied,c.tainted,t.0),(12,true,2)); assert!(c.values.is_empty());
}
#[test] fn short_value_and_tracker_borrows() {
    let mut c = context();
    { let v = VariableValue { css: "short".into() }; let mut t = AttributeTracker(0);
      apply(SubstitutionInput::Unresolved(&v,&mut t), &mut c); assert_eq!(t.0,1); }
    assert_eq!((c.applied,c.tainted),(5,false));
}
#[test] fn owned_prepared_without_substitution() {
    let mut c = context(); let t = AttributeTracker(0);
    apply(SubstitutionInput::Prepared(Ok(Substitution { css: Cow::Owned("owned".into()), attr_tainted:true })), &mut c);
    assert_eq!((c.applied,c.tainted,t.0),(5,true,0));
}
#[test] fn static_prepared_and_keyword() {
    let mut c = context();
    apply(SubstitutionInput::Prepared(Ok(Substitution { css:Cow::Borrowed("inherit"), attr_tainted:false })), &mut c);
    assert_eq!(c.applied,7); assert_eq!(c.values,"borrowed-map");
}
#[test] fn both_error_routes() {
    let mut c=context();let v=VariableValue { css:"error".into() };let mut t=AttributeTracker(0);
    apply(SubstitutionInput::Unresolved(&v,&mut t),&mut c);assert_eq!((c.applied,t.0),(0,1));
    c.applied=99;apply(SubstitutionInput::Prepared(Err(())),&mut c);assert_eq!((c.applied,t.0),(0,1));
}
