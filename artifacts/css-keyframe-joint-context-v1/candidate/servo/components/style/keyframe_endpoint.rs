/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/. */

//! Owned input declarations associated with computed keyframe endpoints.

use crate::properties::{OwnedPropertyDeclarationId, PropertyDeclaration};
use malloc_size_of::{MallocConditionalSizeOf, MallocSizeOf, MallocSizeOfOps};
use servo_arc::Arc;

/// One keyframe's input declarations, without computed target or registration state.
pub struct KeyframeEndpointContext {
    keyframe_index: usize,
    declarations: Vec<PropertyDeclaration>,
}

impl KeyframeEndpointContext {
    /// Own clones in the same prioritized order used by keyframe computation.
    pub fn new(keyframe_index: usize, declarations: Vec<PropertyDeclaration>) -> Self {
        Self {
            keyframe_index,
            declarations,
        }
    }

    /// The keyframe's index within this computation, not a global identity.
    pub fn keyframe_index(&self) -> usize {
        self.keyframe_index
    }

    /// Original input declarations, including retained URL and attribute namespace data.
    pub fn declarations(&self) -> &[PropertyDeclaration] {
        &self.declarations
    }
}

/// A selected computed property's source declaration and owned keyframe context.
pub struct KeyframeEndpoint {
    context: Arc<KeyframeEndpointContext>,
    declaration_index: usize,
    property: OwnedPropertyDeclarationId,
}

impl KeyframeEndpoint {
    /// Associate a declaration with the actual accepted computed output property.
    pub fn new(
        context: Arc<KeyframeEndpointContext>,
        declaration_index: usize,
        property: OwnedPropertyDeclarationId,
    ) -> Self {
        assert!(declaration_index < context.declarations.len());
        Self {
            context,
            declaration_index,
            property,
        }
    }

    /// The immutable input context retained independently of temporary keyframes.
    pub fn context(&self) -> &KeyframeEndpointContext {
        &self.context
    }

    /// The selected declaration's structural index in its owned context.
    pub fn declaration_index(&self) -> usize {
        self.declaration_index
    }

    /// The exact retained input declaration, not an uncomputed numeric substitute.
    pub fn declaration(&self) -> &PropertyDeclaration {
        &self.context.declarations[self.declaration_index]
    }

    /// The output property selected by the existing keyframe computation.
    pub fn property(&self) -> &OwnedPropertyDeclarationId {
        &self.property
    }
}

/// Internal unsupported work is distinct from CSS invalid-at-computed-value defaulting.
#[repr(C)]
#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub enum EndpointResolutionStatus {
    Resolved,
    NotRegisteredCustomProperty,
    PropertyMismatch,
    UnsupportedDeclaration,
    NeedsCascadeSelection,
}

impl KeyframeEndpoint {
    /// Resolve in an isolated context seeded from a complete current provider snapshot.
    /// This does not schedule other sampled roots or define animated-cycle behavior.
    pub fn resolve_registered(
        &self,
        stylist: &crate::stylist::Stylist,
        mut context: crate::values::computed::Context,
        attribute_tracker: &mut crate::dom::AttributeTracker,
    ) -> Result<crate::properties::animated_properties::AnimationValue, EndpointResolutionStatus>
    {
        self.resolve_registered_in_context(stylist, &mut context, attribute_tracker)
    }

    fn resolve_registered_in_context(
        &self,
        stylist: &crate::stylist::Stylist,
        context: &mut crate::values::computed::Context,
        attribute_tracker: &mut crate::dom::AttributeTracker,
    ) -> Result<crate::properties::animated_properties::AnimationValue, EndpointResolutionStatus>
    {
        use crate::custom_properties::{
            handle_invalid_at_computed_value_time, substitute_references_if_needed_and_apply,
        };
        use crate::properties::animated_properties::AnimationValue;
        use crate::properties::{
            CSSWideKeyword, CustomDeclarationValue, KeyframeCustomPropertiesBuilder,
        };
        use crate::properties_and_values::value::CustomAnimatedValue;

        let OwnedPropertyDeclarationId::Custom(name) = self.property() else {
            return Err(EndpointResolutionStatus::NotRegisteredCustomProperty);
        };
        let registration = stylist.get_custom_property_registration(name);
        if registration.is_universal() {
            return Err(EndpointResolutionStatus::NotRegisteredCustomProperty);
        }
        let PropertyDeclaration::Custom(declaration) = self.declaration() else {
            return Err(EndpointResolutionStatus::UnsupportedDeclaration);
        };
        if declaration.name != *name {
            return Err(EndpointResolutionStatus::PropertyMismatch);
        }
        let value = match &declaration.value {
            CustomDeclarationValue::Unparsed(tokens) => {
                let providers = context.builder.custom_properties().clone();
                let mut attributes =
                    KeyframeCustomPropertiesBuilder::new(stylist, context, providers);
                attributes.prepare_custom_endpoint_attributes(context, tokens, attribute_tracker);
                attributes.build_endpoint_attributes(context, attribute_tracker);
                substitute_references_if_needed_and_apply(
                    name,
                    None,
                    tokens,
                    stylist,
                    context,
                    attribute_tracker,
                );
                context
                    .builder
                    .custom_properties()
                    .get(registration, name)
                    .cloned()
            },
            CustomDeclarationValue::GuaranteedInvalid => {
                handle_invalid_at_computed_value_time(name, registration, context);
                context
                    .builder
                    .custom_properties()
                    .get(registration, name)
                    .cloned()
            },
            CustomDeclarationValue::CSSWideKeyword(keyword) => {
                if keyword.revert_kind().is_some() {
                    return Err(EndpointResolutionStatus::NeedsCascadeSelection);
                }
                let inherit = *keyword == CSSWideKeyword::Inherit
                    || (*keyword == CSSWideKeyword::Unset && registration.inherits());
                if inherit && !context.is_root_element() {
                    context
                        .builder
                        .inherited_style
                        .custom_properties()
                        .get(registration, name)
                        .cloned()
                } else {
                    stylist
                        .get_custom_property_initial_values()
                        .get(registration, name)
                        .cloned()
                }
            },
            CustomDeclarationValue::Parsed(_) => {
                return Err(EndpointResolutionStatus::UnsupportedDeclaration);
            },
        };
        Ok(AnimationValue::Custom(CustomAnimatedValue::from_computed(
            name,
            value.as_ref(),
        )))
    }
}

pub enum EndpointDemand {
    Provider(crate::custom_properties::Name),
    Prioritary(crate::properties::PrioritaryPropertyId),
    ContextPreparation,
    Unsupported(EndpointResolutionStatus),
}

impl KeyframeEndpoint {
    pub fn resolve_registered_with_pending(
        &self,
        stylist: &crate::stylist::Stylist,
        context: crate::values::computed::Context,
        attribute_tracker: &mut crate::dom::AttributeTracker,
        pending: &std::collections::HashSet<crate::custom_properties::Name>,
    ) -> Result<crate::properties::animated_properties::AnimationValue, EndpointDemand> {
        self.resolve_registered_with_pending_context(
            stylist,
            context,
            attribute_tracker,
            pending,
            &crate::properties::PrioritaryPropertyIdSet::default(),
        )
    }

    pub fn resolve_registered_with_pending_context(
        &self,
        stylist: &crate::stylist::Stylist,
        mut context: crate::values::computed::Context,
        attribute_tracker: &mut crate::dom::AttributeTracker,
        pending: &std::collections::HashSet<crate::custom_properties::Name>,
        pending_prioritary: &crate::properties::PrioritaryPropertyIdSet,
    ) -> Result<crate::properties::animated_properties::AnimationValue, EndpointDemand> {
        self.resolve_pending_in_context(
            stylist,
            &mut context,
            attribute_tracker,
            pending,
            pending_prioritary,
        )
    }

    fn resolve_pending_in_context(
        &self,
        stylist: &crate::stylist::Stylist,
        context: &mut crate::values::computed::Context,
        attribute_tracker: &mut crate::dom::AttributeTracker,
        pending: &std::collections::HashSet<crate::custom_properties::Name>,
        pending_prioritary: &crate::properties::PrioritaryPropertyIdSet,
    ) -> Result<crate::properties::animated_properties::AnimationValue, EndpointDemand> {
        use crate::custom_properties::{
            SubstitutionDemand, substitute_references_with_pending_and_apply,
        };
        use crate::properties::CustomDeclarationValue;
        use crate::properties::animated_properties::AnimationValue;
        use crate::properties_and_values::value::CustomAnimatedValue;

        if pending.is_empty() && pending_prioritary.is_empty() {
            return self
                .resolve_registered_in_context(stylist, context, attribute_tracker)
                .map_err(EndpointDemand::Unsupported);
        }
        let OwnedPropertyDeclarationId::Custom(name) = self.property() else {
            return Err(EndpointDemand::Unsupported(
                EndpointResolutionStatus::NotRegisteredCustomProperty,
            ));
        };
        let registration = stylist.get_custom_property_registration(name);
        if registration.is_universal() {
            return Err(EndpointDemand::Unsupported(
                EndpointResolutionStatus::NotRegisteredCustomProperty,
            ));
        }
        let PropertyDeclaration::Custom(declaration) = self.declaration() else {
            return Err(EndpointDemand::Unsupported(
                EndpointResolutionStatus::UnsupportedDeclaration,
            ));
        };
        if declaration.name != *name {
            return Err(EndpointDemand::Unsupported(
                EndpointResolutionStatus::PropertyMismatch,
            ));
        }
        let CustomDeclarationValue::Unparsed(tokens) = &declaration.value else {
            return self
                .resolve_registered_in_context(stylist, context, attribute_tracker)
                .map_err(EndpointDemand::Unsupported);
        };
        context.builder.substitution_functions.attributes.clear();
        let external_demand = |demand| match demand {
            SubstitutionDemand::Provider(name) => EndpointDemand::Provider(name),
            SubstitutionDemand::Prioritary(id) => EndpointDemand::Prioritary(id),
            SubstitutionDemand::Attribute { .. } | SubstitutionDemand::ContextPreparation => {
                EndpointDemand::ContextPreparation
            },
        };
        loop {
            match substitute_references_with_pending_and_apply(
                name,
                None,
                tokens,
                stylist,
                context,
                attribute_tracker,
                Some(pending),
                Some(pending_prioritary),
            ) {
                Ok(()) => break,
                Err(SubstitutionDemand::Attribute {
                    name,
                    data,
                    url_data,
                }) => {
                    crate::properties::KeyframeCustomPropertiesBuilder::resolve_requested_attribute(
                        stylist, context, &name, &data, &url_data,
                        attribute_tracker, pending, pending_prioritary,
                    ).map_err(external_demand)?;
                },
                Err(demand) => return Err(external_demand(demand)),
            }
        }
        let value = context.builder.custom_properties().get(registration, name);
        Ok(AnimationValue::Custom(CustomAnimatedValue::from_computed(
            name, value,
        )))
    }
}

/// Unpublished effects from one completed endpoint attempt.
pub struct EndpointEffects {
    pub(crate) flags: crate::computed_value_flags::ComputedValueFlags,
    pub(crate) attributes: crate::dom::AttributeReferences,
    pub(crate) cache_conditions: crate::rule_cache::RuleCacheConditions,
}

impl EndpointEffects {
    /// Whether this completed attempt queried a DOM attribute.
    pub fn references_attributes(&self) -> bool {
        self.attributes.is_some()
    }
}

impl KeyframeEndpoint {
    /// Resolve against an in-progress cascade without publishing attempt effects.
    pub fn resolve_from_cascade(
        &self,
        stylist: &crate::stylist::Stylist,
        context: &crate::values::computed::Context,
        pending: &std::collections::HashSet<crate::custom_properties::Name>,
        pending_prioritary: &crate::properties::PrioritaryPropertyIdSet,
    ) -> Result<
        (
            crate::properties::animated_properties::AnimationValue,
            EndpointEffects,
        ),
        EndpointDemand,
    > {
        let mut cache_conditions = crate::rule_cache::RuleCacheConditions::default();
        let mut tree_counting_caches = crate::context::TreeCountingCaches::default();
        let mut tracker = context.keyframe_attribute_tracker();
        let (value, flags) = {
            let mut attempt = context
                .fork_for_keyframe(&mut cache_conditions, &mut tree_counting_caches)
                .ok_or(EndpointDemand::ContextPreparation)?;
            let value = self.resolve_pending_in_context(
                stylist,
                &mut attempt,
                &mut tracker,
                pending,
                pending_prioritary,
            )?;
            (value, attempt.builder.flags())
        };
        Ok((
            value,
            EndpointEffects {
                flags,
                attributes: tracker.finalize(),
                cache_conditions,
            },
        ))
    }
}

impl MallocSizeOf for KeyframeEndpointContext {
    fn size_of(&self, ops: &mut MallocSizeOfOps) -> usize {
        self.declarations.size_of(ops)
    }
}

impl MallocSizeOf for KeyframeEndpoint {
    fn size_of(&self, ops: &mut MallocSizeOfOps) -> usize {
        let property = match &self.property {
            OwnedPropertyDeclarationId::Longhand(_) => 0,
            OwnedPropertyDeclarationId::Custom(name) => name.size_of(ops),
        };
        property + self.context.conditional_size_of(ops)
    }
}

#[repr(u8)]
pub enum EndpointDemandStatus {
    Resolved,
    Provider,
    Prioritary,
    ContextPreparation,
    Unsupported,
}
