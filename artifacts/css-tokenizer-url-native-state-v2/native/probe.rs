use cssparser::{Parser, Token};
use std::io::{self, BufRead};
fn hex(s: &str) -> String { s.as_bytes().iter().map(|b| format!("{b:02x}")).collect() }
fn option_hex(s: Option<&str>) -> String { match s { None => "none".into(), Some(v) => format!("some:{}",hex(v)) } }
fn main() {
    for (row, line) in io::stdin().lock().lines().enumerate() {
        let line = line.unwrap();
        let bytes: Vec<u8> = (0..line.len()).step_by(2).map(|i| u8::from_str_radix(&line[i..i+2],16).unwrap()).collect();
        let source = String::from_utf8(bytes).unwrap();
        let mut parser = Parser::new(&source);
        parser.look_for_arbitrary_substitution_functions(&["url"]);
        let token = parser.codex_raw_token(row).unwrap();
        let (kind, value) = match token {
            Token::Ident(s) => ("ident", s.to_string()),
            Token::Function(s) => ("function", s.to_string()),
            Token::UnquotedUrl(s) => ("url", s.to_string()),
            Token::BadUrl(s) => ("bad-url", s.to_string()),
            other => panic!("unexpected first token {other:?}"),
        };
        println!("{row}|token|{}|{kind}|{}|{}|{}", parser.codex_fields(),hex(&value),option_hex(parser.current_source_url()),option_hex(parser.current_source_map_url()));
    }
}
