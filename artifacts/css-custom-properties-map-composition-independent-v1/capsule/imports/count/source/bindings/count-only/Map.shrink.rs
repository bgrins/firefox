    pub fn shrink_to_fit(&mut self) {
        if let Some(inner) = Arc::get_mut(&mut self.0) {
            inner.own_properties.shrink_to_fit()
        }
    }
