
fn history_hex(value: &str) -> String {
    value.as_bytes().iter().map(|b| format!("{b:02x}")).collect()
}
fn history_option(value: Option<&str>) -> String {
    match value { None => "none".into(), Some(v) => format!("some:{}", history_hex(v)) }
}
pub fn history_token(token: &Token<'_>) -> String {
    match token {
        Token::Function(v) => format!("f:{}", history_hex(v)),
        Token::Comment(v) => format!("c:{}", history_hex(v)),
        Token::ParenthesisBlock => "o:1".into(),
        Token::SquareBracketBlock => "o:2".into(),
        Token::CurlyBracketBlock => "o:3".into(),
        Token::CloseParenthesis => "x:1".into(),
        Token::CloseSquareBracket => "x:2".into(),
        Token::CloseCurlyBracket => "x:3".into(),
        Token::Colon => "colon".into(),
        _ => "other".into(),
    }
}
#[allow(missing_docs)]
impl Parser<'_> {
    pub fn history_state(&self) -> String {
        let mode = match self.arbitrary_substitution_functions {
            SeenStatus::DontCare => "off".into(),
            SeenStatus::SeenAtLeastOne => "seen".into(),
            SeenStatus::LookingForThem(names) => format!("looking:{}", names.iter().map(|n| history_hex(n)).collect::<Vec<_>>().join(",")),
        };
        let pending = |s: &ParserState| s.at_start_of().map_or(0, |b| b as u8);
        let cache = if self.cached_token.start_position.0 == usize::MAX { "none".into() }
          else { format!("{}:{}:{}:{}",self.cached_token.start_position.0,history_token(&self.cached_token.token),self.cached_token.end_state.position,pending(&self.cached_token.end_state)) };
        format!("{}|{}|{}|{}|{}|{}",self.state.position,pending(&self.state),cache,mode,history_option(self.source_url),history_option(self.source_map_url))
    }
    pub fn history_fetch(&mut self, stop: bool) -> String {
        let prior = self.stop_before;
        self.stop_before = if stop { Delimiter::Semicolon } else { Delimiter::None };
        let token = match self.next_including_whitespace_and_comments() { Ok(t) => history_token(t), Err(_) => "eof".into() };
        self.stop_before = prior;
        token
    }
}

#[allow(missing_docs)]
impl ParserState {
    pub fn history_cursor(&self) -> String {
        format!("{}:{}",self.position,self.at_start_of().map_or(0,|b|b as u8))
    }
}

#[allow(missing_docs)]
impl Parser<'_> {
    pub fn wrapper_next(&mut self, stop: bool) -> String {
        let prior = self.stop_before;
        self.stop_before = if stop { Delimiter::Semicolon } else { Delimiter::None };
        let token = match self.next() { Ok(t) => history_token(t), Err(_) => "eof".into() };
        self.stop_before = prior;
        token
    }
}
