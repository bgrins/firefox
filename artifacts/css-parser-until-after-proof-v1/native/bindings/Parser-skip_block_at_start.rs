    pub(crate) fn skip_block_at_start(&mut self) {
        if let Some(block_type) = self.state.take_at_start_of() {
            self.consume_until_end_of_block(block_type);
        }
    }
