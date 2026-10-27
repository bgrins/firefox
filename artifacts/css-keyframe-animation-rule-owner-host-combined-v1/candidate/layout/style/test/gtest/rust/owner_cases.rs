/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/. */

use servo_arc::Arc;
use std::mem::{align_of, size_of};
use style::animation_rule_sample::{SampledEndpoint, SampledSegment};
use style::gecko_bindings::bindings::{CompositeOperation, IterationCompositeOperation};
use style::properties::animated_properties::AnimationValue;
use style::properties::declaration_block::AnimationRuleSample;
use style::properties::{LonghandId, OwnedPropertyDeclarationId, PropertyDeclarationBlock};
use style::rule_tree::StyleSource;
use style::shared_lock::{Locked, SharedRwLock};

fn sample(lock: &SharedRwLock) -> Option<StyleSource> {
    let mut sample = AnimationRuleSample::with_capacity(1);
    let inserted = sample.compose_segment(
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
        || None,
        || (0.5, 0.5),
    );
    inserted.then(|| sample.into_rule_source(lock))
}

#[no_mangle]
pub extern "C" fn Rust_AnimationRuleSample_OwnerIdentity() {
    let lock = SharedRwLock::new();
    let source = sample(&lock);
    let other = sample(&lock);
    assert!(source.is_some() && other.is_some());
    let source = source.unwrap();
    let other = other.unwrap();
    let cloned = source.clone();
    let retained = source.borrow().to_owned();
    let concrete = StyleSource::from_declarations(source.clone_declarations());
    assert_eq!(source, cloned);
    assert_eq!(source, retained);
    assert_eq!(source.borrow(), retained.borrow());
    assert_ne!(source, other);
    assert_ne!(source, concrete);
    assert_ne!(source.borrow(), concrete.borrow());
    assert_eq!(concrete, concrete.borrow().to_owned());
    assert!(source.is_animation_sample());
    assert!(!concrete.is_animation_sample());
    assert!(std::ptr::eq(source.get(), concrete.get()));
    drop(source);
    drop(cloned);
    assert_eq!(retained.read(&lock.read()).declarations().len(), 1);
}

#[no_mangle]
pub extern "C" fn Rust_AnimationRuleSample_OwnerLifetime() {
    let lock = SharedRwLock::new();
    let source = sample(&lock);
    assert!(source.is_some());
    let source = source.unwrap();
    let guard = lock.read();
    let view = source.declaration_source(&guard);
    assert!(std::ptr::eq(view.declarations(), source.read(&guard)));
    assert!(view.animation().is_some());
    let property = view
        .animation()
        .unwrap()
        .property(&OwnedPropertyDeclarationId::Longhand(LonghandId::Opacity));
    assert!(property.is_some());
    let property = property.unwrap();
    let block = source.clone_declarations();
    drop(guard);
    drop(source);
    let value = property.resolve(|never| -> Result<AnimationValue, ()> { match *never {} });
    assert!(value.is_ok());
    assert!(matches!(value.unwrap(), AnimationValue::Opacity(v) if (v - 0.4).abs() < 0.000001));
    assert_eq!(block.read_with(&lock.read()).declarations().len(), 1);
}

#[no_mangle]
pub extern "C" fn Rust_AnimationRuleSample_OwnerLayout() {
    type Block = Arc<Locked<PropertyDeclarationBlock>>;
    assert_eq!(size_of::<StyleSource>(), size_of::<Block>());
    assert_eq!(align_of::<StyleSource>(), align_of::<Block>());
    assert_eq!(size_of::<Option<StyleSource>>(), size_of::<Option<Block>>());
    assert_eq!(
        align_of::<Option<StyleSource>>(),
        align_of::<Option<Block>>()
    );
    assert_eq!(size_of::<StyleSource>(), size_of::<usize>());
}
