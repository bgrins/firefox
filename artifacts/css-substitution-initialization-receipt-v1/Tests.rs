const FLAGS: RuleCascadeFlags = RuleCascadeFlags(0);
fn reg() -> PropertyDescriptors { PropertyDescriptors { inherits: true } }
fn value(binding: CustomBinding) -> Option<ComputedRegisteredValue> {
    match binding { CustomBinding::Settled(v) => v, CustomBinding::Pending => panic!("Pending") }
}
fn fixture() -> (Cascade, computed::Context) {
    let mut initial = ComputedCustomProperties::default();
    initial.inherited.insert("initial".into(), ComputedRegisteredValue("2px"));
    initial.non_inherited.insert("reset".into(), ComputedRegisteredValue("3px"));
    let mut context = computed::Context::default();
    context.inherited.inherited.insert("parent".into(), ComputedRegisteredValue("20px"));
    (Cascade { stylist: Stylist { initial } }, context)
}
#[test]
fn actual_initialization_selects_parent_and_registered_initial_maps() {
    let (mut cascade, mut context) = fixture();
    cascade.init_custom_properties(&mut context);
    let mut receipt = CustomInitializationReceipt::after_selection(&SeenSubstitutionFunctions::default(), &context.builder.substitution_functions, FLAGS);
    let root = receipt.root.clone();
    assert_eq!(value(receipt.lookup_no_node(&root, FLAGS, &"parent".into(), &reg()).unwrap()), Some(ComputedRegisteredValue("20px")));
    assert_eq!(value(receipt.lookup_no_node(&root, FLAGS, &"reset".into(), &PropertyDescriptors { inherits: false }).unwrap()), Some(ComputedRegisteredValue("3px")));
    assert_eq!(value(receipt.lookup_no_node(&root, FLAGS, &"missing".into(), &reg()).unwrap()), None);
    context.root = true; context.inherited = ComputedCustomProperties::default();
    cascade.init_custom_properties(&mut context);
    assert_eq!(context.builder.substitution_functions.get_var(&reg(), &"initial".into()), Some(&ComputedRegisteredValue("2px")));
}
#[test]
fn unresolved_name_remains_pending_even_when_map_absent_or_typed() {
    let name = "late".to_string();
    let mut seen = SeenSubstitutionFunctions::default(); seen.var.insert(&name, true);
    for present in [false, true] {
        let mut map = ComputedSubstitutionFunctions::default();
        if present { map.custom_properties.inherited.insert(name.clone(), ComputedRegisteredValue("typed-but-unfinished")); }
        let mut receipt = CustomInitializationReceipt::after_selection(&seen, &map, FLAGS); let root = receipt.root.clone();
        assert!(matches!(receipt.lookup_no_node(&root, FLAGS, &name, &reg()), Ok(CustomBinding::Pending)));
    }
}
fn pending_context(name: &Name) -> Context {
    let mut c = Context::empty(); let mut seen = SeenSubstitutionFunctions::default(); seen.var.insert(name, true);
    c.receipt = CustomInitializationReceipt::after_selection(&seen, &c.computed_context.builder.substitution_functions, FLAGS);
    c.var_info.push(VarInfo { var: Some(VarType::Custom(name.clone())), publication: NodePublication::SemanticOpen });
    c.receipt_bind_node(0).unwrap(); c
}
#[test]
fn publication_and_cycle_completion_snapshot_only_the_bound_name() {
    for cycle in [false, true] {
        let name = "late".to_string(); let mut c = pending_context(&name); let root = c.receipt.root.clone();
        if cycle { c.var_info[0].publication.begin_cycle(); } else { c.var_info[0].publication.close(()); c.var_info[0].publication.take_ready(true); }
        assert_eq!(c.receipt_publish(&root, 0), Err(ReceiptError::NotTerminal));
        c.computed_context.builder.substitution_functions.custom_properties.inherited.insert(name.clone(), ComputedRegisteredValue("computed-or-default"));
        c.var_info[0].var.take();
        if cycle { c.var_info[0].publication.settle_cycle(); } else { c.var_info[0].publication.finish(); }
        c.receipt_publish(&root, 0).unwrap();
        c.computed_context.builder.substitution_functions.custom_properties.inherited.remove(&name);
        assert_eq!(value(c.receipt_lookup(&root, &name).unwrap()), Some(ComputedRegisteredValue("computed-or-default")));
        assert_eq!(c.receipt_publish(&root, 0), Err(ReceiptError::AlreadySettled));
    }
}
#[test]
fn foreign_terminal_cannot_settle_pending_name() {
    let name="pending".to_string(); let mut c=pending_context(&name);let root=c.receipt.root.clone();
    c.var_info.push(VarInfo{var:Some(VarType::Custom("other".into())),publication:NodePublication::Complete});
    assert_eq!(c.receipt_publish(&root,1),Err(ReceiptError::WrongNode));
    c.var_info[0].var=Some(VarType::Custom("other".into()));c.var_info[0].publication=NodePublication::Complete;
    assert_eq!(c.receipt_publish(&root,0),Err(ReceiptError::WrongNode));
    assert!(matches!(c.receipt_lookup(&root,&name),Ok(CustomBinding::Pending)));
}
#[test]
fn actual_reset_rejects_pending_and_keeps_settlement_with_fresh_request_identity() {
    let name="later-root".to_string();let mut c=pending_context(&name);let old=c.receipt.root.clone();
    assert!(std::panic::catch_unwind(std::panic::AssertUnwindSafe(||c.receipt_reset(&old))).is_err());
    assert!(Arc::ptr_eq(&old,&c.receipt.root));
    c.var_info[0].publication.close(());c.var_info[0].publication.take_ready(true);c.var_info[0].publication.finish();
    c.receipt_publish(&old,0).unwrap();c.receipt_reset(&old).unwrap();
    assert!(matches!(c.receipt_lookup(&old,&name),Err(ReceiptError::WrongRoot)));
    let new=c.receipt.root.clone();assert_eq!(value(c.receipt_lookup(&new,&name).unwrap()),None);
}
#[test]
fn flags_change_is_not_provider_invalid_and_cannot_be_reversed() {
    let mut c=Context::empty();let root=c.receipt.root.clone();let name="gated".to_string();
    c.computed_context.included_cascade_flags=RuleCascadeFlags(1);
    assert!(matches!(c.receipt_lookup(&root,&name),Err(ReceiptError::Invalidated)));
    c.computed_context.included_cascade_flags=FLAGS;
    assert!(matches!(c.receipt_lookup(&root,&name),Err(ReceiptError::Invalidated)));
    let mut other=Context::empty();assert!(matches!(other.receipt_lookup(&root,&name),Err(ReceiptError::WrongRoot)));
}
#[test]
fn initial_snapshot_is_owned_and_false_seen_is_storage_settled() {
    let name="selected".to_string();let mut seen=SeenSubstitutionFunctions::default();seen.var.insert(&name,false);
    let mut c=Context::empty();c.computed_context.builder.substitution_functions.custom_properties.inherited.insert(name.clone(),ComputedRegisteredValue("20px"));
    c.receipt=CustomInitializationReceipt::after_selection(&seen,&c.computed_context.builder.substitution_functions,FLAGS);
    let root=c.receipt.root.clone();c.computed_context.builder.substitution_functions.custom_properties.inherited.insert(name.clone(),ComputedRegisteredValue("30px"));
    assert_eq!(value(c.receipt_lookup(&root,&name).unwrap()),Some(ComputedRegisteredValue("20px")));
}

#[test]
fn no_node_completion_requires_explicit_post_compute_notification() {
    let name="shortcut".to_string();let mut seen=SeenSubstitutionFunctions::default();seen.var.insert(&name,true);
    let mut c=Context::empty();c.receipt=CustomInitializationReceipt::after_selection(&seen,&c.computed_context.builder.substitution_functions,FLAGS);
    let root=c.receipt.root.clone();
    c.computed_context.builder.substitution_functions.custom_properties.inherited.insert(name.clone(),ComputedRegisteredValue("finished-shortcut"));
    assert!(matches!(c.receipt_lookup(&root,&name),Ok(CustomBinding::Pending)));
    c.receipt_dependency_free_applied(&root,&name).unwrap();
    assert_eq!(value(c.receipt_lookup(&root,&name).unwrap()),Some(ComputedRegisteredValue("finished-shortcut")));
    assert_eq!(c.receipt_dependency_free_applied(&root,&name),Err(ReceiptError::AlreadySettled));
}
