    pub fn expect_exhausted(&mut self) -> Result<(), BasicParseError> {
        let start = self.state();
        let result = match self.next() {
            Err(BasicParseError {
                kind: BasicParseErrorKind::EndOfInput,
                ..
            }) => Ok(()),
            Err(e) => unreachable!("Unexpected error encountered: {:?}", e),
            Ok(_) => Err(BasicParseError::unexpected_token()),
        };
        self.reset(&start);
        result
    }
