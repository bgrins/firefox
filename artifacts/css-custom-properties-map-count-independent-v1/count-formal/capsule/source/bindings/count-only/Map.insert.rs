    pub fn insert(&mut self, name: &Name, value: ComputedRegisteredValue) {
        self.do_insert(name, Some(value))
    }
