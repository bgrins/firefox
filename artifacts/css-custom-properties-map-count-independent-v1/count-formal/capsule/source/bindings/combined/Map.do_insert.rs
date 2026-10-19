    fn do_insert(&mut self, name: &Name, value: Option<ComputedRegisteredValue>) {
        if let Some(inner) = Arc::get_mut(&mut self.0) {
            return inner.insert(name, value);
        }
        if self.get(name) == value.as_ref() {
            return;
        }
        if !self.0.should_expand_chain() {
            return Arc::make_mut(&mut self.0).insert(name, value);
        }
        let len = self.0.len;
        let ancestor_count = self.0.ancestor_count + 1;
        let mut new_inner = Inner {
            own_properties: Default::default(),
            // FIXME: Would be nice to avoid this clone.
            parent: Some(self.0.clone()),
            len,
            ancestor_count,
        };
        new_inner.insert(name, value);
        self.0 = Arc::new(new_inner);
    }
