/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/. */

use crate::deferred_animation_operations::{AnimationOperationArena, NodeId, SegmentOperands};
use crate::gecko_bindings::bindings::{CompositeOperation as C, IterationCompositeOperation as I};
use crate::properties::animated_properties::AnimationValue as V;

fn segment(from: Option<NodeId>, to: Option<NodeId>, composite: C) -> SegmentOperands {
    SegmentOperands {
        from,
        to,
        from_composite: composite,
        to_composite: composite,
        same_offset: false,
    }
}

fn scalar(value: V) -> f32 {
    match value {
        V::Opacity(value) => value,
        _ => panic!("unexpected variant"),
    }
}

#[cfg_attr(test, test)]
fn interpolation() {
    let mut a = AnimationOperationArena::<()>::new();
    let from = a.value(V::Opacity(2.));
    let to = a.value(V::Opacity(6.));
    let root = a
        .compose_segment(
            segment(Some(from), Some(to), C::Replace),
            None,
            None,
            I::Replace,
            0,
            0.25,
            0.25,
        )
        .unwrap()
        .unwrap();
    assert_eq!(
        scalar(
            a.resolve(root, |_| -> Result<V, ()> { panic!("no endpoint") })
                .unwrap()
        ),
        3.
    );
}

#[cfg_attr(test, test)]
fn additive_underlying() {
    let mut a = AnimationOperationArena::<()>::new();
    let base = a.value(V::Opacity(10.));
    let from = a.value(V::Opacity(1.));
    let to = a.value(V::Opacity(3.));
    let root = a
        .compose_segment(
            segment(Some(from), Some(to), C::Add),
            Some(base),
            None,
            I::Replace,
            0,
            0.5,
            0.5,
        )
        .unwrap()
        .unwrap();
    assert_eq!(
        scalar(
            a.resolve(root, |_| -> Result<V, ()> { panic!("no endpoint") })
                .unwrap()
        ),
        12.
    );
}

#[cfg_attr(test, test)]
fn iteration_after_endpoint_composition() {
    let mut a = AnimationOperationArena::<()>::new();
    let base = a.value(V::Opacity(10.));
    let from = a.value(V::Opacity(1.));
    let to = a.value(V::Opacity(3.));
    let last = a.value(V::Opacity(4.));
    let root = a
        .compose_segment(
            segment(Some(from), Some(to), C::Add),
            Some(base),
            Some(last),
            I::Accumulate,
            2,
            0.5,
            0.5,
        )
        .unwrap()
        .unwrap();
    assert_eq!(
        scalar(
            a.resolve(root, |_| -> Result<V, ()> { panic!("no endpoint") })
                .unwrap()
        ),
        20.
    );
}

#[cfg_attr(test, test)]
fn implicit_endpoint_uses_underlying() {
    let mut a = AnimationOperationArena::<()>::new();
    let base = a.value(V::Opacity(10.));
    let to = a.value(V::Opacity(30.));
    let root = a
        .compose_segment(
            segment(None, Some(to), C::Replace),
            Some(base),
            None,
            I::Replace,
            0,
            0.25,
            0.25,
        )
        .unwrap()
        .unwrap();
    assert_eq!(
        scalar(
            a.resolve(root, |_| -> Result<V, ()> { panic!("no endpoint") })
                .unwrap()
        ),
        15.
    );
}

#[cfg_attr(test, test)]
fn equal_offset_selects_after_composition_and_iteration() {
    for (total, expected) in [(-0.5, 19.), (0., 21.)] {
        let mut a = AnimationOperationArena::<()>::new();
        let base = a.value(V::Opacity(10.));
        let from = a.value(V::Opacity(1.));
        let to = a.value(V::Opacity(3.));
        let last = a.value(V::Opacity(4.));
        let mut operands = segment(Some(from), Some(to), C::Add);
        operands.same_offset = true;
        let root = a
            .compose_segment(
                operands,
                Some(base),
                Some(last),
                I::Accumulate,
                2,
                total,
                0.99,
            )
            .unwrap()
            .unwrap();
        assert_eq!(
            scalar(
                a.resolve(root, |_| -> Result<V, ()> { panic!("no endpoint") })
                    .unwrap()
            ),
            expected
        );
    }
}

#[cfg_attr(test, test)]
fn extrapolation_is_not_clamped_by_arena() {
    let mut a = AnimationOperationArena::<()>::new();
    let from = a.value(V::Opacity(2.));
    let to = a.value(V::Opacity(6.));
    let root = a
        .compose_segment(
            segment(Some(from), Some(to), C::Replace),
            None,
            None,
            I::Replace,
            0,
            1.5,
            1.5,
        )
        .unwrap()
        .unwrap();
    assert_eq!(
        scalar(
            a.resolve(root, |_| -> Result<V, ()> { panic!("no endpoint") })
                .unwrap()
        ),
        8.
    );
}

#[cfg_attr(test, test)]
fn successful_shared_chain() {
    let mut a = AnimationOperationArena::new();
    let endpoint = a.endpoint(());
    let mut root = endpoint;
    for _ in 0..128 {
        root = a
            .compose_segment(
                segment(Some(endpoint), Some(endpoint), C::Add),
                Some(root),
                None,
                I::Replace,
                0,
                0.5,
                0.5,
            )
            .unwrap()
            .unwrap();
    }
    let mut calls = 0;
    let value = a
        .resolve(root, |_| {
            calls += 1;
            Ok::<V, ()>(V::Opacity(1.))
        })
        .unwrap();
    assert_eq!(scalar(value), 129.);
    assert_eq!(calls, 1);
}

#[cfg_attr(test, test)]
fn successful_replace_discards_old_endpoint() {
    let mut a = AnimationOperationArena::new();
    let old = a.endpoint("discarded");
    let from = a.endpoint("from");
    let to = a.endpoint("to");
    let root = a
        .compose_segment(
            segment(Some(from), Some(to), C::Replace),
            Some(old),
            None,
            I::Replace,
            0,
            0.25,
            0.25,
        )
        .unwrap()
        .unwrap();
    let mut calls = Vec::new();
    let value = a
        .resolve(root, |name| {
            calls.push(*name);
            Ok::<V, ()>(V::Opacity(match *name {
                "from" => 2.,
                "to" => 6.,
                _ => panic!("discarded endpoint"),
            }))
        })
        .unwrap();
    assert_eq!(scalar(value), 3.);
    assert_eq!(calls, vec!["from", "to"]);
}

#[cfg(feature = "gecko-gtest")]
pub(crate) fn run_all() {
    interpolation();
    additive_underlying();
    iteration_after_endpoint_composition();
    implicit_endpoint_uses_underlying();
    equal_offset_selects_after_composition_and_iteration();
    extrapolation_is_not_clamped_by_arena();
    successful_shared_chain();
    successful_replace_discards_old_endpoint();
}
