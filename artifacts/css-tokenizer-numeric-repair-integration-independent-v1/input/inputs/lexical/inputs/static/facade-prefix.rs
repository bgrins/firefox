#![allow(dead_code)]
macro_rules! match_byte { ($value:expr, $($arms:tt)*) => { match $value { $($arms)* } }; }
#[derive(Debug)]
enum Token<'a> {
    Number { value: f32, int_value: Option<i32>, has_sign: bool },
    Percentage { unit_value: f32, int_value: Option<i32>, has_sign: bool },
    Dimension { value: f32, int_value: Option<i32>, has_sign: bool, unit: &'a str },
}
use Token::*;
struct Parser<'a> { input: &'a str, position: usize }
impl<'a> Parser<'a> {
    fn is_eof(&self) -> bool { self.position >= self.input.len() }
    fn has_at_least(&self, n: usize) -> bool { self.position + n < self.input.len() }
    fn next_byte_unchecked(&self) -> u8 { self.byte_at(0) }
    fn byte_at(&self, n: usize) -> u8 { self.input.as_bytes()[self.position + n] }
    fn advance(&mut self, n: usize) { self.position += n; }
    fn has_newline_at(&self, n: usize) -> bool {
        self.position + n < self.input.len() && matches!(self.byte_at(n), b'\n' | b'\r' | b'\x0c')
    }
}
fn consume_name<'a>(p: &mut Parser<'a>) -> &'a str {
    let start = p.position;
    while !p.is_eof() && (p.next_byte_unchecked().is_ascii_alphanumeric() || p.next_byte_unchecked() == b'-' || p.next_byte_unchecked() == b'_') { p.advance(1); }
    assert!(p.is_eof() || p.next_byte_unchecked().is_ascii_whitespace() || p.next_byte_unchecked() == b';');
    &p.input[start..p.position]
}
