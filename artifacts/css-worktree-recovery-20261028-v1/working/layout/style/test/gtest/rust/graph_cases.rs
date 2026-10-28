/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/. */

use style::deferred_animation_operations::{
    AnimationOperationArena, NodeId, ResolveError, SegmentOperands,
};
use style::gecko_bindings::bindings::{CompositeOperation, IterationCompositeOperation};

fn segment(from: NodeId, to: NodeId, composite: CompositeOperation) -> SegmentOperands {
    SegmentOperands {
        from: Some(from),
        to: Some(to),
        from_composite: composite,
        to_composite: composite,
        same_offset: false,
    }
}

fn complete_replace_does_not_resolve_discarded_underlying() {
    let mut arena = AnimationOperationArena::new();
    let old = arena.endpoint("discarded");
    let from = arena.endpoint("from");
    let to = arena.endpoint("to");
    let root = arena
        .compose_segment(
            segment(from, to, CompositeOperation::Replace),
            Some(old),
            None,
            IterationCompositeOperation::Replace,
            0,
            0.5,
            0.5,
        )
        .unwrap()
        .unwrap();
    assert_eq!(arena.endpoints(root).unwrap(), vec![&"from", &"to"]);
    let mut visited = Vec::new();
    let result = arena.resolve(root, |endpoint| {
        visited.push(*endpoint);
        Err("provider failure")
    });
    assert!(matches!(
        result,
        Err(ResolveError::Endpoint("provider failure"))
    ));
    assert_eq!(visited, vec!["from"]);
}

fn additive_operation_retains_pending_underlying() {
    let mut arena = AnimationOperationArena::new();
    let old = arena.endpoint("underlying");
    let from = arena.endpoint("from");
    let to = arena.endpoint("to");
    let root = arena
        .compose_segment(
            segment(from, to, CompositeOperation::Add),
            Some(old),
            None,
            IterationCompositeOperation::Replace,
            0,
            0.5,
            0.5,
        )
        .unwrap()
        .unwrap();
    assert_eq!(
        arena.endpoints(root).unwrap(),
        vec![&"underlying", &"from", &"to"]
    );
}

fn missing_underlying_does_not_construct_a_replacement() {
    let mut arena = AnimationOperationArena::new();
    let endpoint = arena.endpoint(());
    let root = arena
        .compose_segment(
            segment(endpoint, endpoint, CompositeOperation::Add),
            None,
            None,
            IterationCompositeOperation::Replace,
            0,
            0.5,
            0.5,
        )
        .unwrap();
    assert!(root.is_none());
}

fn deep_shared_stack_has_no_recursive_graph_ownership_or_depth_limit() {
    let mut arena = AnimationOperationArena::new();
    let endpoint = arena.endpoint(());
    let mut root = endpoint;
    for _ in 0..10_000 {
        root = arena
            .compose_segment(
                segment(endpoint, endpoint, CompositeOperation::Add),
                Some(root),
                None,
                IterationCompositeOperation::Replace,
                0,
                0.5,
                0.5,
            )
            .unwrap()
            .unwrap();
    }
    assert_eq!(arena.endpoints(root).unwrap().len(), 1);
    let result = arena.resolve(root, |_| Err(()));
    assert!(matches!(result, Err(ResolveError::Endpoint(()))));
}
#[cfg(feature = "gecko-gtest")]
pub(crate) fn run_all() {
    complete_replace_does_not_resolve_discarded_underlying();
    additive_operation_retains_pending_underlying();
    missing_underlying_does_not_construct_a_replacement();
    deep_shared_stack_has_no_recursive_graph_ownership_or_depth_limit();
}
