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
fn byte_to_decimal_digit(b: u8) -> Option<u32> {
    if b.is_ascii_digit() {
        Some((b - b'0') as u32)
    } else {
        None
    }
}

fn consume_numeric<'a>(parser: &mut Parser<'a>) -> Token<'a> {
    // Parse [+-]?\d*(\.\d+)?([eE][+-]?\d+)?
    // But this is always called so that there is at least one digit in \d*(\.\d+)?

    // Do all the math in f64 so that large numbers overflow to +/-inf
    // and i32::{MIN, MAX} are within range.

    let (has_sign, sign) = match parser.next_byte_unchecked() {
        b'-' => (true, -1.),
        b'+' => (true, 1.),
        _ => (false, 1.),
    };
    if has_sign {
        parser.advance(1);
    }

    let mut integral_part: f64 = 0.;
    while let Some(digit) = byte_to_decimal_digit(parser.next_byte_unchecked()) {
        integral_part = integral_part * 10. + digit as f64;
        parser.advance(1);
        if parser.is_eof() {
            break;
        }
    }

    let mut is_integer = true;

    let mut fractional_part: f64 = 0.;
    if parser.has_at_least(1)
        && parser.next_byte_unchecked() == b'.'
        && parser.byte_at(1).is_ascii_digit()
    {
        is_integer = false;
        parser.advance(1); // Consume '.'
        let mut factor = 0.1;
        while let Some(digit) = byte_to_decimal_digit(parser.next_byte_unchecked()) {
            fractional_part += digit as f64 * factor;
            factor *= 0.1;
            parser.advance(1);
            if parser.is_eof() {
                break;
            }
        }
    }

    let mut value = sign * (integral_part + fractional_part);

    if parser.has_at_least(1)
        && matches!(parser.next_byte_unchecked(), b'e' | b'E')
        && (parser.byte_at(1).is_ascii_digit()
            || (parser.has_at_least(2)
                && matches!(parser.byte_at(1), b'+' | b'-')
                && parser.byte_at(2).is_ascii_digit()))
    {
        is_integer = false;
        parser.advance(1);
        let (has_sign, sign) = match parser.next_byte_unchecked() {
            b'-' => (true, -1.),
            b'+' => (true, 1.),
            _ => (false, 1.),
        };
        if has_sign {
            parser.advance(1);
        }
        let mut exponent: f64 = 0.;
        while let Some(digit) = byte_to_decimal_digit(parser.next_byte_unchecked()) {
            exponent = exponent * 10. + digit as f64;
            parser.advance(1);
            if parser.is_eof() {
                break;
            }
        }
        value *= f64::powf(10., sign * exponent);
    }

    let int_value = if is_integer {
        Some(if value >= i32::MAX as f64 {
            i32::MAX
        } else if value <= i32::MIN as f64 {
            i32::MIN
        } else {
            value as i32
        })
    } else {
        None
    };

    if !parser.is_eof() && parser.next_byte_unchecked() == b'%' {
        parser.advance(1);
        return Percentage {
            unit_value: (value / 100.) as f32,
            int_value,
            has_sign,
        };
    }
    let value = value as f32;
    if is_ident_start(parser) {
        let unit = consume_name(parser);
        Dimension {
            value,
            int_value,
            has_sign,
            unit,
        }
    } else {
        Number {
            value,
            int_value,
            has_sign,
        }
    }
}

fn is_ident_start(parser: &Parser) -> bool {
    !parser.is_eof()
        && match_byte! { parser.next_byte_unchecked(),
            b'a'..=b'z' | b'A'..=b'Z' | b'_' | b'\0' => true,
            b'-' => {
                parser.has_at_least(1) && match_byte! { parser.byte_at(1),
                    b'a'..=b'z' | b'A'..=b'Z' | b'-' | b'_' | b'\0' => {
                        true
                    }
                    b'\\' => !parser.has_newline_at(2),
                    b => !b.is_ascii(),
                }
            },
            b'\\' => !parser.has_newline_at(1),
            b => !b.is_ascii(),
        }
}

fn main() {
    let inputs = ["0.5".to_owned(), "5e-1".to_owned(), format!("5{}e-309", "0".repeat(308)), format!("5{}e-400", "0".repeat(399)), format!("0.{}5e399", "0".repeat(399)), "0e999".to_owned(), "1e999".to_owned(), format!("17{}e-308px", "0".repeat(308)), "17px".to_owned()];
    for (i,input) in inputs.iter().enumerate() {
        let mut p = Parser { input, position: 0 };
        let token = consume_numeric(&mut p);
        assert_eq!(p.position, input.len());
        println!("case={i}\tconsumed={}\ttoken={token:?}", p.position);
    }
}
