/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/. */

#![deny(unsafe_code)]

use crate::properties::PropertyDeclarationBlock;
use crate::shared_lock::{Locked, SharedRwLockReadGuard};
use servo_arc::{Arc, ArcBorrow};
#[cfg(feature = "gecko")]
use servo_arc::{ArcUnion, ArcUnionBorrow, ArcUnionBorrowPtr};
use std::io::Write;
use std::ptr;

/// An owned declaration source for a rule node.
#[cfg(feature = "gecko")]
#[derive(Clone, Debug)]
pub struct StyleSource(
    ArcUnion<Locked<PropertyDeclarationBlock>, crate::animation_rule_sample::AnimationRuleSource>,
);

#[cfg(not(feature = "gecko"))]
#[derive(Clone, Debug)]
pub struct StyleSource(Arc<Locked<PropertyDeclarationBlock>>);

const _: [(); std::mem::size_of::<Arc<Locked<PropertyDeclarationBlock>>>()] =
    [(); std::mem::size_of::<StyleSource>()];
const _: [(); std::mem::size_of::<Option<Arc<Locked<PropertyDeclarationBlock>>>>()] =
    [(); std::mem::size_of::<Option<StyleSource>>()];

/// A source borrowed while collecting applicable declarations.
#[cfg(feature = "gecko")]
#[derive(Clone, Copy, Debug)]
pub struct StyleSourceBorrow<'a>(
    ArcUnionBorrowPtr<
        'a,
        Locked<PropertyDeclarationBlock>,
        crate::animation_rule_sample::AnimationRuleSource,
    >,
);

#[cfg(not(feature = "gecko"))]
#[derive(Clone, Copy, Debug)]
pub struct StyleSourceBorrow<'a>(ArcBorrow<'a, Locked<PropertyDeclarationBlock>>);

const _: [(); std::mem::size_of::<ArcBorrow<'static, Locked<PropertyDeclarationBlock>>>()] =
    [(); std::mem::size_of::<StyleSourceBorrow<'static>>()];
const _: [(); std::mem::size_of::<Option<ArcBorrow<'static, Locked<PropertyDeclarationBlock>>>>()] =
    [(); std::mem::size_of::<Option<StyleSourceBorrow<'static>>>()];

malloc_size_of::malloc_size_of_is_0!(StyleSourceBorrow<'_>);

/// Declarations and their optional sampled owner, borrowed for one cascade.
#[derive(Clone, Copy)]
pub struct DeclarationSource<'a> {
    declarations: &'a PropertyDeclarationBlock,
    #[cfg(feature = "gecko")]
    animation: Option<&'a crate::animation_rule_sample::AnimationRuleSource>,
}

impl<'a> DeclarationSource<'a> {
    /// A direct concrete declaration input, without a sampled owner.
    pub fn from_declarations(declarations: &'a PropertyDeclarationBlock) -> Self {
        Self {
            declarations,
            #[cfg(feature = "gecko")]
            animation: None,
        }
    }

    /// Concrete declarations, also retaining the existing block identity for revert handling.
    pub fn declarations(self) -> &'a PropertyDeclarationBlock {
        self.declarations
    }

    /// The owner of the concrete property roots, if this is an animation sample.
    #[cfg(feature = "gecko")]
    pub fn animation(self) -> Option<&'a crate::animation_rule_sample::AnimationRuleSource> {
        self.animation
    }
}

// Declaration blocks are measured by their owners. Animation sample reporting
// needs a shared seen-pointer state for the retained arena and declaration block.
malloc_size_of::malloc_size_of_is_0!(StyleSource);

impl PartialEq for StyleSource {
    fn eq(&self, other: &Self) -> bool {
        #[cfg(feature = "gecko")]
        {
            ArcUnion::ptr_eq(&self.0, &other.0)
        }
        #[cfg(not(feature = "gecko"))]
        {
            Arc::ptr_eq(&self.0, &other.0)
        }
    }
}

impl<'a> PartialEq for StyleSourceBorrow<'a> {
    fn eq(&self, other: &Self) -> bool {
        #[cfg(feature = "gecko")]
        {
            ArcUnionBorrowPtr::ptr_eq(&self.0, &other.0)
        }
        #[cfg(not(feature = "gecko"))]
        {
            ArcBorrow::ptr_eq(&self.0, &other.0)
        }
    }
}

impl<'a> StyleSourceBorrow<'a> {
    /// Borrow a concrete declaration block.
    #[inline]
    pub fn from_declarations(decls: ArcBorrow<'a, Locked<PropertyDeclarationBlock>>) -> Self {
        #[cfg(feature = "gecko")]
        {
            Self(ArcUnionBorrowPtr::from_first(decls))
        }
        #[cfg(not(feature = "gecko"))]
        {
            Self(decls)
        }
    }

    /// Retain the actual source owner in the rule tree.
    #[inline]
    pub fn to_owned(&self) -> StyleSource {
        #[cfg(feature = "gecko")]
        {
            StyleSource(self.0.to_owned())
        }
        #[cfg(not(feature = "gecko"))]
        {
            StyleSource::from_declarations(self.0.clone_arc())
        }
    }

    #[inline]
    pub(super) fn key(&self) -> ptr::NonNull<()> {
        #[cfg(feature = "gecko")]
        {
            match self.0.borrow() {
                ArcUnionBorrow::First(decls) => ptr::NonNull::from(decls.get()).cast(),
                ArcUnionBorrow::Second(rule) => ptr::NonNull::from(rule.get()).cast(),
            }
        }
        #[cfg(not(feature = "gecko"))]
        {
            ptr::NonNull::from(self.0.get()).cast()
        }
    }

    pub(super) fn any_normal(&self, guard: &SharedRwLockReadGuard) -> bool {
        #[cfg(feature = "gecko")]
        if let ArcUnionBorrow::Second(rule) = self.0.borrow() {
            if rule.get().has_pending_customs() {
                return true;
            }
        }
        self.read(guard).any_normal()
    }

    /// Read this source's concrete declarations.
    #[inline]
    pub fn read<'b>(&self, guard: &'b SharedRwLockReadGuard) -> &'b PropertyDeclarationBlock
    where
        'a: 'b,
    {
        #[cfg(feature = "gecko")]
        {
            match self.0.borrow() {
                ArcUnionBorrow::First(decls) => decls.get().read_with(guard),
                ArcUnionBorrow::Second(rule) => rule.get().declarations().read_with(guard),
            }
        }
        #[cfg(not(feature = "gecko"))]
        {
            self.0.get().read_with(guard)
        }
    }
}

impl StyleSource {
    #[inline]
    pub(super) fn key(&self) -> ptr::NonNull<()> {
        self.borrow().key()
    }

    /// Borrow the actual source owner.
    #[inline]
    pub fn borrow(&self) -> StyleSourceBorrow<'_> {
        #[cfg(feature = "gecko")]
        {
            StyleSourceBorrow(ArcUnionBorrowPtr::from_union(&self.0))
        }
        #[cfg(not(feature = "gecko"))]
        {
            StyleSourceBorrow(self.0.borrow_arc())
        }
    }

    /// Create a source from a concrete declaration block.
    #[inline]
    pub fn from_declarations(decls: Arc<Locked<PropertyDeclarationBlock>>) -> Self {
        #[cfg(feature = "gecko")]
        {
            Self(ArcUnion::from_first(decls))
        }
        #[cfg(not(feature = "gecko"))]
        {
            Self(decls)
        }
    }

    /// Retain an immutable normal-animation sample.
    #[cfg(feature = "gecko")]
    pub fn from_animation(rule: Arc<crate::animation_rule_sample::AnimationRuleSource>) -> Self {
        Self(ArcUnion::from_second(rule))
    }

    /// Whether rule-cache identity must retain a sampled owner.
    pub fn is_animation_sample(&self) -> bool {
        #[cfg(feature = "gecko")]
        {
            self.0.is_second()
        }
        #[cfg(not(feature = "gecko"))]
        {
            false
        }
    }

    pub(super) fn dump<W: Write>(&self, guard: &SharedRwLockReadGuard, writer: &mut W) {
        let _ = write!(writer, "  -> {:?}", self.read(guard).declarations());
    }

    /// Read the source's concrete declarations.
    #[inline]
    pub fn read<'a>(&'a self, guard: &'a SharedRwLockReadGuard) -> &'a PropertyDeclarationBlock {
        self.get().read_with(guard)
    }

    /// Read declarations while preserving their sampled owner for cascade admission.
    pub fn declaration_source<'a>(
        &'a self,
        guard: &'a SharedRwLockReadGuard,
    ) -> DeclarationSource<'a> {
        DeclarationSource {
            declarations: self.read(guard),
            #[cfg(feature = "gecko")]
            animation: match self.0.borrow() {
                ArcUnionBorrow::Second(rule) => Some(rule.get()),
                ArcUnionBorrow::First(_) => None,
            },
        }
    }

    /// The concrete block, including the materialized block of an animation sample.
    #[inline]
    pub fn get(&self) -> &Locked<PropertyDeclarationBlock> {
        self.declarations().get()
    }

    /// Borrow the block's Arc without changing its ownership.
    #[inline]
    pub fn declarations(&self) -> ArcBorrow<'_, Locked<PropertyDeclarationBlock>> {
        #[cfg(feature = "gecko")]
        {
            match self.0.borrow() {
                ArcUnionBorrow::First(block) => block,
                ArcUnionBorrow::Second(rule) => rule.get().declarations().borrow_arc(),
            }
        }
        #[cfg(not(feature = "gecko"))]
        {
            self.0.borrow_arc()
        }
    }

    /// Return an owned concrete block for compatibility callers.
    #[inline]
    pub fn clone_declarations(&self) -> Arc<Locked<PropertyDeclarationBlock>> {
        self.declarations().clone_arc()
    }

    /// Marks this block as part of the rule tree.
    #[inline]
    pub fn mark_in_rule_tree(&self) {
        use std::sync::atomic::Ordering;
        self.declarations().with_arc(|block| {
            if block.is_static() {
                // Static blocks are already immutable.
                return;
            }
            // SAFETY: The Arc keeps the block alive; only its relaxed atomic is accessed.
            #[allow(unsafe_code)]
            unsafe {
                let immutable = &block.read_unchecked().immutable;
                if !immutable.load(Ordering::Relaxed) {
                    immutable.store(true, Ordering::Relaxed);
                }
            }
        });
    }
}

#[cfg(all(test, feature = "gecko"))]
mod tests {
    use super::*;
    use crate::animation_rule_sample::{SampledEndpoint, SampledSegment};
    use crate::gecko_bindings::bindings::{CompositeOperation, IterationCompositeOperation};
    use crate::properties::animated_properties::AnimationValue;
    use crate::properties::declaration_block::AnimationRuleSample;
    use crate::properties::{LonghandId, OwnedPropertyDeclarationId};
    use crate::shared_lock::SharedRwLock;

    fn sampled_source(lock: &SharedRwLock) -> StyleSource {
        let mut sample = AnimationRuleSample::with_capacity(1);
        assert!(sample.compose_segment(
            OwnedPropertyDeclarationId::Longhand(LonghandId::Opacity),
            SampledSegment {
                from: Some(SampledEndpoint::Value(AnimationValue::Opacity(0.2))),
                to: Some(SampledEndpoint::Value(AnimationValue::Opacity(0.6))),
                from_composite: CompositeOperation::Replace,
                to_composite: CompositeOperation::Replace,
                same_offset: false,
                last: None,
                iteration_composite: IterationCompositeOperation::Replace,
                current_iteration: 0,
            },
            || panic!("replace needs no base"),
            || (0.5, 0.5),
        ));
        sample.into_rule_source(lock)
    }

    #[test]
    fn sample_identity_is_not_its_concrete_block_identity() {
        let lock = SharedRwLock::new();
        let source = sampled_source(&lock);
        let retained = source.borrow().to_owned();
        let concrete = StyleSource::from_declarations(source.clone_declarations());
        let other_sample = sampled_source(&lock);
        assert_eq!(source, retained);
        assert_eq!(source.key(), retained.key());
        assert_ne!(source, concrete);
        assert_ne!(source.key(), concrete.key());
        assert_ne!(source, other_sample);
        assert!(source.is_animation_sample());
        assert!(!concrete.is_animation_sample());
        assert_eq!(concrete, concrete.borrow().to_owned());
    }

    #[test]
    fn cascade_source_and_retained_property_share_the_sample() {
        let lock = SharedRwLock::new();
        let source = sampled_source(&lock);
        let guard = lock.read();
        let view = source.declaration_source(&guard);
        assert!(std::ptr::eq(view.declarations(), source.read(&guard)));
        assert_eq!(view.declarations().declarations().len(), 1);
        let property = view
            .animation()
            .unwrap()
            .property(&OwnedPropertyDeclarationId::Longhand(LonghandId::Opacity))
            .unwrap();
        drop(guard);
        drop(source);
        let value = property
            .resolve(|never| -> Result<AnimationValue, ()> { match *never {} })
            .unwrap();
        match value {
            AnimationValue::Opacity(value) => assert!((value - 0.4).abs() < 0.000001),
            _ => panic!("wrong property"),
        }
    }
}
