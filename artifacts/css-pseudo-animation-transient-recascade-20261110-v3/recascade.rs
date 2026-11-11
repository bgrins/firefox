#[unsafe(no_mangle)]
pub extern "C" fn Servo_RecascadeStyleForMissingPseudo(
    element: &RawGeckoElement,
    pseudo_type: PseudoStyleType,
    base: &ComputedValues,
    primary: &ComputedValues,
    animation_values: &AnimationValueMap,
    transition_values: &AnimationValueMap,
    snapshots: *const ServoElementSnapshotTable,
    raw_data: &PerDocumentStyleData,
) -> Strong<ComputedValues> {
    use style::rule_tree::{CascadeLevel, CascadeOrigin};
    use style::style_resolver::{
        PrimaryStyle, PseudoElementResolution, ResolvedStyle, StyleResolverForElement,
    };
    use style::stylesheets::layer_rule::LayerOrder;

    let Some(pseudo) = PseudoElement::from_pseudo_type(pseudo_type, None) else {
        return Strong::null();
    };
    if !matches!(
        pseudo,
        PseudoElement::Before | PseudoElement::After | PseudoElement::Marker
    ) || base.pseudo().as_ref() != Some(&pseudo)
        || primary.pseudo().is_some()
        || snapshots.is_null()
    {
        return Strong::null();
    }
    let element = GeckoElement(element);
    if element
        .borrow_data()
        .is_none_or(|data| !data.has_styles() || !ptr::eq(&**data.styles.primary(), primary))
    {
        return Strong::null();
    }

    let global = &*GLOBAL_STYLE_DATA;
    let guard = global.shared_lock.read();
    let data = raw_data.borrow();
    let guards = StylesheetGuards::same(&guard);
    let tree = data.stylist.rule_tree();
    let mut inputs = CascadeInputs::new_from_style(base);
    inputs.rules.get_or_insert_with(|| tree.root().clone());
    for (origin, values) in [
        (CascadeOrigin::Animations, animation_values),
        (CascadeOrigin::Transitions, transition_values),
    ] {
        let block = (!values.is_empty()).then(|| {
            Arc::new(
                global
                    .shared_lock
                    .wrap(PropertyDeclarationBlock::from_animation_value_map(values)),
            )
        });
        for path in [&mut inputs.rules, &mut inputs.visited_rules]
            .into_iter()
            .flatten()
        {
            let mut important_changed = false;
            if let Some(updated) = tree.update_rule_at_level(
                CascadeLevel::new(origin),
                LayerOrder::root(),
                block.as_ref().map(|b| b.borrow_arc()),
                path,
                &guards,
                &mut important_changed,
            ) {
                *path = updated;
            }
            debug_assert!(!important_changed);
        }
    }

    if matches!(pseudo, PseudoElement::Marker) {
        return data
            .stylist
            .compute_pseudo_element_style_with_inputs(
                inputs,
                &pseudo,
                &guards,
                Some(primary),
                Some(element),
            )
            .into();
    }

    let shared = create_shared_context(
        global,
        &guard,
        &data.stylist,
        TraversalFlags::empty(),
        unsafe { &*snapshots },
    );
    let mut local = ThreadLocalStyleContext::new();
    local.current_dom_depth = element.as_node().depth();
    let mut context = StyleContext {
        shared: &shared,
        thread_local: &mut local,
    };
    let primary = PrimaryStyle {
        style: ResolvedStyle(unsafe { ArcBorrow::from_ref(primary) }.clone_arc()),
        reused_via_rule_node: false,
    };
    StyleResolverForElement::new(
        element,
        &mut context,
        RuleInclusion::All,
        PseudoElementResolution::Force,
    )
    .cascade_style_and_visited_for_pseudo_with_default_parents(inputs, &pseudo, &primary)
    .0
    .into()
}
