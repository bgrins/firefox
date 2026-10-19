#![allow(dead_code)]
use std::ops::Range;
mod cow_rc_str {
include!("source/third_party/rust/cssparser/src/cow_rc_str.rs");
pub fn is_shared(value: &CowRcStr<'_>) -> bool { value.borrowed_len_or_max == usize::MAX }
}
use cow_rc_str::CowRcStr;
macro_rules! match_byte { ($value:expr, $($arms:tt)*) => { match $value { $($arms)* } }; }
#[derive(Clone,Copy)] struct SourcePosition(usize);
struct SourceLocation {line:u32,column:u32}
struct ParserState {position:usize,current_line_start_position:u32,line_number_and_block_type:u32}
impl ParserState {
const BLOCK_TYPE_BITS:u32=2;
    pub fn position(&self) -> SourcePosition {
        SourcePosition(self.position)
    }
    pub fn source_location(&self) -> SourceLocation {
        SourceLocation {
            line: self.line_number(),
            column: (self.position as u32)
                .wrapping_sub(self.current_line_start_position)
                .wrapping_add(1),
        }
    }
    pub(crate) fn line_number(&self) -> u32 {
        self.line_number_and_block_type >> Self::BLOCK_TYPE_BITS
    }
    pub(crate) fn advance_line_number(&mut self, count: u32) {
        self.line_number_and_block_type += count << Self::BLOCK_TYPE_BITS;
    }
}
struct Parser<'a> {input:&'a str,state:ParserState,source_map_url:Option<&'a str>,source_url:Option<&'a str>}
impl<'a> Parser<'a> {
    pub fn position(&self) -> SourcePosition {
        debug_assert!(self.input.is_char_boundary(self.state.position));
        SourcePosition(self.state.position)
    }
    pub fn slice_from(&self, start_pos: SourcePosition) -> &'a str {
        self.slice(start_pos..self.position())
    }
    pub fn slice(&self, range: Range<SourcePosition>) -> &'a str {
        debug_assert!(self.input.is_char_boundary(range.start.0));
        debug_assert!(self.input.is_char_boundary(range.end.0));
        unsafe { self.input.get_unchecked(range.start.0..range.end.0) }
    }
    pub(crate) fn next_byte(&self) -> Option<u8> {
        if self.is_eof() {
            None
        } else {
            Some(self.input.as_bytes()[self.state.position])
        }
    }
    pub(crate) fn is_eof(&self) -> bool {
        !self.has_at_least(0)
    }
    fn has_at_least(&self, n: usize) -> bool {
        self.state.position + n < self.input.len()
    }
    pub(crate) fn advance(&mut self, n: usize) {
        if cfg!(debug_assertions) {
            // Each byte must either be an ASCII byte or a sequence
            // leader, but not a 4-byte leader; also newlines are
            // rejected.
            for i in 0..n {
                let b = self.byte_at(i);
                debug_assert!(b.is_ascii() || (b & 0xF0 != 0xF0 && b & 0xC0 != 0x80));
                debug_assert!(b != b'\r' && b != b'\n' && b != b'\x0C');
            }
        }
        self.state.position += n
    }
    fn next_byte_unchecked(&self) -> u8 {
        self.byte_at(0)
    }
    fn byte_at(&self, offset: usize) -> u8 {
        self.input.as_bytes()[self.state.position + offset]
    }
    fn consume_4byte_intro(&mut self) {
        debug_assert!(self.next_byte_unchecked() & 0xF0 == 0xF0);
        // This takes two UTF-16 characters to represent, so we
        // actually have an undercount.
        self.state.current_line_start_position =
            self.state.current_line_start_position.wrapping_sub(1);
        self.state.position += 1;
    }
    fn consume_continuation_byte(&mut self) {
        debug_assert!(self.next_byte_unchecked() & 0xC0 == 0x80);
        // Continuation bytes contribute to column overcount.  Note
        // that due to the special case for the 4-byte sequence intro,
        // we must use wrapping add here.
        self.state.current_line_start_position =
            self.state.current_line_start_position.wrapping_add(1);
        self.state.position += 1;
    }
    fn next_char(&self) -> char {
        unsafe { self.input.get_unchecked(self.state.position().0..) }
            .chars()
            .next()
            .unwrap()
    }
    fn consume_newline(&mut self) {
        let byte = self.next_byte_unchecked();
        debug_assert!(byte == b'\r' || byte == b'\n' || byte == b'\x0C');
        self.state.position += 1;
        if byte == b'\r' && self.next_byte() == Some(b'\n') {
            self.state.position += 1;
        }
        self.state.current_line_start_position = self.state.position as u32;
        self.state.advance_line_number(1);
    }
    fn consume_char(&mut self) -> char {
        let c = self.next_char();
        let len_utf8 = c.len_utf8();
        self.state.position += len_utf8;
        // Note that due to the special case for the 4-byte sequence
        // intro, we must use wrapping add here.
        self.state.current_line_start_position = self
            .state
            .current_line_start_position
            .wrapping_add((len_utf8 - c.len_utf16()) as u32);
        c
    }
}
#[derive(Debug)] enum Token<'a> {QuotedString(CowRcStr<'a>),BadString(CowRcStr<'a>)}
use Token::*;
fn consume_string<'a>(parser: &mut Parser<'a>, single_quote: bool) -> Token<'a> {
    match consume_quoted_string(parser, single_quote) {
        Ok(value) => QuotedString(value),
        Err(value) => BadString(value),
    }
}
fn consume_quoted_string<'a>(
    parser: &mut Parser<'a>,
    single_quote: bool,
) -> Result<CowRcStr<'a>, CowRcStr<'a>> {
    parser.advance(1); // Skip the initial quote
    // start_pos is at code point boundary, after " or '
    let start_pos = parser.position();
    let mut string_bytes;
    loop {
        if parser.is_eof() {
            return Ok(parser.slice_from(start_pos).into());
        }
        match_byte! { parser.next_byte_unchecked(),
            b'"' => {
                if !single_quote {
                    let value = parser.slice_from(start_pos);
                    parser.advance(1);
                    return Ok(value.into())
                }
                parser.advance(1);
            }
            b'\'' => {
                if single_quote {
                    let value = parser.slice_from(start_pos);
                    parser.advance(1);
                    return Ok(value.into())
                }
                parser.advance(1);
            }
            b'\\' | b'\0' => {
                // * The parser’s input is UTF-8 since it’s `&str`.
                // * start_pos is at a code point boundary
                // * so is the current position (which is before '\\' or '\0'
                //
                // So `string_bytes` is well-formed UTF-8.
                string_bytes = parser.slice_from(start_pos).as_bytes().to_owned();
                break
            }
            b'\n' | b'\r' | b'\x0C' => {
                return Err(parser.slice_from(start_pos).into())
            },
            b'\x80'..=b'\xBF' => { parser.consume_continuation_byte(); }
            b'\xF0'..=b'\xFF' => { parser.consume_4byte_intro(); }
            _ => {
                // ASCII or other leading byte.
                parser.advance(1);
            }
        }
    }

    while !parser.is_eof() {
        let b = parser.next_byte_unchecked();
        match_byte! { b,
            b'\n' | b'\r' | b'\x0C' => {
                return Err(
                    // string_bytes is well-formed UTF-8, see other comments.
                    unsafe {
                        from_utf8_release_unchecked(string_bytes)
                    }.into()
                );
            }
            b'"' => {
                parser.advance(1);
                if !single_quote {
                    break;
                }
            }
            b'\'' => {
                parser.advance(1);
                if single_quote {
                    break;
                }
            }
            b'\\' => {
                parser.advance(1);
                if !parser.is_eof() {
                    match parser.next_byte_unchecked() {
                        // Escaped newline
                        b'\n' | b'\x0C' | b'\r' => {
                            parser.consume_newline();
                        }
                        // This pushes one well-formed code point
                        _ => consume_escape_and_write(parser, &mut string_bytes)
                    }
                }
                // else: escaped EOF, do nothing.
                continue;
            }
            b'\0' => {
                parser.advance(1);
                string_bytes.extend("\u{FFFD}".as_bytes());
                continue;
            }
            b'\x80'..=b'\xBF' => { parser.consume_continuation_byte(); }
            b'\xF0'..=b'\xFF' => { parser.consume_4byte_intro(); }
            _ => {
                // ASCII or other leading byte.
                parser.advance(1);
            },
        }

        // If this byte is part of a multi-byte code point,
        // we’ll end up copying the whole code point before this loop does something else.
        string_bytes.push(b);
    }

    Ok(
        // string_bytes is well-formed UTF-8, see other comments.
        unsafe { from_utf8_release_unchecked(string_bytes) }.into(),
    )
}
fn byte_to_hex_digit(b: u8) -> Option<u32> {
    Some(match_byte! { b,
        b'0' ..= b'9' => b - b'0',
        b'a' ..= b'f' => b - b'a' + 10,
        b'A' ..= b'F' => b - b'A' + 10,
        _ => {
            return None
        }
    } as u32)
}
fn consume_hex_digits(parser: &mut Parser<'_>) -> (u32, u32) {
    let mut value = 0;
    let mut digits = 0;
    while digits < 6 && !parser.is_eof() {
        match byte_to_hex_digit(parser.next_byte_unchecked()) {
            Some(digit) => {
                value = value * 16 + digit;
                digits += 1;
                parser.advance(1);
            }
            None => break,
        }
    }
    (value, digits)
}
fn consume_escape_and_write(parser: &mut Parser, bytes: &mut Vec<u8>) {
    bytes.extend(consume_escape(parser).encode_utf8(&mut [0; 4]).as_bytes())
}
fn consume_escape(parser: &mut Parser) -> char {
    if parser.is_eof() {
        return '\u{FFFD}';
    } // Escaped EOF
    match_byte! { parser.next_byte_unchecked(),
        b'0'..=b'9' | b'A'..=b'F' | b'a'..=b'f' => {
            let (c, _) = consume_hex_digits(parser);
            if !parser.is_eof() {
                match_byte! { parser.next_byte_unchecked(),
                    b' ' | b'\t' => {
                        parser.advance(1)
                    }
                    b'\n' | b'\x0C' | b'\r' => {
                        parser.consume_newline();
                    }
                    _ => {}
                }
            }
            static REPLACEMENT_CHAR: char = '\u{FFFD}';
            if c != 0 {
                let c = char::from_u32(c);
                c.unwrap_or(REPLACEMENT_CHAR)
            } else {
                REPLACEMENT_CHAR
            }
        },
        b'\0' => {
            parser.advance(1);
            '\u{FFFD}'
        }
        _ => parser.consume_char(),
    }
}
unsafe fn from_utf8_release_unchecked(string_bytes: Vec<u8>) -> String {
    unsafe {
        if cfg!(debug_assertions) {
            String::from_utf8(string_bytes).unwrap()
        } else {
            String::from_utf8_unchecked(string_bytes)
        }
    }
}

fn main(){
let cases:[(&str,bool,&str,usize,u32,u32,bool,&str);808]=[
("\"",false,"",5,3,6,false,""),
("\"a",false,"a",6,3,7,false,""),
("\"\"",false,"",6,3,7,false,""),
("\"'",false,"'",6,3,7,false,""),
("\"\\",false,"",6,3,7,true,""),
("\"\u{a}",true,"",5,3,6,false,"\u{a}"),
("\"\u{d}",true,"",5,3,6,false,"\u{d}"),
("\"\u{c}",true,"",5,3,6,false,"\u{c}"),
("\"\u{0}",false,"�",6,3,7,true,""),
("\"é",false,"é",7,3,7,false,""),
("\"𐀀",false,"𐀀",9,3,8,false,""),
("\"aa",false,"aa",7,3,8,false,""),
("\"a\"",false,"a",7,3,8,false,""),
("\"a'",false,"a'",7,3,8,false,""),
("\"a\\",false,"a",7,3,8,true,""),
("\"a\u{a}",true,"a",6,3,7,false,"\u{a}"),
("\"a\u{d}",true,"a",6,3,7,false,"\u{d}"),
("\"a\u{c}",true,"a",6,3,7,false,"\u{c}"),
("\"a\u{0}",false,"a�",7,3,8,true,""),
("\"aé",false,"aé",8,3,8,false,""),
("\"a𐀀",false,"a𐀀",10,3,9,false,""),
("\"\"a",false,"",6,3,7,false,"a"),
("\"\"\"",false,"",6,3,7,false,"\""),
("\"\"'",false,"",6,3,7,false,"'"),
("\"\"\\",false,"",6,3,7,false,"\\"),
("\"\"\u{a}",false,"",6,3,7,false,"\u{a}"),
("\"\"\u{d}",false,"",6,3,7,false,"\u{d}"),
("\"\"\u{c}",false,"",6,3,7,false,"\u{c}"),
("\"\"\u{0}",false,"",6,3,7,false,"\u{0}"),
("\"\"é",false,"",6,3,7,false,"é"),
("\"\"𐀀",false,"",6,3,7,false,"𐀀"),
("\"'a",false,"'a",7,3,8,false,""),
("\"'\"",false,"'",7,3,8,false,""),
("\"''",false,"''",7,3,8,false,""),
("\"'\\",false,"'",7,3,8,true,""),
("\"'\u{a}",true,"'",6,3,7,false,"\u{a}"),
("\"'\u{d}",true,"'",6,3,7,false,"\u{d}"),
("\"'\u{c}",true,"'",6,3,7,false,"\u{c}"),
("\"'\u{0}",false,"'�",7,3,8,true,""),
("\"'é",false,"'é",8,3,8,false,""),
("\"'𐀀",false,"'𐀀",10,3,9,false,""),
("\"\\a",false,"\u{a}",7,3,8,true,""),
("\"\\\"",false,"\"",7,3,8,true,""),
("\"\\'",false,"'",7,3,8,true,""),
("\"\\\\",false,"\\",7,3,8,true,""),
("\"\\\u{a}",false,"",7,4,1,true,""),
("\"\\\u{d}",false,"",7,4,1,true,""),
("\"\\\u{c}",false,"",7,4,1,true,""),
("\"\\\u{0}",false,"�",7,3,8,true,""),
("\"\\é",false,"é",8,3,8,true,""),
("\"\\𐀀",false,"𐀀",10,3,9,true,""),
("\"\u{a}a",true,"",5,3,6,false,"\u{a}a"),
("\"\u{a}\"",true,"",5,3,6,false,"\u{a}\""),
("\"\u{a}'",true,"",5,3,6,false,"\u{a}'"),
("\"\u{a}\\",true,"",5,3,6,false,"\u{a}\\"),
("\"\u{a}\u{a}",true,"",5,3,6,false,"\u{a}\u{a}"),
("\"\u{a}\u{d}",true,"",5,3,6,false,"\u{a}\u{d}"),
("\"\u{a}\u{c}",true,"",5,3,6,false,"\u{a}\u{c}"),
("\"\u{a}\u{0}",true,"",5,3,6,false,"\u{a}\u{0}"),
("\"\u{a}é",true,"",5,3,6,false,"\u{a}é"),
("\"\u{a}𐀀",true,"",5,3,6,false,"\u{a}𐀀"),
("\"\u{d}a",true,"",5,3,6,false,"\u{d}a"),
("\"\u{d}\"",true,"",5,3,6,false,"\u{d}\""),
("\"\u{d}'",true,"",5,3,6,false,"\u{d}'"),
("\"\u{d}\\",true,"",5,3,6,false,"\u{d}\\"),
("\"\u{d}\u{a}",true,"",5,3,6,false,"\u{d}\u{a}"),
("\"\u{d}\u{d}",true,"",5,3,6,false,"\u{d}\u{d}"),
("\"\u{d}\u{c}",true,"",5,3,6,false,"\u{d}\u{c}"),
("\"\u{d}\u{0}",true,"",5,3,6,false,"\u{d}\u{0}"),
("\"\u{d}é",true,"",5,3,6,false,"\u{d}é"),
("\"\u{d}𐀀",true,"",5,3,6,false,"\u{d}𐀀"),
("\"\u{c}a",true,"",5,3,6,false,"\u{c}a"),
("\"\u{c}\"",true,"",5,3,6,false,"\u{c}\""),
("\"\u{c}'",true,"",5,3,6,false,"\u{c}'"),
("\"\u{c}\\",true,"",5,3,6,false,"\u{c}\\"),
("\"\u{c}\u{a}",true,"",5,3,6,false,"\u{c}\u{a}"),
("\"\u{c}\u{d}",true,"",5,3,6,false,"\u{c}\u{d}"),
("\"\u{c}\u{c}",true,"",5,3,6,false,"\u{c}\u{c}"),
("\"\u{c}\u{0}",true,"",5,3,6,false,"\u{c}\u{0}"),
("\"\u{c}é",true,"",5,3,6,false,"\u{c}é"),
("\"\u{c}𐀀",true,"",5,3,6,false,"\u{c}𐀀"),
("\"\u{0}a",false,"�a",7,3,8,true,""),
("\"\u{0}\"",false,"�",7,3,8,true,""),
("\"\u{0}'",false,"�'",7,3,8,true,""),
("\"\u{0}\\",false,"�",7,3,8,true,""),
("\"\u{0}\u{a}",true,"�",6,3,7,true,"\u{a}"),
("\"\u{0}\u{d}",true,"�",6,3,7,true,"\u{d}"),
("\"\u{0}\u{c}",true,"�",6,3,7,true,"\u{c}"),
("\"\u{0}\u{0}",false,"��",7,3,8,true,""),
("\"\u{0}é",false,"�é",8,3,8,true,""),
("\"\u{0}𐀀",false,"�𐀀",10,3,9,true,""),
("\"éa",false,"éa",8,3,8,false,""),
("\"é\"",false,"é",8,3,8,false,""),
("\"é'",false,"é'",8,3,8,false,""),
("\"é\\",false,"é",8,3,8,true,""),
("\"é\u{a}",true,"é",7,3,7,false,"\u{a}"),
("\"é\u{d}",true,"é",7,3,7,false,"\u{d}"),
("\"é\u{c}",true,"é",7,3,7,false,"\u{c}"),
("\"é\u{0}",false,"é�",8,3,8,true,""),
("\"éé",false,"éé",9,3,8,false,""),
("\"é𐀀",false,"é𐀀",11,3,9,false,""),
("\"𐀀a",false,"𐀀a",10,3,9,false,""),
("\"𐀀\"",false,"𐀀",10,3,9,false,""),
("\"𐀀'",false,"𐀀'",10,3,9,false,""),
("\"𐀀\\",false,"𐀀",10,3,9,true,""),
("\"𐀀\u{a}",true,"𐀀",9,3,8,false,"\u{a}"),
("\"𐀀\u{d}",true,"𐀀",9,3,8,false,"\u{d}"),
("\"𐀀\u{c}",true,"𐀀",9,3,8,false,"\u{c}"),
("\"𐀀\u{0}",false,"𐀀�",10,3,9,true,""),
("\"𐀀é",false,"𐀀é",11,3,9,false,""),
("\"𐀀𐀀",false,"𐀀𐀀",13,3,10,false,""),
("\"abc",false,"abc",8,3,9,false,""),
("\"abc\";tail",false,"abc",9,3,10,false,";tail"),
("\"a\\\u{a}b",false,"ab",9,4,2,true,""),
("\"a\\\u{a}b\";tail",false,"ab",10,4,3,true,";tail"),
("\"a\\\u{d}\u{a}b",false,"ab",10,4,2,true,""),
("\"a\\\u{d}\u{a}b\";tail",false,"ab",11,4,3,true,";tail"),
("\"\\0",false,"�",7,3,8,true,""),
("\"\\0\";tail",false,"�",8,3,9,true,";tail"),
("\"\\000000",false,"�",12,3,13,true,""),
("\"\\000000\";tail",false,"�",13,3,14,true,";tail"),
("\"\\D800",false,"�",10,3,11,true,""),
("\"\\D800\";tail",false,"�",11,3,12,true,";tail"),
("\"\\10ffff",false,"􏿿",12,3,13,true,""),
("\"\\10ffff\";tail",false,"􏿿",13,3,14,true,";tail"),
("\"\\110000",false,"�",12,3,13,true,""),
("\"\\110000\";tail",false,"�",13,3,14,true,";tail"),
("\"\\61 b",false,"ab",10,3,11,true,""),
("\"\\61 b\";tail",false,"ab",11,3,12,true,";tail"),
("\"\\000061b",false,"ab",13,3,14,true,""),
("\"\\000061b\";tail",false,"ab",14,3,15,true,";tail"),
("\"\\61\u{d}\u{a}b",false,"ab",11,4,2,true,""),
("\"\\61\u{d}\u{a}b\";tail",false,"ab",12,4,3,true,";tail"),
("\"é𐀀\\61 x",false,"é𐀀ax",16,3,14,true,""),
("\"é𐀀\\61 x\";tail",false,"é𐀀ax",17,3,15,true,";tail"),
("\"x\u{0}y",false,"x�y",8,3,9,true,""),
("\"x\u{0}y\";tail",false,"x�y",9,3,10,true,";tail"),
("\"\\𐀀x",false,"𐀀x",11,3,10,true,""),
("\"\\𐀀x\";tail",false,"𐀀x",12,3,11,true,";tail"),
("\"/*# sourceURL=not-a-directive*/",false,"/*# sourceURL=not-a-directive*/",36,3,37,false,""),
("\"/*# sourceURL=not-a-directive*/\";tail",false,"/*# sourceURL=not-a-directive*/",37,3,38,false,";tail"),
("\"\\\\\";tail",false,"\\",8,3,9,true,";tail"),
("\"\\\"\";tail",false,"\"",8,3,9,true,";tail"),
("\"\\'\";tail",false,"'",8,3,9,true,";tail"),
("\"a\u{a}; color:green",true,"a",6,3,7,false,"\u{a}; color:green"),
("\"a\u{a}; color:green\";tail",true,"a",6,3,7,false,"\u{a}; color:green\";tail"),
("\"\\\"tail",false,"\"tail",11,3,12,true,""),
("\"\\\u{0}\"tail",false,"�",8,3,9,true,"tail"),
("\"\\\u{0}\u{a}",true,"�",7,3,8,true,"\u{a}"),
("\"\\é\"tail",false,"é",9,3,9,true,"tail"),
("\"\\é\u{a}",true,"é",8,3,8,true,"\u{a}"),
("\"\\𐀀\"tail",false,"𐀀",11,3,10,true,"tail"),
("\"\\𐀀\u{a}",true,"𐀀",10,3,9,true,"\u{a}"),
("\"\\\u{a}\"tail",false,"",8,4,2,true,"tail"),
("\"\\\u{a}\u{a}",true,"",7,4,1,true,"\u{a}"),
("\"\\\u{d}\"tail",false,"",8,4,2,true,"tail"),
("\"\\\u{d}\u{a}",false,"",8,4,1,true,""),
("\"\\\u{d}\u{a}\"tail",false,"",9,4,2,true,"tail"),
("\"\\\u{d}\u{a}\u{a}",true,"",8,4,1,true,"\u{a}"),
("\"\\\u{c}\"tail",false,"",8,4,2,true,"tail"),
("\"\\\u{c}\u{a}",true,"",7,4,1,true,"\u{a}"),
("\"\\1",false,"\u{1}",7,3,8,true,""),
("\"\\1\"tail",false,"\u{1}",8,3,9,true,"tail"),
("\"\\1\u{a}",false,"\u{1}",8,4,1,true,""),
("\"\\f",false,"\u{f}",7,3,8,true,""),
("\"\\f\"tail",false,"\u{f}",8,3,9,true,"tail"),
("\"\\f\u{a}",false,"\u{f}",8,4,1,true,""),
("\"\\ff",false,"ÿ",8,3,9,true,""),
("\"\\ff\"tail",false,"ÿ",9,3,10,true,"tail"),
("\"\\ff\u{a}",false,"ÿ",9,4,1,true,""),
("\"\\fff",false,"࿿",9,3,10,true,""),
("\"\\fff\"tail",false,"࿿",10,3,11,true,"tail"),
("\"\\fff\u{a}",false,"࿿",10,4,1,true,""),
("\"\\ffff",false,"￿",10,3,11,true,""),
("\"\\ffff\"tail",false,"￿",11,3,12,true,"tail"),
("\"\\ffff\u{a}",false,"￿",11,4,1,true,""),
("\"\\10000",false,"𐀀",11,3,12,true,""),
("\"\\10000\"tail",false,"𐀀",12,3,13,true,"tail"),
("\"\\10000\u{a}",false,"𐀀",12,4,1,true,""),
("\"\\ffffff",false,"�",12,3,13,true,""),
("\"\\ffffff\"tail",false,"�",13,3,14,true,"tail"),
("\"\\ffffff\u{a}",false,"�",13,4,1,true,""),
("\"\\000061b\"tail",false,"ab",14,3,15,true,"tail"),
("\"\\000061b\u{a}",true,"ab",13,3,14,true,"\u{a}"),
("\"\\61\u{d}\u{a}",false,"a",10,4,1,true,""),
("\"\\61\u{d}\u{a}\"tail",false,"a",11,4,2,true,"tail"),
("\"\\61\u{d}\u{a}\u{a}",true,"a",10,4,1,true,"\u{a}"),
("\"\\61\u{9}",false,"a",9,3,10,true,""),
("\"\\61\u{9}\"tail",false,"a",10,3,11,true,"tail"),
("\"\\61\u{9}\u{a}",true,"a",9,3,10,true,"\u{a}"),
("\"\\61\u{c}",false,"a",9,4,1,true,""),
("\"\\61\u{c}\"tail",false,"a",10,4,2,true,"tail"),
("\"\\61\u{c}\u{a}",true,"a",9,4,1,true,"\u{a}"),
("\"\\61  ",false,"a ",10,3,11,true,""),
("\"\\61  \"tail",false,"a ",11,3,12,true,"tail"),
("\"\\61  \u{a}",true,"a ",10,3,11,true,"\u{a}"),
("\"\\00000",false,"�",11,3,12,true,""),
("\"\\00000\"tail",false,"�",12,3,13,true,"tail"),
("\"\\00000\u{a}",false,"�",12,4,1,true,""),
("\"\\DFFF",false,"�",10,3,11,true,""),
("\"\\DFFF\"tail",false,"�",11,3,12,true,"tail"),
("\"\\DFFF\u{a}",false,"�",11,4,1,true,""),
("\"\\110000\"tail",false,"�",13,3,14,true,"tail"),
("\"\\110000\u{a}",false,"�",13,4,1,true,""),
("\"é𐀀\\",false,"é𐀀",12,3,10,true,""),
("\"é𐀀\\\"tail",false,"é𐀀\"tail",17,3,15,true,""),
("\"é𐀀\\\u{a}",false,"é𐀀",13,4,1,true,""),
("\"é𐀀\\\u{0}",false,"é𐀀�",13,3,11,true,""),
("\"é𐀀\\\u{0}\"tail",false,"é𐀀�",14,3,12,true,"tail"),
("\"é𐀀\\\u{0}\u{a}",true,"é𐀀�",13,3,11,true,"\u{a}"),
("\"é𐀀\\é",false,"é𐀀é",14,3,11,true,""),
("\"é𐀀\\é\"tail",false,"é𐀀é",15,3,12,true,"tail"),
("\"é𐀀\\é\u{a}",true,"é𐀀é",14,3,11,true,"\u{a}"),
("\"é𐀀\\𐀀",false,"é𐀀𐀀",16,3,12,true,""),
("\"é𐀀\\𐀀\"tail",false,"é𐀀𐀀",17,3,13,true,"tail"),
("\"é𐀀\\𐀀\u{a}",true,"é𐀀𐀀",16,3,12,true,"\u{a}"),
("\"é𐀀\\\u{a}\"tail",false,"é𐀀",14,4,2,true,"tail"),
("\"é𐀀\\\u{a}\u{a}",true,"é𐀀",13,4,1,true,"\u{a}"),
("\"é𐀀\\\u{d}",false,"é𐀀",13,4,1,true,""),
("\"é𐀀\\\u{d}\"tail",false,"é𐀀",14,4,2,true,"tail"),
("\"é𐀀\\\u{d}\u{a}",false,"é𐀀",14,4,1,true,""),
("\"é𐀀\\\u{d}\u{a}\"tail",false,"é𐀀",15,4,2,true,"tail"),
("\"é𐀀\\\u{d}\u{a}\u{a}",true,"é𐀀",14,4,1,true,"\u{a}"),
("\"é𐀀\\\u{c}",false,"é𐀀",13,4,1,true,""),
("\"é𐀀\\\u{c}\"tail",false,"é𐀀",14,4,2,true,"tail"),
("\"é𐀀\\\u{c}\u{a}",true,"é𐀀",13,4,1,true,"\u{a}"),
("\"é𐀀\\1",false,"é𐀀\u{1}",13,3,11,true,""),
("\"é𐀀\\1\"tail",false,"é𐀀\u{1}",14,3,12,true,"tail"),
("\"é𐀀\\1\u{a}",false,"é𐀀\u{1}",14,4,1,true,""),
("\"é𐀀\\f",false,"é𐀀\u{f}",13,3,11,true,""),
("\"é𐀀\\f\"tail",false,"é𐀀\u{f}",14,3,12,true,"tail"),
("\"é𐀀\\f\u{a}",false,"é𐀀\u{f}",14,4,1,true,""),
("\"é𐀀\\ff",false,"é𐀀ÿ",14,3,12,true,""),
("\"é𐀀\\ff\"tail",false,"é𐀀ÿ",15,3,13,true,"tail"),
("\"é𐀀\\ff\u{a}",false,"é𐀀ÿ",15,4,1,true,""),
("\"é𐀀\\fff",false,"é𐀀࿿",15,3,13,true,""),
("\"é𐀀\\fff\"tail",false,"é𐀀࿿",16,3,14,true,"tail"),
("\"é𐀀\\fff\u{a}",false,"é𐀀࿿",16,4,1,true,""),
("\"é𐀀\\ffff",false,"é𐀀￿",16,3,14,true,""),
("\"é𐀀\\ffff\"tail",false,"é𐀀￿",17,3,15,true,"tail"),
("\"é𐀀\\ffff\u{a}",false,"é𐀀￿",17,4,1,true,""),
("\"é𐀀\\10000",false,"é𐀀𐀀",17,3,15,true,""),
("\"é𐀀\\10000\"tail",false,"é𐀀𐀀",18,3,16,true,"tail"),
("\"é𐀀\\10000\u{a}",false,"é𐀀𐀀",18,4,1,true,""),
("\"é𐀀\\ffffff",false,"é𐀀�",18,3,16,true,""),
("\"é𐀀\\ffffff\"tail",false,"é𐀀�",19,3,17,true,"tail"),
("\"é𐀀\\ffffff\u{a}",false,"é𐀀�",19,4,1,true,""),
("\"é𐀀\\000061b",false,"é𐀀ab",19,3,17,true,""),
("\"é𐀀\\000061b\"tail",false,"é𐀀ab",20,3,18,true,"tail"),
("\"é𐀀\\000061b\u{a}",true,"é𐀀ab",19,3,17,true,"\u{a}"),
("\"é𐀀\\61\u{d}\u{a}",false,"é𐀀a",16,4,1,true,""),
("\"é𐀀\\61\u{d}\u{a}\"tail",false,"é𐀀a",17,4,2,true,"tail"),
("\"é𐀀\\61\u{d}\u{a}\u{a}",true,"é𐀀a",16,4,1,true,"\u{a}"),
("\"é𐀀\\61\u{9}",false,"é𐀀a",15,3,13,true,""),
("\"é𐀀\\61\u{9}\"tail",false,"é𐀀a",16,3,14,true,"tail"),
("\"é𐀀\\61\u{9}\u{a}",true,"é𐀀a",15,3,13,true,"\u{a}"),
("\"é𐀀\\61\u{c}",false,"é𐀀a",15,4,1,true,""),
("\"é𐀀\\61\u{c}\"tail",false,"é𐀀a",16,4,2,true,"tail"),
("\"é𐀀\\61\u{c}\u{a}",true,"é𐀀a",15,4,1,true,"\u{a}"),
("\"é𐀀\\61  ",false,"é𐀀a ",16,3,14,true,""),
("\"é𐀀\\61  \"tail",false,"é𐀀a ",17,3,15,true,"tail"),
("\"é𐀀\\61  \u{a}",true,"é𐀀a ",16,3,14,true,"\u{a}"),
("\"é𐀀\\00000",false,"é𐀀�",17,3,15,true,""),
("\"é𐀀\\00000\"tail",false,"é𐀀�",18,3,16,true,"tail"),
("\"é𐀀\\00000\u{a}",false,"é𐀀�",18,4,1,true,""),
("\"é𐀀\\DFFF",false,"é𐀀�",16,3,14,true,""),
("\"é𐀀\\DFFF\"tail",false,"é𐀀�",17,3,15,true,"tail"),
("\"é𐀀\\DFFF\u{a}",false,"é𐀀�",17,4,1,true,""),
("\"é𐀀\\110000",false,"é𐀀�",18,3,16,true,""),
("\"é𐀀\\110000\"tail",false,"é𐀀�",19,3,17,true,"tail"),
("\"é𐀀\\110000\u{a}",false,"é𐀀�",19,4,1,true,""),
("\"\u{0}\\\"tail",false,"�\"tail",12,3,13,true,""),
("\"\u{0}\\\u{a}",false,"�",8,4,1,true,""),
("\"\u{0}\\\u{0}",false,"��",8,3,9,true,""),
("\"\u{0}\\\u{0}\"tail",false,"��",9,3,10,true,"tail"),
("\"\u{0}\\\u{0}\u{a}",true,"��",8,3,9,true,"\u{a}"),
("\"\u{0}\\é",false,"�é",9,3,9,true,""),
("\"\u{0}\\é\"tail",false,"�é",10,3,10,true,"tail"),
("\"\u{0}\\é\u{a}",true,"�é",9,3,9,true,"\u{a}"),
("\"\u{0}\\𐀀",false,"�𐀀",11,3,10,true,""),
("\"\u{0}\\𐀀\"tail",false,"�𐀀",12,3,11,true,"tail"),
("\"\u{0}\\𐀀\u{a}",true,"�𐀀",11,3,10,true,"\u{a}"),
("\"\u{0}\\\u{a}\"tail",false,"�",9,4,2,true,"tail"),
("\"\u{0}\\\u{a}\u{a}",true,"�",8,4,1,true,"\u{a}"),
("\"\u{0}\\\u{d}",false,"�",8,4,1,true,""),
("\"\u{0}\\\u{d}\"tail",false,"�",9,4,2,true,"tail"),
("\"\u{0}\\\u{d}\u{a}",false,"�",9,4,1,true,""),
("\"\u{0}\\\u{d}\u{a}\"tail",false,"�",10,4,2,true,"tail"),
("\"\u{0}\\\u{d}\u{a}\u{a}",true,"�",9,4,1,true,"\u{a}"),
("\"\u{0}\\\u{c}",false,"�",8,4,1,true,""),
("\"\u{0}\\\u{c}\"tail",false,"�",9,4,2,true,"tail"),
("\"\u{0}\\\u{c}\u{a}",true,"�",8,4,1,true,"\u{a}"),
("\"\u{0}\\1",false,"�\u{1}",8,3,9,true,""),
("\"\u{0}\\1\"tail",false,"�\u{1}",9,3,10,true,"tail"),
("\"\u{0}\\1\u{a}",false,"�\u{1}",9,4,1,true,""),
("\"\u{0}\\f",false,"�\u{f}",8,3,9,true,""),
("\"\u{0}\\f\"tail",false,"�\u{f}",9,3,10,true,"tail"),
("\"\u{0}\\f\u{a}",false,"�\u{f}",9,4,1,true,""),
("\"\u{0}\\ff",false,"�ÿ",9,3,10,true,""),
("\"\u{0}\\ff\"tail",false,"�ÿ",10,3,11,true,"tail"),
("\"\u{0}\\ff\u{a}",false,"�ÿ",10,4,1,true,""),
("\"\u{0}\\fff",false,"�࿿",10,3,11,true,""),
("\"\u{0}\\fff\"tail",false,"�࿿",11,3,12,true,"tail"),
("\"\u{0}\\fff\u{a}",false,"�࿿",11,4,1,true,""),
("\"\u{0}\\ffff",false,"�￿",11,3,12,true,""),
("\"\u{0}\\ffff\"tail",false,"�￿",12,3,13,true,"tail"),
("\"\u{0}\\ffff\u{a}",false,"�￿",12,4,1,true,""),
("\"\u{0}\\10000",false,"�𐀀",12,3,13,true,""),
("\"\u{0}\\10000\"tail",false,"�𐀀",13,3,14,true,"tail"),
("\"\u{0}\\10000\u{a}",false,"�𐀀",13,4,1,true,""),
("\"\u{0}\\ffffff",false,"��",13,3,14,true,""),
("\"\u{0}\\ffffff\"tail",false,"��",14,3,15,true,"tail"),
("\"\u{0}\\ffffff\u{a}",false,"��",14,4,1,true,""),
("\"\u{0}\\000061b",false,"�ab",14,3,15,true,""),
("\"\u{0}\\000061b\"tail",false,"�ab",15,3,16,true,"tail"),
("\"\u{0}\\000061b\u{a}",true,"�ab",14,3,15,true,"\u{a}"),
("\"\u{0}\\61\u{d}\u{a}",false,"�a",11,4,1,true,""),
("\"\u{0}\\61\u{d}\u{a}\"tail",false,"�a",12,4,2,true,"tail"),
("\"\u{0}\\61\u{d}\u{a}\u{a}",true,"�a",11,4,1,true,"\u{a}"),
("\"\u{0}\\61\u{9}",false,"�a",10,3,11,true,""),
("\"\u{0}\\61\u{9}\"tail",false,"�a",11,3,12,true,"tail"),
("\"\u{0}\\61\u{9}\u{a}",true,"�a",10,3,11,true,"\u{a}"),
("\"\u{0}\\61\u{c}",false,"�a",10,4,1,true,""),
("\"\u{0}\\61\u{c}\"tail",false,"�a",11,4,2,true,"tail"),
("\"\u{0}\\61\u{c}\u{a}",true,"�a",10,4,1,true,"\u{a}"),
("\"\u{0}\\61  ",false,"�a ",11,3,12,true,""),
("\"\u{0}\\61  \"tail",false,"�a ",12,3,13,true,"tail"),
("\"\u{0}\\61  \u{a}",true,"�a ",11,3,12,true,"\u{a}"),
("\"\u{0}\\00000",false,"��",12,3,13,true,""),
("\"\u{0}\\00000\"tail",false,"��",13,3,14,true,"tail"),
("\"\u{0}\\00000\u{a}",false,"��",13,4,1,true,""),
("\"\u{0}\\DFFF",false,"��",11,3,12,true,""),
("\"\u{0}\\DFFF\"tail",false,"��",12,3,13,true,"tail"),
("\"\u{0}\\DFFF\u{a}",false,"��",12,4,1,true,""),
("\"\u{0}\\110000",false,"��",13,3,14,true,""),
("\"\u{0}\\110000\"tail",false,"��",14,3,15,true,"tail"),
("\"\u{0}\\110000\u{a}",false,"��",14,4,1,true,""),
("\"\\61 \\",false,"a",10,3,11,true,""),
("\"\\61 \\\"tail",false,"a\"tail",15,3,16,true,""),
("\"\\61 \\\u{a}",false,"a",11,4,1,true,""),
("\"\\61 \\\u{0}",false,"a�",11,3,12,true,""),
("\"\\61 \\\u{0}\"tail",false,"a�",12,3,13,true,"tail"),
("\"\\61 \\\u{0}\u{a}",true,"a�",11,3,12,true,"\u{a}"),
("\"\\61 \\é",false,"aé",12,3,12,true,""),
("\"\\61 \\é\"tail",false,"aé",13,3,13,true,"tail"),
("\"\\61 \\é\u{a}",true,"aé",12,3,12,true,"\u{a}"),
("\"\\61 \\𐀀",false,"a𐀀",14,3,13,true,""),
("\"\\61 \\𐀀\"tail",false,"a𐀀",15,3,14,true,"tail"),
("\"\\61 \\𐀀\u{a}",true,"a𐀀",14,3,13,true,"\u{a}"),
("\"\\61 \\\u{a}\"tail",false,"a",12,4,2,true,"tail"),
("\"\\61 \\\u{a}\u{a}",true,"a",11,4,1,true,"\u{a}"),
("\"\\61 \\\u{d}",false,"a",11,4,1,true,""),
("\"\\61 \\\u{d}\"tail",false,"a",12,4,2,true,"tail"),
("\"\\61 \\\u{d}\u{a}",false,"a",12,4,1,true,""),
("\"\\61 \\\u{d}\u{a}\"tail",false,"a",13,4,2,true,"tail"),
("\"\\61 \\\u{d}\u{a}\u{a}",true,"a",12,4,1,true,"\u{a}"),
("\"\\61 \\\u{c}",false,"a",11,4,1,true,""),
("\"\\61 \\\u{c}\"tail",false,"a",12,4,2,true,"tail"),
("\"\\61 \\\u{c}\u{a}",true,"a",11,4,1,true,"\u{a}"),
("\"\\61 \\1",false,"a\u{1}",11,3,12,true,""),
("\"\\61 \\1\"tail",false,"a\u{1}",12,3,13,true,"tail"),
("\"\\61 \\1\u{a}",false,"a\u{1}",12,4,1,true,""),
("\"\\61 \\f",false,"a\u{f}",11,3,12,true,""),
("\"\\61 \\f\"tail",false,"a\u{f}",12,3,13,true,"tail"),
("\"\\61 \\f\u{a}",false,"a\u{f}",12,4,1,true,""),
("\"\\61 \\ff",false,"aÿ",12,3,13,true,""),
("\"\\61 \\ff\"tail",false,"aÿ",13,3,14,true,"tail"),
("\"\\61 \\ff\u{a}",false,"aÿ",13,4,1,true,""),
("\"\\61 \\fff",false,"a࿿",13,3,14,true,""),
("\"\\61 \\fff\"tail",false,"a࿿",14,3,15,true,"tail"),
("\"\\61 \\fff\u{a}",false,"a࿿",14,4,1,true,""),
("\"\\61 \\ffff",false,"a￿",14,3,15,true,""),
("\"\\61 \\ffff\"tail",false,"a￿",15,3,16,true,"tail"),
("\"\\61 \\ffff\u{a}",false,"a￿",15,4,1,true,""),
("\"\\61 \\10000",false,"a𐀀",15,3,16,true,""),
("\"\\61 \\10000\"tail",false,"a𐀀",16,3,17,true,"tail"),
("\"\\61 \\10000\u{a}",false,"a𐀀",16,4,1,true,""),
("\"\\61 \\ffffff",false,"a�",16,3,17,true,""),
("\"\\61 \\ffffff\"tail",false,"a�",17,3,18,true,"tail"),
("\"\\61 \\ffffff\u{a}",false,"a�",17,4,1,true,""),
("\"\\61 \\000061b",false,"aab",17,3,18,true,""),
("\"\\61 \\000061b\"tail",false,"aab",18,3,19,true,"tail"),
("\"\\61 \\000061b\u{a}",true,"aab",17,3,18,true,"\u{a}"),
("\"\\61 \\61\u{d}\u{a}",false,"aa",14,4,1,true,""),
("\"\\61 \\61\u{d}\u{a}\"tail",false,"aa",15,4,2,true,"tail"),
("\"\\61 \\61\u{d}\u{a}\u{a}",true,"aa",14,4,1,true,"\u{a}"),
("\"\\61 \\61\u{9}",false,"aa",13,3,14,true,""),
("\"\\61 \\61\u{9}\"tail",false,"aa",14,3,15,true,"tail"),
("\"\\61 \\61\u{9}\u{a}",true,"aa",13,3,14,true,"\u{a}"),
("\"\\61 \\61\u{c}",false,"aa",13,4,1,true,""),
("\"\\61 \\61\u{c}\"tail",false,"aa",14,4,2,true,"tail"),
("\"\\61 \\61\u{c}\u{a}",true,"aa",13,4,1,true,"\u{a}"),
("\"\\61 \\61  ",false,"aa ",14,3,15,true,""),
("\"\\61 \\61  \"tail",false,"aa ",15,3,16,true,"tail"),
("\"\\61 \\61  \u{a}",true,"aa ",14,3,15,true,"\u{a}"),
("\"\\61 \\00000",false,"a�",15,3,16,true,""),
("\"\\61 \\00000\"tail",false,"a�",16,3,17,true,"tail"),
("\"\\61 \\00000\u{a}",false,"a�",16,4,1,true,""),
("\"\\61 \\DFFF",false,"a�",14,3,15,true,""),
("\"\\61 \\DFFF\"tail",false,"a�",15,3,16,true,"tail"),
("\"\\61 \\DFFF\u{a}",false,"a�",15,4,1,true,""),
("\"\\61 \\110000",false,"a�",16,3,17,true,""),
("\"\\61 \\110000\"tail",false,"a�",17,3,18,true,"tail"),
("\"\\61 \\110000\u{a}",false,"a�",17,4,1,true,""),
("'",false,"",5,3,6,false,""),
("'a",false,"a",6,3,7,false,""),
("'\"",false,"\"",6,3,7,false,""),
("''",false,"",6,3,7,false,""),
("'\\",false,"",6,3,7,true,""),
("'\u{a}",true,"",5,3,6,false,"\u{a}"),
("'\u{d}",true,"",5,3,6,false,"\u{d}"),
("'\u{c}",true,"",5,3,6,false,"\u{c}"),
("'\u{0}",false,"�",6,3,7,true,""),
("'é",false,"é",7,3,7,false,""),
("'𐀀",false,"𐀀",9,3,8,false,""),
("'aa",false,"aa",7,3,8,false,""),
("'a\"",false,"a\"",7,3,8,false,""),
("'a'",false,"a",7,3,8,false,""),
("'a\\",false,"a",7,3,8,true,""),
("'a\u{a}",true,"a",6,3,7,false,"\u{a}"),
("'a\u{d}",true,"a",6,3,7,false,"\u{d}"),
("'a\u{c}",true,"a",6,3,7,false,"\u{c}"),
("'a\u{0}",false,"a�",7,3,8,true,""),
("'aé",false,"aé",8,3,8,false,""),
("'a𐀀",false,"a𐀀",10,3,9,false,""),
("'\"a",false,"\"a",7,3,8,false,""),
("'\"\"",false,"\"\"",7,3,8,false,""),
("'\"'",false,"\"",7,3,8,false,""),
("'\"\\",false,"\"",7,3,8,true,""),
("'\"\u{a}",true,"\"",6,3,7,false,"\u{a}"),
("'\"\u{d}",true,"\"",6,3,7,false,"\u{d}"),
("'\"\u{c}",true,"\"",6,3,7,false,"\u{c}"),
("'\"\u{0}",false,"\"�",7,3,8,true,""),
("'\"é",false,"\"é",8,3,8,false,""),
("'\"𐀀",false,"\"𐀀",10,3,9,false,""),
("''a",false,"",6,3,7,false,"a"),
("''\"",false,"",6,3,7,false,"\""),
("'''",false,"",6,3,7,false,"'"),
("''\\",false,"",6,3,7,false,"\\"),
("''\u{a}",false,"",6,3,7,false,"\u{a}"),
("''\u{d}",false,"",6,3,7,false,"\u{d}"),
("''\u{c}",false,"",6,3,7,false,"\u{c}"),
("''\u{0}",false,"",6,3,7,false,"\u{0}"),
("''é",false,"",6,3,7,false,"é"),
("''𐀀",false,"",6,3,7,false,"𐀀"),
("'\\a",false,"\u{a}",7,3,8,true,""),
("'\\\"",false,"\"",7,3,8,true,""),
("'\\'",false,"'",7,3,8,true,""),
("'\\\\",false,"\\",7,3,8,true,""),
("'\\\u{a}",false,"",7,4,1,true,""),
("'\\\u{d}",false,"",7,4,1,true,""),
("'\\\u{c}",false,"",7,4,1,true,""),
("'\\\u{0}",false,"�",7,3,8,true,""),
("'\\é",false,"é",8,3,8,true,""),
("'\\𐀀",false,"𐀀",10,3,9,true,""),
("'\u{a}a",true,"",5,3,6,false,"\u{a}a"),
("'\u{a}\"",true,"",5,3,6,false,"\u{a}\""),
("'\u{a}'",true,"",5,3,6,false,"\u{a}'"),
("'\u{a}\\",true,"",5,3,6,false,"\u{a}\\"),
("'\u{a}\u{a}",true,"",5,3,6,false,"\u{a}\u{a}"),
("'\u{a}\u{d}",true,"",5,3,6,false,"\u{a}\u{d}"),
("'\u{a}\u{c}",true,"",5,3,6,false,"\u{a}\u{c}"),
("'\u{a}\u{0}",true,"",5,3,6,false,"\u{a}\u{0}"),
("'\u{a}é",true,"",5,3,6,false,"\u{a}é"),
("'\u{a}𐀀",true,"",5,3,6,false,"\u{a}𐀀"),
("'\u{d}a",true,"",5,3,6,false,"\u{d}a"),
("'\u{d}\"",true,"",5,3,6,false,"\u{d}\""),
("'\u{d}'",true,"",5,3,6,false,"\u{d}'"),
("'\u{d}\\",true,"",5,3,6,false,"\u{d}\\"),
("'\u{d}\u{a}",true,"",5,3,6,false,"\u{d}\u{a}"),
("'\u{d}\u{d}",true,"",5,3,6,false,"\u{d}\u{d}"),
("'\u{d}\u{c}",true,"",5,3,6,false,"\u{d}\u{c}"),
("'\u{d}\u{0}",true,"",5,3,6,false,"\u{d}\u{0}"),
("'\u{d}é",true,"",5,3,6,false,"\u{d}é"),
("'\u{d}𐀀",true,"",5,3,6,false,"\u{d}𐀀"),
("'\u{c}a",true,"",5,3,6,false,"\u{c}a"),
("'\u{c}\"",true,"",5,3,6,false,"\u{c}\""),
("'\u{c}'",true,"",5,3,6,false,"\u{c}'"),
("'\u{c}\\",true,"",5,3,6,false,"\u{c}\\"),
("'\u{c}\u{a}",true,"",5,3,6,false,"\u{c}\u{a}"),
("'\u{c}\u{d}",true,"",5,3,6,false,"\u{c}\u{d}"),
("'\u{c}\u{c}",true,"",5,3,6,false,"\u{c}\u{c}"),
("'\u{c}\u{0}",true,"",5,3,6,false,"\u{c}\u{0}"),
("'\u{c}é",true,"",5,3,6,false,"\u{c}é"),
("'\u{c}𐀀",true,"",5,3,6,false,"\u{c}𐀀"),
("'\u{0}a",false,"�a",7,3,8,true,""),
("'\u{0}\"",false,"�\"",7,3,8,true,""),
("'\u{0}'",false,"�",7,3,8,true,""),
("'\u{0}\\",false,"�",7,3,8,true,""),
("'\u{0}\u{a}",true,"�",6,3,7,true,"\u{a}"),
("'\u{0}\u{d}",true,"�",6,3,7,true,"\u{d}"),
("'\u{0}\u{c}",true,"�",6,3,7,true,"\u{c}"),
("'\u{0}\u{0}",false,"��",7,3,8,true,""),
("'\u{0}é",false,"�é",8,3,8,true,""),
("'\u{0}𐀀",false,"�𐀀",10,3,9,true,""),
("'éa",false,"éa",8,3,8,false,""),
("'é\"",false,"é\"",8,3,8,false,""),
("'é'",false,"é",8,3,8,false,""),
("'é\\",false,"é",8,3,8,true,""),
("'é\u{a}",true,"é",7,3,7,false,"\u{a}"),
("'é\u{d}",true,"é",7,3,7,false,"\u{d}"),
("'é\u{c}",true,"é",7,3,7,false,"\u{c}"),
("'é\u{0}",false,"é�",8,3,8,true,""),
("'éé",false,"éé",9,3,8,false,""),
("'é𐀀",false,"é𐀀",11,3,9,false,""),
("'𐀀a",false,"𐀀a",10,3,9,false,""),
("'𐀀\"",false,"𐀀\"",10,3,9,false,""),
("'𐀀'",false,"𐀀",10,3,9,false,""),
("'𐀀\\",false,"𐀀",10,3,9,true,""),
("'𐀀\u{a}",true,"𐀀",9,3,8,false,"\u{a}"),
("'𐀀\u{d}",true,"𐀀",9,3,8,false,"\u{d}"),
("'𐀀\u{c}",true,"𐀀",9,3,8,false,"\u{c}"),
("'𐀀\u{0}",false,"𐀀�",10,3,9,true,""),
("'𐀀é",false,"𐀀é",11,3,9,false,""),
("'𐀀𐀀",false,"𐀀𐀀",13,3,10,false,""),
("'abc",false,"abc",8,3,9,false,""),
("'abc';tail",false,"abc",9,3,10,false,";tail"),
("'a\\\u{a}b",false,"ab",9,4,2,true,""),
("'a\\\u{a}b';tail",false,"ab",10,4,3,true,";tail"),
("'a\\\u{d}\u{a}b",false,"ab",10,4,2,true,""),
("'a\\\u{d}\u{a}b';tail",false,"ab",11,4,3,true,";tail"),
("'\\0",false,"�",7,3,8,true,""),
("'\\0';tail",false,"�",8,3,9,true,";tail"),
("'\\000000",false,"�",12,3,13,true,""),
("'\\000000';tail",false,"�",13,3,14,true,";tail"),
("'\\D800",false,"�",10,3,11,true,""),
("'\\D800';tail",false,"�",11,3,12,true,";tail"),
("'\\10ffff",false,"􏿿",12,3,13,true,""),
("'\\10ffff';tail",false,"􏿿",13,3,14,true,";tail"),
("'\\110000",false,"�",12,3,13,true,""),
("'\\110000';tail",false,"�",13,3,14,true,";tail"),
("'\\61 b",false,"ab",10,3,11,true,""),
("'\\61 b';tail",false,"ab",11,3,12,true,";tail"),
("'\\000061b",false,"ab",13,3,14,true,""),
("'\\000061b';tail",false,"ab",14,3,15,true,";tail"),
("'\\61\u{d}\u{a}b",false,"ab",11,4,2,true,""),
("'\\61\u{d}\u{a}b';tail",false,"ab",12,4,3,true,";tail"),
("'é𐀀\\61 x",false,"é𐀀ax",16,3,14,true,""),
("'é𐀀\\61 x';tail",false,"é𐀀ax",17,3,15,true,";tail"),
("'x\u{0}y",false,"x�y",8,3,9,true,""),
("'x\u{0}y';tail",false,"x�y",9,3,10,true,";tail"),
("'\\𐀀x",false,"𐀀x",11,3,10,true,""),
("'\\𐀀x';tail",false,"𐀀x",12,3,11,true,";tail"),
("'/*# sourceURL=not-a-directive*/",false,"/*# sourceURL=not-a-directive*/",36,3,37,false,""),
("'/*# sourceURL=not-a-directive*/';tail",false,"/*# sourceURL=not-a-directive*/",37,3,38,false,";tail"),
("'\\\\';tail",false,"\\",8,3,9,true,";tail"),
("'\\\"';tail",false,"\"",8,3,9,true,";tail"),
("'\\'';tail",false,"'",8,3,9,true,";tail"),
("'a\u{a}; color:green",true,"a",6,3,7,false,"\u{a}; color:green"),
("'a\u{a}; color:green';tail",true,"a",6,3,7,false,"\u{a}; color:green';tail"),
("'\\'tail",false,"'tail",11,3,12,true,""),
("'\\\u{0}'tail",false,"�",8,3,9,true,"tail"),
("'\\\u{0}\u{a}",true,"�",7,3,8,true,"\u{a}"),
("'\\é'tail",false,"é",9,3,9,true,"tail"),
("'\\é\u{a}",true,"é",8,3,8,true,"\u{a}"),
("'\\𐀀'tail",false,"𐀀",11,3,10,true,"tail"),
("'\\𐀀\u{a}",true,"𐀀",10,3,9,true,"\u{a}"),
("'\\\u{a}'tail",false,"",8,4,2,true,"tail"),
("'\\\u{a}\u{a}",true,"",7,4,1,true,"\u{a}"),
("'\\\u{d}'tail",false,"",8,4,2,true,"tail"),
("'\\\u{d}\u{a}",false,"",8,4,1,true,""),
("'\\\u{d}\u{a}'tail",false,"",9,4,2,true,"tail"),
("'\\\u{d}\u{a}\u{a}",true,"",8,4,1,true,"\u{a}"),
("'\\\u{c}'tail",false,"",8,4,2,true,"tail"),
("'\\\u{c}\u{a}",true,"",7,4,1,true,"\u{a}"),
("'\\1",false,"\u{1}",7,3,8,true,""),
("'\\1'tail",false,"\u{1}",8,3,9,true,"tail"),
("'\\1\u{a}",false,"\u{1}",8,4,1,true,""),
("'\\f",false,"\u{f}",7,3,8,true,""),
("'\\f'tail",false,"\u{f}",8,3,9,true,"tail"),
("'\\f\u{a}",false,"\u{f}",8,4,1,true,""),
("'\\ff",false,"ÿ",8,3,9,true,""),
("'\\ff'tail",false,"ÿ",9,3,10,true,"tail"),
("'\\ff\u{a}",false,"ÿ",9,4,1,true,""),
("'\\fff",false,"࿿",9,3,10,true,""),
("'\\fff'tail",false,"࿿",10,3,11,true,"tail"),
("'\\fff\u{a}",false,"࿿",10,4,1,true,""),
("'\\ffff",false,"￿",10,3,11,true,""),
("'\\ffff'tail",false,"￿",11,3,12,true,"tail"),
("'\\ffff\u{a}",false,"￿",11,4,1,true,""),
("'\\10000",false,"𐀀",11,3,12,true,""),
("'\\10000'tail",false,"𐀀",12,3,13,true,"tail"),
("'\\10000\u{a}",false,"𐀀",12,4,1,true,""),
("'\\ffffff",false,"�",12,3,13,true,""),
("'\\ffffff'tail",false,"�",13,3,14,true,"tail"),
("'\\ffffff\u{a}",false,"�",13,4,1,true,""),
("'\\000061b'tail",false,"ab",14,3,15,true,"tail"),
("'\\000061b\u{a}",true,"ab",13,3,14,true,"\u{a}"),
("'\\61\u{d}\u{a}",false,"a",10,4,1,true,""),
("'\\61\u{d}\u{a}'tail",false,"a",11,4,2,true,"tail"),
("'\\61\u{d}\u{a}\u{a}",true,"a",10,4,1,true,"\u{a}"),
("'\\61\u{9}",false,"a",9,3,10,true,""),
("'\\61\u{9}'tail",false,"a",10,3,11,true,"tail"),
("'\\61\u{9}\u{a}",true,"a",9,3,10,true,"\u{a}"),
("'\\61\u{c}",false,"a",9,4,1,true,""),
("'\\61\u{c}'tail",false,"a",10,4,2,true,"tail"),
("'\\61\u{c}\u{a}",true,"a",9,4,1,true,"\u{a}"),
("'\\61  ",false,"a ",10,3,11,true,""),
("'\\61  'tail",false,"a ",11,3,12,true,"tail"),
("'\\61  \u{a}",true,"a ",10,3,11,true,"\u{a}"),
("'\\00000",false,"�",11,3,12,true,""),
("'\\00000'tail",false,"�",12,3,13,true,"tail"),
("'\\00000\u{a}",false,"�",12,4,1,true,""),
("'\\DFFF",false,"�",10,3,11,true,""),
("'\\DFFF'tail",false,"�",11,3,12,true,"tail"),
("'\\DFFF\u{a}",false,"�",11,4,1,true,""),
("'\\110000'tail",false,"�",13,3,14,true,"tail"),
("'\\110000\u{a}",false,"�",13,4,1,true,""),
("'é𐀀\\",false,"é𐀀",12,3,10,true,""),
("'é𐀀\\'tail",false,"é𐀀'tail",17,3,15,true,""),
("'é𐀀\\\u{a}",false,"é𐀀",13,4,1,true,""),
("'é𐀀\\\u{0}",false,"é𐀀�",13,3,11,true,""),
("'é𐀀\\\u{0}'tail",false,"é𐀀�",14,3,12,true,"tail"),
("'é𐀀\\\u{0}\u{a}",true,"é𐀀�",13,3,11,true,"\u{a}"),
("'é𐀀\\é",false,"é𐀀é",14,3,11,true,""),
("'é𐀀\\é'tail",false,"é𐀀é",15,3,12,true,"tail"),
("'é𐀀\\é\u{a}",true,"é𐀀é",14,3,11,true,"\u{a}"),
("'é𐀀\\𐀀",false,"é𐀀𐀀",16,3,12,true,""),
("'é𐀀\\𐀀'tail",false,"é𐀀𐀀",17,3,13,true,"tail"),
("'é𐀀\\𐀀\u{a}",true,"é𐀀𐀀",16,3,12,true,"\u{a}"),
("'é𐀀\\\u{a}'tail",false,"é𐀀",14,4,2,true,"tail"),
("'é𐀀\\\u{a}\u{a}",true,"é𐀀",13,4,1,true,"\u{a}"),
("'é𐀀\\\u{d}",false,"é𐀀",13,4,1,true,""),
("'é𐀀\\\u{d}'tail",false,"é𐀀",14,4,2,true,"tail"),
("'é𐀀\\\u{d}\u{a}",false,"é𐀀",14,4,1,true,""),
("'é𐀀\\\u{d}\u{a}'tail",false,"é𐀀",15,4,2,true,"tail"),
("'é𐀀\\\u{d}\u{a}\u{a}",true,"é𐀀",14,4,1,true,"\u{a}"),
("'é𐀀\\\u{c}",false,"é𐀀",13,4,1,true,""),
("'é𐀀\\\u{c}'tail",false,"é𐀀",14,4,2,true,"tail"),
("'é𐀀\\\u{c}\u{a}",true,"é𐀀",13,4,1,true,"\u{a}"),
("'é𐀀\\1",false,"é𐀀\u{1}",13,3,11,true,""),
("'é𐀀\\1'tail",false,"é𐀀\u{1}",14,3,12,true,"tail"),
("'é𐀀\\1\u{a}",false,"é𐀀\u{1}",14,4,1,true,""),
("'é𐀀\\f",false,"é𐀀\u{f}",13,3,11,true,""),
("'é𐀀\\f'tail",false,"é𐀀\u{f}",14,3,12,true,"tail"),
("'é𐀀\\f\u{a}",false,"é𐀀\u{f}",14,4,1,true,""),
("'é𐀀\\ff",false,"é𐀀ÿ",14,3,12,true,""),
("'é𐀀\\ff'tail",false,"é𐀀ÿ",15,3,13,true,"tail"),
("'é𐀀\\ff\u{a}",false,"é𐀀ÿ",15,4,1,true,""),
("'é𐀀\\fff",false,"é𐀀࿿",15,3,13,true,""),
("'é𐀀\\fff'tail",false,"é𐀀࿿",16,3,14,true,"tail"),
("'é𐀀\\fff\u{a}",false,"é𐀀࿿",16,4,1,true,""),
("'é𐀀\\ffff",false,"é𐀀￿",16,3,14,true,""),
("'é𐀀\\ffff'tail",false,"é𐀀￿",17,3,15,true,"tail"),
("'é𐀀\\ffff\u{a}",false,"é𐀀￿",17,4,1,true,""),
("'é𐀀\\10000",false,"é𐀀𐀀",17,3,15,true,""),
("'é𐀀\\10000'tail",false,"é𐀀𐀀",18,3,16,true,"tail"),
("'é𐀀\\10000\u{a}",false,"é𐀀𐀀",18,4,1,true,""),
("'é𐀀\\ffffff",false,"é𐀀�",18,3,16,true,""),
("'é𐀀\\ffffff'tail",false,"é𐀀�",19,3,17,true,"tail"),
("'é𐀀\\ffffff\u{a}",false,"é𐀀�",19,4,1,true,""),
("'é𐀀\\000061b",false,"é𐀀ab",19,3,17,true,""),
("'é𐀀\\000061b'tail",false,"é𐀀ab",20,3,18,true,"tail"),
("'é𐀀\\000061b\u{a}",true,"é𐀀ab",19,3,17,true,"\u{a}"),
("'é𐀀\\61\u{d}\u{a}",false,"é𐀀a",16,4,1,true,""),
("'é𐀀\\61\u{d}\u{a}'tail",false,"é𐀀a",17,4,2,true,"tail"),
("'é𐀀\\61\u{d}\u{a}\u{a}",true,"é𐀀a",16,4,1,true,"\u{a}"),
("'é𐀀\\61\u{9}",false,"é𐀀a",15,3,13,true,""),
("'é𐀀\\61\u{9}'tail",false,"é𐀀a",16,3,14,true,"tail"),
("'é𐀀\\61\u{9}\u{a}",true,"é𐀀a",15,3,13,true,"\u{a}"),
("'é𐀀\\61\u{c}",false,"é𐀀a",15,4,1,true,""),
("'é𐀀\\61\u{c}'tail",false,"é𐀀a",16,4,2,true,"tail"),
("'é𐀀\\61\u{c}\u{a}",true,"é𐀀a",15,4,1,true,"\u{a}"),
("'é𐀀\\61  ",false,"é𐀀a ",16,3,14,true,""),
("'é𐀀\\61  'tail",false,"é𐀀a ",17,3,15,true,"tail"),
("'é𐀀\\61  \u{a}",true,"é𐀀a ",16,3,14,true,"\u{a}"),
("'é𐀀\\00000",false,"é𐀀�",17,3,15,true,""),
("'é𐀀\\00000'tail",false,"é𐀀�",18,3,16,true,"tail"),
("'é𐀀\\00000\u{a}",false,"é𐀀�",18,4,1,true,""),
("'é𐀀\\DFFF",false,"é𐀀�",16,3,14,true,""),
("'é𐀀\\DFFF'tail",false,"é𐀀�",17,3,15,true,"tail"),
("'é𐀀\\DFFF\u{a}",false,"é𐀀�",17,4,1,true,""),
("'é𐀀\\110000",false,"é𐀀�",18,3,16,true,""),
("'é𐀀\\110000'tail",false,"é𐀀�",19,3,17,true,"tail"),
("'é𐀀\\110000\u{a}",false,"é𐀀�",19,4,1,true,""),
("'\u{0}\\'tail",false,"�'tail",12,3,13,true,""),
("'\u{0}\\\u{a}",false,"�",8,4,1,true,""),
("'\u{0}\\\u{0}",false,"��",8,3,9,true,""),
("'\u{0}\\\u{0}'tail",false,"��",9,3,10,true,"tail"),
("'\u{0}\\\u{0}\u{a}",true,"��",8,3,9,true,"\u{a}"),
("'\u{0}\\é",false,"�é",9,3,9,true,""),
("'\u{0}\\é'tail",false,"�é",10,3,10,true,"tail"),
("'\u{0}\\é\u{a}",true,"�é",9,3,9,true,"\u{a}"),
("'\u{0}\\𐀀",false,"�𐀀",11,3,10,true,""),
("'\u{0}\\𐀀'tail",false,"�𐀀",12,3,11,true,"tail"),
("'\u{0}\\𐀀\u{a}",true,"�𐀀",11,3,10,true,"\u{a}"),
("'\u{0}\\\u{a}'tail",false,"�",9,4,2,true,"tail"),
("'\u{0}\\\u{a}\u{a}",true,"�",8,4,1,true,"\u{a}"),
("'\u{0}\\\u{d}",false,"�",8,4,1,true,""),
("'\u{0}\\\u{d}'tail",false,"�",9,4,2,true,"tail"),
("'\u{0}\\\u{d}\u{a}",false,"�",9,4,1,true,""),
("'\u{0}\\\u{d}\u{a}'tail",false,"�",10,4,2,true,"tail"),
("'\u{0}\\\u{d}\u{a}\u{a}",true,"�",9,4,1,true,"\u{a}"),
("'\u{0}\\\u{c}",false,"�",8,4,1,true,""),
("'\u{0}\\\u{c}'tail",false,"�",9,4,2,true,"tail"),
("'\u{0}\\\u{c}\u{a}",true,"�",8,4,1,true,"\u{a}"),
("'\u{0}\\1",false,"�\u{1}",8,3,9,true,""),
("'\u{0}\\1'tail",false,"�\u{1}",9,3,10,true,"tail"),
("'\u{0}\\1\u{a}",false,"�\u{1}",9,4,1,true,""),
("'\u{0}\\f",false,"�\u{f}",8,3,9,true,""),
("'\u{0}\\f'tail",false,"�\u{f}",9,3,10,true,"tail"),
("'\u{0}\\f\u{a}",false,"�\u{f}",9,4,1,true,""),
("'\u{0}\\ff",false,"�ÿ",9,3,10,true,""),
("'\u{0}\\ff'tail",false,"�ÿ",10,3,11,true,"tail"),
("'\u{0}\\ff\u{a}",false,"�ÿ",10,4,1,true,""),
("'\u{0}\\fff",false,"�࿿",10,3,11,true,""),
("'\u{0}\\fff'tail",false,"�࿿",11,3,12,true,"tail"),
("'\u{0}\\fff\u{a}",false,"�࿿",11,4,1,true,""),
("'\u{0}\\ffff",false,"�￿",11,3,12,true,""),
("'\u{0}\\ffff'tail",false,"�￿",12,3,13,true,"tail"),
("'\u{0}\\ffff\u{a}",false,"�￿",12,4,1,true,""),
("'\u{0}\\10000",false,"�𐀀",12,3,13,true,""),
("'\u{0}\\10000'tail",false,"�𐀀",13,3,14,true,"tail"),
("'\u{0}\\10000\u{a}",false,"�𐀀",13,4,1,true,""),
("'\u{0}\\ffffff",false,"��",13,3,14,true,""),
("'\u{0}\\ffffff'tail",false,"��",14,3,15,true,"tail"),
("'\u{0}\\ffffff\u{a}",false,"��",14,4,1,true,""),
("'\u{0}\\000061b",false,"�ab",14,3,15,true,""),
("'\u{0}\\000061b'tail",false,"�ab",15,3,16,true,"tail"),
("'\u{0}\\000061b\u{a}",true,"�ab",14,3,15,true,"\u{a}"),
("'\u{0}\\61\u{d}\u{a}",false,"�a",11,4,1,true,""),
("'\u{0}\\61\u{d}\u{a}'tail",false,"�a",12,4,2,true,"tail"),
("'\u{0}\\61\u{d}\u{a}\u{a}",true,"�a",11,4,1,true,"\u{a}"),
("'\u{0}\\61\u{9}",false,"�a",10,3,11,true,""),
("'\u{0}\\61\u{9}'tail",false,"�a",11,3,12,true,"tail"),
("'\u{0}\\61\u{9}\u{a}",true,"�a",10,3,11,true,"\u{a}"),
("'\u{0}\\61\u{c}",false,"�a",10,4,1,true,""),
("'\u{0}\\61\u{c}'tail",false,"�a",11,4,2,true,"tail"),
("'\u{0}\\61\u{c}\u{a}",true,"�a",10,4,1,true,"\u{a}"),
("'\u{0}\\61  ",false,"�a ",11,3,12,true,""),
("'\u{0}\\61  'tail",false,"�a ",12,3,13,true,"tail"),
("'\u{0}\\61  \u{a}",true,"�a ",11,3,12,true,"\u{a}"),
("'\u{0}\\00000",false,"��",12,3,13,true,""),
("'\u{0}\\00000'tail",false,"��",13,3,14,true,"tail"),
("'\u{0}\\00000\u{a}",false,"��",13,4,1,true,""),
("'\u{0}\\DFFF",false,"��",11,3,12,true,""),
("'\u{0}\\DFFF'tail",false,"��",12,3,13,true,"tail"),
("'\u{0}\\DFFF\u{a}",false,"��",12,4,1,true,""),
("'\u{0}\\110000",false,"��",13,3,14,true,""),
("'\u{0}\\110000'tail",false,"��",14,3,15,true,"tail"),
("'\u{0}\\110000\u{a}",false,"��",14,4,1,true,""),
("'\\61 \\",false,"a",10,3,11,true,""),
("'\\61 \\'tail",false,"a'tail",15,3,16,true,""),
("'\\61 \\\u{a}",false,"a",11,4,1,true,""),
("'\\61 \\\u{0}",false,"a�",11,3,12,true,""),
("'\\61 \\\u{0}'tail",false,"a�",12,3,13,true,"tail"),
("'\\61 \\\u{0}\u{a}",true,"a�",11,3,12,true,"\u{a}"),
("'\\61 \\é",false,"aé",12,3,12,true,""),
("'\\61 \\é'tail",false,"aé",13,3,13,true,"tail"),
("'\\61 \\é\u{a}",true,"aé",12,3,12,true,"\u{a}"),
("'\\61 \\𐀀",false,"a𐀀",14,3,13,true,""),
("'\\61 \\𐀀'tail",false,"a𐀀",15,3,14,true,"tail"),
("'\\61 \\𐀀\u{a}",true,"a𐀀",14,3,13,true,"\u{a}"),
("'\\61 \\\u{a}'tail",false,"a",12,4,2,true,"tail"),
("'\\61 \\\u{a}\u{a}",true,"a",11,4,1,true,"\u{a}"),
("'\\61 \\\u{d}",false,"a",11,4,1,true,""),
("'\\61 \\\u{d}'tail",false,"a",12,4,2,true,"tail"),
("'\\61 \\\u{d}\u{a}",false,"a",12,4,1,true,""),
("'\\61 \\\u{d}\u{a}'tail",false,"a",13,4,2,true,"tail"),
("'\\61 \\\u{d}\u{a}\u{a}",true,"a",12,4,1,true,"\u{a}"),
("'\\61 \\\u{c}",false,"a",11,4,1,true,""),
("'\\61 \\\u{c}'tail",false,"a",12,4,2,true,"tail"),
("'\\61 \\\u{c}\u{a}",true,"a",11,4,1,true,"\u{a}"),
("'\\61 \\1",false,"a\u{1}",11,3,12,true,""),
("'\\61 \\1'tail",false,"a\u{1}",12,3,13,true,"tail"),
("'\\61 \\1\u{a}",false,"a\u{1}",12,4,1,true,""),
("'\\61 \\f",false,"a\u{f}",11,3,12,true,""),
("'\\61 \\f'tail",false,"a\u{f}",12,3,13,true,"tail"),
("'\\61 \\f\u{a}",false,"a\u{f}",12,4,1,true,""),
("'\\61 \\ff",false,"aÿ",12,3,13,true,""),
("'\\61 \\ff'tail",false,"aÿ",13,3,14,true,"tail"),
("'\\61 \\ff\u{a}",false,"aÿ",13,4,1,true,""),
("'\\61 \\fff",false,"a࿿",13,3,14,true,""),
("'\\61 \\fff'tail",false,"a࿿",14,3,15,true,"tail"),
("'\\61 \\fff\u{a}",false,"a࿿",14,4,1,true,""),
("'\\61 \\ffff",false,"a￿",14,3,15,true,""),
("'\\61 \\ffff'tail",false,"a￿",15,3,16,true,"tail"),
("'\\61 \\ffff\u{a}",false,"a￿",15,4,1,true,""),
("'\\61 \\10000",false,"a𐀀",15,3,16,true,""),
("'\\61 \\10000'tail",false,"a𐀀",16,3,17,true,"tail"),
("'\\61 \\10000\u{a}",false,"a𐀀",16,4,1,true,""),
("'\\61 \\ffffff",false,"a�",16,3,17,true,""),
("'\\61 \\ffffff'tail",false,"a�",17,3,18,true,"tail"),
("'\\61 \\ffffff\u{a}",false,"a�",17,4,1,true,""),
("'\\61 \\000061b",false,"aab",17,3,18,true,""),
("'\\61 \\000061b'tail",false,"aab",18,3,19,true,"tail"),
("'\\61 \\000061b\u{a}",true,"aab",17,3,18,true,"\u{a}"),
("'\\61 \\61\u{d}\u{a}",false,"aa",14,4,1,true,""),
("'\\61 \\61\u{d}\u{a}'tail",false,"aa",15,4,2,true,"tail"),
("'\\61 \\61\u{d}\u{a}\u{a}",true,"aa",14,4,1,true,"\u{a}"),
("'\\61 \\61\u{9}",false,"aa",13,3,14,true,""),
("'\\61 \\61\u{9}'tail",false,"aa",14,3,15,true,"tail"),
("'\\61 \\61\u{9}\u{a}",true,"aa",13,3,14,true,"\u{a}"),
("'\\61 \\61\u{c}",false,"aa",13,4,1,true,""),
("'\\61 \\61\u{c}'tail",false,"aa",14,4,2,true,"tail"),
("'\\61 \\61\u{c}\u{a}",true,"aa",13,4,1,true,"\u{a}"),
("'\\61 \\61  ",false,"aa ",14,3,15,true,""),
("'\\61 \\61  'tail",false,"aa ",15,3,16,true,"tail"),
("'\\61 \\61  \u{a}",true,"aa ",14,3,15,true,"\u{a}"),
("'\\61 \\00000",false,"a�",15,3,16,true,""),
("'\\61 \\00000'tail",false,"a�",16,3,17,true,"tail"),
("'\\61 \\00000\u{a}",false,"a�",16,4,1,true,""),
("'\\61 \\DFFF",false,"a�",14,3,15,true,""),
("'\\61 \\DFFF'tail",false,"a�",15,3,16,true,"tail"),
("'\\61 \\DFFF\u{a}",false,"a�",15,4,1,true,""),
("'\\61 \\110000",false,"a�",16,3,17,true,""),
("'\\61 \\110000'tail",false,"a�",17,3,18,true,"tail"),
("'\\61 \\110000\u{a}",false,"a�",17,4,1,true,""),
 ];
for (id,(raw,bad,value,pos,line,column,allocated,remainder)) in cases.into_iter().enumerate(){
let storage=format!("seed{}",raw);let input=&*storage;
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let token=consume_string(&mut p,raw.starts_with('\''));
let v=match token{QuotedString(v)=>{assert!(!bad,"kind {id}");v},BadString(v)=>{assert!(bad,"kind {id}");v}};
assert_eq!(&*v,value,"payload {id}");
let cloned=v.clone();assert_eq!(&*cloned,value,"provider clone {id}");drop(cloned);
assert_eq!(cow_rc_str::is_shared(&v),allocated,"storage {id}");
if !allocated{assert_eq!(v.as_ptr() as usize-input.as_ptr() as usize,5,"borrowed slice {id}");}
assert!(std::str::from_utf8(v.as_bytes()).is_ok(),"output UTF8 {id}");
assert_eq!(p.state.position,pos,"position {id}");
assert_eq!(&input[pos..],remainder,"reconsume/suffix {id}");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(line,column),"location {id}");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URL observers {id}");
assert!(input.is_char_boundary(pos));
}
println!("PASS strings=808 payload_storage_raw_slice_endpoint_suffix_UTF8_location_URLs");
}
