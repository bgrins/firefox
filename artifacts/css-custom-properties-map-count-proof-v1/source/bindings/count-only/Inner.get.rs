    fn get(&self, name: &Name) -> Option<&ComputedRegisteredValue> {
        if let Some(p) = self.own_properties.get(name) {
            return p.as_ref();
        }
        self.parent.as_ref()?.get(name)
    }
