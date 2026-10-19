#[allow(missing_docs)]
impl<'a> Parser<'a> {
    pub fn codex_raw_token(&mut self) -> Option<Token<'a>> {
        self.state.take_at_start_of();
        if self.is_eof() { None } else { Some(self.next_unchecked()) }
    }
    pub fn codex_pending(&self) -> bool { self.state.at_start_of().is_some() }
    pub fn codex_seen(&self) -> bool {
        matches!(self.arbitrary_substitution_functions, SeenStatus::SeenAtLeastOne)
    }
}
