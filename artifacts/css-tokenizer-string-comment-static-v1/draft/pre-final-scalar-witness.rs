#![allow(dead_code)]
use std::ops::Range;
type CowRcStr<'a> = std::borrow::Cow<'a,str>;
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
fn check_for_source_map<'a>(parser: &mut Parser<'a>, contents: &'a str) {
    let directive = "# sourceMappingURL=";
    let directive_old = "@ sourceMappingURL=";

    // If there is a source map directive, extract the URL.
    if contents.starts_with(directive) || contents.starts_with(directive_old) {
        let contents = &contents[directive.len()..];
        parser.source_map_url = contents.split([' ', '\t', '\x0C', '\r', '\n']).next();
    }

    let directive = "# sourceURL=";
    let directive_old = "@ sourceURL=";

    // If there is a source map directive, extract the URL.
    if contents.starts_with(directive) || contents.starts_with(directive_old) {
        let contents = &contents[directive.len()..];
        parser.source_url = contents.split([' ', '\t', '\x0C', '\r', '\n']).next()
    }
}
fn consume_comment<'a>(parser: &mut Parser<'a>) -> &'a str {
    parser.advance(2); // consume "/*"
    let start_position = parser.position();
    while !parser.is_eof() {
        match_byte! { parser.next_byte_unchecked(),
            b'*' => {
                let end_position = parser.position();
                parser.advance(1);
                if parser.next_byte() == Some(b'/') {
                    parser.advance(1);
                    let contents = parser.slice(start_position..end_position);
                    check_for_source_map(parser, contents);
                    return contents
                }
            }
            b'\n' | b'\x0C' | b'\r' => {
                parser.consume_newline();
            }
            b'\x80'..=b'\xBF' => { parser.consume_continuation_byte(); }
            b'\xF0'..=b'\xFF' => { parser.consume_4byte_intro(); }
            _ => {
                // ASCII or other leading byte.
                parser.advance(1);
            }
        }
    }
    let contents = parser.slice_from(start_position);
    check_for_source_map(parser, contents);
    contents
}
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
let cases:[(bool,&str,bool,&str,usize,u32,u32);646]=[
(true,"\"",false,"",1,0,2),
(true,"\"a",false,"a",2,0,3),
(true,"\"\"",false,"",2,0,3),
(true,"\"'",false,"'",2,0,3),
(true,"\"\\",false,"",2,0,3),
(true,"\"\u{a}",true,"",1,0,2),
(true,"\"\u{d}",true,"",1,0,2),
(true,"\"\u{c}",true,"",1,0,2),
(true,"\"\u{0}",false,"�",2,0,3),
(true,"\"é",false,"é",3,0,3),
(true,"\"😀",false,"😀",5,0,4),
(true,"\"aa",false,"aa",3,0,4),
(true,"\"a\"",false,"a",3,0,4),
(true,"\"a'",false,"a'",3,0,4),
(true,"\"a\\",false,"a",3,0,4),
(true,"\"a\u{a}",true,"a",2,0,3),
(true,"\"a\u{d}",true,"a",2,0,3),
(true,"\"a\u{c}",true,"a",2,0,3),
(true,"\"a\u{0}",false,"a�",3,0,4),
(true,"\"aé",false,"aé",4,0,4),
(true,"\"a😀",false,"a😀",6,0,5),
(true,"\"\"a",false,"",2,0,3),
(true,"\"\"\"",false,"",2,0,3),
(true,"\"\"'",false,"",2,0,3),
(true,"\"\"\\",false,"",2,0,3),
(true,"\"\"\u{a}",false,"",2,0,3),
(true,"\"\"\u{d}",false,"",2,0,3),
(true,"\"\"\u{c}",false,"",2,0,3),
(true,"\"\"\u{0}",false,"",2,0,3),
(true,"\"\"é",false,"",2,0,3),
(true,"\"\"😀",false,"",2,0,3),
(true,"\"'a",false,"'a",3,0,4),
(true,"\"'\"",false,"'",3,0,4),
(true,"\"''",false,"''",3,0,4),
(true,"\"'\\",false,"'",3,0,4),
(true,"\"'\u{a}",true,"'",2,0,3),
(true,"\"'\u{d}",true,"'",2,0,3),
(true,"\"'\u{c}",true,"'",2,0,3),
(true,"\"'\u{0}",false,"'�",3,0,4),
(true,"\"'é",false,"'é",4,0,4),
(true,"\"'😀",false,"'😀",6,0,5),
(true,"\"\\a",false,"\u{a}",3,0,4),
(true,"\"\\\"",false,"\"",3,0,4),
(true,"\"\\'",false,"'",3,0,4),
(true,"\"\\\\",false,"\\",3,0,4),
(true,"\"\\\u{a}",false,"",3,1,1),
(true,"\"\\\u{d}",false,"",3,1,1),
(true,"\"\\\u{c}",false,"",3,1,1),
(true,"\"\\\u{0}",false,"�",3,0,4),
(true,"\"\\é",false,"é",4,0,4),
(true,"\"\\😀",false,"😀",6,0,5),
(true,"\"\u{a}a",true,"",1,0,2),
(true,"\"\u{a}\"",true,"",1,0,2),
(true,"\"\u{a}'",true,"",1,0,2),
(true,"\"\u{a}\\",true,"",1,0,2),
(true,"\"\u{a}\u{a}",true,"",1,0,2),
(true,"\"\u{a}\u{d}",true,"",1,0,2),
(true,"\"\u{a}\u{c}",true,"",1,0,2),
(true,"\"\u{a}\u{0}",true,"",1,0,2),
(true,"\"\u{a}é",true,"",1,0,2),
(true,"\"\u{a}😀",true,"",1,0,2),
(true,"\"\u{d}a",true,"",1,0,2),
(true,"\"\u{d}\"",true,"",1,0,2),
(true,"\"\u{d}'",true,"",1,0,2),
(true,"\"\u{d}\\",true,"",1,0,2),
(true,"\"\u{d}\u{a}",true,"",1,0,2),
(true,"\"\u{d}\u{d}",true,"",1,0,2),
(true,"\"\u{d}\u{c}",true,"",1,0,2),
(true,"\"\u{d}\u{0}",true,"",1,0,2),
(true,"\"\u{d}é",true,"",1,0,2),
(true,"\"\u{d}😀",true,"",1,0,2),
(true,"\"\u{c}a",true,"",1,0,2),
(true,"\"\u{c}\"",true,"",1,0,2),
(true,"\"\u{c}'",true,"",1,0,2),
(true,"\"\u{c}\\",true,"",1,0,2),
(true,"\"\u{c}\u{a}",true,"",1,0,2),
(true,"\"\u{c}\u{d}",true,"",1,0,2),
(true,"\"\u{c}\u{c}",true,"",1,0,2),
(true,"\"\u{c}\u{0}",true,"",1,0,2),
(true,"\"\u{c}é",true,"",1,0,2),
(true,"\"\u{c}😀",true,"",1,0,2),
(true,"\"\u{0}a",false,"�a",3,0,4),
(true,"\"\u{0}\"",false,"�",3,0,4),
(true,"\"\u{0}'",false,"�'",3,0,4),
(true,"\"\u{0}\\",false,"�",3,0,4),
(true,"\"\u{0}\u{a}",true,"�",2,0,3),
(true,"\"\u{0}\u{d}",true,"�",2,0,3),
(true,"\"\u{0}\u{c}",true,"�",2,0,3),
(true,"\"\u{0}\u{0}",false,"��",3,0,4),
(true,"\"\u{0}é",false,"�é",4,0,4),
(true,"\"\u{0}😀",false,"�😀",6,0,5),
(true,"\"éa",false,"éa",4,0,4),
(true,"\"é\"",false,"é",4,0,4),
(true,"\"é'",false,"é'",4,0,4),
(true,"\"é\\",false,"é",4,0,4),
(true,"\"é\u{a}",true,"é",3,0,3),
(true,"\"é\u{d}",true,"é",3,0,3),
(true,"\"é\u{c}",true,"é",3,0,3),
(true,"\"é\u{0}",false,"é�",4,0,4),
(true,"\"éé",false,"éé",5,0,4),
(true,"\"é😀",false,"é😀",7,0,5),
(true,"\"😀a",false,"😀a",6,0,5),
(true,"\"😀\"",false,"😀",6,0,5),
(true,"\"😀'",false,"😀'",6,0,5),
(true,"\"😀\\",false,"😀",6,0,5),
(true,"\"😀\u{a}",true,"😀",5,0,4),
(true,"\"😀\u{d}",true,"😀",5,0,4),
(true,"\"😀\u{c}",true,"😀",5,0,4),
(true,"\"😀\u{0}",false,"😀�",6,0,5),
(true,"\"😀é",false,"😀é",7,0,5),
(true,"\"😀😀",false,"😀😀",9,0,6),
(true,"\"abc",false,"abc",4,0,5),
(true,"\"abc\";tail",false,"abc",5,0,6),
(true,"\"a\\\u{a}b",false,"ab",5,1,2),
(true,"\"a\\\u{a}b\";tail",false,"ab",6,1,3),
(true,"\"a\\\u{d}\u{a}b",false,"ab",6,1,2),
(true,"\"a\\\u{d}\u{a}b\";tail",false,"ab",7,1,3),
(true,"\"\\0",false,"�",3,0,4),
(true,"\"\\0\";tail",false,"�",4,0,5),
(true,"\"\\000000",false,"�",8,0,9),
(true,"\"\\000000\";tail",false,"�",9,0,10),
(true,"\"\\D800",false,"�",6,0,7),
(true,"\"\\D800\";tail",false,"�",7,0,8),
(true,"\"\\10ffff",false,"􏿿",8,0,9),
(true,"\"\\10ffff\";tail",false,"􏿿",9,0,10),
(true,"\"\\110000",false,"�",8,0,9),
(true,"\"\\110000\";tail",false,"�",9,0,10),
(true,"\"\\61 b",false,"ab",6,0,7),
(true,"\"\\61 b\";tail",false,"ab",7,0,8),
(true,"\"\\000061b",false,"ab",9,0,10),
(true,"\"\\000061b\";tail",false,"ab",10,0,11),
(true,"\"\\61\u{d}\u{a}b",false,"ab",7,1,2),
(true,"\"\\61\u{d}\u{a}b\";tail",false,"ab",8,1,3),
(true,"\"é😀\\61 x",false,"é😀ax",12,0,10),
(true,"\"é😀\\61 x\";tail",false,"é😀ax",13,0,11),
(true,"\"x\u{0}y",false,"x�y",4,0,5),
(true,"\"x\u{0}y\";tail",false,"x�y",5,0,6),
(true,"\"\\😀x",false,"😀x",7,0,6),
(true,"\"\\😀x\";tail",false,"😀x",8,0,7),
(true,"\"/*not a comment*/",false,"/*not a comment*/",18,0,19),
(true,"\"/*not a comment*/\";tail",false,"/*not a comment*/",19,0,20),
(true,"\"\\\\",false,"\\",3,0,4),
(true,"\"\\\\\";tail",false,"\\",4,0,5),
(true,"\"\\\"",false,"\"",3,0,4),
(true,"\"\\\"\";tail",false,"\"",4,0,5),
(true,"\"\\'",false,"'",3,0,4),
(true,"\"\\'\";tail",false,"'",4,0,5),
(true,"\"a\u{a}; color:green",true,"a",2,0,3),
(true,"\"a\u{a}; color:green\";tail",true,"a",2,0,3),
(true,"'",false,"",1,0,2),
(true,"'a",false,"a",2,0,3),
(true,"'\"",false,"\"",2,0,3),
(true,"''",false,"",2,0,3),
(true,"'\\",false,"",2,0,3),
(true,"'\u{a}",true,"",1,0,2),
(true,"'\u{d}",true,"",1,0,2),
(true,"'\u{c}",true,"",1,0,2),
(true,"'\u{0}",false,"�",2,0,3),
(true,"'é",false,"é",3,0,3),
(true,"'😀",false,"😀",5,0,4),
(true,"'aa",false,"aa",3,0,4),
(true,"'a\"",false,"a\"",3,0,4),
(true,"'a'",false,"a",3,0,4),
(true,"'a\\",false,"a",3,0,4),
(true,"'a\u{a}",true,"a",2,0,3),
(true,"'a\u{d}",true,"a",2,0,3),
(true,"'a\u{c}",true,"a",2,0,3),
(true,"'a\u{0}",false,"a�",3,0,4),
(true,"'aé",false,"aé",4,0,4),
(true,"'a😀",false,"a😀",6,0,5),
(true,"'\"a",false,"\"a",3,0,4),
(true,"'\"\"",false,"\"\"",3,0,4),
(true,"'\"'",false,"\"",3,0,4),
(true,"'\"\\",false,"\"",3,0,4),
(true,"'\"\u{a}",true,"\"",2,0,3),
(true,"'\"\u{d}",true,"\"",2,0,3),
(true,"'\"\u{c}",true,"\"",2,0,3),
(true,"'\"\u{0}",false,"\"�",3,0,4),
(true,"'\"é",false,"\"é",4,0,4),
(true,"'\"😀",false,"\"😀",6,0,5),
(true,"''a",false,"",2,0,3),
(true,"''\"",false,"",2,0,3),
(true,"'''",false,"",2,0,3),
(true,"''\\",false,"",2,0,3),
(true,"''\u{a}",false,"",2,0,3),
(true,"''\u{d}",false,"",2,0,3),
(true,"''\u{c}",false,"",2,0,3),
(true,"''\u{0}",false,"",2,0,3),
(true,"''é",false,"",2,0,3),
(true,"''😀",false,"",2,0,3),
(true,"'\\a",false,"\u{a}",3,0,4),
(true,"'\\\"",false,"\"",3,0,4),
(true,"'\\'",false,"'",3,0,4),
(true,"'\\\\",false,"\\",3,0,4),
(true,"'\\\u{a}",false,"",3,1,1),
(true,"'\\\u{d}",false,"",3,1,1),
(true,"'\\\u{c}",false,"",3,1,1),
(true,"'\\\u{0}",false,"�",3,0,4),
(true,"'\\é",false,"é",4,0,4),
(true,"'\\😀",false,"😀",6,0,5),
(true,"'\u{a}a",true,"",1,0,2),
(true,"'\u{a}\"",true,"",1,0,2),
(true,"'\u{a}'",true,"",1,0,2),
(true,"'\u{a}\\",true,"",1,0,2),
(true,"'\u{a}\u{a}",true,"",1,0,2),
(true,"'\u{a}\u{d}",true,"",1,0,2),
(true,"'\u{a}\u{c}",true,"",1,0,2),
(true,"'\u{a}\u{0}",true,"",1,0,2),
(true,"'\u{a}é",true,"",1,0,2),
(true,"'\u{a}😀",true,"",1,0,2),
(true,"'\u{d}a",true,"",1,0,2),
(true,"'\u{d}\"",true,"",1,0,2),
(true,"'\u{d}'",true,"",1,0,2),
(true,"'\u{d}\\",true,"",1,0,2),
(true,"'\u{d}\u{a}",true,"",1,0,2),
(true,"'\u{d}\u{d}",true,"",1,0,2),
(true,"'\u{d}\u{c}",true,"",1,0,2),
(true,"'\u{d}\u{0}",true,"",1,0,2),
(true,"'\u{d}é",true,"",1,0,2),
(true,"'\u{d}😀",true,"",1,0,2),
(true,"'\u{c}a",true,"",1,0,2),
(true,"'\u{c}\"",true,"",1,0,2),
(true,"'\u{c}'",true,"",1,0,2),
(true,"'\u{c}\\",true,"",1,0,2),
(true,"'\u{c}\u{a}",true,"",1,0,2),
(true,"'\u{c}\u{d}",true,"",1,0,2),
(true,"'\u{c}\u{c}",true,"",1,0,2),
(true,"'\u{c}\u{0}",true,"",1,0,2),
(true,"'\u{c}é",true,"",1,0,2),
(true,"'\u{c}😀",true,"",1,0,2),
(true,"'\u{0}a",false,"�a",3,0,4),
(true,"'\u{0}\"",false,"�\"",3,0,4),
(true,"'\u{0}'",false,"�",3,0,4),
(true,"'\u{0}\\",false,"�",3,0,4),
(true,"'\u{0}\u{a}",true,"�",2,0,3),
(true,"'\u{0}\u{d}",true,"�",2,0,3),
(true,"'\u{0}\u{c}",true,"�",2,0,3),
(true,"'\u{0}\u{0}",false,"��",3,0,4),
(true,"'\u{0}é",false,"�é",4,0,4),
(true,"'\u{0}😀",false,"�😀",6,0,5),
(true,"'éa",false,"éa",4,0,4),
(true,"'é\"",false,"é\"",4,0,4),
(true,"'é'",false,"é",4,0,4),
(true,"'é\\",false,"é",4,0,4),
(true,"'é\u{a}",true,"é",3,0,3),
(true,"'é\u{d}",true,"é",3,0,3),
(true,"'é\u{c}",true,"é",3,0,3),
(true,"'é\u{0}",false,"é�",4,0,4),
(true,"'éé",false,"éé",5,0,4),
(true,"'é😀",false,"é😀",7,0,5),
(true,"'😀a",false,"😀a",6,0,5),
(true,"'😀\"",false,"😀\"",6,0,5),
(true,"'😀'",false,"😀",6,0,5),
(true,"'😀\\",false,"😀",6,0,5),
(true,"'😀\u{a}",true,"😀",5,0,4),
(true,"'😀\u{d}",true,"😀",5,0,4),
(true,"'😀\u{c}",true,"😀",5,0,4),
(true,"'😀\u{0}",false,"😀�",6,0,5),
(true,"'😀é",false,"😀é",7,0,5),
(true,"'😀😀",false,"😀😀",9,0,6),
(true,"'abc",false,"abc",4,0,5),
(true,"'abc';tail",false,"abc",5,0,6),
(true,"'a\\\u{a}b",false,"ab",5,1,2),
(true,"'a\\\u{a}b';tail",false,"ab",6,1,3),
(true,"'a\\\u{d}\u{a}b",false,"ab",6,1,2),
(true,"'a\\\u{d}\u{a}b';tail",false,"ab",7,1,3),
(true,"'\\0",false,"�",3,0,4),
(true,"'\\0';tail",false,"�",4,0,5),
(true,"'\\000000",false,"�",8,0,9),
(true,"'\\000000';tail",false,"�",9,0,10),
(true,"'\\D800",false,"�",6,0,7),
(true,"'\\D800';tail",false,"�",7,0,8),
(true,"'\\10ffff",false,"􏿿",8,0,9),
(true,"'\\10ffff';tail",false,"􏿿",9,0,10),
(true,"'\\110000",false,"�",8,0,9),
(true,"'\\110000';tail",false,"�",9,0,10),
(true,"'\\61 b",false,"ab",6,0,7),
(true,"'\\61 b';tail",false,"ab",7,0,8),
(true,"'\\000061b",false,"ab",9,0,10),
(true,"'\\000061b';tail",false,"ab",10,0,11),
(true,"'\\61\u{d}\u{a}b",false,"ab",7,1,2),
(true,"'\\61\u{d}\u{a}b';tail",false,"ab",8,1,3),
(true,"'é😀\\61 x",false,"é😀ax",12,0,10),
(true,"'é😀\\61 x';tail",false,"é😀ax",13,0,11),
(true,"'x\u{0}y",false,"x�y",4,0,5),
(true,"'x\u{0}y';tail",false,"x�y",5,0,6),
(true,"'\\😀x",false,"😀x",7,0,6),
(true,"'\\😀x';tail",false,"😀x",8,0,7),
(true,"'/*not a comment*/",false,"/*not a comment*/",18,0,19),
(true,"'/*not a comment*/';tail",false,"/*not a comment*/",19,0,20),
(true,"'\\\\",false,"\\",3,0,4),
(true,"'\\\\';tail",false,"\\",4,0,5),
(true,"'\\\"",false,"\"",3,0,4),
(true,"'\\\"';tail",false,"\"",4,0,5),
(true,"'\\'",false,"'",3,0,4),
(true,"'\\'';tail",false,"'",4,0,5),
(true,"'a\u{a}; color:green",true,"a",2,0,3),
(true,"'a\u{a}; color:green';tail",true,"a",2,0,3),
(false,"/*",false,"",2,0,3),
(false,"/**",false,"*",3,0,4),
(false,"/*/",false,"/",3,0,4),
(false,"/*a",false,"a",3,0,4),
(false,"/*\u{a}",false,"\u{a}",3,1,1),
(false,"/***",false,"**",4,0,5),
(false,"/**/",false,"",4,0,5),
(false,"/**a",false,"*a",4,0,5),
(false,"/**\u{a}",false,"*\u{a}",4,1,1),
(false,"/*/*",false,"/*",4,0,5),
(false,"/*//",false,"//",4,0,5),
(false,"/*/a",false,"/a",4,0,5),
(false,"/*/\u{a}",false,"/\u{a}",4,1,1),
(false,"/*a*",false,"a*",4,0,5),
(false,"/*a/",false,"a/",4,0,5),
(false,"/*aa",false,"aa",4,0,5),
(false,"/*a\u{a}",false,"a\u{a}",4,1,1),
(false,"/*\u{a}*",false,"\u{a}*",4,1,2),
(false,"/*\u{a}/",false,"\u{a}/",4,1,2),
(false,"/*\u{a}a",false,"\u{a}a",4,1,2),
(false,"/*\u{a}\u{a}",false,"\u{a}\u{a}",4,2,1),
(false,"/****",false,"***",5,0,6),
(false,"/***/",false,"*",5,0,6),
(false,"/***a",false,"**a",5,0,6),
(false,"/***\u{a}",false,"**\u{a}",5,1,1),
(false,"/**/*",false,"",4,0,5),
(false,"/**//",false,"",4,0,5),
(false,"/**/a",false,"",4,0,5),
(false,"/**/\u{a}",false,"",4,0,5),
(false,"/**a*",false,"*a*",5,0,6),
(false,"/**a/",false,"*a/",5,0,6),
(false,"/**aa",false,"*aa",5,0,6),
(false,"/**a\u{a}",false,"*a\u{a}",5,1,1),
(false,"/**\u{a}*",false,"*\u{a}*",5,1,2),
(false,"/**\u{a}/",false,"*\u{a}/",5,1,2),
(false,"/**\u{a}a",false,"*\u{a}a",5,1,2),
(false,"/**\u{a}\u{a}",false,"*\u{a}\u{a}",5,2,1),
(false,"/*/**",false,"/**",5,0,6),
(false,"/*/*/",false,"/",5,0,6),
(false,"/*/*a",false,"/*a",5,0,6),
(false,"/*/*\u{a}",false,"/*\u{a}",5,1,1),
(false,"/*//*",false,"//*",5,0,6),
(false,"/*///",false,"///",5,0,6),
(false,"/*//a",false,"//a",5,0,6),
(false,"/*//\u{a}",false,"//\u{a}",5,1,1),
(false,"/*/a*",false,"/a*",5,0,6),
(false,"/*/a/",false,"/a/",5,0,6),
(false,"/*/aa",false,"/aa",5,0,6),
(false,"/*/a\u{a}",false,"/a\u{a}",5,1,1),
(false,"/*/\u{a}*",false,"/\u{a}*",5,1,2),
(false,"/*/\u{a}/",false,"/\u{a}/",5,1,2),
(false,"/*/\u{a}a",false,"/\u{a}a",5,1,2),
(false,"/*/\u{a}\u{a}",false,"/\u{a}\u{a}",5,2,1),
(false,"/*a**",false,"a**",5,0,6),
(false,"/*a*/",false,"a",5,0,6),
(false,"/*a*a",false,"a*a",5,0,6),
(false,"/*a*\u{a}",false,"a*\u{a}",5,1,1),
(false,"/*a/*",false,"a/*",5,0,6),
(false,"/*a//",false,"a//",5,0,6),
(false,"/*a/a",false,"a/a",5,0,6),
(false,"/*a/\u{a}",false,"a/\u{a}",5,1,1),
(false,"/*aa*",false,"aa*",5,0,6),
(false,"/*aa/",false,"aa/",5,0,6),
(false,"/*aaa",false,"aaa",5,0,6),
(false,"/*aa\u{a}",false,"aa\u{a}",5,1,1),
(false,"/*a\u{a}*",false,"a\u{a}*",5,1,2),
(false,"/*a\u{a}/",false,"a\u{a}/",5,1,2),
(false,"/*a\u{a}a",false,"a\u{a}a",5,1,2),
(false,"/*a\u{a}\u{a}",false,"a\u{a}\u{a}",5,2,1),
(false,"/*\u{a}**",false,"\u{a}**",5,1,3),
(false,"/*\u{a}*/",false,"\u{a}",5,1,3),
(false,"/*\u{a}*a",false,"\u{a}*a",5,1,3),
(false,"/*\u{a}*\u{a}",false,"\u{a}*\u{a}",5,2,1),
(false,"/*\u{a}/*",false,"\u{a}/*",5,1,3),
(false,"/*\u{a}//",false,"\u{a}//",5,1,3),
(false,"/*\u{a}/a",false,"\u{a}/a",5,1,3),
(false,"/*\u{a}/\u{a}",false,"\u{a}/\u{a}",5,2,1),
(false,"/*\u{a}a*",false,"\u{a}a*",5,1,3),
(false,"/*\u{a}a/",false,"\u{a}a/",5,1,3),
(false,"/*\u{a}aa",false,"\u{a}aa",5,1,3),
(false,"/*\u{a}a\u{a}",false,"\u{a}a\u{a}",5,2,1),
(false,"/*\u{a}\u{a}*",false,"\u{a}\u{a}*",5,2,2),
(false,"/*\u{a}\u{a}/",false,"\u{a}\u{a}/",5,2,2),
(false,"/*\u{a}\u{a}a",false,"\u{a}\u{a}a",5,2,2),
(false,"/*\u{a}\u{a}\u{a}",false,"\u{a}\u{a}\u{a}",5,3,1),
(false,"/*****",false,"****",6,0,7),
(false,"/****/",false,"**",6,0,7),
(false,"/****a",false,"***a",6,0,7),
(false,"/****\u{a}",false,"***\u{a}",6,1,1),
(false,"/***/*",false,"*",5,0,6),
(false,"/***//",false,"*",5,0,6),
(false,"/***/a",false,"*",5,0,6),
(false,"/***/\u{a}",false,"*",5,0,6),
(false,"/***a*",false,"**a*",6,0,7),
(false,"/***a/",false,"**a/",6,0,7),
(false,"/***aa",false,"**aa",6,0,7),
(false,"/***a\u{a}",false,"**a\u{a}",6,1,1),
(false,"/***\u{a}*",false,"**\u{a}*",6,1,2),
(false,"/***\u{a}/",false,"**\u{a}/",6,1,2),
(false,"/***\u{a}a",false,"**\u{a}a",6,1,2),
(false,"/***\u{a}\u{a}",false,"**\u{a}\u{a}",6,2,1),
(false,"/**/**",false,"",4,0,5),
(false,"/**/*/",false,"",4,0,5),
(false,"/**/*a",false,"",4,0,5),
(false,"/**/*\u{a}",false,"",4,0,5),
(false,"/**//*",false,"",4,0,5),
(false,"/**///",false,"",4,0,5),
(false,"/**//a",false,"",4,0,5),
(false,"/**//\u{a}",false,"",4,0,5),
(false,"/**/a*",false,"",4,0,5),
(false,"/**/a/",false,"",4,0,5),
(false,"/**/aa",false,"",4,0,5),
(false,"/**/a\u{a}",false,"",4,0,5),
(false,"/**/\u{a}*",false,"",4,0,5),
(false,"/**/\u{a}/",false,"",4,0,5),
(false,"/**/\u{a}a",false,"",4,0,5),
(false,"/**/\u{a}\u{a}",false,"",4,0,5),
(false,"/**a**",false,"*a**",6,0,7),
(false,"/**a*/",false,"*a",6,0,7),
(false,"/**a*a",false,"*a*a",6,0,7),
(false,"/**a*\u{a}",false,"*a*\u{a}",6,1,1),
(false,"/**a/*",false,"*a/*",6,0,7),
(false,"/**a//",false,"*a//",6,0,7),
(false,"/**a/a",false,"*a/a",6,0,7),
(false,"/**a/\u{a}",false,"*a/\u{a}",6,1,1),
(false,"/**aa*",false,"*aa*",6,0,7),
(false,"/**aa/",false,"*aa/",6,0,7),
(false,"/**aaa",false,"*aaa",6,0,7),
(false,"/**aa\u{a}",false,"*aa\u{a}",6,1,1),
(false,"/**a\u{a}*",false,"*a\u{a}*",6,1,2),
(false,"/**a\u{a}/",false,"*a\u{a}/",6,1,2),
(false,"/**a\u{a}a",false,"*a\u{a}a",6,1,2),
(false,"/**a\u{a}\u{a}",false,"*a\u{a}\u{a}",6,2,1),
(false,"/**\u{a}**",false,"*\u{a}**",6,1,3),
(false,"/**\u{a}*/",false,"*\u{a}",6,1,3),
(false,"/**\u{a}*a",false,"*\u{a}*a",6,1,3),
(false,"/**\u{a}*\u{a}",false,"*\u{a}*\u{a}",6,2,1),
(false,"/**\u{a}/*",false,"*\u{a}/*",6,1,3),
(false,"/**\u{a}//",false,"*\u{a}//",6,1,3),
(false,"/**\u{a}/a",false,"*\u{a}/a",6,1,3),
(false,"/**\u{a}/\u{a}",false,"*\u{a}/\u{a}",6,2,1),
(false,"/**\u{a}a*",false,"*\u{a}a*",6,1,3),
(false,"/**\u{a}a/",false,"*\u{a}a/",6,1,3),
(false,"/**\u{a}aa",false,"*\u{a}aa",6,1,3),
(false,"/**\u{a}a\u{a}",false,"*\u{a}a\u{a}",6,2,1),
(false,"/**\u{a}\u{a}*",false,"*\u{a}\u{a}*",6,2,2),
(false,"/**\u{a}\u{a}/",false,"*\u{a}\u{a}/",6,2,2),
(false,"/**\u{a}\u{a}a",false,"*\u{a}\u{a}a",6,2,2),
(false,"/**\u{a}\u{a}\u{a}",false,"*\u{a}\u{a}\u{a}",6,3,1),
(false,"/*/***",false,"/***",6,0,7),
(false,"/*/**/",false,"/*",6,0,7),
(false,"/*/**a",false,"/**a",6,0,7),
(false,"/*/**\u{a}",false,"/**\u{a}",6,1,1),
(false,"/*/*/*",false,"/",5,0,6),
(false,"/*/*//",false,"/",5,0,6),
(false,"/*/*/a",false,"/",5,0,6),
(false,"/*/*/\u{a}",false,"/",5,0,6),
(false,"/*/*a*",false,"/*a*",6,0,7),
(false,"/*/*a/",false,"/*a/",6,0,7),
(false,"/*/*aa",false,"/*aa",6,0,7),
(false,"/*/*a\u{a}",false,"/*a\u{a}",6,1,1),
(false,"/*/*\u{a}*",false,"/*\u{a}*",6,1,2),
(false,"/*/*\u{a}/",false,"/*\u{a}/",6,1,2),
(false,"/*/*\u{a}a",false,"/*\u{a}a",6,1,2),
(false,"/*/*\u{a}\u{a}",false,"/*\u{a}\u{a}",6,2,1),
(false,"/*//**",false,"//**",6,0,7),
(false,"/*//*/",false,"//",6,0,7),
(false,"/*//*a",false,"//*a",6,0,7),
(false,"/*//*\u{a}",false,"//*\u{a}",6,1,1),
(false,"/*///*",false,"///*",6,0,7),
(false,"/*////",false,"////",6,0,7),
(false,"/*///a",false,"///a",6,0,7),
(false,"/*///\u{a}",false,"///\u{a}",6,1,1),
(false,"/*//a*",false,"//a*",6,0,7),
(false,"/*//a/",false,"//a/",6,0,7),
(false,"/*//aa",false,"//aa",6,0,7),
(false,"/*//a\u{a}",false,"//a\u{a}",6,1,1),
(false,"/*//\u{a}*",false,"//\u{a}*",6,1,2),
(false,"/*//\u{a}/",false,"//\u{a}/",6,1,2),
(false,"/*//\u{a}a",false,"//\u{a}a",6,1,2),
(false,"/*//\u{a}\u{a}",false,"//\u{a}\u{a}",6,2,1),
(false,"/*/a**",false,"/a**",6,0,7),
(false,"/*/a*/",false,"/a",6,0,7),
(false,"/*/a*a",false,"/a*a",6,0,7),
(false,"/*/a*\u{a}",false,"/a*\u{a}",6,1,1),
(false,"/*/a/*",false,"/a/*",6,0,7),
(false,"/*/a//",false,"/a//",6,0,7),
(false,"/*/a/a",false,"/a/a",6,0,7),
(false,"/*/a/\u{a}",false,"/a/\u{a}",6,1,1),
(false,"/*/aa*",false,"/aa*",6,0,7),
(false,"/*/aa/",false,"/aa/",6,0,7),
(false,"/*/aaa",false,"/aaa",6,0,7),
(false,"/*/aa\u{a}",false,"/aa\u{a}",6,1,1),
(false,"/*/a\u{a}*",false,"/a\u{a}*",6,1,2),
(false,"/*/a\u{a}/",false,"/a\u{a}/",6,1,2),
(false,"/*/a\u{a}a",false,"/a\u{a}a",6,1,2),
(false,"/*/a\u{a}\u{a}",false,"/a\u{a}\u{a}",6,2,1),
(false,"/*/\u{a}**",false,"/\u{a}**",6,1,3),
(false,"/*/\u{a}*/",false,"/\u{a}",6,1,3),
(false,"/*/\u{a}*a",false,"/\u{a}*a",6,1,3),
(false,"/*/\u{a}*\u{a}",false,"/\u{a}*\u{a}",6,2,1),
(false,"/*/\u{a}/*",false,"/\u{a}/*",6,1,3),
(false,"/*/\u{a}//",false,"/\u{a}//",6,1,3),
(false,"/*/\u{a}/a",false,"/\u{a}/a",6,1,3),
(false,"/*/\u{a}/\u{a}",false,"/\u{a}/\u{a}",6,2,1),
(false,"/*/\u{a}a*",false,"/\u{a}a*",6,1,3),
(false,"/*/\u{a}a/",false,"/\u{a}a/",6,1,3),
(false,"/*/\u{a}aa",false,"/\u{a}aa",6,1,3),
(false,"/*/\u{a}a\u{a}",false,"/\u{a}a\u{a}",6,2,1),
(false,"/*/\u{a}\u{a}*",false,"/\u{a}\u{a}*",6,2,2),
(false,"/*/\u{a}\u{a}/",false,"/\u{a}\u{a}/",6,2,2),
(false,"/*/\u{a}\u{a}a",false,"/\u{a}\u{a}a",6,2,2),
(false,"/*/\u{a}\u{a}\u{a}",false,"/\u{a}\u{a}\u{a}",6,3,1),
(false,"/*a***",false,"a***",6,0,7),
(false,"/*a**/",false,"a*",6,0,7),
(false,"/*a**a",false,"a**a",6,0,7),
(false,"/*a**\u{a}",false,"a**\u{a}",6,1,1),
(false,"/*a*/*",false,"a",5,0,6),
(false,"/*a*//",false,"a",5,0,6),
(false,"/*a*/a",false,"a",5,0,6),
(false,"/*a*/\u{a}",false,"a",5,0,6),
(false,"/*a*a*",false,"a*a*",6,0,7),
(false,"/*a*a/",false,"a*a/",6,0,7),
(false,"/*a*aa",false,"a*aa",6,0,7),
(false,"/*a*a\u{a}",false,"a*a\u{a}",6,1,1),
(false,"/*a*\u{a}*",false,"a*\u{a}*",6,1,2),
(false,"/*a*\u{a}/",false,"a*\u{a}/",6,1,2),
(false,"/*a*\u{a}a",false,"a*\u{a}a",6,1,2),
(false,"/*a*\u{a}\u{a}",false,"a*\u{a}\u{a}",6,2,1),
(false,"/*a/**",false,"a/**",6,0,7),
(false,"/*a/*/",false,"a/",6,0,7),
(false,"/*a/*a",false,"a/*a",6,0,7),
(false,"/*a/*\u{a}",false,"a/*\u{a}",6,1,1),
(false,"/*a//*",false,"a//*",6,0,7),
(false,"/*a///",false,"a///",6,0,7),
(false,"/*a//a",false,"a//a",6,0,7),
(false,"/*a//\u{a}",false,"a//\u{a}",6,1,1),
(false,"/*a/a*",false,"a/a*",6,0,7),
(false,"/*a/a/",false,"a/a/",6,0,7),
(false,"/*a/aa",false,"a/aa",6,0,7),
(false,"/*a/a\u{a}",false,"a/a\u{a}",6,1,1),
(false,"/*a/\u{a}*",false,"a/\u{a}*",6,1,2),
(false,"/*a/\u{a}/",false,"a/\u{a}/",6,1,2),
(false,"/*a/\u{a}a",false,"a/\u{a}a",6,1,2),
(false,"/*a/\u{a}\u{a}",false,"a/\u{a}\u{a}",6,2,1),
(false,"/*aa**",false,"aa**",6,0,7),
(false,"/*aa*/",false,"aa",6,0,7),
(false,"/*aa*a",false,"aa*a",6,0,7),
(false,"/*aa*\u{a}",false,"aa*\u{a}",6,1,1),
(false,"/*aa/*",false,"aa/*",6,0,7),
(false,"/*aa//",false,"aa//",6,0,7),
(false,"/*aa/a",false,"aa/a",6,0,7),
(false,"/*aa/\u{a}",false,"aa/\u{a}",6,1,1),
(false,"/*aaa*",false,"aaa*",6,0,7),
(false,"/*aaa/",false,"aaa/",6,0,7),
(false,"/*aaaa",false,"aaaa",6,0,7),
(false,"/*aaa\u{a}",false,"aaa\u{a}",6,1,1),
(false,"/*aa\u{a}*",false,"aa\u{a}*",6,1,2),
(false,"/*aa\u{a}/",false,"aa\u{a}/",6,1,2),
(false,"/*aa\u{a}a",false,"aa\u{a}a",6,1,2),
(false,"/*aa\u{a}\u{a}",false,"aa\u{a}\u{a}",6,2,1),
(false,"/*a\u{a}**",false,"a\u{a}**",6,1,3),
(false,"/*a\u{a}*/",false,"a\u{a}",6,1,3),
(false,"/*a\u{a}*a",false,"a\u{a}*a",6,1,3),
(false,"/*a\u{a}*\u{a}",false,"a\u{a}*\u{a}",6,2,1),
(false,"/*a\u{a}/*",false,"a\u{a}/*",6,1,3),
(false,"/*a\u{a}//",false,"a\u{a}//",6,1,3),
(false,"/*a\u{a}/a",false,"a\u{a}/a",6,1,3),
(false,"/*a\u{a}/\u{a}",false,"a\u{a}/\u{a}",6,2,1),
(false,"/*a\u{a}a*",false,"a\u{a}a*",6,1,3),
(false,"/*a\u{a}a/",false,"a\u{a}a/",6,1,3),
(false,"/*a\u{a}aa",false,"a\u{a}aa",6,1,3),
(false,"/*a\u{a}a\u{a}",false,"a\u{a}a\u{a}",6,2,1),
(false,"/*a\u{a}\u{a}*",false,"a\u{a}\u{a}*",6,2,2),
(false,"/*a\u{a}\u{a}/",false,"a\u{a}\u{a}/",6,2,2),
(false,"/*a\u{a}\u{a}a",false,"a\u{a}\u{a}a",6,2,2),
(false,"/*a\u{a}\u{a}\u{a}",false,"a\u{a}\u{a}\u{a}",6,3,1),
(false,"/*\u{a}***",false,"\u{a}***",6,1,4),
(false,"/*\u{a}**/",false,"\u{a}*",6,1,4),
(false,"/*\u{a}**a",false,"\u{a}**a",6,1,4),
(false,"/*\u{a}**\u{a}",false,"\u{a}**\u{a}",6,2,1),
(false,"/*\u{a}*/*",false,"\u{a}",5,1,3),
(false,"/*\u{a}*//",false,"\u{a}",5,1,3),
(false,"/*\u{a}*/a",false,"\u{a}",5,1,3),
(false,"/*\u{a}*/\u{a}",false,"\u{a}",5,1,3),
(false,"/*\u{a}*a*",false,"\u{a}*a*",6,1,4),
(false,"/*\u{a}*a/",false,"\u{a}*a/",6,1,4),
(false,"/*\u{a}*aa",false,"\u{a}*aa",6,1,4),
(false,"/*\u{a}*a\u{a}",false,"\u{a}*a\u{a}",6,2,1),
(false,"/*\u{a}*\u{a}*",false,"\u{a}*\u{a}*",6,2,2),
(false,"/*\u{a}*\u{a}/",false,"\u{a}*\u{a}/",6,2,2),
(false,"/*\u{a}*\u{a}a",false,"\u{a}*\u{a}a",6,2,2),
(false,"/*\u{a}*\u{a}\u{a}",false,"\u{a}*\u{a}\u{a}",6,3,1),
(false,"/*\u{a}/**",false,"\u{a}/**",6,1,4),
(false,"/*\u{a}/*/",false,"\u{a}/",6,1,4),
(false,"/*\u{a}/*a",false,"\u{a}/*a",6,1,4),
(false,"/*\u{a}/*\u{a}",false,"\u{a}/*\u{a}",6,2,1),
(false,"/*\u{a}//*",false,"\u{a}//*",6,1,4),
(false,"/*\u{a}///",false,"\u{a}///",6,1,4),
(false,"/*\u{a}//a",false,"\u{a}//a",6,1,4),
(false,"/*\u{a}//\u{a}",false,"\u{a}//\u{a}",6,2,1),
(false,"/*\u{a}/a*",false,"\u{a}/a*",6,1,4),
(false,"/*\u{a}/a/",false,"\u{a}/a/",6,1,4),
(false,"/*\u{a}/aa",false,"\u{a}/aa",6,1,4),
(false,"/*\u{a}/a\u{a}",false,"\u{a}/a\u{a}",6,2,1),
(false,"/*\u{a}/\u{a}*",false,"\u{a}/\u{a}*",6,2,2),
(false,"/*\u{a}/\u{a}/",false,"\u{a}/\u{a}/",6,2,2),
(false,"/*\u{a}/\u{a}a",false,"\u{a}/\u{a}a",6,2,2),
(false,"/*\u{a}/\u{a}\u{a}",false,"\u{a}/\u{a}\u{a}",6,3,1),
(false,"/*\u{a}a**",false,"\u{a}a**",6,1,4),
(false,"/*\u{a}a*/",false,"\u{a}a",6,1,4),
(false,"/*\u{a}a*a",false,"\u{a}a*a",6,1,4),
(false,"/*\u{a}a*\u{a}",false,"\u{a}a*\u{a}",6,2,1),
(false,"/*\u{a}a/*",false,"\u{a}a/*",6,1,4),
(false,"/*\u{a}a//",false,"\u{a}a//",6,1,4),
(false,"/*\u{a}a/a",false,"\u{a}a/a",6,1,4),
(false,"/*\u{a}a/\u{a}",false,"\u{a}a/\u{a}",6,2,1),
(false,"/*\u{a}aa*",false,"\u{a}aa*",6,1,4),
(false,"/*\u{a}aa/",false,"\u{a}aa/",6,1,4),
(false,"/*\u{a}aaa",false,"\u{a}aaa",6,1,4),
(false,"/*\u{a}aa\u{a}",false,"\u{a}aa\u{a}",6,2,1),
(false,"/*\u{a}a\u{a}*",false,"\u{a}a\u{a}*",6,2,2),
(false,"/*\u{a}a\u{a}/",false,"\u{a}a\u{a}/",6,2,2),
(false,"/*\u{a}a\u{a}a",false,"\u{a}a\u{a}a",6,2,2),
(false,"/*\u{a}a\u{a}\u{a}",false,"\u{a}a\u{a}\u{a}",6,3,1),
(false,"/*\u{a}\u{a}**",false,"\u{a}\u{a}**",6,2,3),
(false,"/*\u{a}\u{a}*/",false,"\u{a}\u{a}",6,2,3),
(false,"/*\u{a}\u{a}*a",false,"\u{a}\u{a}*a",6,2,3),
(false,"/*\u{a}\u{a}*\u{a}",false,"\u{a}\u{a}*\u{a}",6,3,1),
(false,"/*\u{a}\u{a}/*",false,"\u{a}\u{a}/*",6,2,3),
(false,"/*\u{a}\u{a}//",false,"\u{a}\u{a}//",6,2,3),
(false,"/*\u{a}\u{a}/a",false,"\u{a}\u{a}/a",6,2,3),
(false,"/*\u{a}\u{a}/\u{a}",false,"\u{a}\u{a}/\u{a}",6,3,1),
(false,"/*\u{a}\u{a}a*",false,"\u{a}\u{a}a*",6,2,3),
(false,"/*\u{a}\u{a}a/",false,"\u{a}\u{a}a/",6,2,3),
(false,"/*\u{a}\u{a}aa",false,"\u{a}\u{a}aa",6,2,3),
(false,"/*\u{a}\u{a}a\u{a}",false,"\u{a}\u{a}a\u{a}",6,3,1),
(false,"/*\u{a}\u{a}\u{a}*",false,"\u{a}\u{a}\u{a}*",6,3,2),
(false,"/*\u{a}\u{a}\u{a}/",false,"\u{a}\u{a}\u{a}/",6,3,2),
(false,"/*\u{a}\u{a}\u{a}a",false,"\u{a}\u{a}\u{a}a",6,3,2),
(false,"/*\u{a}\u{a}\u{a}\u{a}",false,"\u{a}\u{a}\u{a}\u{a}",6,4,1),
(false,"/**/tail",false,"",4,0,5),
(false,"/*a\u{d}\u{a}é😀\u{0}*/tail",false,"a\u{d}\u{a}é😀\u{0}",14,1,7),
(false,"/*# sourceMappingURL=a.map */",false,"# sourceMappingURL=a.map ",29,0,30),
(false,"/*@ sourceURL=b.css\u{d}\u{a}*/",false,"@ sourceURL=b.css\u{d}\u{a}",23,1,3),
(false,"/* outer /* inner */tail",false," outer /* inner ",20,0,21),
(false,"/*\\*/tail",false,"\\",5,0,6),
(false,"/*é😀",false,"é😀",8,0,6),
 ];
for (id,(string,input,bad,value,pos,line,column)) in cases.into_iter().enumerate(){
let mut p=Parser{input,state:ParserState{position:0,current_line_start_position:0,line_number_and_block_type:0},source_map_url:None,source_url:None};
if string {let token=consume_string(&mut p,input.starts_with('\''));match token {QuotedString(v)=>{assert!(!bad,"case {id}");assert_eq!(&*v,value,"case {id}");},BadString(v)=>{assert!(bad,"case {id}");assert_eq!(&*v,value,"case {id}");}}}
else {assert_eq!(consume_comment(&mut p),value,"case {id}");}
assert_eq!(p.state.position,pos,"position case {id}");let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(line,column),"location case {id}");
assert!(input.is_char_boundary(p.state.position));
}
println!("PASS strings=298 comments=348 total=646");
}
