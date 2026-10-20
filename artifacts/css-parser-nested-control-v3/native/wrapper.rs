#[allow(missing_docs)]
impl Parser<'_> {
    pub fn nested_snapshot(&self) -> String {
        format!("{}|{}|{}|{}", self.history_state(), self.stop_before.bits, self.current_block_depth, self.nested_block_limit)
    }
    pub fn nested_limit(&mut self, limit: u8) { self.nested_block_limit = limit; }
    pub fn nested_depth(&mut self, depth: u8) { self.current_block_depth = depth; }
    pub fn nested_probe(&mut self, count: usize, accept: bool) -> bool {
        let result: Result<(), ParseError<()>> = self.parse_nested_block(|p| {
            for _ in 0..count { p.next()?; }
            if accept { Ok(()) } else { Err(ParseError::custom(())) }
        });
        result.is_ok()
    }
    pub fn until_probe(&mut self, count: usize, stop: bool) -> bool {
        let result: Result<(), ParseError<()>> = parse_until_before(self, Delimiter::Semicolon,
            if stop { ParseUntilErrorBehavior::Stop } else { ParseUntilErrorBehavior::Consume },
            |p| { for _ in 0..count { p.next()?; } Err(ParseError::custom(())) });
        result.is_ok()
    }
    pub fn link_empty_projection(&mut self) -> bool {
        if self.try_parse(|p| p.expect_ident_matching("none")).is_ok() { return true; }
        let result: Result<Vec<()>, ParseError<()>> = self.parse_comma_separated(|p| {
            p.expect_function_matching("param")?;
            p.parse_nested_block(|p| {
                if !p.expect_ident()?.starts_with("--") { return Err(ParseError::custom(())); }
                p.expect_comma()?;
                let state = p.state();
                if !matches!(p.next_including_whitespace_and_comments(), Ok(Token::WhiteSpace(_))) { p.reset(&state); }
                p.parse_until_before(Delimiter::Bang | Delimiter::Semicolon, |p| {
                    match p.next_including_whitespace_and_comments() {
                        Err(_) => Ok(()),
                        Ok(_) => Err(ParseError::custom(())),
                    }
                })
            })
        });
        result.is_ok()
    }
}
