use std::borrow::Cow;
struct VariableValue { css: String }
trait ElementContext {}
struct TestElement;
impl ElementContext for TestElement {}
type AttributeReferences = usize;
pub struct AttributeTracker<'a> {
    /// The element that queries for attributes.
    pub context: &'a dyn ElementContext,
    /// The set of attributes we have queried.
    pub references: AttributeReferences,
}
struct Context { values: String, applied: usize, tainted: bool }
struct Substitution<'a> { css: Cow<'a, str>, attr_tainted: bool }
fn substitute_internal<'a>(value: &'a VariableValue, values: &'a str,
    _context: &Context, tracker: &mut AttributeTracker) -> Result<Substitution<'a>, ()> {
    tracker.references += 1;
    match value.css.as_str() {
        "error" => Err(()),
        "map" => Ok(Substitution { css: Cow::Borrowed(values), attr_tainted: true }),
        _ => Ok(Substitution { css: Cow::Borrowed(&value.css), attr_tainted: false }),
    }
}
