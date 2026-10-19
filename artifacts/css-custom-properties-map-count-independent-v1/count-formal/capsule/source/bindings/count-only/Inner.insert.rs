    fn insert(&mut self, name: &Name, value: Option<ComputedRegisteredValue>) {
        match (self.get(name).is_some(), value.is_some()) {
            (false, true) => self.len += 1,
            (true, false) => self.len -= 1,
            _ => {},
        }
        self.own_properties.insert(name.clone(), value);
    }
