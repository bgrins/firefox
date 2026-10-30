include!("borrow-common.rs");
fn apply(substitution: Result<Substitution, ()>, context: &mut Context) {
    let length = substitution.map(|v| v.css.len()).unwrap_or(0);
    context.applied = length;
}
fn ordinary(value: &VariableValue, tracker: &mut AttributeTracker, context: &mut Context) {
    let substitution = substitute_internal(value, &context.values, context, tracker);
    apply(substitution, context);
}
fn main() {}
