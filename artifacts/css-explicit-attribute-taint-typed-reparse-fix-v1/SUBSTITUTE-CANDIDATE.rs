fn substitute_internal<'a>(
    variable_value: &'a VariableValue,
    property_id: Option<PropertyIdRef>,
    substitution_functions: &'a ComputedSubstitutionFunctions,
    stylist: &Stylist,
    computed_context: &computed::Context,
    attribute_tracker: &mut AttributeTracker,
    seen: &mut SmallVec<[&'a Name; 8]>,
    attr_taint: Option<&mut AttrTaint>,
) -> Result<Substitution<'a>, ()> {
    let mut substitution = do_substitute_chunk(
        &variable_value.css,
        /* start = */ 0,
        /* end = */ variable_value.css.len(),
        variable_value.first_token_type,
        variable_value.last_token_type,
        &variable_value.url_data,
        property_id,
        substitution_functions,
        stylist,
        computed_context,
        &variable_value.references.refs,
        attribute_tracker,
        seen,
        attr_taint,
    )?;
    substitution.attr_tainted |= variable_value.explicitly_attr_tainted;
    Ok(substitution)
}
