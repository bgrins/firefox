#[unsafe(no_mangle)]
pub extern "C" fn Servo_AnimationValueMap_FromComputedStyleForTesting(
    style: &ComputedValues,
    property: &structs::CSSPropertyId,
) -> *mut AnimationValueMap {
    let Some(property) = OwnedPropertyDeclarationId::from_gecko_css_property_id(property) else {
        return ptr::null_mut();
    };
    let Some(value) = AnimationValue::from_computed_values(property.as_borrowed(), style) else {
        return ptr::null_mut();
    };
    let mut values = Box::new(AnimationValueMap::default());
    values.insert(property, value);
    Box::into_raw(values)
}
