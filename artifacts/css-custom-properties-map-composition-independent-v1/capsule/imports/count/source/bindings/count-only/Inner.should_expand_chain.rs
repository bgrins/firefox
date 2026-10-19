    fn should_expand_chain(&self) -> bool {
        const SMALL_THRESHOLD: usize = 8;
        if self.own_properties.len() <= SMALL_THRESHOLD {
            return false; // Just copy, to avoid very long chains.
        }
        self.ancestor_count < ANCESTOR_COUNT_LIMIT as u8
    }
