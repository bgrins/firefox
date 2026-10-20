    pub fn parse_entirely<F, T, E>(&mut self, parse: F) -> Result<T, ParseError<E>>
    where
        F: FnOnce(&mut Parser<'i>) -> Result<T, ParseError<E>>,
    {
        let result = parse(self)?;
        self.expect_exhausted()?;
        Ok(result)
    }
