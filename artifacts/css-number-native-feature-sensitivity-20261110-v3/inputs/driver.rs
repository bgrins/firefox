use cssparser::{Parser, Token};
use std::io::{self, BufRead};

fn hex(bytes: &[u8]) -> String {
    bytes.iter().map(|b| format!("{b:02x}")).collect()
}

#[derive(Debug, PartialEq)]
struct Snapshot {
    start: usize,
    end: usize,
    kind: &'static str,
    unit: String,
    has_sign: bool,
    is_integer: bool,
    bits: u32,
    remaining: String,
    debug: String,
    line: u32,
    column: u32,
}

fn observe(parser: &mut Parser<'_>, source: &str, id: &str, phase: &str) -> Snapshot {
    let start = parser.position().byte_index();
    eprintln!("CALL\t{id}\t{phase}");
    let token = parser.next_including_whitespace_and_comments().unwrap().clone();
    eprintln!("END\t{id}\t{phase}");
    let debug = format!("{token:?}");
    let (kind, unit, has_sign, is_integer, value) = match token {
        Token::Number { has_sign, int_value, value } =>
            ("number", String::new(), has_sign, int_value.is_some(), value),
        Token::Percentage { has_sign, int_value, unit_value } =>
            ("percentage", String::new(), has_sign, int_value.is_some(), unit_value),
        Token::Dimension { has_sign, int_value, value, unit } =>
            ("dimension", unit.to_string(), has_sign, int_value.is_some(), value),
        _ => ("other", String::new(), false, false, 0.0),
    };
    let end = parser.position().byte_index();
    assert!(source.is_char_boundary(start) && source.is_char_boundary(end));
    let location = parser.state().source_location();
    let result = Snapshot {
        start, end, kind, unit, has_sign, is_integer, bits: value.to_bits(),
        remaining: hex(&source.as_bytes()[end..]), debug,
        line: location.line, column: location.column,
    };
    println!("PUBLIC\t{id}\t{phase}\t{}\t{}\t{}\t{}\t{}\t{}\t{:08x}\t{}\t{}\t{}\t{}",
        result.start, result.end, result.kind, hex(result.unit.as_bytes()), result.has_sign,
        result.is_integer, result.bits, result.remaining, hex(result.debug.as_bytes()),
        result.line, result.column);
    result
}

fn main() {
    for line in io::stdin().lock().lines() {
        let line = line.unwrap();
        let fields: Vec<_> = line.split('\t').collect();
        assert_eq!(fields.len(), 5);
        let id = fields[0];
        let warmup: usize = fields[1].parse().unwrap();
        let start: usize = fields[2].parse().unwrap();
        let history = fields[3] == "history";
        assert!(history || fields[3] == "single");
        let raw = fields[4];
        assert_eq!(raw.len() % 2, 0);
        let bytes: Vec<u8> = (0..raw.len()).step_by(2)
            .map(|i| u8::from_str_radix(&raw[i..i + 2], 16).unwrap()).collect();
        let source = String::from_utf8(bytes).unwrap();
        let mut parser = Parser::new(&source);
        for _ in 0..warmup {
            parser.next_including_whitespace_and_comments().unwrap();
        }
        assert_eq!(parser.position().byte_index(), start);
        let before = parser.state();
        let first = observe(&mut parser, &source, id, "cold");
        assert_ne!(first.kind, "other");
        if !history {
            continue;
        }
        parser.reset(&before);
        let cached = observe(&mut parser, &source, id, "cached");
        assert_eq!(first, cached);
        let suffix = observe(&mut parser, &source, id, "suffix");
        assert!(suffix.end > first.end);
        parser.reset(&before);
        let reparsed = observe(&mut parser, &source, id, "reparsed");
        assert_eq!(first, reparsed);
        let suffix_again = observe(&mut parser, &source, id, "suffix-replay");
        assert_eq!(suffix, suffix_again);
    }
}
