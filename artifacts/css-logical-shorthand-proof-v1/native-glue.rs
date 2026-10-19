struct PrioritizedPropertyIter<'a> {
    properties: &'a [PropertyValuePair],
    sorted_property_indices: Box<[PropertyAndIndex]>,
    curr: usize,
}

impl<'a> PrioritizedPropertyIter<'a> {
    fn new(properties: &'a [PropertyValuePair]) -> Self {
        use style::values::animated::compare_property_priority;

        // If we fail to convert a NonCustomCSSPropertyId into a PropertyId we
        // shouldn't fail outright but instead by treating that property as the
        // 'all' property we make it sort last.
        let mut sorted_property_indices: Box<[PropertyAndIndex]> = properties
            .iter()
            .enumerate()
            .map(|(index, pair)| {
                let property = PropertyId::from_gecko_css_property_id(&pair.mProperty)
                    .unwrap_or(PropertyId::NonCustom(ShorthandId::All.into()));
                PropertyAndIndex { property, index }
            })
            .collect();
        sorted_property_indices.sort_by(|a, b| compare_property_priority(&a.property, &b.property));

        PrioritizedPropertyIter {
            properties,
            sorted_property_indices,
            curr: 0,
        }
    }

    fn reset(&mut self) {
        self.curr = 0;
    }
}

impl<'a> Iterator for PrioritizedPropertyIter<'a> {
    type Item = &'a PropertyValuePair;

    fn next(&mut self) -> Option<&'a PropertyValuePair> {
        if self.curr >= self.sorted_property_indices.len() {
            return None;
        }
        self.curr += 1;
        Some(&self.properties[self.sorted_property_indices[self.curr - 1].index])
    }
}

#[unsafe(no_mangle)]
pub extern "C" fn Servo_GetComputedKeyframeValues(
    keyframes: &nsTArray<structs::Keyframe>,
    element: &RawGeckoElement,
    pseudo_type: PseudoStyleType,
    style: &ComputedValues,
    raw_data: &PerDocumentStyleData,
    computed_keyframes: &mut nsTArray<structs::ComputedKeyframeValues>,
) {
    use style::applicable_declarations::CascadePriority;
    use style::properties::{KeyframeCustomPropertiesBuilder, PropertyDeclaration};
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
            builder.build(&mut context, &mut attribute_tracker);
        };

        let mut property_index = 0;
        for property in iter {
            if simulate_compute_values_failure(property) {
                continue;
            }

            let mut maybe_append_animation_value =
                |property: PropertyDeclarationId, value: Option<AnimationValue>| {
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

                    animation_values.push(structs::PropertyStyleAnimationValuePair {
                        mProperty: property.to_gecko_css_property_id(),
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
                    maybe_append_animation_value(prop.as_borrowed(), None);
                }
                continue;
            }

            let declarations = unsafe { &*property.mServoDeclarationBlock.mRawPtr };
            let guard = declarations.read_with(&guard);
            let iter = guard.to_animation_value_iter(&mut context, style, &default_values);

            for value in iter {
                maybe_append_animation_value(value.id(), Some(value.clone()));
            }
        }
    }
}
