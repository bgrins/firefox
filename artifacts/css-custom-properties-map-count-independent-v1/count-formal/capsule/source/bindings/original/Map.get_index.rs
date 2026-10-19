    pub fn get_index(&self, index: usize) -> Option<(&Name, &Option<ComputedRegisteredValue>)> {
        if index >= self.len() {
            return None;
        }
        // FIXME: This is O(n) which is a bit unfortunate.
        self.0.iter().nth(index)
    }
