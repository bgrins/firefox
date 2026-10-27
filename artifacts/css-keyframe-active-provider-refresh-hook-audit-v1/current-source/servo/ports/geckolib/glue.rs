pub extern "C" fn Servo_GetComputedKeyframeValues(
    keyframes: &nsTArray<structs::Keyframe>,
    element: &RawGeckoElement,
    pseudo_type: PseudoStyleType,
    style: &ComputedValues,
    raw_data: &PerDocumentStyleData,
    computed_keyframes: &mut nsTArray<structs::ComputedKeyframeValues>,
) -> bool {
    use style::applicable_declarations::CascadePriority;
    use style::keyframe_endpoint::{KeyframeEndpoint, KeyframeEndpointContext};
    use style::properties::{
        CustomDeclarationValue, KeyframeCustomPropertiesBuilder, PropertyDeclaration,
    };
    use style::properties_and_values::value::CustomAnimatedValue;
    let data = raw_data.borrow();
    let element = GeckoElement(element);
    let pseudo = PseudoElement::from_pseudo_type(pseudo_type, None);
    let parent_element = if pseudo.is_none() {
        element.inheritance_parent()
    } else {
        Some(element)
    };
    let parent_data = parent_element.as_ref().and_then(|e| e.borrow_data());
    let parent_style = parent_data
        .as_ref()
        .map(|d| d.styles.primary())
        .map(|x| &**x);

    let container_size_query =
        ContainerSizeQuery::for_element(element, parent_style, pseudo.is_some());
    let mut conditions = Default::default();
    let mut tree_counting_caches = TreeCountingCaches::default();
    let mut context = create_context_for_animation(
        &data,
        &style,
        parent_style,
        /* for_smil_animation = */ false,
        &mut conditions,
        container_size_query,
        &element,
        &mut tree_counting_caches,
    );

    let restriction = pseudo.map_or(PropertyFlags::empty(), |p| p.property_restriction());

    let global_style_data = &*GLOBAL_STYLE_DATA;
    let guard = global_style_data.shared_lock.read();
    let default_values = data.default_computed_values();
    let mut attribute_tracker = AttributeTracker::new(&element);

    for (index, keyframe) in keyframes.iter().enumerate() {
        let ref mut animation_values = computed_keyframes[index];

        let mut seen = PropertyDeclarationIdSet::default();
        let mut iter = PrioritizedPropertyIter::new(&keyframe.mPropertyValues);

        let mut endpoint_declarations = Vec::new();
        let mut endpoint_offsets = Vec::new();
        for property in &mut iter {
            endpoint_offsets.push(endpoint_declarations.len());
            if property.mServoDeclarationBlock.mRawPtr.is_null() {
                continue;
            }
            let declarations = unsafe { &*property.mServoDeclarationBlock.mRawPtr };
            let declarations = declarations.read_with(&guard);
            endpoint_declarations.extend(declarations.normal_declaration_iter().cloned());
        }
        iter.reset();
        let endpoint_context = Arc::new(KeyframeEndpointContext::new(index, endpoint_declarations));

        // FIXME (bug 1883255): This is pretty much a hack. Instead, the AnimatedValue should be
        // better integrated in the cascade.
        {
            let mut builder = KeyframeCustomPropertiesBuilder::new(
                &data.stylist,
                &mut context,
                style.custom_properties().clone(),
            );
            let priority = CascadePriority::same_tree_author_normal_at_root_layer();
            for property in &mut iter {
                let is_custom = match PropertyId::from_gecko_css_property_id(&property.mProperty) {
                    Some(PropertyId::Custom(..)) => true,
                    _ => false,
                };
                if !is_custom {
                    break; // Custom props are guaranteed to sort earlier.
                }
                if property.mServoDeclarationBlock.mRawPtr.is_null() {
                    continue;
                }
                let declarations = unsafe { &*property.mServoDeclarationBlock.mRawPtr };
                let guard = declarations.read_with(&guard);
                for decl in guard.normal_declaration_iter() {
                    if let PropertyDeclaration::Custom(ref declaration) = *decl {
                        builder.cascade(&mut context, declaration, priority);
                    }
                }
            }
            iter.reset();
            for property in &mut iter {
                if simulate_compute_values_failure(property)
                    || property.mServoDeclarationBlock.mRawPtr.is_null()
                {
                    continue;
                }
                let declarations = unsafe { &*property.mServoDeclarationBlock.mRawPtr };
                let guard = declarations.read_with(&guard);
                for declaration in guard.normal_declaration_iter() {
                    if let PropertyDeclaration::WithVariables(declaration) = declaration {
                        builder.prepare_attributes(
                            &mut context,
                            &declaration.value,
                            &mut attribute_tracker,
                        );
                    }
                }
            }
            iter.reset();
            builder.build(&mut context, &mut attribute_tracker);
        };

        let mut property_index = 0;
        for (property_slot, property) in iter.enumerate() {
            if simulate_compute_values_failure(property) {
                continue;
            }
            let mut endpoint_declaration_index = endpoint_offsets[property_slot];

            let mut maybe_append_animation_value =
                |property: PropertyDeclarationId,
                 value: Option<AnimationValue>,
                 source_index: Option<usize>| {
                    debug_assert!(!property.is_logical());
                    debug_assert!(property.is_animatable());

                    if property == PropertyDeclarationId::Longhand(LonghandId::Display)
                        && !static_prefs::pref!("layout.css.display-animations.enabled")
                    {
                        return;
                    }

                    // Skip restricted properties
                    if !restriction.is_empty() && !property.flags().contains(restriction) {
                        return;
                    }

                    if seen.contains(property) {
                        return;
                    }
                    seen.insert(property);

                    let endpoint = source_index.filter(|_| value.is_some()).map_or(
                        structs::RefPtr::null(),
                        |source_index| {
                            structs::RefPtr::from_arc(Arc::new(KeyframeEndpoint::new(
                                endpoint_context.clone(),
                                source_index,
                                property.to_owned(),
                            )))
                        },
                    );
                    animation_values.push(structs::PropertyStyleAnimationValuePair {
                        mProperty: property.to_gecko_css_property_id(),
                        mEndpoint: endpoint,
                        mValue: structs::AnimationValue {
                            mServo: value.map_or(structs::RefPtr::null(), |v| {
                                structs::RefPtr::from_arc(Arc::new(v))
                            }),
                        },
                    });
                    property_index += 1;
                };

            if property.mServoDeclarationBlock.mRawPtr.is_null() {
                if let Some(prop) =
                    OwnedPropertyDeclarationId::from_gecko_css_property_id(&property.mProperty)
                {
                    maybe_append_animation_value(prop.as_borrowed(), None, None);
                }
                continue;
            }

            let declarations = unsafe { &*property.mServoDeclarationBlock.mRawPtr };
            let guard = declarations.read_with(&guard);
            for declaration in guard.normal_declaration_iter() {
                let source_index = endpoint_declaration_index;
                endpoint_declaration_index += 1;
                if let PropertyDeclaration::Custom(custom) = declaration
                    && matches!(custom.value, CustomDeclarationValue::Unparsed(_))
                {
                    let registration = data.stylist.get_custom_property_registration(&custom.name);
                    if !registration.is_universal() {
                        let value = context
                            .builder
                            .custom_properties()
                            .get(registration, &custom.name);
                        let value = AnimationValue::Custom(CustomAnimatedValue::from_computed(
                            &custom.name,
                            value,
                        ));
                        maybe_append_animation_value(
                            value.id(),
                            Some(value.clone()),
                            Some(source_index),
                        );
                        continue;
                    }
                }

                if let Some(value) = AnimationValue::from_declaration(
                    declaration,
                    &mut context,
                    style,
                    &default_values,
                    &mut attribute_tracker,
                ) {
                    maybe_append_animation_value(
                        value.id(),
                        Some(value.clone()),
                        Some(source_index),
                    );
                }
            }
        }
    }
    attribute_tracker.references.is_some()
}

pub extern "C" fn Servo_AnimationRuleSample_Compose(
    sample: &mut AnimationRuleSample,
    base_values: &structs::RawServoAnimationValueTable,
    css_property: &structs::CSSPropertyId,
    segment: &structs::AnimationPropertySegment,
    last_segment: &structs::AnimationPropertySegment,
    computed_timing: &structs::ComputedTiming,
    iteration_composite: IterationCompositeOperation,
) {
    use style::animation_rule_sample::{SampledEndpoint, SampledSegment};

    let property = match OwnedPropertyDeclarationId::from_gecko_css_property_id(css_property) {
        Some(property) if property.as_borrowed().is_animatable() => property,
        _ => return,
    };
    let from = unsafe { segment.mFromValue.mServo.mRawPtr.as_ref() }
        .map(|value| SampledEndpoint::Value(value.clone()));
    let to = unsafe { segment.mToValue.mServo.mRawPtr.as_ref() }
        .map(|value| SampledEndpoint::Value(value.clone()));
    let last = unsafe { last_segment.mToValue.mServo.mRawPtr.as_ref() }
        .map(|value| SampledEndpoint::Value(value.clone()));
    let inserted = sample.compose_segment(
        property,
        SampledSegment {
            from,
            to,
            from_composite: segment.mFromComposite,
            to_composite: segment.mToComposite,
            same_offset: segment.mFromKey == segment.mToKey,
            last,
            iteration_composite,
            current_iteration: computed_timing.mCurrentIterationForAccumulation,
        },
        || unsafe {
            bindings::Gecko_AnimationGetBaseStyle(base_values, css_property)
                .as_ref()
                .cloned()
        },
        || {
            let progress =
                unsafe { bindings::Gecko_GetProgressFromComputedTiming(computed_timing) };
            let position = if segment.mToKey == segment.mFromKey {
                progress
            } else {
                unsafe {
                    bindings::Gecko_GetPositionInSegment(
                        segment,
                        progress,
                        computed_timing.mBeforeFlag,
                    )
                }
            };
            (progress, position)
        },
    );
    if !inserted {
        warn!("Underlying value should be valid when we expect to use it");
    }
}

pub extern "C" fn Servo_TraverseSubtree(
    root: &RawGeckoElement,
    raw_data: &PerDocumentStyleData,
    snapshots: *const ServoElementSnapshotTable,
    raw_flags: ServoTraversalFlags,
) -> bool {
    let traversal_flags = TraversalFlags::from_bits_retain(raw_flags);
    debug_assert!(!snapshots.is_null());

    let element = GeckoElement(root);

    debug!("Servo_TraverseSubtree (flags={:?})", traversal_flags);
    debug!("{:?}", ShowSubtreeData(element.as_node()));

    if cfg!(debug_assertions) {
        if let Some(parent) = element.traversal_parent() {
            let data = parent
                .borrow_data()
                .expect("Styling element with unstyled parent");
            assert!(
                !data.styles.is_display_none(),
                "Styling element with display: none parent"
            );
        }
    }

    let needs_animation_only_restyle =
        element.has_animation_only_dirty_descendants() || element.has_animation_restyle_hints();

    let per_doc_data = raw_data.borrow();
    debug_assert!(!per_doc_data.stylist.stylesheets_have_changed());

    let global_style_data = &*GLOBAL_STYLE_DATA;
    let guard = global_style_data.shared_lock.read();

    let was_initial_style = !element.has_data();

    if needs_animation_only_restyle {
        debug!(
            "Servo_TraverseSubtree doing animation-only restyle (aodd={})",
            element.has_animation_only_dirty_descendants()
        );
        traverse_subtree(
            element,
            &global_style_data,
            &per_doc_data,
            &guard,
            traversal_flags | TraversalFlags::AnimationOnly,
            unsafe { &*snapshots },
        );
    }

    traverse_subtree(
        element,
        &global_style_data,
        &per_doc_data,
        &guard,
        traversal_flags,
        unsafe { &*snapshots },
    );

    debug!(
        "Servo_TraverseSubtree complete (dd={}, aodd={}, lfcd={}, lfc={}, data={:?})",
        element.has_dirty_descendants(),
        element.has_animation_only_dirty_descendants(),
        element.descendants_need_frames(),
        element.needs_frame(),
        element.borrow_data().unwrap()
    );

    if was_initial_style {
        debug_assert!(!element.borrow_data().unwrap().contains_restyle_data());
        false
    } else {
        let element_was_restyled = element.borrow_data().unwrap().contains_restyle_data();
        element_was_restyled
    }
}
