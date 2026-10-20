#[allow(missing_docs)]
impl Parser<'_> {
    pub fn after_snapshot(&self) -> String {
        format!("{}|{}|{}|{}", self.history_state(), self.stop_before.bits, self.current_block_depth, self.nested_block_limit)
    }
    pub fn after_outer(&mut self, bits: u8) { assert_eq!(bits & !254, 0); self.stop_before = Delimiters { bits }; }
    pub fn after_limit(&mut self, value: u8) { self.nested_block_limit = value; }
    pub fn after_depth(&mut self, value: u8) { self.current_block_depth = value; }
    pub fn after_next(&mut self) -> String {
        match self.next() { Ok(t) => history_token(t), Err(_) => "eof".into() }
    }
    pub fn after_probe(&mut self, bits: u8, count: usize, accept: bool, stop: bool) -> bool {
        assert_eq!(bits & !30, 0);
        assert!(count <= 1);
        let result: Result<(), ParseError<()>> = parse_until_after(self, Delimiters { bits },
            if stop { ParseUntilErrorBehavior::Stop } else { ParseUntilErrorBehavior::Consume },
            |p| { for _ in 0..count { p.next()?; }
                if accept { Ok(()) } else { Err(ParseError::custom(())) } });
        result.is_ok()
    }
}
