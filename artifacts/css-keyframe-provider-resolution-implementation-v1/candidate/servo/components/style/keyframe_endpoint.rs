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
                    KeyframeCustomPropertiesBuilder::new(stylist, &mut context, providers);
                attributes.prepare_custom_endpoint_attributes(
                    &mut context,
                    tokens,
                    attribute_tracker,
                );
                attributes.build_endpoint_attributes(&mut context, attribute_tracker);
                substitute_references_if_needed_and_apply(
                    name,
                    None,
                    tokens,
                    stylist,
                    &mut context,
                    attribute_tracker,
                );
                context
                    .builder
                    .custom_properties()
                    .get(registration, name)
                    .cloned()
            },
            CustomDeclarationValue::GuaranteedInvalid => {
                handle_invalid_at_computed_value_time(name, registration, &mut context);
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
