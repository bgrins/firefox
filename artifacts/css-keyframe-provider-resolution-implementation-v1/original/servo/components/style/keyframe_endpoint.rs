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
