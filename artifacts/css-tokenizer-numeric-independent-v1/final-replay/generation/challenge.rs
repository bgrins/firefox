#![allow(dead_code)]

#[derive(Debug, PartialEq)]
struct Observed { kind: u8, bits: u32, integer: Option<i32>, sign: bool, unit: String, consumed: usize }
mod before {
macro_rules! match_byte { ($value:expr, $($arms:tt)*) => { match $value { $($arms)* } }; }
#[derive(Debug, PartialEq)]
enum Token<'a> {
    Number { value: f32, int_value: Option<i32>, has_sign: bool },
    Percentage { unit_value: f32, int_value: Option<i32>, has_sign: bool },
    Dimension { value: f32, int_value: Option<i32>, has_sign: bool, unit: &'a str },
}
use Token::*;
struct Parser<'a> { input: &'a str, position: usize }
impl<'a> Parser<'a> {
    fn position(&self) -> usize { self.position }
    fn slice_from(&self, start: usize) -> &'a str { &self.input[start..self.position] }
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

    &p.input[start..p.position]
}
fn byte_to_decimal_digit(b: u8) -> Option<u32> {
    if b.is_ascii_digit() {
        Some((b - b'0') as u32)
    } else {
        None
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

    #[inline(never)]
    pub(super) fn bench(input: &str) -> u32 {
        let mut p = Parser { input, position: 0 };
        let t = consume_numeric(&mut p);
        let bits = match t { Number { value, .. } | Dimension { value, .. } => value.to_bits(), Percentage { unit_value, .. } => unit_value.to_bits() };
        bits ^ p.position as u32
    }
    pub(super) fn run(input: &str) -> super::Observed {
        let mut p = Parser { input, position: 0 };
        let (kind, value, integer, sign, unit) = match consume_numeric(&mut p) {
            Number { value, int_value, has_sign } => (0, value, int_value, has_sign, ""),
            Percentage { unit_value, int_value, has_sign } => (1, unit_value, int_value, has_sign, ""),
            Dimension { value, int_value, has_sign, unit } => (2, value, int_value, has_sign, unit),
        };
        super::Observed { kind, bits: value.to_bits(), integer, sign, unit: unit.to_owned(), consumed: p.position }
    }
}
mod candidate {
macro_rules! match_byte { ($value:expr, $($arms:tt)*) => { match $value { $($arms)* } }; }
#[derive(Debug, PartialEq)]
enum Token<'a> {
    Number { value: f32, int_value: Option<i32>, has_sign: bool },
    Percentage { unit_value: f32, int_value: Option<i32>, has_sign: bool },
    Dimension { value: f32, int_value: Option<i32>, has_sign: bool, unit: &'a str },
}
use Token::*;
struct Parser<'a> { input: &'a str, position: usize }
impl<'a> Parser<'a> {
    fn position(&self) -> usize { self.position }
    fn slice_from(&self, start: usize) -> &'a str { &self.input[start..self.position] }
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

    &p.input[start..p.position]
}
fn byte_to_decimal_digit(b: u8) -> Option<u32> {
    if b.is_ascii_digit() {
        Some((b - b'0') as u32)
    } else {
        None
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
fn consume_numeric<'a>(parser: &mut Parser<'a>) -> Token<'a> {
    // Parse [+-]?\d*(\.\d+)?([eE][+-]?\d+)?
    // But this is always called so that there is at least one digit in \d*(\.\d+)?

    // Do all the math in f64 so that large numbers overflow to +/-inf
    // and i32::{MIN, MAX} are within range.

    let start_position = parser.position();
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

    let mut needs_reparse = !integral_part.is_finite();
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
        needs_reparse |= factor < f64::MIN_POSITIVE;
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
        let factor = f64::powf(10., sign * exponent);
        needs_reparse |= !factor.is_normal();
        value *= factor;
    }

    if needs_reparse {
        value = parser.slice_from(start_position).parse::<f64>().unwrap();
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

    #[inline(never)]
    pub(super) fn bench(input: &str) -> u32 {
        let mut p = Parser { input, position: 0 };
        let t = consume_numeric(&mut p);
        let bits = match t { Number { value, .. } | Dimension { value, .. } => value.to_bits(), Percentage { unit_value, .. } => unit_value.to_bits() };
        bits ^ p.position as u32
    }
    pub(super) fn run(input: &str) -> super::Observed {
        let mut p = Parser { input, position: 0 };
        let (kind, value, integer, sign, unit) = match consume_numeric(&mut p) {
            Number { value, int_value, has_sign } => (0, value, int_value, has_sign, ""),
            Percentage { unit_value, int_value, has_sign } => (1, unit_value, int_value, has_sign, ""),
            Dimension { value, int_value, has_sign, unit } => (2, value, int_value, has_sign, unit),
        };
        super::Observed { kind, bits: value.to_bits(), integer, sign, unit: unit.to_owned(), consumed: p.position }
    }
}


fn main() {
 let mut cases=0;
 for n in [0,307,308,309,323,324,400] {
  for sign in ["", "-", "+"] {
   for base in [format!("{}5e-{}", "0".repeat(n), 0), format!("0.{}5e{}", "0".repeat(n), n), format!("5{}e-{}", "0".repeat(n), n+1), format!("0.{}0e9999", "0".repeat(n))] {
    let number=format!("{sign}{base}");
    let expected=number.parse::<f64>().unwrap();
    for (suffix,unit,kind,extra) in [(";tail","",0,0),("%tail","",1,1),("px;tail","px",2,2),("e+;tail","e",2,1),("e-;tail","e-",2,2),(".;tail","",0,0)] {
     let input=format!("{number}{suffix}");
     let result=candidate::run(&input);
     let original=before::run(&input);
     assert_eq!((result.kind,&*result.unit,result.consumed,result.sign,result.integer),(kind,unit,number.len()+extra,!sign.is_empty(),None),"{input}");
     assert_eq!((result.kind,&result.unit,result.consumed,result.sign,result.integer),(original.kind,&original.unit,original.consumed,original.sign,original.integer));
     let value=if kind==1 {expected/100.} else {expected};
     assert_eq!(result.bits,(value as f32).to_bits(),"{input}");
     cases+=1;
    }
   }
  }
 }
 println!("PASS {cases} independent signed/zero/compensation/suffix checks");
}
