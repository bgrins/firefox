include!("lifetime-common.rs");
enum SubstitutionInput<'a> {
    Unresolved(&'a VariableValue, &'a mut AttributeTracker),
    Prepared(Result<Substitution<'static>, ()>),
}
fn main() {}
