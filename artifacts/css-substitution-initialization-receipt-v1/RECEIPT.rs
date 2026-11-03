struct CustomInitializationReceipt {
    node_names: PrecomputedHashMap<usize, Name>,
    initial: ComputedCustomProperties,
    unresolved: PrecomputedHashSet<Name>,
    settled: PrecomputedHashMap<Name, Option<ComputedRegisteredValue>>,
    flags: RuleCascadeFlags,
    valid: bool,
    root: Arc<()>,
}

#[derive(Debug, PartialEq)]
enum ReceiptError {
    Invalidated,
    WrongRoot,
    NotTerminal,
    AlreadySettled,
    WrongNode,
}

enum CustomBinding {
    Pending,
    Settled(Option<ComputedRegisteredValue>),
}

impl CustomInitializationReceipt {
    fn after_selection(
        seen: &SeenSubstitutionFunctions,
        map: &ComputedSubstitutionFunctions,
        flags: RuleCascadeFlags,
    ) -> Self {
        Self {
            node_names: PrecomputedHashMap::default(),
            initial: map.custom_properties.clone(),
            unresolved: seen.var.iter().filter_map(|(name, pending)| {
                pending.then(|| (*name).clone())
            }).collect(),
            settled: PrecomputedHashMap::default(),
            flags,
            valid: true,
            root: Arc::new(()),
        }
    }

    fn guard(&mut self, root: &Arc<()>, flags: RuleCascadeFlags) -> Result<(), ReceiptError> {
        self.valid &= flags == self.flags;
        if !self.valid {
            return Err(ReceiptError::Invalidated);
        }
        if !Arc::ptr_eq(root, &self.root) {
            return Err(ReceiptError::WrongRoot);
        }
        Ok(())
    }

    fn lookup_no_node(
        &mut self,
        root: &Arc<()>,
        flags: RuleCascadeFlags,
        name: &Name,
        registration: &PropertyDescriptors,
    ) -> Result<CustomBinding, ReceiptError> {
        self.guard(root, flags)?;
        if self.unresolved.contains(name) {
            return Ok(CustomBinding::Pending);
        }
        Ok(CustomBinding::Settled(match self.settled.get(name) {
            Some(value) => value.clone(),
            None => self.initial.get(registration, name).cloned(),
        }))
    }

    fn bind_custom_node(&mut self, index: usize, info: &VarInfo) -> Result<(), ReceiptError> {
        let Some(VarType::Custom(name)) = &info.var else { return Err(ReceiptError::WrongNode) };
        if !self.unresolved.contains(name) || self.node_names.contains_key(&index) {
            return Err(ReceiptError::WrongNode);
        }
        self.node_names.insert(index, name.clone());
        Ok(())
    }

    fn after_indexed_publication(
        &mut self,
        root: &Arc<()>,
        flags: RuleCascadeFlags,
        index: usize,
        nodes: &[VarInfo],
        map: &ComputedSubstitutionFunctions,
        stylist: &Stylist,
    ) -> Result<(), ReceiptError> {
        self.guard(root, flags)?;
        let name = self.node_names.get(&index).ok_or(ReceiptError::WrongNode)?;
        let info = nodes.get(index).ok_or(ReceiptError::WrongNode)?;
        if info.var.as_ref().is_some_and(|var| !matches!(var, VarType::Custom(n) if n == name)) {
            return Err(ReceiptError::WrongNode);
        }
        if !info.publication.can_retire() {
            return Err(ReceiptError::NotTerminal);
        }
        if !self.unresolved.remove(name) {
            return Err(ReceiptError::AlreadySettled);
        }
        let registration = stylist.get_custom_property_registration(name);
        self.settled.insert(name.clone(), map.get_var(registration, name).cloned());
        Ok(())
    }

    fn after_retirement(&mut self, root: &Arc<()>, flags: RuleCascadeFlags) -> Result<(), ReceiptError> {
        self.guard(root, flags)?;
        self.node_names.clear();
        self.root = Arc::new(());
        Ok(())
    }

    fn after_dependency_free_apply(
        &mut self,
        root: &Arc<()>,
        flags: RuleCascadeFlags,
        name: &Name,
        map: &ComputedSubstitutionFunctions,
        stylist: &Stylist,
    ) -> Result<(), ReceiptError> {
        self.guard(root, flags)?;
        if self.node_names.values().any(|bound| bound == name) {
            return Err(ReceiptError::WrongNode);
        }
        if !self.unresolved.remove(name) {
            return Err(ReceiptError::AlreadySettled);
        }
        self.settled.insert(name.clone(), map.get_var(stylist.get_custom_property_registration(name), name).cloned());
        Ok(())
    }
}
