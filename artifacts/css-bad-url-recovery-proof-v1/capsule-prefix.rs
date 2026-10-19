#![allow(dead_code)]
include!("fallback-macro.rs");
#[cfg(feature = "fast_match_byte")]
pub use cssparser_macros::match_byte;
#[macro_use]
mod macros;
pub use macros::_cssparser_internal_to_lowercase;
mod cow_rc_str;
mod parser;
mod tokenizer;
use std::io::{self, BufRead};

fn hex(text: &str) -> String {
    text.as_bytes().iter().map(|byte| format!("{byte:02x}")).collect()
}

fn main() {
    for line in io::stdin().lock().lines() {
        let line = line.unwrap();
        let bytes: Vec<u8> = (0..line.len()).step_by(2)
            .map(|index| u8::from_str_radix(&line[index..index + 2], 16).unwrap()).collect();
        let text = String::from_utf8(bytes).unwrap();
        let mut parser = parser::Parser::new(&text);
        let token = parser.next_including_whitespace_and_comments().unwrap().clone();
        let (kind, payload) = match token {
            tokenizer::Token::UnquotedUrl(value) => ("url", value.to_string()),
            tokenizer::Token::BadUrl(value) => ("bad-url", value.to_string()),
            _ => panic!("unexpected token: {token:?}"),
        };
        let position = parser.position().byte_index();
        let location = parser.current_source_location();
        println!("{} {} {} {} {} {}", kind, hex(&payload), hex(&text[position..]), position, location.line, location.column);
    }
}
