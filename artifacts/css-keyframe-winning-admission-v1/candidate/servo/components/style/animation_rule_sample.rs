/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/. */

//! Owned per-property operation roots for normal animation-rule sampling.

use crate::FxHashMap;
use crate::deferred_animation_operations::{
    AnimationOperationArena, NodeId, ResolveError, SegmentOperands,
};
use crate::gecko_bindings::bindings::{CompositeOperation, IterationCompositeOperation};
use crate::properties::OwnedPropertyDeclarationId;
use crate::properties::animated_properties::AnimationValue;
use std::sync::Arc;

/// An owned operand, with no cached-value alternative for a retained recipe.
pub enum SampledEndpoint<E> {
    /// An already computed native value.
    Value(AnimationValue),
    /// A recipe owned by the sampling pass.
    Recipe(E),
}

/// Inputs selected by the existing segment and timing algorithms.
pub struct SampledSegment<E> {
    /// Missing endpoints use the underlying property root or base value.
    pub from: Option<SampledEndpoint<E>>,
    /// The selected segment's end operand.
    pub to: Option<SampledEndpoint<E>>,
    /// The from endpoint's composite mode.
    pub from_composite: CompositeOperation,
    /// The to endpoint's composite mode.
    pub to_composite: CompositeOperation,
    /// Whether the selected segment's offsets are equal.
    pub same_offset: bool,
    /// The last keyframe's value for iteration accumulation.
    pub last: Option<SampledEndpoint<E>>,
    /// The effect's iteration composite mode.
    pub iteration_composite: IterationCompositeOperation,
    /// The iteration count used for accumulation.
    pub current_iteration: u64,
}

/// An append-only normal-rule sample. Node handles never leave this owner.
pub struct AnimationOperationSample<E: 'static> {
    arena: AnimationOperationArena<E>,
    roots: FxHashMap<OwnedPropertyDeclarationId, NodeId>,
}

impl<E: 'static> AnimationOperationSample<E> {
    /// Reserve capacity for property roots.
    pub fn with_capacity(capacity: usize) -> Self {
        Self {
            arena: AnimationOperationArena::new(),
            roots: FxHashMap::with_capacity_and_hasher(capacity, Default::default()),
        }
    }

    fn operand(&mut self, endpoint: SampledEndpoint<E>) -> NodeId {
        match endpoint {
            SampledEndpoint::Value(value) => self.arena.value(value),
            SampledEndpoint::Recipe(recipe) => self.arena.endpoint(recipe),
        }
    }

    /// Compose one selected segment; false preserves native missing-base no-insertion.
    pub fn compose_segment(
        &mut self,
        property: OwnedPropertyDeclarationId,
        segment: SampledSegment<E>,
        base: impl FnOnce() -> Option<AnimationValue>,
        progress: impl FnOnce() -> (f64, f64),
    ) -> bool {
        let from = segment.from.map(|value| self.operand(value));
        let to = segment.to.map(|value| self.operand(value));
        let last = segment.last.map(|value| self.operand(value));
        let operands = SegmentOperands {
            from,
            to,
            from_composite: segment.from_composite,
            to_composite: segment.to_composite,
            same_offset: segment.same_offset,
        };
        let needed = operands.needs_underlying(
            segment.iteration_composite,
            segment.current_iteration,
            last.is_some(),
        );
        let underlying = if needed {
            self.roots
                .get(&property)
                .copied()
                .or_else(|| base().map(|value| self.arena.value(value)))
        } else {
            None
        };
        if needed && underlying.is_none() {
            return false;
        }
        let (total_progress, segment_progress) = progress();
        let root = self
            .arena
            .compose_segment(
                operands,
                underlying,
                last,
                segment.iteration_composite,
                segment.current_iteration,
                total_progress,
                segment_progress,
            )
            .expect("all operands belong to this sample")
            .expect("required underlying value was checked");
        self.roots.insert(property, root);
        true
    }

    /// Freeze collection without rehashing the property-root table.
    pub fn freeze(self) -> FrozenAnimationRule<E> {
        FrozenAnimationRule {
            arena: Arc::new(self.arena),
            roots: self.roots,
        }
    }
}

/// Owns a complete sampled rule before winning-property selection.
pub struct FrozenAnimationRule<E: 'static> {
    arena: Arc<AnimationOperationArena<E>>,
    roots: FxHashMap<OwnedPropertyDeclarationId, NodeId>,
}

impl<E: 'static> FrozenAnimationRule<E> {
    /// The number of surviving property roots.
    pub fn len(&self) -> usize {
        self.roots.len()
    }

    /// Whether no property was inserted.
    pub fn is_empty(&self) -> bool {
        self.roots.is_empty()
    }

    /// Retain one property independently of the containing rule.
    pub fn get(
        &self,
        property: &OwnedPropertyDeclarationId,
    ) -> Option<SampledAnimationProperty<E>> {
        self.roots
            .get(property)
            .map(|root| SampledAnimationProperty {
                arena: self.arena.clone(),
                root: *root,
            })
    }

    /// Consume the property table in its existing iteration order.
    pub fn into_properties(
        self,
    ) -> impl Iterator<Item = (OwnedPropertyDeclarationId, SampledAnimationProperty<E>)> {
        let arena = self.arena;
        self.roots.into_iter().map(move |(property, root)| {
            (
                property,
                SampledAnimationProperty {
                    arena: arena.clone(),
                    root,
                },
            )
        })
    }
}

impl FrozenAnimationRule<std::convert::Infallible> {
    /// Materialize all concrete roots without discarding their owner.
    pub fn concrete_values(&self) -> Vec<(OwnedPropertyDeclarationId, AnimationValue)> {
        let (properties, roots): (Vec<_>, Vec<_>) = self
            .roots
            .iter()
            .map(|(property, root)| (property.clone(), *root))
            .unzip();
        let values = self
            .arena
            .resolve_concrete_roots(&roots)
            .expect("all roots belong to the frozen arena");
        properties.into_iter().zip(values).collect()
    }

    /// Materialize concrete roots and release the sampled rule.
    pub fn into_concrete_values(self) -> Vec<(OwnedPropertyDeclarationId, AnimationValue)> {
        self.concrete_values()
    }
}

/// A frozen property root retains its arena and recipe payloads without borrowing the collector.
pub struct SampledAnimationProperty<E: 'static> {
    arena: Arc<AnimationOperationArena<E>>,
    root: NodeId,
}

impl<E: 'static> Clone for SampledAnimationProperty<E> {
    fn clone(&self) -> Self {
        Self {
            arena: self.arena.clone(),
            root: self.root,
        }
    }
}

impl<E: 'static> SampledAnimationProperty<E> {
    /// Return reachable recipes only, not discarded lower-effect recipes.
    pub fn endpoints(&self) -> Vec<&E> {
        self.arena
            .endpoints(self.root)
            .expect("root belongs to the frozen arena")
    }

    /// Materialize against one coherent provider context; endpoint errors remain errors.
    pub fn resolve<Error>(
        &self,
        resolve_endpoint: impl FnMut(&E) -> Result<AnimationValue, Error>,
    ) -> Result<AnimationValue, Error> {
        match self.arena.resolve(self.root, resolve_endpoint) {
            Ok(value) => Ok(value),
            Err(ResolveError::Endpoint(error)) => Err(error),
            Err(ResolveError::InvalidNode) => unreachable!("root belongs to the frozen arena"),
        }
    }
}

/// A concrete normal-animation rule retaining its sampled operation identities.
pub struct AnimationRuleSource {
    pending_custom: crate::selector_map::PrecomputedHashMap<
        crate::custom_properties::Name,
        crate::native_provider_completion::PendingProperty,
    >,
    sample: FrozenAnimationRule<std::convert::Infallible>,
    declarations:
        servo_arc::Arc<crate::shared_lock::Locked<crate::properties::PropertyDeclarationBlock>>,
}

impl AnimationRuleSource {
    pub(crate) fn new(
        sample: FrozenAnimationRule<std::convert::Infallible>,
        declarations: servo_arc::Arc<
            crate::shared_lock::Locked<crate::properties::PropertyDeclarationBlock>,
        >,
    ) -> Self {
        Self {
            sample,
            declarations,
            pending_custom: Default::default(),
        }
    }

    #[cfg(test)]
    pub(crate) fn new_pending_for_testing(
        declarations: servo_arc::Arc<
            crate::shared_lock::Locked<crate::properties::PropertyDeclarationBlock>,
        >,
        pending_custom: crate::selector_map::PrecomputedHashMap<
            crate::custom_properties::Name,
            crate::native_provider_completion::PendingProperty,
        >,
    ) -> Self {
        Self {
            sample: AnimationOperationSample::with_capacity(0).freeze(),
            declarations,
            pending_custom,
        }
    }

    pub(crate) fn pending_customs(
        &self,
    ) -> impl Iterator<
        Item = (
            &crate::custom_properties::Name,
            &crate::native_provider_completion::PendingProperty,
        ),
    > {
        self.pending_custom.iter()
    }

    pub(crate) fn has_pending_custom(&self, name: &crate::custom_properties::Name) -> bool {
        self.pending_custom.contains_key(name)
    }

    pub(crate) fn has_pending_customs(&self) -> bool {
        !self.pending_custom.is_empty()
    }

    /// The concrete declarations materialized from this sample.
    pub fn declarations(
        &self,
    ) -> &servo_arc::Arc<crate::shared_lock::Locked<crate::properties::PropertyDeclarationBlock>>
    {
        &self.declarations
    }

    /// Retain the selected property root independently of this rule.
    pub fn property(
        &self,
        property: &OwnedPropertyDeclarationId,
    ) -> Option<SampledAnimationProperty<std::convert::Infallible>> {
        if let OwnedPropertyDeclarationId::Custom(name) = property {
            if self.has_pending_custom(name) {
                return None;
            }
        }
        self.sample.get(property)
    }

    /// Whether this sample owns a root for the declaration.
    pub fn contains(&self, property: crate::properties::PropertyDeclarationId) -> bool {
        if let crate::properties::PropertyDeclarationId::Custom(name) = property {
            if self.has_pending_custom(name) {
                return true;
            }
        }
        self.sample.roots.contains_key(&property.to_owned())
    }
}

impl std::fmt::Debug for AnimationRuleSource {
    fn fmt(&self, formatter: &mut std::fmt::Formatter) -> std::fmt::Result {
        formatter
            .debug_struct("AnimationRuleSource")
            .field("properties", &self.sample.len())
            .field("pending_custom", &self.pending_custom.len())
            .finish()
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::properties::LonghandId;

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

    #[test]
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

    #[test]
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

    #[test]
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

    #[test]
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

    #[test]
    fn missing_underlying_does_not_sample_progress_or_insert() {
        let mut sample = AnimationOperationSample::<String>::with_capacity(1);
        let mut implicit = segment(
            SampledEndpoint::Value(AnimationValue::Opacity(2.)),
            SampledEndpoint::Value(AnimationValue::Opacity(6.)),
        );
        implicit.from = None;
        assert!(!sample.compose_segment(
            property(),
            implicit,
            || None,
            || panic!("no composition")
        ));
        assert!(sample.freeze().is_empty());
    }

    #[test]
    fn concrete_bulk_values_match_individual_roots_in_table_order() {
        let mut sample = AnimationOperationSample::<std::convert::Infallible>::with_capacity(2);
        let other = OwnedPropertyDeclarationId::Longhand(LonghandId::FloodOpacity);
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
            other.clone(),
            segment(
                SampledEndpoint::Value(AnimationValue::FloodOpacity(10.)),
                SampledEndpoint::Value(AnimationValue::FloodOpacity(30.)),
            ),
            || None,
            || (0.5, 0.5),
        );
        let frozen = sample.freeze();
        let expected: Vec<_> = frozen
            .roots
            .iter()
            .map(|(property, _)| {
                let value = frozen
                    .get(property)
                    .unwrap()
                    .resolve(|never| -> Result<_, std::convert::Infallible> { match *never {} })
                    .unwrap();
                (property.clone(), scalar(value))
            })
            .collect();
        let actual: Vec<_> = frozen
            .into_concrete_values()
            .into_iter()
            .map(|(property, value)| (property, scalar(value)))
            .collect();
        assert_eq!(actual, expected);
    }
}
