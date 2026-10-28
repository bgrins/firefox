/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/. */

use crate::gecko_bindings::bindings::{CompositeOperation, IterationCompositeOperation};
use crate::properties::animated_properties::AnimationValue;
use crate::values::animated::{Animate, Procedure};

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub struct NodeId(usize);

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub struct InvalidNode;

#[derive(Debug)]
pub enum ResolveError<E> {
    InvalidNode,
    Endpoint(E),
}

enum Node<E> {
    Value(AnimationValue),
    Endpoint(E),
    Animate {
        from: NodeId,
        to: NodeId,
        procedure: Procedure,
        fallback_from: bool,
    },
    Select {
        from: NodeId,
        to: NodeId,
        select_from: bool,
    },
}

impl<E> Node<E> {
    fn operands(&self) -> Option<[NodeId; 2]> {
        match self {
            Self::Value(_) | Self::Endpoint(_) => None,
            Self::Animate { from, to, .. } | Self::Select { from, to, .. } => Some([*from, *to]),
        }
    }
}

pub struct AnimationOperationArena<E> {
    nodes: Vec<Node<E>>,
}

impl<E> AnimationOperationArena<E> {
    pub fn new() -> Self {
        Self { nodes: Vec::new() }
    }

    fn push(&mut self, node: Node<E>) -> NodeId {
        let id = NodeId(self.nodes.len());
        self.nodes.push(node);
        id
    }

    pub fn value(&mut self, value: AnimationValue) -> NodeId {
        self.push(Node::Value(value))
    }

    pub fn endpoint(&mut self, endpoint: E) -> NodeId {
        self.push(Node::Endpoint(endpoint))
    }

    fn check(&self, id: NodeId) -> Result<(), InvalidNode> {
        self.nodes.get(id.0).map(|_| ()).ok_or(InvalidNode)
    }

    fn animate(
        &mut self,
        from: NodeId,
        to: NodeId,
        procedure: Procedure,
        fallback_from: bool,
    ) -> Result<NodeId, InvalidNode> {
        self.check(from)?;
        self.check(to)?;
        Ok(self.push(Node::Animate {
            from,
            to,
            procedure,
            fallback_from,
        }))
    }

    pub fn endpoints(&self, root: NodeId) -> Result<Vec<&E>, InvalidNode> {
        self.check(root)?;
        let mut seen = vec![false; self.nodes.len()];
        let mut stack = vec![root];
        let mut endpoints = Vec::new();
        while let Some(id) = stack.pop() {
            if seen[id.0] {
                continue;
            }
            seen[id.0] = true;
            let node = &self.nodes[id.0];
            if let Node::Endpoint(endpoint) = node {
                endpoints.push(endpoint);
            }
            if let Some([from, to]) = node.operands() {
                stack.push(to);
                stack.push(from);
            }
        }
        Ok(endpoints)
    }

    pub fn resolve<Error>(
        &self,
        root: NodeId,
        mut resolve_endpoint: impl FnMut(&E) -> Result<AnimationValue, Error>,
    ) -> Result<AnimationValue, ResolveError<Error>> {
        self.check(root).map_err(|_| ResolveError::InvalidNode)?;
        let mut values: Vec<Option<AnimationValue>> = std::iter::repeat_with(|| None)
            .take(self.nodes.len())
            .collect();
        let mut reachable = vec![false; self.nodes.len()];
        let mut stack = vec![root];
        while let Some(id) = stack.pop() {
            if reachable[id.0] {
                continue;
            }
            reachable[id.0] = true;
            if let Some([from, to]) = self.nodes[id.0].operands() {
                stack.push(to);
                stack.push(from);
            }
        }
        // Operands precede their operation, so insertion order is postorder.
        for (index, node) in self.nodes.iter().enumerate() {
            if !reachable[index] {
                continue;
            }
            let result = match node {
                Node::Value(value) => value.clone(),
                Node::Endpoint(endpoint) => {
                    resolve_endpoint(endpoint).map_err(ResolveError::Endpoint)?
                },
                Node::Animate {
                    from,
                    to,
                    procedure,
                    fallback_from,
                } => {
                    let from = values[from.0].as_ref().unwrap();
                    let to = values[to.0].as_ref().unwrap();
                    from.animate(to, *procedure).unwrap_or_else(|_| {
                        if *fallback_from {
                            from.clone()
                        } else {
                            to.clone()
                        }
                    })
                },
                Node::Select {
                    from,
                    to,
                    select_from,
                } => values[if *select_from { from.0 } else { to.0 }]
                    .as_ref()
                    .unwrap()
                    .clone(),
            };
            values[index] = Some(result);
        }
        Ok(values[root.0].take().unwrap())
    }

    fn composite_endpoint(
        &mut self,
        endpoint: Option<NodeId>,
        composite: CompositeOperation,
        underlying: Option<NodeId>,
    ) -> Result<NodeId, InvalidNode> {
        let Some(endpoint) = endpoint else {
            return underlying.ok_or(InvalidNode);
        };
        match composite {
            CompositeOperation::Add => self.animate(
                underlying.ok_or(InvalidNode)?,
                endpoint,
                Procedure::Add,
                false,
            ),
            CompositeOperation::Accumulate => self.animate(
                underlying.ok_or(InvalidNode)?,
                endpoint,
                Procedure::Accumulate { count: 1 },
                false,
            ),
            _ => Ok(endpoint),
        }
    }

    pub fn compose_segment(
        &mut self,
        segment: SegmentOperands,
        underlying: Option<NodeId>,
        last: Option<NodeId>,
        iteration_composite: IterationCompositeOperation,
        current_iteration: u64,
        total_progress: f64,
        segment_progress: f64,
    ) -> Result<Option<NodeId>, InvalidNode> {
        let needs_underlying =
            segment.needs_underlying(iteration_composite, current_iteration, last.is_some());
        if needs_underlying && underlying.is_none() {
            return Ok(None);
        }
        for id in [segment.from, segment.to].into_iter().flatten() {
            self.check(id)?;
        }
        if needs_underlying {
            self.check(underlying.unwrap())?;
        }
        let accumulate =
            iteration_composite == IterationCompositeOperation::Accumulate && current_iteration > 0;
        if accumulate {
            self.check(last.or(underlying).ok_or(InvalidNode)?)?;
        }
        let mut from = self.composite_endpoint(segment.from, segment.from_composite, underlying)?;
        let mut to = self.composite_endpoint(segment.to, segment.to_composite, underlying)?;
        if accumulate {
            let last = last.or(underlying).unwrap();
            let procedure = Procedure::Accumulate {
                count: current_iteration,
            };
            from = self.animate(last, from, procedure, false)?;
            to = self.animate(last, to, procedure, false)?;
        }
        let root = if segment.same_offset {
            self.push(Node::Select {
                from,
                to,
                select_from: total_progress < 0.,
            })
        } else {
            self.animate(
                from,
                to,
                Procedure::Interpolate {
                    progress: segment_progress,
                },
                segment_progress < 0.5,
            )?
        };
        Ok(Some(root))
    }
}

pub struct SegmentOperands {
    pub from: Option<NodeId>,
    pub to: Option<NodeId>,
    pub from_composite: CompositeOperation,
    pub to_composite: CompositeOperation,
    pub same_offset: bool,
}

impl SegmentOperands {
    pub fn needs_underlying(
        &self,
        iteration_composite: IterationCompositeOperation,
        current_iteration: u64,
        last_present: bool,
    ) -> bool {
        self.from.is_none()
            || self.to.is_none()
            || self.from_composite != CompositeOperation::Replace
            || self.to_composite != CompositeOperation::Replace
            || (iteration_composite == IterationCompositeOperation::Accumulate
                && current_iteration > 0
                && !last_present)
    }
}

impl AnimationOperationArena<std::convert::Infallible> {
    pub fn resolve_concrete_roots(
        &self,
        roots: &[NodeId],
    ) -> Result<Vec<AnimationValue>, InvalidNode> {
        for root in roots {
            self.check(*root)?;
        }
        if roots.is_empty() {
            return Ok(Vec::new());
        }
        let mut reachable = vec![false; self.nodes.len()];
        let mut stack = roots.to_vec();
        while let Some(id) = stack.pop() {
            if reachable[id.0] {
                continue;
            }
            reachable[id.0] = true;
            if let Some([from, to]) = self.nodes[id.0].operands() {
                stack.push(to);
                stack.push(from);
            }
        }
        let mut values: Vec<Option<AnimationValue>> = std::iter::repeat_with(|| None)
            .take(self.nodes.len())
            .collect();
        for (index, node) in self.nodes.iter().enumerate() {
            if !reachable[index] {
                continue;
            }
            let value = match node {
                Node::Value(value) => value.clone(),
                Node::Endpoint(never) => match *never {},
                Node::Animate {
                    from,
                    to,
                    procedure,
                    fallback_from,
                } => {
                    let from = values[from.0].as_ref().unwrap();
                    let to = values[to.0].as_ref().unwrap();
                    from.animate(to, *procedure).unwrap_or_else(|_| {
                        if *fallback_from {
                            from.clone()
                        } else {
                            to.clone()
                        }
                    })
                },
                Node::Select {
                    from,
                    to,
                    select_from,
                } => values[if *select_from { from.0 } else { to.0 }]
                    .as_ref()
                    .unwrap()
                    .clone(),
            };
            values[index] = Some(value);
        }
        Ok(roots
            .iter()
            .map(|root| values[root.0].as_ref().unwrap().clone())
            .collect())
    }
}

#[cfg(test)]
mod concrete_tests {
    use super::*;

    #[test]
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
                        |never| -> Result<AnimationValue, std::convert::Infallible> {
                            match *never {}
                        },
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

    #[test]
    fn empty_and_invalid_root_sets_are_explicit() {
        let arena = AnimationOperationArena::<std::convert::Infallible>::new();
        assert!(arena.resolve_concrete_roots(&[]).unwrap().is_empty());
        assert!(matches!(
            arena.resolve_concrete_roots(&[NodeId(0)]),
            Err(InvalidNode)
        ));
    }
}
