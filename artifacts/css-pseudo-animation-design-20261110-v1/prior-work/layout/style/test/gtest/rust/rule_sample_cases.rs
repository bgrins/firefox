/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/. */

use style::animation_rule_sample::{AnimationOperationSample, SampledEndpoint, SampledSegment};
use style::deferred_animation_operations::{AnimationOperationArena, InvalidNode, SegmentOperands};
use style::gecko_bindings::bindings::{CompositeOperation, IterationCompositeOperation};
use style::properties::animated_properties::AnimationValue;
use style::properties::{LonghandId, OwnedPropertyDeclarationId};

fn property() -> OwnedPropertyDeclarationId {
    OwnedPropertyDeclarationId::Longhand(LonghandId::Opacity)
}

fn segment<E>(from: SampledEndpoint<E>, to: SampledEndpoint<E>) -> SampledSegment<E> {
    SampledSegment {
        from: Some(from),
        to: Some(to),
        from_composite: CompositeOperation::Replace,
        to_composite: CompositeOperation::Replace,
        same_offset: false,
        last: None,
        iteration_composite: IterationCompositeOperation::Replace,
        current_iteration: 0,
    }
}

fn scalar(value: AnimationValue) -> f32 {
    match value {
        AnimationValue::Opacity(value) | AnimationValue::FloodOpacity(value) => value,
        _ => panic!("wrong property"),
    }
}

fn frozen_property_owns_recipe_after_collector_and_map_are_gone() {
    let mut sample = AnimationOperationSample::with_capacity(1);
    sample.compose_segment(
        property(),
        segment(
            SampledEndpoint::Recipe(String::from("from")),
            SampledEndpoint::Recipe(String::from("to")),
        ),
        || panic!("replace needs no base"),
        || (0.5, 0.5),
    );
    let roots = sample.freeze();
    let root = roots.get(&property()).unwrap();
    let retained = root.clone();
    drop(root);
    drop(roots);
    assert_eq!(
        retained
            .endpoints()
            .iter()
            .map(|v| v.as_str())
            .collect::<Vec<_>>(),
        vec!["from", "to"]
    );
    assert_eq!(
        scalar(
            retained
                .resolve(|recipe| -> Result<_, ()> {
                    Ok(AnimationValue::Opacity(if recipe == "from" {
                        20.
                    } else {
                        30.
                    }))
                })
                .unwrap()
        ),
        25.
    );
}

fn additive_effect_retains_lower_recipe_root_instead_of_cached_value() {
    let mut sample = AnimationOperationSample::with_capacity(1);
    sample.compose_segment(
        property(),
        segment(
            SampledEndpoint::Recipe(String::from("provider")),
            SampledEndpoint::Value(AnimationValue::Opacity(30.)),
        ),
        || panic!("replace needs no base"),
        || (0.5, 0.5),
    );
    let mut upper = segment(
        SampledEndpoint::Value(AnimationValue::Opacity(1.)),
        SampledEndpoint::Value(AnimationValue::Opacity(3.)),
    );
    upper.from_composite = CompositeOperation::Add;
    upper.to_composite = CompositeOperation::Add;
    sample.compose_segment(
        property(),
        upper,
        || panic!("lower root supplies base"),
        || (0.5, 0.5),
    );
    let roots = sample.freeze();
    let root = roots.get(&property()).unwrap();
    assert_eq!(root.endpoints().len(), 1);
    assert_eq!(
        scalar(
            root.resolve(|_| -> Result<_, ()> { Ok(AnimationValue::Opacity(10.)) })
                .unwrap()
        ),
        22.
    );
    assert_eq!(
        scalar(
            root.resolve(|_| -> Result<_, ()> { Ok(AnimationValue::Opacity(20.)) })
                .unwrap()
        ),
        27.
    );
}

fn replace_does_not_resolve_discarded_recipe() {
    let mut sample = AnimationOperationSample::with_capacity(1);
    sample.compose_segment(
        property(),
        segment(
            SampledEndpoint::Recipe(String::from("invalid")),
            SampledEndpoint::Value(AnimationValue::Opacity(30.)),
        ),
        || None,
        || (0.5, 0.5),
    );
    sample.compose_segment(
        property(),
        segment(
            SampledEndpoint::Value(AnimationValue::Opacity(2.)),
            SampledEndpoint::Value(AnimationValue::Opacity(6.)),
        ),
        || panic!("replace needs no base"),
        || (0.25, 0.25),
    );
    let roots = sample.freeze();
    let root = roots.get(&property()).unwrap();
    assert!(root.endpoints().is_empty());
    assert_eq!(
        scalar(
            root.resolve(|_| -> Result<_, ()> { panic!("discarded endpoint") })
                .unwrap()
        ),
        3.
    );
}

fn endpoint_failure_is_not_a_cached_value_or_animation_fallback() {
    let mut sample = AnimationOperationSample::with_capacity(1);
    let mut selected = segment(
        SampledEndpoint::Recipe(String::from("invalid")),
        SampledEndpoint::Value(AnimationValue::Opacity(30.)),
    );
    selected.same_offset = true;
    sample.compose_segment(property(), selected, || None, || (0., 0.));
    let roots = sample.freeze();
    assert!(matches!(
        roots
            .get(&property())
            .unwrap()
            .resolve(|_| Err("endpoint error")),
        Err("endpoint error")
    ));
}

fn missing_underlying_does_not_sample_progress_or_insert() {
    let mut sample = AnimationOperationSample::<String>::with_capacity(1);
    let mut implicit = segment(
        SampledEndpoint::Value(AnimationValue::Opacity(2.)),
        SampledEndpoint::Value(AnimationValue::Opacity(6.)),
    );
    implicit.from = None;
    assert!(!sample.compose_segment(property(), implicit, || None, || panic!("no composition")));
    assert!(sample.freeze().is_empty());
}

fn concrete_bulk_values_match_individual_roots_in_table_order() {
    let make_sample = || {
        let mut sample = AnimationOperationSample::<std::convert::Infallible>::with_capacity(2);
        sample.compose_segment(
            property(),
            segment(
                SampledEndpoint::Value(AnimationValue::Opacity(2.)),
                SampledEndpoint::Value(AnimationValue::Opacity(6.)),
            ),
            || None,
            || (0.25, 0.25),
        );
        sample.compose_segment(
            OwnedPropertyDeclarationId::Longhand(LonghandId::FloodOpacity),
            segment(
                SampledEndpoint::Value(AnimationValue::FloodOpacity(10.)),
                SampledEndpoint::Value(AnimationValue::FloodOpacity(30.)),
            ),
            || None,
            || (0.5, 0.5),
        );
        sample
    };
    let expected: Vec<_> = make_sample()
        .freeze()
        .into_properties()
        .map(|(property, root)| {
            let value = root
                .resolve(|never| -> Result<_, std::convert::Infallible> { match *never {} })
                .unwrap();
            (property, scalar(value))
        })
        .collect();
    let actual: Vec<_> = make_sample()
        .freeze()
        .into_concrete_values()
        .into_iter()
        .map(|(property, value)| (property, scalar(value)))
        .collect();
    assert_eq!(actual.len(), 2);
    assert_eq!(actual, expected);
}

fn shared_and_repeated_roots_match_individual_resolution() {
    let mut arena = AnimationOperationArena::<std::convert::Infallible>::new();
    let from = arena.value(AnimationValue::Opacity(2.));
    let to = arena.value(AnimationValue::Opacity(6.));
    let first = arena
        .compose_segment(
            SegmentOperands {
                from: Some(from),
                to: Some(to),
                from_composite: CompositeOperation::Replace,
                to_composite: CompositeOperation::Replace,
                same_offset: false,
            },
            None,
            None,
            IterationCompositeOperation::Replace,
            0,
            0.5,
            0.5,
        )
        .unwrap()
        .unwrap();
    let second = arena
        .compose_segment(
            SegmentOperands {
                from: Some(from),
                to: Some(to),
                from_composite: CompositeOperation::Add,
                to_composite: CompositeOperation::Add,
                same_offset: false,
            },
            Some(first),
            None,
            IterationCompositeOperation::Replace,
            0,
            0.5,
            0.5,
        )
        .unwrap()
        .unwrap();
    let roots = [second, first, second];
    let expected: Vec<_> = roots
        .iter()
        .map(|root| {
            arena
                .resolve(
                    *root,
                    |never| -> Result<AnimationValue, std::convert::Infallible> { match *never {} },
                )
                .unwrap()
        })
        .collect();
    let actual = arena.resolve_concrete_roots(&roots).unwrap();
    assert_eq!(actual.len(), expected.len());
    for (actual, expected) in actual.into_iter().zip(expected) {
        match (actual, expected) {
            (AnimationValue::Opacity(a), AnimationValue::Opacity(b)) => {
                assert_eq!(a.to_bits(), b.to_bits())
            },
            _ => panic!("unexpected property"),
        }
    }
}

fn empty_and_invalid_root_sets_are_explicit() {
    let arena = AnimationOperationArena::<std::convert::Infallible>::new();
    assert!(arena.resolve_concrete_roots(&[]).unwrap().is_empty());
    let mut other = AnimationOperationArena::<std::convert::Infallible>::new();
    let absent_index = other.value(AnimationValue::Opacity(1.));
    assert!(matches!(
        arena.resolve_concrete_roots(&[absent_index]),
        Err(InvalidNode)
    ));
}

#[no_mangle]
pub extern "C" fn Rust_AnimationRuleSample_FrozenOwnership() {
    frozen_property_owns_recipe_after_collector_and_map_are_gone();
}

#[no_mangle]
pub extern "C" fn Rust_AnimationRuleSample_AdditiveRecipe() {
    additive_effect_retains_lower_recipe_root_instead_of_cached_value();
}

#[no_mangle]
pub extern "C" fn Rust_AnimationRuleSample_Replacement() {
    replace_does_not_resolve_discarded_recipe();
}

#[no_mangle]
pub extern "C" fn Rust_AnimationRuleSample_EndpointError() {
    endpoint_failure_is_not_a_cached_value_or_animation_fallback();
}

#[no_mangle]
pub extern "C" fn Rust_AnimationRuleSample_MissingUnderlying() {
    missing_underlying_does_not_sample_progress_or_insert();
}

#[no_mangle]
pub extern "C" fn Rust_AnimationRuleSample_ConcreteBulk() {
    concrete_bulk_values_match_individual_roots_in_table_order();
}

#[no_mangle]
pub extern "C" fn Rust_AnimationRuleSample_RepeatedRoots() {
    shared_and_repeated_roots_match_individual_resolution();
}

#[no_mangle]
pub extern "C" fn Rust_AnimationRuleSample_InvalidRoots() {
    empty_and_invalid_root_sets_are_explicit();
}
