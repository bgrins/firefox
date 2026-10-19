fn substitute_one_reference<'a>(
    css: &'a str,
    url_data: &UrlExtraData,
    property_id: Option<PropertyIdRef>,
    substitution_functions: &'a ComputedSubstitutionFunctions,
    reference: &'a SubstitutionFunctionReference,
    stylist: &Stylist,
    computed_context: &computed::Context,
    attribute_tracker: &mut AttributeTracker,
    seen: &mut SmallVec<[&'a Name; 8]>,
) -> Result<Substitution<'a>, ()> {
    let simple_attr_subst = |s: &str| {
        Some(Substitution::new(
            Cow::Owned(quoted_css_string(s)),
            TokenSerializationType::Nothing,
            TokenSerializationType::Nothing,
            /* attr_tainted */ true,
        ))
    };
    let substitution: Option<_> = match reference.substitution_kind {
        SubstitutionFunctionKind::Var => {
            let registration = stylist.get_custom_property_registration(&reference.name);
            match substitution_functions.get_var(registration, &reference.name) {
                None => None,
                // If the referenced value is itself still unresolved (i.e. it has references), we
                // are substituting against a partially-resolved map -- this happens while applying
                // a prioritary property in the middle of custom-property resolution. Resolve it
                // recursively, guarding against cycles (which the resolver will also remove, but it
                // may not have gotten to this variable yet).
                Some(v) => match v.as_universal() {
                    Some(u) if u.has_references() => {
                        if seen.contains(&&reference.name) {
                            // Cycle: the primary is guaranteed-invalid, so fall through to the
                            // fallback (if any), like any other invalid primary.
                            None
                        } else {
                            seen.push(&reference.name);
                            let result = substitute_internal(
                                u,
                                property_id,
                                substitution_functions,
                                stylist,
                                computed_context,
                                attribute_tracker,
                                seen,
                                /* attr_taint */ None,
                            );
                            seen.pop();
                            match result {
                                Ok(mut substitution) => {
                                    substitution.attr_tainted |= v.attr_tainted;
                                    Some(substitution)
                                },
                                // The primary couldn't be resolved (invalid); use the fallback.
                                Err(()) => None,
                            }
                        }
                    },
                    _ => Some(Substitution::from_value(
                        v.to_variable_value(),
                        v.attr_tainted,
                    )),
                },
            }
        },
        SubstitutionFunctionKind::Env => {
            let device = stylist.device();
            device
                .environment()
                .get(&reference.name, device, url_data)
                .map(|v| Substitution::from_value(v, /* attr_tainted */ false))
        },
        // https://drafts.csswg.org/css-values-5/#attr-substitution
        SubstitutionFunctionKind::Attr => {
            let namespace = match reference.attribute_data.namespace {
                ParsedNamespace::Known(ref ns) => Some(ns),
                ParsedNamespace::Unknown => None,
            };
            namespace
                .and_then(|namespace| {
                    LocalName::with_name(&reference.name, |local_name| {
                        attribute_tracker.query(local_name, namespace)
                    })
                })
                .map_or_else(
                    || {
                        // Special case when fallback and <attr-type> are omitted.
                        // See FAILURE: https://drafts.csswg.org/css-values-5/#attr-substitution
                        if reference.fallback.is_none()
                            && reference.attribute_data.kind == AttributeType::None
                        {
                            simple_attr_subst("")
                        } else {
                            None
                        }
                    },
                    |attr| {
                        let attr = if let AttributeType::Type(_) = &reference.attribute_data.kind {
                            // If we're evaluating a container query, we haven't run the cascade
                            // and populated substitution_functions.attributes, so we can't do the
                            // get_attr() lookup here.
                            // TODO: This means chained attr() references will not work reliably in
                            // container style queries:
                            // https://bugzilla.mozilla.org/show_bug.cgi?id=2028861
                            if computed_context.in_container_query {
                                attr
                            } else {
                                substitution_functions
                                    .get_attr(&reference.name)
                                    .map(|v| v.to_variable_value())?
                                    .css
                            }
                        } else {
                            attr
                        };
                        let mut parser = Parser::new(&attr);
                        match &reference.attribute_data.kind {
                            AttributeType::Unit(unit) => {
                                let css = {
                                    // Verify that attribute data is a <number-token>.
                                    parser.skip_whitespace();
                                    let start = parser.position();
                                    parser.expect_number().ok()?;
                                    let mut s = String::from(parser.slice_from(start));
                                    parser.expect_exhausted().ok()?;
                                    s.push_str(unit.as_ref());
                                    s
                                };
                                let serialization = match unit {
                                    AttrUnit::Number => TokenSerializationType::Number,
                                    AttrUnit::Percentage => TokenSerializationType::Percentage,
                                    _ => TokenSerializationType::Dimension,
                                };
                                let value =
                                    ComputedValue::new(css, url_data, serialization, serialization);
                                Some(Substitution::from_value(
                                    value, /* attr_tainted */ true,
                                ))
                            },
                            AttributeType::Type(syntax) => {
                                let value = SpecifiedRegisteredValue::parse(
                                    &mut parser,
                                    syntax,
                                    url_data,
                                    None,
                                    AllowComputationallyDependent::Yes,
                                    AttrTaint::default(),
                                    property_id,
                                )
                                .ok()?;
                                let value = value.to_variable_value();
                                Some(Substitution::from_value(
                                    value, /* attr_tainted */ true,
                                ))
                            },
                            AttributeType::RawString | AttributeType::None => {
                                simple_attr_subst(&attr)
                            },
                            AttributeType::Invalid => None,
                        }
                    },
                )
        },
    };

    if let Some(s) = substitution {
        return Ok(s);
    }

    let Some(ref fallback) = reference.fallback else {
        return Err(());
    };

    do_substitute_chunk(
        css,
        fallback.start.get(),
        reference.end - 1, // Skip the closing parenthesis of the reference value.
        fallback.first_token_type,
        fallback.last_token_type,
        url_data,
        property_id,
        substitution_functions,
        stylist,
        computed_context,
        &fallback.references.refs,
        attribute_tracker,
        seen,
        /* attr_taint */ None,
    )
}
