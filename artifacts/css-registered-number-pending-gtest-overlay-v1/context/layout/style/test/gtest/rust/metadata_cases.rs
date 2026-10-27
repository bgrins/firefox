/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/. */

use crate::deferred_animation_operations::{AnimationOperationArena, SegmentOperands};
use crate::gecko_bindings::bindings::{CompositeOperation as C, IterationCompositeOperation as I};
use crate::properties::{
    animated_properties::AnimationValue as V, CustomDeclarationValue, PropertyDeclaration,
};
use style::custom_properties::Name;
use style::properties_and_values::value::{
    ComputedValue, ComputedValueComponent, CustomAnimatedValue, ValueInner,
};
use style::stylesheets::UrlExtraData;

fn number(name: &Name, value: f32, tainted: bool, url: &UrlExtraData) -> V {
    let mut value = ComputedValue::new(
        ValueInner::Component(ComputedValueComponent::Number(value)),
        url.clone(),
    );
    value.attr_tainted = tainted;
    V::Custom(CustomAnimatedValue::from_computed(name, Some(&value)))
}

fn check(value: V, name: &Name, expected: &str, tainted: bool, url: &UrlExtraData) {
    let V::Custom(ref custom) = value else {
        panic!("not custom")
    };
    assert_eq!(custom.is_attr_tainted(), tainted);
    let PropertyDeclaration::Custom(declaration) = value.uncompute() else {
        panic!("not custom declaration")
    };
    assert_eq!(&declaration.name, name);
    let CustomDeclarationValue::Parsed(parsed) = declaration.value else {
        panic!("not typed numeric declaration")
    };
    assert_eq!(parsed.attr_tainted, tainted);
    let tokens = parsed.to_variable_value();
    assert_eq!(tokens.css, expected);
    assert_eq!(tokens.url_data.ptr(), url.ptr());
}

fn interpolation_metadata(left_url: &UrlExtraData, right_url: &UrlExtraData) {
    assert_ne!(left_url.ptr(), right_url.ptr());
    let name = Name::from("arena-number");
    for (left_taint, right_taint) in [(false, false), (false, true), (true, false)] {
        let mut a = AnimationOperationArena::<()>::new();
        let from = a.value(number(&name, 2., left_taint, left_url));
        let to = a.value(number(&name, 6., right_taint, right_url));
        let operands = SegmentOperands {
            from: Some(from),
            to: Some(to),
            from_composite: C::Replace,
            to_composite: C::Replace,
            same_offset: false,
        };
        let root = a
            .compose_segment(operands, None, None, I::Replace, 0, 0.25, 0.25)
            .unwrap()
            .unwrap();
        check(
            a.resolve(root, |_| -> Result<V, ()> { panic!("no endpoint") })
                .unwrap(),
            &name,
            "3",
            left_taint || right_taint,
            left_url,
        );
    }
}

fn iteration_metadata(left_url: &UrlExtraData, right_url: &UrlExtraData) {
    assert_ne!(left_url.ptr(), right_url.ptr());
    let name = Name::from("arena-number");
    let mut a = AnimationOperationArena::<()>::new();
    let from = a.value(number(&name, 1., false, left_url));
    let to = a.value(number(&name, 3., false, left_url));
    let last = a.value(number(&name, 4., true, right_url));
    let operands = SegmentOperands {
        from: Some(from),
        to: Some(to),
        from_composite: C::Replace,
        to_composite: C::Replace,
        same_offset: false,
    };
    let root = a
        .compose_segment(operands, None, Some(last), I::Accumulate, 2, 0.5, 0.5)
        .unwrap()
        .unwrap();
    check(
        a.resolve(root, |_| -> Result<V, ()> { panic!("no endpoint") })
            .unwrap(),
        &name,
        "10",
        true,
        right_url,
    );
}

fn fallback_metadata(left_url: &UrlExtraData, right_url: &UrlExtraData) {
    assert_ne!(left_url.ptr(), right_url.ptr());
    let name = Name::from("arena-number");
    let other = Name::from("arena-other");
    for (progress, expected_name, expected_value, expected_taint, expected_url) in [
        (0.25, &name, "2", true, left_url),
        (0.75, &other, "6", false, right_url),
    ] {
        let mut a = AnimationOperationArena::<()>::new();
        let from = a.value(number(&name, 2., true, left_url));
        let to = a.value(number(&other, 6., false, right_url));
        let operands = SegmentOperands {
            from: Some(from),
            to: Some(to),
            from_composite: C::Replace,
            to_composite: C::Replace,
            same_offset: false,
        };
        let root = a
            .compose_segment(operands, None, None, I::Replace, 0, progress, progress)
            .unwrap()
            .unwrap();
        check(
            a.resolve(root, |_| -> Result<V, ()> { panic!("no endpoint") })
                .unwrap(),
            expected_name,
            expected_value,
            expected_taint,
            expected_url,
        );
    }
}

fn additive_underlying_metadata(left_url: &UrlExtraData, right_url: &UrlExtraData) {
    assert_ne!(left_url.ptr(), right_url.ptr());
    let name = Name::from("arena-number");
    let mut a = AnimationOperationArena::<()>::new();
    let underlying = a.value(number(&name, 10., true, left_url));
    let from = a.value(number(&name, 1., false, right_url));
    let to = a.value(number(&name, 3., false, right_url));
    let operands = SegmentOperands {
        from: Some(from),
        to: Some(to),
        from_composite: C::Add,
        to_composite: C::Add,
        same_offset: false,
    };
    let root = a
        .compose_segment(operands, Some(underlying), None, I::Replace, 0, 0.5, 0.5)
        .unwrap()
        .unwrap();
    check(
        a.resolve(root, |_| -> Result<V, ()> { panic!("no endpoint") })
            .unwrap(),
        &name,
        "12",
        true,
        left_url,
    );
}

fn implicit_underlying_metadata(left_url: &UrlExtraData, right_url: &UrlExtraData) {
    assert_ne!(left_url.ptr(), right_url.ptr());
    let name = Name::from("arena-number");
    let mut a = AnimationOperationArena::<()>::new();
    let underlying = a.value(number(&name, 10., true, left_url));
    let to = a.value(number(&name, 30., false, right_url));
    let operands = SegmentOperands {
        from: None,
        to: Some(to),
        from_composite: C::Replace,
        to_composite: C::Replace,
        same_offset: false,
    };
    let root = a
        .compose_segment(operands, Some(underlying), None, I::Replace, 0, 0.25, 0.25)
        .unwrap()
        .unwrap();
    check(
        a.resolve(root, |_| -> Result<V, ()> { panic!("no endpoint") })
            .unwrap(),
        &name,
        "15",
        true,
        left_url,
    );
}

pub(crate) fn run_all(left_url: &UrlExtraData, right_url: &UrlExtraData) {
    interpolation_metadata(left_url, right_url);
    iteration_metadata(left_url, right_url);
    fallback_metadata(left_url, right_url);
    additive_underlying_metadata(left_url, right_url);
    implicit_underlying_metadata(left_url, right_url);
}
