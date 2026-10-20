    pub(crate) fn next_unchecked(&mut self) -> Token<'a> {
        debug_assert!(self.state.at_start_of().is_none());
        next_token_unchecked(self)
    }
