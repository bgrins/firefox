std::thread_local! {
    static CODEX_ACTIVE: std::cell::Cell<bool> = const { std::cell::Cell::new(false) };
    static CODEX_ROW: std::cell::Cell<usize> = const { std::cell::Cell::new(0) };
}
fn codex_hex(bytes: &[u8]) -> String {
    bytes.iter().map(|b| format!("{b:02x}")).collect()
}
fn codex_state(s: &crate::parser::ParserState) -> String {
    format!("{}|{}|{}", s.position, s.current_line_start_position, s.codex_packed())
}
fn codex_url_call<'a>(parser: &mut Parser<'a>) -> Result<Token<'a>, ()> {
    CODEX_ACTIVE.set(true);
    println!("{}|enter|{}", CODEX_ROW.get(), codex_state(&parser.state));
    let result = consume_unquoted_url(parser);
    let (kind, value) = match &result {
        Err(()) => ("function", String::new()),
        Ok(Token::UnquotedUrl(s)) => ("url", codex_hex(s.as_bytes())),
        Ok(Token::BadUrl(s)) => ("bad-url", codex_hex(s.as_bytes())),
        other => panic!("unexpected URL provider result: {other:?}"),
    };
    println!("{}|exit|{}|{}|{}", CODEX_ROW.get(), codex_state(&parser.state), kind, value);
    CODEX_ACTIVE.set(false);
    result
}
#[allow(missing_docs)]
impl<'a> Parser<'a> {
    pub fn codex_raw_token(&mut self, row: usize) -> Option<Token<'a>> {
        CODEX_ROW.set(row);
        self.state.take_at_start_of();
        if self.is_eof() { None } else { Some(self.next_unchecked()) }
    }
    pub fn codex_fields(&self) -> String { codex_state(&self.state) }
    fn codex_step(&self, kind: &str, before: &str, argument: usize) {
        if CODEX_ACTIVE.get() {
            println!("{}|step|{}|{}|{}|{}", CODEX_ROW.get(), kind, argument, before, codex_state(&self.state));
        }
    }
    fn codex_advance(&mut self, n: usize) {
        let before = codex_state(&self.state);
        self.advance(n);
        self.codex_step("advance", &before, n);
    }
    fn codex_consume_known_byte(&mut self, b: u8) {
        let before = codex_state(&self.state);
        self.consume_known_byte(b);
        self.codex_step("known", &before, b as usize);
    }
    fn codex_consume_4byte_intro(&mut self) {
        let before = codex_state(&self.state);
        self.consume_4byte_intro();
        self.codex_step("intro", &before, 0);
    }
    fn codex_consume_continuation_byte(&mut self) {
        let before = codex_state(&self.state);
        self.consume_continuation_byte();
        self.codex_step("continuation", &before, 0);
    }
    fn codex_consume_newline(&mut self) {
        let before = codex_state(&self.state);
        self.consume_newline();
        self.codex_step("newline", &before, 0);
    }
    fn codex_consume_char(&mut self) -> char {
        let before = codex_state(&self.state);
        let c = self.consume_char();
        self.codex_step("character", &before, c as usize);
        c
    }
    fn codex_slice_from(&self, start: SourcePosition) -> &'a str {
        let result = self.slice_from(start);
        if CODEX_ACTIVE.get() {
            println!("{}|slice|{}|{}|{}", CODEX_ROW.get(), start.byte_index(), codex_state(&self.state), codex_hex(result.as_bytes()));
        }
        result
    }
    fn codex_bulk(&self, start: usize, count: u32, last: usize) {
        if CODEX_ACTIVE.get() {
            println!("{}|bulk|{}|{}|{}|{}", CODEX_ROW.get(), start, count, last, codex_state(&self.state));
        }
    }
}
