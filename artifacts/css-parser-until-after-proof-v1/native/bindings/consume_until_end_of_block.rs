    pub(crate) fn consume_until_end_of_block(&mut self, block_type: BlockType) {
        let mut stack = SmallVec::<[BlockType; 16]>::new();
        stack.push(block_type);

        // FIXME: have a special-purpose tokenizer method for this that does less work.
        while !self.is_eof() {
            let token = self.next_unchecked();
            if let Some(nested_block_type) = self.state.take_at_start_of() {
                stack.push(nested_block_type);
                continue;
            }
            if let Some(b) = BlockType::closing(&token) {
                if *stack.last().unwrap() == b {
                    stack.pop();
                    if stack.is_empty() {
                        return;
                    }
                }
            }
        }
    }
