
use std::cell::Cell;
#[derive(Clone, Copy)] struct Bits(u8);
impl Bits {
    const RECASCADE_SELF: Self = Self(1);
    const RECASCADE_SELF_IF_INHERIT_RESET_STYLE: Self = Self(2);
    const RESTYLE_IF_AFFECTED_BY_WM_OR_ANCESTOR_FONT: Self = Self(4);
    const INHERITS_RESET_STYLE: Self = Self(2);
    const USES_FONT_OR_WM_RELATIVE_UNITS: Self = Self(4);
    fn intersects(self, other: Self) -> bool { self.0 & other.0 != 0 }
    fn contains(self, other: Self) -> bool { self.0 & other.0 == other.0 }
}
type RestyleHint = Bits;
type ComputedValueFlags = Bits;
struct ComputedValues { flags: Bits }
struct Data { hint: Bits }
struct Flags(bool);
impl Flags { fn for_animation_only(&self) -> bool { self.0 } }
struct Context { shared: () }
struct Element { calls: Cell<u32>, relevant: Cell<bool> }
impl Element {
    fn has_animations(&self, _: ()) -> bool {
        self.calls.set(self.calls.get() + 1);
        self.relevant.get()
    }
}
fn needs_to_recascade_self(
    hint: RestyleHint,
    style: &ComputedValues,
    has_animations: bool,
) -> bool {
    if hint.intersects(RestyleHint::RECASCADE_SELF) {
        return true;
    }
    if hint.intersects(RestyleHint::RECASCADE_SELF_IF_INHERIT_RESET_STYLE)
        && style
            .flags
            .contains(ComputedValueFlags::INHERITS_RESET_STYLE)
    {
        return true;
    }
    if hint.intersects(RestyleHint::RESTYLE_IF_AFFECTED_BY_WM_OR_ANCESTOR_FONT)
        && (has_animations
            || style
                .flags
                .contains(ComputedValueFlags::USES_FONT_OR_WM_RELATIVE_UNITS))
    {
        return true;
    }
    false
}

fn query(data: &Data, flags: &Flags, element: &Element, context: &Context) -> bool {
    let has_animations = !flags.for_animation_only()
        && data
            .hint
            .intersects(RestyleHint::RESTYLE_IF_AFFECTED_BY_WM_OR_ANCESTOR_FONT)
        && element.has_animations(context.shared);
has_animations
}

#[test] fn animated_target_without_style_bit_is_admitted() {
    let style = ComputedValues { flags: Bits(0) };
    assert!(needs_to_recascade_self(Bits(4), &style, true));
    assert!(!needs_to_recascade_self(Bits(4), &style, false));
}
#[test] fn ordinary_relative_and_other_recascade_paths_survive() {
    assert!(needs_to_recascade_self(Bits(4), &ComputedValues { flags: Bits(4) }, false));
    assert!(needs_to_recascade_self(Bits(1), &ComputedValues { flags: Bits(0) }, false));
    assert!(needs_to_recascade_self(Bits(2), &ComputedValues { flags: Bits(2) }, false));
    assert!(!needs_to_recascade_self(Bits(2), &ComputedValues { flags: Bits(0) }, true));
    assert!(!needs_to_recascade_self(Bits(0), &ComputedValues { flags: Bits(4) }, true));
}
#[test] fn query_requires_normal_pass_and_font_hint() {
    let element = Element { calls: Cell::new(0), relevant: Cell::new(true) };
    let context = Context { shared: () };
    assert!(!query(&Data { hint: Bits(0) }, &Flags(false), &element, &context));
    assert!(!query(&Data { hint: Bits(4) }, &Flags(true), &element, &context));
    assert_eq!(element.calls.get(), 0);
    assert!(query(&Data { hint: Bits(4) }, &Flags(false), &element, &context));
    assert_eq!(element.calls.get(), 1);
}
#[test] fn membership_is_requeried_after_removal_and_retarget() {
    let element = Element { calls: Cell::new(0), relevant: Cell::new(true) };
    let context = Context { shared: () };
    let data = Data { hint: Bits(4) };
    assert!(query(&data, &Flags(false), &element, &context));
    element.relevant.set(false);
    assert!(!query(&data, &Flags(false), &element, &context));
    element.relevant.set(true);
    assert!(query(&data, &Flags(false), &element, &context));
    assert_eq!(element.calls.get(), 3);
}
