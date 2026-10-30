include!("lifetime-common.rs");
enum SubstitutionInput<'a, 'b> {
    Unresolved(&'a VariableValue, &'a mut AttributeTracker<'b>),
    Prepared(Result<Substitution<'static>, ()>),
}
fn apply(input: SubstitutionInput<'_, '_>, context: &mut Context) {
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
fn ordinary<'b>(value: &VariableValue, tracker: &mut AttributeTracker<'b>, context: &mut Context) {
    apply(SubstitutionInput::Unresolved(value, tracker), context);
}
fn context() -> Context { Context { values: "borrowed-map".into(), applied: 99, tainted: false } }
#[test] fn map_borrow_ends_before_mutation() {
    let mut c = context(); let mut t = AttributeTracker { context: &TestElement, references: 0 };
    let v = VariableValue { css: "map".into() };
    let sub = substitute_internal(&v, &c.values, &c, &mut t).unwrap();
    assert!(matches!(sub.css, Cow::Borrowed(_)));
    assert_eq!(sub.css.as_ptr(), c.values.as_ptr());
    apply(SubstitutionInput::Unresolved(&v, &mut t), &mut c);
    assert_eq!((c.applied,c.tainted,t.references),(12,true,2)); assert!(c.values.is_empty());
}
#[test] fn short_value_and_tracker_borrows() {
    let mut c = context();
    { let v = VariableValue { css: "short".into() }; let mut t = AttributeTracker { context: &TestElement, references: 0 };
      ordinary(&v, &mut t, &mut c); assert_eq!(t.references,1); }
    assert_eq!((c.applied,c.tainted),(5,false));
}
#[test] fn owned_prepared_without_substitution() {
    let mut c = context(); let t = AttributeTracker { context: &TestElement, references: 0 };
    apply(SubstitutionInput::Prepared(Ok(Substitution { css: Cow::Owned("owned".into()), attr_tainted:true })), &mut c);
    assert_eq!((c.applied,c.tainted,t.references),(5,true,0));
}
#[test] fn static_prepared_and_keyword() {
    let mut c = context();
    apply(SubstitutionInput::Prepared(Ok(Substitution { css:Cow::Borrowed("inherit"), attr_tainted:false })), &mut c);
    assert_eq!(c.applied,7); assert_eq!(c.values,"borrowed-map");
}
#[test] fn both_error_routes() {
    let mut c=context();let v=VariableValue { css:"error".into() };let mut t=AttributeTracker { context: &TestElement, references: 0 };
    apply(SubstitutionInput::Unresolved(&v,&mut t),&mut c);assert_eq!((c.applied,t.references),(0,1));
    c.applied=99;apply(SubstitutionInput::Prepared(Err(())),&mut c);assert_eq!((c.applied,t.references),(0,1));
}

#[test] fn tracker_storage_outlives_temporary_input_borrow() {
    let element = TestElement;
    let mut tracker = AttributeTracker { context: &element, references: 0 };
    let mut c = context();
    { let value = VariableValue { css: "short".into() }; ordinary(&value, &mut tracker, &mut c); }
    assert_eq!(tracker.references, 1);
    let _stored: &dyn ElementContext = tracker.context;
    { let value = VariableValue { css: "next".into() }; ordinary(&value, &mut tracker, &mut c); }
    assert_eq!(tracker.references, 2);
}
