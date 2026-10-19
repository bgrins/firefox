    fn iter(&self) -> Iter<'_> {
        Iter {
            current: self,
            current_iter: self.own_properties.iter(),
            descendants: Default::default(),
        }
    }
