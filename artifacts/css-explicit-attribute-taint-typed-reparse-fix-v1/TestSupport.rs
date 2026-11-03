#![allow(dead_code)]
use std::borrow::Cow;
type Name = str;
type PropertyIdRef = ();
type Stylist = ();
type AttributeTracker = ();
trait Array { type Item; }
impl<T, const N: usize> Array for [T; N] { type Item = T; }
type SmallVec<A> = Vec<<A as Array>::Item>;
mod computed { pub type Context = (); }
#[derive(Default)]
struct AttrTaint(Vec<(usize, usize)>);
#[derive(Default)]
struct References { refs: Vec<()>, attr: bool }
struct VariableValue {
    css: String,
    first_token_type: u8,
    last_token_type: u8,
    url_data: (),
    references: References,
    explicitly_attr_tainted: bool,
}
impl VariableValue {
    fn is_attr_tainted(&self) -> bool {
        self.references.attr | self.explicitly_attr_tainted
    }
}
#[derive(Default, Debug)]
struct Substitution<'a> {
    css: Cow<'a, str>,
    first_token_type: u8,
    last_token_type: u8,
    attr_tainted: bool,
}
struct ComputedSubstitutionFunctions { invalid: bool, selected_taint: bool }
fn do_substitute_chunk<'a>(
    css: &'a str, start: usize, end: usize, first: u8, last: u8,
    _: &(), _: Option<PropertyIdRef>, values: &'a ComputedSubstitutionFunctions,
    _: &Stylist, _: &computed::Context, _: &'a [()], _: &mut AttributeTracker,
    _: &mut SmallVec<[&'a Name; 8]>, _: Option<&mut AttrTaint>,
) -> Result<Substitution<'a>, ()> {
    if values.invalid { return Err(()); }
    Ok(Substitution { css: Cow::Borrowed(&css[start..end]), first_token_type: first,
        last_token_type: last, attr_tainted: values.selected_taint })
}
fn value(css: &str, explicit: bool, attr: bool) -> VariableValue {
    VariableValue { css: css.into(), first_token_type: 3, last_token_type: 7,
        url_data: (), references: References { refs: vec![], attr },
        explicitly_attr_tainted: explicit }
}
fn run<'a>(value: &'a VariableValue, state: &'a ComputedSubstitutionFunctions) -> Result<Substitution<'a>, ()> {
    substitute_internal(value, None, state, &(), &(), &mut (), &mut vec![], None)
}
#[test]
fn explicit_reference_free_transport() {
    let v = value("\"é image\"", true, false);
    let state = ComputedSubstitutionFunctions { invalid: false, selected_taint: false };
    let result = run(&v, &state).unwrap();
    assert!(result.attr_tainted);
    assert_eq!(result.css, v.css);
    assert_eq!((result.first_token_type, result.last_token_type), (3, 7));
}
#[test]
fn explicit_empty_keeps_aggregate_without_range() {
    let v = value("", true, false);
    let state = ComputedSubstitutionFunctions { invalid: false, selected_taint: false };
    let mut ranges = AttrTaint::default();
    let result = substitute_internal(&v, None, &state, &(), &(), &mut (), &mut vec![], Some(&mut ranges)).unwrap();
    assert!(result.attr_tainted);
    assert!(result.css.is_empty());
    assert!(ranges.0.is_empty());
}
#[test]
fn clean_literal_stays_clean() {
    let v = value("\"literal\"", false, false);
    let state = ComputedSubstitutionFunctions { invalid: false, selected_taint: false };
    assert!(!run(&v, &state).unwrap().attr_tainted);
}
#[test]
fn syntactic_unused_attr_is_not_explicit_origin() {
    let v = value("\"selected clean primary\"", false, true);
    let state = ComputedSubstitutionFunctions { invalid: false, selected_taint: false };
    assert!(!run(&v, &state).unwrap().attr_tainted);
}
#[test]
fn selected_child_origin_survives() {
    let v = value("\"child\"", false, true);
    let state = ComputedSubstitutionFunctions { invalid: false, selected_taint: true };
    assert!(run(&v, &state).unwrap().attr_tainted);
}
#[test]
fn invalid_is_not_recovered_by_taint() {
    let v = value("invalid", true, false);
    let state = ComputedSubstitutionFunctions { invalid: true, selected_taint: false };
    assert!(run(&v, &state).is_err());
}
