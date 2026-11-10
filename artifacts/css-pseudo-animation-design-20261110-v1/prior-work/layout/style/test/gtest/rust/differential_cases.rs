/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/. */

use crate::deferred_animation_operations::{AnimationOperationArena, SegmentOperands};
use crate::gecko_bindings::bindings::{CompositeOperation as C, IterationCompositeOperation as I};
use crate::gecko_bindings::structs::URLExtraData;
use crate::properties::{
    animated_properties::AnimationValue as V, CustomDeclarationValue, PropertyDeclaration,
};
use servo_arc::Arc;
use std::ffi::{c_void, CString};
use std::os::raw::c_char;
use style::custom_properties::Name;
use style::properties_and_values::value::{
    ComputedValue, ComputedValueComponent, CustomAnimatedValue, ValueInner,
};
use style::stylesheets::UrlExtraData;

extern "C" {
    fn GTest_CompareAnimationSegment(
        label: *const c_char,
        from: *mut c_void,
        to: *mut c_void,
        underlying: *mut c_void,
        last: *mut c_void,
        from_composite: C,
        to_composite: C,
        iteration: I,
        count: u64,
        progress: f64,
        same_offset: bool,
        expected: *const c_void,
    );
}

fn pointer(value: &Option<Arc<V>>) -> *mut c_void {
    value.as_ref().map_or(std::ptr::null_mut(), |value| {
        &**value as *const V as *mut c_void
    })
}

fn compare(
    label: &str,
    from: Option<V>,
    to: Option<V>,
    underlying: Option<V>,
    last: Option<V>,
    from_composite: C,
    to_composite: C,
    iteration: I,
    count: u64,
    progress: f64,
    same_offset: bool,
) {
    let from = from.map(Arc::new);
    let to = to.map(Arc::new);
    let underlying = underlying.map(Arc::new);
    let last = last.map(Arc::new);
    let mut arena = AnimationOperationArena::<std::convert::Infallible>::new();
    let from_id = from.as_ref().map(|value| arena.value((**value).clone()));
    let to_id = to.as_ref().map(|value| arena.value((**value).clone()));
    let underlying_id = underlying
        .as_ref()
        .map(|value| arena.value((**value).clone()));
    let last_id = last.as_ref().map(|value| arena.value((**value).clone()));
    let operands = SegmentOperands {
        from: from_id,
        to: to_id,
        from_composite,
        to_composite,
        same_offset,
    };
    let Some(root) = arena
        .compose_segment(
            operands,
            underlying_id,
            last_id,
            iteration,
            count,
            progress,
            progress,
        )
        .unwrap()
    else {
        crate::host_failure(format!(
            "{label}: production wrapper requires a valid underlying value"
        ));
        return;
    };
    let expected = arena
        .resolve(root, |_| -> Result<V, ()> {
            panic!("concrete inputs only")
        })
        .unwrap();
    let compare_result = |route: &str, expected: &V| {
        let label = CString::new(format!("{label} / {route}")).unwrap();
        // Native RefPtr inputs must point into real servo_arc allocations, held through the synchronous call.
        unsafe {
            GTest_CompareAnimationSegment(
                label.as_ptr(),
                pointer(&from),
                pointer(&to),
                pointer(&underlying),
                pointer(&last),
                from_composite,
                to_composite,
                iteration,
                count,
                progress,
                same_offset,
                expected as *const V as *const c_void,
            );
        }
    };
    compare_result("generic", &expected);
    let bulk = arena.resolve_concrete_roots(&[root]).unwrap();
    assert_eq!(bulk.len(), 1);
    compare_result("concrete-bulk", &bulk[0]);
}

fn numeric_cases() {
    let o = |value| Some(V::Opacity(value));
    compare(
        "interpolate",
        o(2.),
        o(6.),
        None,
        None,
        C::Replace,
        C::Replace,
        I::Replace,
        0,
        0.25,
        false,
    );
    compare(
        "replace ignores underlying",
        o(2.),
        o(6.),
        o(99.),
        None,
        C::Replace,
        C::Replace,
        I::Replace,
        0,
        0.25,
        false,
    );
    compare(
        "add",
        o(1.),
        o(3.),
        o(10.),
        None,
        C::Add,
        C::Add,
        I::Replace,
        0,
        0.5,
        false,
    );
    compare(
        "endpoint accumulate",
        o(1.),
        o(3.),
        o(10.),
        None,
        C::Accumulate,
        C::Accumulate,
        I::Replace,
        0,
        0.5,
        false,
    );
    compare(
        "mixed composite",
        o(1.),
        o(3.),
        o(10.),
        None,
        C::Add,
        C::Replace,
        I::Replace,
        0,
        0.5,
        false,
    );
    compare(
        "iteration last",
        o(1.),
        o(3.),
        o(10.),
        o(4.),
        C::Add,
        C::Add,
        I::Accumulate,
        2,
        0.5,
        false,
    );
    compare(
        "iteration underlying",
        o(1.),
        o(3.),
        o(10.),
        None,
        C::Replace,
        C::Replace,
        I::Accumulate,
        2,
        0.5,
        false,
    );
    compare(
        "implicit from",
        None,
        o(30.),
        o(10.),
        None,
        C::Replace,
        C::Replace,
        I::Replace,
        0,
        0.25,
        false,
    );
    compare(
        "implicit to",
        o(2.),
        None,
        o(10.),
        None,
        C::Replace,
        C::Replace,
        I::Replace,
        0,
        0.25,
        false,
    );
    compare(
        "both implicit",
        None,
        None,
        o(10.),
        None,
        C::Replace,
        C::Replace,
        I::Replace,
        0,
        0.25,
        false,
    );
    compare(
        "equal offset negative",
        o(1.),
        o(3.),
        o(10.),
        o(4.),
        C::Add,
        C::Add,
        I::Accumulate,
        2,
        -0.5,
        true,
    );
    compare(
        "equal offset nonnegative",
        o(1.),
        o(3.),
        o(10.),
        o(4.),
        C::Add,
        C::Add,
        I::Accumulate,
        2,
        0.,
        true,
    );
    compare(
        "equal offset negative zero",
        o(1.),
        o(3.),
        o(10.),
        o(4.),
        C::Add,
        C::Add,
        I::Accumulate,
        2,
        -0.0,
        true,
    );
    compare(
        "zero iterations ignore last",
        o(2.),
        o(6.),
        None,
        o(999.),
        C::Replace,
        C::Replace,
        I::Accumulate,
        0,
        0.25,
        false,
    );
    compare(
        "extrapolate",
        o(2.),
        o(6.),
        None,
        None,
        C::Replace,
        C::Replace,
        I::Replace,
        0,
        1.5,
        false,
    );
    compare(
        "infinite input native behavior",
        o(f32::INFINITY),
        o(2.),
        None,
        None,
        C::Replace,
        C::Replace,
        I::Replace,
        0,
        0.5,
        false,
    );
    compare(
        "NaN input native behavior",
        o(f32::NAN),
        o(2.),
        None,
        None,
        C::Replace,
        C::Replace,
        I::Replace,
        0,
        0.5,
        false,
    );
}

fn number(name: &Name, value: f32, tainted: bool, url: &UrlExtraData) -> V {
    let mut value = ComputedValue::new(
        ValueInner::Component(ComputedValueComponent::Number(value)),
        url.clone(),
    );
    value.attr_tainted = tainted;
    V::Custom(CustomAnimatedValue::from_computed(name, Some(&value)))
}

fn metadata_cases(left: &UrlExtraData, right: &UrlExtraData) {
    let name = Name::from("arena-native-number");
    let other = Name::from("arena-native-other");
    let n = |value, tainted, url| Some(number(&name, value, tainted, url));
    let other_n = |value, tainted, url| Some(number(&other, value, tainted, url));
    compare(
        "custom interpolate",
        n(2., false, left),
        n(6., true, right),
        None,
        None,
        C::Replace,
        C::Replace,
        I::Replace,
        0,
        0.25,
        false,
    );
    compare(
        "custom add underlying taint",
        n(1., false, right),
        n(3., false, right),
        n(10., true, left),
        None,
        C::Add,
        C::Add,
        I::Replace,
        0,
        0.5,
        false,
    );
    compare(
        "custom implicit underlying taint",
        None,
        n(30., false, right),
        n(10., true, left),
        None,
        C::Replace,
        C::Replace,
        I::Replace,
        0,
        0.25,
        false,
    );
    compare(
        "custom iteration metadata",
        n(1., false, left),
        n(3., false, left),
        None,
        n(4., true, right),
        C::Replace,
        C::Replace,
        I::Accumulate,
        2,
        0.5,
        false,
    );
    compare(
        "interpolate error left fallback",
        n(2., true, left),
        other_n(6., false, right),
        None,
        None,
        C::Replace,
        C::Replace,
        I::Replace,
        0,
        0.25,
        false,
    );
    compare(
        "interpolate error right fallback",
        n(2., true, left),
        other_n(6., false, right),
        None,
        None,
        C::Replace,
        C::Replace,
        I::Replace,
        0,
        0.75,
        false,
    );
    compare(
        "endpoint add error fallback",
        n(1., false, right),
        n(3., false, right),
        other_n(10., true, left),
        None,
        C::Add,
        C::Add,
        I::Replace,
        0,
        0.5,
        false,
    );
    compare(
        "iteration error fallback",
        n(1., false, left),
        n(3., false, left),
        None,
        other_n(4., true, right),
        C::Replace,
        C::Replace,
        I::Accumulate,
        2,
        0.5,
        false,
    );
    compare(
        "both add and iteration error fallback",
        n(1., true, right),
        n(3., false, right),
        other_n(10., true, left),
        other_n(4., true, left),
        C::Add,
        C::Add,
        I::Accumulate,
        2,
        0.25,
        false,
    );
    compare(
        "interpolation error tie chooses to",
        n(2., true, left),
        other_n(6., false, right),
        None,
        None,
        C::Replace,
        C::Replace,
        I::Replace,
        0,
        0.5,
        false,
    );
    compare(
        "iteration failure retains successful add",
        n(1., false, right),
        n(3., false, right),
        n(10., true, left),
        other_n(4., false, right),
        C::Add,
        C::Add,
        I::Accumulate,
        2,
        0.5,
        false,
    );
}

#[no_mangle]
pub unsafe extern "C" fn Rust_RunAnimationOperationArenaDifferential(
    left: *mut URLExtraData,
    right: *mut URLExtraData,
) {
    if left.is_null() || right.is_null() || left == right {
        crate::host_failure("missing distinct real URL fixtures".into());
        return;
    }
    let left = UrlExtraData::new(left);
    let right = UrlExtraData::new(right);
    numeric_cases();
    metadata_cases(&left, &right);
}

#[no_mangle]
pub unsafe extern "C" fn Rust_CompareAnimationOperationArenaValues(
    actual: *const c_void,
    expected: *const c_void,
) {
    let (Some(actual), Some(expected)) = (
        (actual as *const V).as_ref(),
        (expected as *const V).as_ref(),
    ) else {
        crate::host_failure("missing differential result".into());
        return;
    };
    match (actual, expected) {
        (V::Opacity(actual), V::Opacity(expected)) => {
            if actual.is_nan() && expected.is_nan() {
                return;
            }
            assert_eq!(actual.to_bits(), expected.to_bits());
        }
        (V::Custom(actual_custom), V::Custom(expected_custom)) => {
            assert_eq!(actual, expected);
            assert_eq!(
                actual_custom.is_attr_tainted(),
                expected_custom.is_attr_tainted()
            );
            let (PropertyDeclaration::Custom(actual), PropertyDeclaration::Custom(expected)) =
                (actual.uncompute(), expected.uncompute())
            else {
                crate::host_failure("custom uncompute lost its variant".into());
                return;
            };
            assert_eq!(actual.name, expected.name);
            let (CustomDeclarationValue::Parsed(actual), CustomDeclarationValue::Parsed(expected)) =
                (actual.value, expected.value)
            else {
                crate::host_failure("numeric result was not a typed declaration".into());
                return;
            };
            assert_eq!(actual.attr_tainted, expected.attr_tainted);
            let actual = actual.to_variable_value();
            let expected = expected.to_variable_value();
            assert_eq!(actual.css, expected.css);
            assert_eq!(actual.url_data.ptr(), expected.url_data.ptr());
        }
        _ => crate::host_failure("differential variants differ or are outside this probe".into()),
    }
}
