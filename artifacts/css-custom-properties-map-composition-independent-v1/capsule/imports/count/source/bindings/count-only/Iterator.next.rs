    fn next(&mut self) -> Option<Self::Item> {
        loop {
            let (name, value) = match self.current_iter.next() {
                Some(v) => v,
                None => {
                    let parent = self.current.parent.as_deref()?;
                    self.descendants.push(self.current);
                    self.current = parent;
                    self.current_iter = parent.own_properties.iter();
                    continue;
                },
            };
            // If the property is overridden by a descendant we've already visited it.
            for descendant in &self.descendants {
                if descendant.own_properties.contains_key(name) {
                    continue;
                }
            }
            return Some((name, value));
        }
    }
