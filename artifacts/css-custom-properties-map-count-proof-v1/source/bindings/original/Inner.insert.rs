    fn insert(&mut self, name: &Name, value: Option<ComputedRegisteredValue>) {
        let new = self.own_properties.insert(name.clone(), value).is_none();
        if new && self.parent.as_ref().is_none_or(|p| p.get(name).is_none()) {
            self.len += 1;
        }
    }
