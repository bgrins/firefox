/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/. */

use crate::animation_rule_sample::SampledAnimationProperty;
use crate::custom_properties::Name;
use crate::keyframe_endpoint::KeyframeEndpoint;
use crate::properties::animated_properties::AnimationValue;
use crate::properties_and_values::value::ComputedValue;
use crate::winning_provider_completion::{Evaluation, ProviderView, WinningProviders};
use servo_arc::Arc;
use std::collections::HashMap;

#[derive(Clone)]
pub(crate) struct PendingProperty {
    pub(crate) root: SampledAnimationProperty<Arc<KeyframeEndpoint>>,
    pub(crate) computations: Vec<Arc<KeyframeEndpoint>>,
}

pub(crate) type NativeWinners<C> =
    WinningProviders<C, Name, Option<ComputedValue>, PendingProperty>;
pub(crate) type NativeProviders<'a> =
    ProviderView<'a, Name, Option<ComputedValue>, PendingProperty>;

pub(crate) enum Demand<E> {
    Provider(Name),
    Error(E),
}

pub(crate) enum NativeFailure<E> {
    Endpoint(E),
    MissingComputation,
    WrongProperty,
}

// The callback must use an isolated endpoint context and return unpublished effects.
// Demand::Provider is control flow; guaranteed-invalid is Ready(None) in the view.
pub(crate) fn evaluate_property<C, X, E>(
    context: &C,
    name: &Name,
    property: &PendingProperty,
    providers: &NativeProviders<'_>,
    mut endpoint: impl FnMut(
        &C,
        &KeyframeEndpoint,
        &NativeProviders<'_>,
    ) -> Result<(AnimationValue, X), Demand<E>>,
) -> Evaluation<Name, Option<ComputedValue>, Vec<X>, NativeFailure<E>> {
    let mut values = HashMap::new();
    let mut effects = Vec::new();
    for descriptor in &property.computations {
        let key = &**descriptor as *const KeyframeEndpoint;
        if values.contains_key(&key) {
            continue;
        }
        let (value, local_effects) = match endpoint(context, descriptor, providers) {
            Ok(result) => result,
            Err(Demand::Provider(name)) => return Evaluation::Need(name),
            Err(Demand::Error(error)) => {
                return Evaluation::Error(NativeFailure::Endpoint(error));
            },
        };
        values.insert(key, value);
        effects.push(local_effects);
    }
    let result = property.root.resolve(|descriptor| {
        let key = &**descriptor as *const KeyframeEndpoint;
        values
            .get(&key)
            .cloned()
            .ok_or(NativeFailure::MissingComputation)
    });
    let value = match result {
        Ok(AnimationValue::Custom(value)) if value.name == *name => value.value.clone(),
        Ok(_) => return Evaluation::Error(NativeFailure::WrongProperty),
        Err(error) => return Evaluation::Error(error),
    };
    Evaluation::Complete { value, effects }
}

pub(crate) enum AdmittedCustomProperty {
    Ordinary(crate::properties::CustomDeclaration),
    Animated(PendingProperty),
}

pub(crate) struct CollectedCustomProperties {
    winners: Vec<(Name, AdmittedCustomProperty)>,
}

pub(crate) type AdmittedNativeWinners<C> =
    WinningProviders<C, Name, Option<ComputedValue>, AdmittedCustomProperty>;

impl CollectedCustomProperties {
    pub(crate) fn from_admitted(winners: Vec<(Name, AdmittedCustomProperty)>) -> Self {
        Self { winners }
    }

    pub(crate) fn into_owner<C>(
        self,
        context: C,
        already_computed: HashMap<Name, Option<ComputedValue>>,
    ) -> Result<AdmittedNativeWinners<C>, Name> {
        let mut owner = WinningProviders::new(context, already_computed);
        for (name, winner) in self.winners {
            if owner
                .admit(
                    name.clone(),
                    crate::winning_provider_completion::Winner::Pending(winner),
                )
                .is_err()
            {
                return Err(name);
            }
        }
        Ok(owner)
    }
}
