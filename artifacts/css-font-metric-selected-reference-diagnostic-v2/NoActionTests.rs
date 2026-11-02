fn exercise(dynamic: Option<LonghandId>) {
    let mut values = vec![PropertyDeclaration::Synthesis(LonghandId::FontSize, 20)];
    if let Some(id) = dynamic {
        let mut attr = reference("data-literal", None);
        attr.substitution_kind = SubstitutionFunctionKind::Attr;
        attr.attribute_data = AttrData {
            namespace: Some("".into()), typed: true,
            valid_non_type: false, expected_consumer: Some(id),
        };
        values.push(PropertyDeclaration::WithVariables(VariableDeclaration {
            longhand: id,
            value: Arc::new(UnparsedValue {
                result: Box::new(PropertyDeclaration::Synthesis(id, 123)),
                variable_value: VariableValue {
                    css: "literal typed attr".into(),
                    references: References { refs: vec![attr], flags: ReferenceFlags::ATTR },
                    url_data: UrlExtraData,
                },
            }),
        }));
    }
    let mut decls = declarations(&values, &vec![priority(2, 2, 2, 0); values.len()]);
    decls.prioritary_positions.fill(DeclarationPosition { most_important: DeclarationIndex::MAX });
    for (index, value) in values.iter().enumerate() {
        let PropertyDeclarationId::Longhand(id) = value.id();
        decls.prioritary_positions[PrioritaryPropertyId::from_longhand(id).unwrap() as usize].most_important = index as DeclarationIndex;
        decls.longhand_declarations[index].next_index = 0;
    }
    let mut cascade = Cascade::default();
    let mut stylist = Stylist::default();
    stylist.registered.insert("len".into(), PropertyDescriptors { syntax: Some(Syntax { components: vec![] }) });
    let mut computed = computed::Context::default();
    computed.builder.substitution_functions.vars.insert("len".into(), variable("1em", vec![], ReferenceFlags::from_unit("em")));
    let mut cache = ShorthandsWithPropertyReferencesCache;
    let mut tracker = AttributeTracker::default();
    tracker.raw.insert("data-literal".into(), variable(
        if dynamic == Some(LonghandId::FontFamily) { "monospace" } else { "20px" },
        vec![], ReferenceFlags::empty(),
    ));
    let mut c = Context {
        count: 0, index_map: OrderIndexMap::default(), non_custom_index_map: Default::default(),
        var_info: vec![], stack: vec![], frames: vec![], frame_root: None, frame_reply: None,
        stylist: &stylist, computed_context: &mut computed, decls: &decls,
        font_preparation: None, completed_font_inputs: LonghandSet::default(), font_completion_flags: None,
        metric_action: None, metric_references: None, priority_completion: PriorityCompletion::default(),
        metric_drain: MetricDrain::new(&decls), cascade: &mut cascade, cache: &mut cache,
    };
    let root = VarType::Custom("len".into());
    let result = c.poll_root(root.clone(), &Default::default(), &mut tracker, &mut font_publication_demand);
    assert!(c.cascade.ensured_prioritary.contains(PrioritaryPropertyId::FontSize));
    assert!(c.cascade.publications.iter().any(|v| matches!(v, PropertyDeclaration::Synthesis(LonghandId::FontSize, 20))));
    if let Some(id) = dynamic {
        assert!(selected_declarations_have_only_attr_references(c.decls));
        assert!(matches!(result, VisitResult::ComputationPending(_)));
        assert!(!c.cascade.completed_prioritary.contains(PrioritaryPropertyId::FontSize));
        assert!(!c.cascade.completed_prioritary.contains(PrioritaryPropertyId::FontFamily));
        assert!(!c.cascade.completed_prioritary.contains(PrioritaryPropertyId::XTextScale));
        assert!(c.pending_metric_action().is_none());
        assert_eq!(c.frame_root, Some(root.clone()));
        assert!(matches!(c.frames.last().unwrap().phase, FramePhase::Publish));
        assert!(matches!(c.visited(&root), Some(VisitResult::ComputationPending(_))));
        assert!(c.map().vars["len"].as_universal().is_some());
        assert_eq!(c.computed_context.computations.get(), 0);
        let count = c.cascade.publications.len();
        let substitutions = c.cascade.substitutions.get();
        let frame_count = c.frames.len();
        let lowlinks: Vec<_> = c.var_info.iter().map(|n| n.lowlink).collect();
        let mut diagnostic = Vec::new();
        c.write_metric_diagnostic(&mut diagnostic, result, None);
        let diagnostic = String::from_utf8(diagnostic).unwrap();
        assert!(diagnostic.contains("progress=not-driven"));
        assert!(diagnostic.contains("ensured=FontSize cascade_complete=false"));
        assert!(diagnostic.contains("phase=publish"));
        assert_eq!(count, c.cascade.publications.len());
        assert_eq!(substitutions, c.cascade.substitutions.get());
        assert_eq!(frame_count, c.frames.len());
        assert_eq!(lowlinks, c.var_info.iter().map(|n| n.lowlink).collect::<Vec<_>>());
        assert!(c.pending_metric_action().is_none());
        assert_eq!(c.frame_root, Some(root.clone()));
        println!("{diagnostic}");
        let again = c.poll_root(root, &Default::default(), &mut tracker, &mut font_publication_demand);
        assert!(matches!(again, VisitResult::ComputationPending(_)));
        assert_eq!(count, c.cascade.publications.len());
        assert_eq!(substitutions, c.cascade.substitutions.get());
        println!("dynamic={id:?}: FontSize applied+ensured, not complete; custom len Publish Pending(None); no action; terminal assertion would reject");
    } else {
        assert!(matches!(result, VisitResult::Complete));
        assert!(c.cascade.completed_prioritary.contains(PrioritaryPropertyId::FontSize));
        assert!(c.map().vars["len"].as_universal().is_none());
        println!("literal control: FontSize certified, custom len completes");
    }
}

fn selected_declarations_have_only_attr_references(decls: &Declarations) -> bool {
    decls.longhand_declarations.iter().all(|entry| {
        if let PropertyDeclaration::WithVariables(value) = entry.decl {
            value.value.variable_value.references.refs.iter().all(|r| r.substitution_kind == SubstitutionFunctionKind::Attr && r.fallback.is_none())
        } else { true }
    })
}

#[test]
fn dynamic_appearance_leaves_size_pending_without_action() {
    exercise(Some(LonghandId::Appearance));
}

#[test]
fn dynamic_family_leaves_size_pending_without_action() {
    exercise(Some(LonghandId::FontFamily));
}

#[test]
fn literal_chain_certifies_size_and_completes() {
    exercise(None);
}
