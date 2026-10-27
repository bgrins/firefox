/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/. */

use style::keyframe_endpoint::KeyframeEndpoint;
use style::properties::{LonghandId, OwnedPropertyDeclarationId, PropertyDeclaration};
use style::values::computed::ToComputedValue;
use style::values::specified::Opacity;

#[no_mangle]
pub unsafe extern "C" fn Rust_CheckTransitionEndpoint(
    endpoint: *const KeyframeEndpoint,
    expected: f32,
    keyframe_index: usize,
) {
    assert!(!endpoint.is_null());
    let endpoint = &*endpoint;
    assert_eq!(
        endpoint.property(),
        &OwnedPropertyDeclarationId::Longhand(LonghandId::Opacity)
    );
    assert_eq!(endpoint.context().keyframe_index(), keyframe_index);
    assert_eq!(endpoint.context().declarations().len(), 1);
    assert_eq!(endpoint.declaration_index(), 0);
    assert!(std::ptr::eq(
        endpoint.declaration(),
        &endpoint.context().declarations()[0]
    ));
    let PropertyDeclaration::Opacity(value) = endpoint.declaration() else {
        crate::host_failure("transition endpoint is not an opacity declaration".into());
        return;
    };
    assert_eq!(value, &Opacity::from_computed_value(&expected));
}
