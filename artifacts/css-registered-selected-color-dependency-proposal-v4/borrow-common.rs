use std::borrow::Cow;
struct VariableValue { css: String }
struct AttributeTracker(usize);
struct Context { values: String, applied: usize, tainted: bool }
struct Substitution<'a> { css: Cow<'a, str>, attr_tainted: bool }
fn substitute_internal<'a>(value: &'a VariableValue, values: &'a str,
    _context: &Context, tracker: &mut AttributeTracker) -> Result<Substitution<'a>, ()> {
    tracker.0 += 1;
    match value.css.as_str() {
        "error" => Err(()),
        "map" => Ok(Substitution { css: Cow::Borrowed(values), attr_tainted: true }),
        _ => Ok(Substitution { css: Cow::Borrowed(&value.css), attr_tainted: false }),
    }
}
