#![allow(dead_code)]
use std::ops::Range;
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
}
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

fn main(){
 { let input="seed/*";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"","body history 0 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 0 step 0");
assert_eq!(p.state.position,6,"position history 0 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,7),"location history 0 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 0 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/**";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"*","body history 1 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 1 step 0");
assert_eq!(p.state.position,7,"position history 1 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,8),"location history 1 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 1 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*/";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"/","body history 2 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 2 step 0");
assert_eq!(p.state.position,7,"position history 2 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,8),"location history 2 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 2 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*a";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"a","body history 3 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 3 step 0");
assert_eq!(p.state.position,7,"position history 3 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,8),"location history 3 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 3 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*\u{a}";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"\u{a}","body history 4 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 4 step 0");
assert_eq!(p.state.position,7,"position history 4 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,1),"location history 4 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 4 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/***";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"**","body history 5 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 5 step 0");
assert_eq!(p.state.position,8,"position history 5 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,9),"location history 5 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 5 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/**a";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"*a","body history 6 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 6 step 0");
assert_eq!(p.state.position,8,"position history 6 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,9),"location history 6 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 6 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/**\u{a}";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"*\u{a}","body history 7 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 7 step 0");
assert_eq!(p.state.position,8,"position history 7 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,1),"location history 7 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 7 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*/*";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"/*","body history 8 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 8 step 0");
assert_eq!(p.state.position,8,"position history 8 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,9),"location history 8 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 8 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*//";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"//","body history 9 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 9 step 0");
assert_eq!(p.state.position,8,"position history 9 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,9),"location history 9 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 9 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*/a";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"/a","body history 10 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 10 step 0");
assert_eq!(p.state.position,8,"position history 10 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,9),"location history 10 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 10 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*/\u{a}";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"/\u{a}","body history 11 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 11 step 0");
assert_eq!(p.state.position,8,"position history 11 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,1),"location history 11 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 11 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*a*";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"a*","body history 12 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 12 step 0");
assert_eq!(p.state.position,8,"position history 12 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,9),"location history 12 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 12 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*a/";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"a/","body history 13 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 13 step 0");
assert_eq!(p.state.position,8,"position history 13 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,9),"location history 13 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 13 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*aa";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"aa","body history 14 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 14 step 0");
assert_eq!(p.state.position,8,"position history 14 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,9),"location history 14 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 14 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*a\u{a}";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"a\u{a}","body history 15 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 15 step 0");
assert_eq!(p.state.position,8,"position history 15 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,1),"location history 15 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 15 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*\u{a}*";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"\u{a}*","body history 16 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 16 step 0");
assert_eq!(p.state.position,8,"position history 16 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,2),"location history 16 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 16 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*\u{a}/";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"\u{a}/","body history 17 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 17 step 0");
assert_eq!(p.state.position,8,"position history 17 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,2),"location history 17 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 17 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*\u{a}a";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"\u{a}a","body history 18 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 18 step 0");
assert_eq!(p.state.position,8,"position history 18 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,2),"location history 18 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 18 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*\u{a}\u{a}";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"\u{a}\u{a}","body history 19 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 19 step 0");
assert_eq!(p.state.position,8,"position history 19 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(5,1),"location history 19 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 19 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/****";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"***","body history 20 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 20 step 0");
assert_eq!(p.state.position,9,"position history 20 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,10),"location history 20 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 20 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/***a";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"**a","body history 21 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 21 step 0");
assert_eq!(p.state.position,9,"position history 21 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,10),"location history 21 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 21 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/***\u{a}";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"**\u{a}","body history 22 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 22 step 0");
assert_eq!(p.state.position,9,"position history 22 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,1),"location history 22 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 22 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/**a*";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"*a*","body history 23 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 23 step 0");
assert_eq!(p.state.position,9,"position history 23 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,10),"location history 23 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 23 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/**a/";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"*a/","body history 24 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 24 step 0");
assert_eq!(p.state.position,9,"position history 24 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,10),"location history 24 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 24 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/**aa";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"*aa","body history 25 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 25 step 0");
assert_eq!(p.state.position,9,"position history 25 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,10),"location history 25 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 25 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/**a\u{a}";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"*a\u{a}","body history 26 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 26 step 0");
assert_eq!(p.state.position,9,"position history 26 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,1),"location history 26 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 26 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/**\u{a}*";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"*\u{a}*","body history 27 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 27 step 0");
assert_eq!(p.state.position,9,"position history 27 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,2),"location history 27 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 27 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/**\u{a}/";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"*\u{a}/","body history 28 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 28 step 0");
assert_eq!(p.state.position,9,"position history 28 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,2),"location history 28 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 28 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/**\u{a}a";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"*\u{a}a","body history 29 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 29 step 0");
assert_eq!(p.state.position,9,"position history 29 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,2),"location history 29 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 29 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/**\u{a}\u{a}";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"*\u{a}\u{a}","body history 30 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 30 step 0");
assert_eq!(p.state.position,9,"position history 30 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(5,1),"location history 30 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 30 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*/**";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"/**","body history 31 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 31 step 0");
assert_eq!(p.state.position,9,"position history 31 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,10),"location history 31 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 31 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*/*a";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"/*a","body history 32 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 32 step 0");
assert_eq!(p.state.position,9,"position history 32 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,10),"location history 32 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 32 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*/*\u{a}";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"/*\u{a}","body history 33 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 33 step 0");
assert_eq!(p.state.position,9,"position history 33 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,1),"location history 33 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 33 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*//*";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"//*","body history 34 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 34 step 0");
assert_eq!(p.state.position,9,"position history 34 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,10),"location history 34 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 34 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*///";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"///","body history 35 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 35 step 0");
assert_eq!(p.state.position,9,"position history 35 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,10),"location history 35 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 35 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*//a";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"//a","body history 36 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 36 step 0");
assert_eq!(p.state.position,9,"position history 36 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,10),"location history 36 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 36 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*//\u{a}";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"//\u{a}","body history 37 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 37 step 0");
assert_eq!(p.state.position,9,"position history 37 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,1),"location history 37 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 37 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*/a*";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"/a*","body history 38 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 38 step 0");
assert_eq!(p.state.position,9,"position history 38 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,10),"location history 38 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 38 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*/a/";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"/a/","body history 39 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 39 step 0");
assert_eq!(p.state.position,9,"position history 39 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,10),"location history 39 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 39 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*/aa";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"/aa","body history 40 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 40 step 0");
assert_eq!(p.state.position,9,"position history 40 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,10),"location history 40 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 40 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*/a\u{a}";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"/a\u{a}","body history 41 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 41 step 0");
assert_eq!(p.state.position,9,"position history 41 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,1),"location history 41 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 41 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*/\u{a}*";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"/\u{a}*","body history 42 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 42 step 0");
assert_eq!(p.state.position,9,"position history 42 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,2),"location history 42 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 42 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*/\u{a}/";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"/\u{a}/","body history 43 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 43 step 0");
assert_eq!(p.state.position,9,"position history 43 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,2),"location history 43 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 43 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*/\u{a}a";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"/\u{a}a","body history 44 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 44 step 0");
assert_eq!(p.state.position,9,"position history 44 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,2),"location history 44 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 44 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*/\u{a}\u{a}";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"/\u{a}\u{a}","body history 45 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 45 step 0");
assert_eq!(p.state.position,9,"position history 45 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(5,1),"location history 45 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 45 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*a**";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"a**","body history 46 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 46 step 0");
assert_eq!(p.state.position,9,"position history 46 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,10),"location history 46 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 46 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*a*a";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"a*a","body history 47 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 47 step 0");
assert_eq!(p.state.position,9,"position history 47 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,10),"location history 47 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 47 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*a*\u{a}";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"a*\u{a}","body history 48 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 48 step 0");
assert_eq!(p.state.position,9,"position history 48 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,1),"location history 48 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 48 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*a/*";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"a/*","body history 49 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 49 step 0");
assert_eq!(p.state.position,9,"position history 49 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,10),"location history 49 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 49 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*a//";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"a//","body history 50 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 50 step 0");
assert_eq!(p.state.position,9,"position history 50 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,10),"location history 50 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 50 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*a/a";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"a/a","body history 51 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 51 step 0");
assert_eq!(p.state.position,9,"position history 51 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,10),"location history 51 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 51 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*a/\u{a}";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"a/\u{a}","body history 52 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 52 step 0");
assert_eq!(p.state.position,9,"position history 52 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,1),"location history 52 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 52 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*aa*";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"aa*","body history 53 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 53 step 0");
assert_eq!(p.state.position,9,"position history 53 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,10),"location history 53 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 53 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*aa/";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"aa/","body history 54 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 54 step 0");
assert_eq!(p.state.position,9,"position history 54 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,10),"location history 54 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 54 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*aaa";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"aaa","body history 55 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 55 step 0");
assert_eq!(p.state.position,9,"position history 55 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,10),"location history 55 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 55 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*aa\u{a}";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"aa\u{a}","body history 56 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 56 step 0");
assert_eq!(p.state.position,9,"position history 56 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,1),"location history 56 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 56 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*a\u{a}*";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"a\u{a}*","body history 57 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 57 step 0");
assert_eq!(p.state.position,9,"position history 57 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,2),"location history 57 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 57 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*a\u{a}/";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"a\u{a}/","body history 58 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 58 step 0");
assert_eq!(p.state.position,9,"position history 58 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,2),"location history 58 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 58 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*a\u{a}a";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"a\u{a}a","body history 59 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 59 step 0");
assert_eq!(p.state.position,9,"position history 59 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,2),"location history 59 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 59 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*a\u{a}\u{a}";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"a\u{a}\u{a}","body history 60 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 60 step 0");
assert_eq!(p.state.position,9,"position history 60 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(5,1),"location history 60 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 60 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*\u{a}**";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"\u{a}**","body history 61 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 61 step 0");
assert_eq!(p.state.position,9,"position history 61 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,3),"location history 61 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 61 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*\u{a}*a";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"\u{a}*a","body history 62 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 62 step 0");
assert_eq!(p.state.position,9,"position history 62 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,3),"location history 62 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 62 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*\u{a}*\u{a}";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"\u{a}*\u{a}","body history 63 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 63 step 0");
assert_eq!(p.state.position,9,"position history 63 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(5,1),"location history 63 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 63 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*\u{a}/*";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"\u{a}/*","body history 64 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 64 step 0");
assert_eq!(p.state.position,9,"position history 64 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,3),"location history 64 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 64 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*\u{a}//";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"\u{a}//","body history 65 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 65 step 0");
assert_eq!(p.state.position,9,"position history 65 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,3),"location history 65 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 65 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*\u{a}/a";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"\u{a}/a","body history 66 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 66 step 0");
assert_eq!(p.state.position,9,"position history 66 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,3),"location history 66 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 66 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*\u{a}/\u{a}";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"\u{a}/\u{a}","body history 67 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 67 step 0");
assert_eq!(p.state.position,9,"position history 67 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(5,1),"location history 67 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 67 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*\u{a}a*";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"\u{a}a*","body history 68 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 68 step 0");
assert_eq!(p.state.position,9,"position history 68 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,3),"location history 68 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 68 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*\u{a}a/";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"\u{a}a/","body history 69 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 69 step 0");
assert_eq!(p.state.position,9,"position history 69 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,3),"location history 69 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 69 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*\u{a}aa";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"\u{a}aa","body history 70 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 70 step 0");
assert_eq!(p.state.position,9,"position history 70 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,3),"location history 70 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 70 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*\u{a}a\u{a}";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"\u{a}a\u{a}","body history 71 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 71 step 0");
assert_eq!(p.state.position,9,"position history 71 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(5,1),"location history 71 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 71 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*\u{a}\u{a}*";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"\u{a}\u{a}*","body history 72 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 72 step 0");
assert_eq!(p.state.position,9,"position history 72 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(5,2),"location history 72 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 72 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*\u{a}\u{a}/";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"\u{a}\u{a}/","body history 73 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 73 step 0");
assert_eq!(p.state.position,9,"position history 73 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(5,2),"location history 73 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 73 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*\u{a}\u{a}a";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"\u{a}\u{a}a","body history 74 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 74 step 0");
assert_eq!(p.state.position,9,"position history 74 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(5,2),"location history 74 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 74 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*\u{a}\u{a}\u{a}";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"\u{a}\u{a}\u{a}","body history 75 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 75 step 0");
assert_eq!(p.state.position,9,"position history 75 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(6,1),"location history 75 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 75 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*****";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"****","body history 76 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 76 step 0");
assert_eq!(p.state.position,10,"position history 76 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,11),"location history 76 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 76 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/****a";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"***a","body history 77 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 77 step 0");
assert_eq!(p.state.position,10,"position history 77 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,11),"location history 77 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 77 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/****\u{a}";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"***\u{a}","body history 78 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 78 step 0");
assert_eq!(p.state.position,10,"position history 78 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,1),"location history 78 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 78 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/***a*";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"**a*","body history 79 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 79 step 0");
assert_eq!(p.state.position,10,"position history 79 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,11),"location history 79 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 79 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/***a/";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"**a/","body history 80 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 80 step 0");
assert_eq!(p.state.position,10,"position history 80 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,11),"location history 80 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 80 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/***aa";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"**aa","body history 81 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 81 step 0");
assert_eq!(p.state.position,10,"position history 81 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,11),"location history 81 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 81 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/***a\u{a}";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"**a\u{a}","body history 82 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 82 step 0");
assert_eq!(p.state.position,10,"position history 82 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,1),"location history 82 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 82 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/***\u{a}*";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"**\u{a}*","body history 83 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 83 step 0");
assert_eq!(p.state.position,10,"position history 83 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,2),"location history 83 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 83 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/***\u{a}/";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"**\u{a}/","body history 84 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 84 step 0");
assert_eq!(p.state.position,10,"position history 84 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,2),"location history 84 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 84 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/***\u{a}a";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"**\u{a}a","body history 85 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 85 step 0");
assert_eq!(p.state.position,10,"position history 85 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,2),"location history 85 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 85 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/***\u{a}\u{a}";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"**\u{a}\u{a}","body history 86 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 86 step 0");
assert_eq!(p.state.position,10,"position history 86 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(5,1),"location history 86 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 86 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/**a**";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"*a**","body history 87 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 87 step 0");
assert_eq!(p.state.position,10,"position history 87 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,11),"location history 87 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 87 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/**a*a";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"*a*a","body history 88 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 88 step 0");
assert_eq!(p.state.position,10,"position history 88 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,11),"location history 88 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 88 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/**a*\u{a}";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"*a*\u{a}","body history 89 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 89 step 0");
assert_eq!(p.state.position,10,"position history 89 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,1),"location history 89 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 89 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/**a/*";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"*a/*","body history 90 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 90 step 0");
assert_eq!(p.state.position,10,"position history 90 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,11),"location history 90 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 90 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/**a//";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"*a//","body history 91 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 91 step 0");
assert_eq!(p.state.position,10,"position history 91 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,11),"location history 91 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 91 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/**a/a";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"*a/a","body history 92 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 92 step 0");
assert_eq!(p.state.position,10,"position history 92 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,11),"location history 92 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 92 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/**a/\u{a}";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"*a/\u{a}","body history 93 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 93 step 0");
assert_eq!(p.state.position,10,"position history 93 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,1),"location history 93 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 93 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/**aa*";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"*aa*","body history 94 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 94 step 0");
assert_eq!(p.state.position,10,"position history 94 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,11),"location history 94 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 94 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/**aa/";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"*aa/","body history 95 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 95 step 0");
assert_eq!(p.state.position,10,"position history 95 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,11),"location history 95 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 95 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/**aaa";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"*aaa","body history 96 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 96 step 0");
assert_eq!(p.state.position,10,"position history 96 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,11),"location history 96 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 96 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/**aa\u{a}";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"*aa\u{a}","body history 97 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 97 step 0");
assert_eq!(p.state.position,10,"position history 97 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,1),"location history 97 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 97 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/**a\u{a}*";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"*a\u{a}*","body history 98 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 98 step 0");
assert_eq!(p.state.position,10,"position history 98 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,2),"location history 98 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 98 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/**a\u{a}/";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"*a\u{a}/","body history 99 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 99 step 0");
assert_eq!(p.state.position,10,"position history 99 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,2),"location history 99 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 99 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/**a\u{a}a";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"*a\u{a}a","body history 100 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 100 step 0");
assert_eq!(p.state.position,10,"position history 100 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,2),"location history 100 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 100 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/**a\u{a}\u{a}";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"*a\u{a}\u{a}","body history 101 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 101 step 0");
assert_eq!(p.state.position,10,"position history 101 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(5,1),"location history 101 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 101 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/**\u{a}**";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"*\u{a}**","body history 102 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 102 step 0");
assert_eq!(p.state.position,10,"position history 102 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,3),"location history 102 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 102 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/**\u{a}*a";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"*\u{a}*a","body history 103 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 103 step 0");
assert_eq!(p.state.position,10,"position history 103 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,3),"location history 103 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 103 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/**\u{a}*\u{a}";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"*\u{a}*\u{a}","body history 104 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 104 step 0");
assert_eq!(p.state.position,10,"position history 104 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(5,1),"location history 104 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 104 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/**\u{a}/*";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"*\u{a}/*","body history 105 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 105 step 0");
assert_eq!(p.state.position,10,"position history 105 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,3),"location history 105 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 105 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/**\u{a}//";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"*\u{a}//","body history 106 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 106 step 0");
assert_eq!(p.state.position,10,"position history 106 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,3),"location history 106 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 106 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/**\u{a}/a";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"*\u{a}/a","body history 107 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 107 step 0");
assert_eq!(p.state.position,10,"position history 107 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,3),"location history 107 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 107 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/**\u{a}/\u{a}";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"*\u{a}/\u{a}","body history 108 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 108 step 0");
assert_eq!(p.state.position,10,"position history 108 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(5,1),"location history 108 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 108 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/**\u{a}a*";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"*\u{a}a*","body history 109 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 109 step 0");
assert_eq!(p.state.position,10,"position history 109 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,3),"location history 109 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 109 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/**\u{a}a/";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"*\u{a}a/","body history 110 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 110 step 0");
assert_eq!(p.state.position,10,"position history 110 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,3),"location history 110 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 110 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/**\u{a}aa";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"*\u{a}aa","body history 111 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 111 step 0");
assert_eq!(p.state.position,10,"position history 111 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,3),"location history 111 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 111 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/**\u{a}a\u{a}";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"*\u{a}a\u{a}","body history 112 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 112 step 0");
assert_eq!(p.state.position,10,"position history 112 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(5,1),"location history 112 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 112 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/**\u{a}\u{a}*";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"*\u{a}\u{a}*","body history 113 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 113 step 0");
assert_eq!(p.state.position,10,"position history 113 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(5,2),"location history 113 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 113 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/**\u{a}\u{a}/";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"*\u{a}\u{a}/","body history 114 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 114 step 0");
assert_eq!(p.state.position,10,"position history 114 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(5,2),"location history 114 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 114 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/**\u{a}\u{a}a";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"*\u{a}\u{a}a","body history 115 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 115 step 0");
assert_eq!(p.state.position,10,"position history 115 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(5,2),"location history 115 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 115 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/**\u{a}\u{a}\u{a}";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"*\u{a}\u{a}\u{a}","body history 116 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 116 step 0");
assert_eq!(p.state.position,10,"position history 116 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(6,1),"location history 116 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 116 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*/***";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"/***","body history 117 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 117 step 0");
assert_eq!(p.state.position,10,"position history 117 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,11),"location history 117 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 117 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*/**a";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"/**a","body history 118 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 118 step 0");
assert_eq!(p.state.position,10,"position history 118 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,11),"location history 118 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 118 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*/**\u{a}";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"/**\u{a}","body history 119 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 119 step 0");
assert_eq!(p.state.position,10,"position history 119 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,1),"location history 119 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 119 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*/*a*";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"/*a*","body history 120 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 120 step 0");
assert_eq!(p.state.position,10,"position history 120 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,11),"location history 120 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 120 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*/*a/";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"/*a/","body history 121 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 121 step 0");
assert_eq!(p.state.position,10,"position history 121 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,11),"location history 121 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 121 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*/*aa";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"/*aa","body history 122 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 122 step 0");
assert_eq!(p.state.position,10,"position history 122 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,11),"location history 122 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 122 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*/*a\u{a}";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"/*a\u{a}","body history 123 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 123 step 0");
assert_eq!(p.state.position,10,"position history 123 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,1),"location history 123 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 123 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*/*\u{a}*";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"/*\u{a}*","body history 124 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 124 step 0");
assert_eq!(p.state.position,10,"position history 124 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,2),"location history 124 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 124 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*/*\u{a}/";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"/*\u{a}/","body history 125 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 125 step 0");
assert_eq!(p.state.position,10,"position history 125 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,2),"location history 125 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 125 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*/*\u{a}a";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"/*\u{a}a","body history 126 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 126 step 0");
assert_eq!(p.state.position,10,"position history 126 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,2),"location history 126 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 126 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*/*\u{a}\u{a}";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"/*\u{a}\u{a}","body history 127 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 127 step 0");
assert_eq!(p.state.position,10,"position history 127 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(5,1),"location history 127 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 127 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*//**";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"//**","body history 128 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 128 step 0");
assert_eq!(p.state.position,10,"position history 128 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,11),"location history 128 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 128 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*//*a";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"//*a","body history 129 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 129 step 0");
assert_eq!(p.state.position,10,"position history 129 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,11),"location history 129 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 129 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*//*\u{a}";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"//*\u{a}","body history 130 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 130 step 0");
assert_eq!(p.state.position,10,"position history 130 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,1),"location history 130 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 130 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*///*";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"///*","body history 131 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 131 step 0");
assert_eq!(p.state.position,10,"position history 131 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,11),"location history 131 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 131 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*////";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"////","body history 132 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 132 step 0");
assert_eq!(p.state.position,10,"position history 132 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,11),"location history 132 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 132 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*///a";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"///a","body history 133 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 133 step 0");
assert_eq!(p.state.position,10,"position history 133 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,11),"location history 133 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 133 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*///\u{a}";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"///\u{a}","body history 134 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 134 step 0");
assert_eq!(p.state.position,10,"position history 134 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,1),"location history 134 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 134 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*//a*";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"//a*","body history 135 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 135 step 0");
assert_eq!(p.state.position,10,"position history 135 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,11),"location history 135 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 135 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*//a/";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"//a/","body history 136 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 136 step 0");
assert_eq!(p.state.position,10,"position history 136 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,11),"location history 136 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 136 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*//aa";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"//aa","body history 137 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 137 step 0");
assert_eq!(p.state.position,10,"position history 137 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,11),"location history 137 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 137 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*//a\u{a}";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"//a\u{a}","body history 138 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 138 step 0");
assert_eq!(p.state.position,10,"position history 138 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,1),"location history 138 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 138 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*//\u{a}*";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"//\u{a}*","body history 139 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 139 step 0");
assert_eq!(p.state.position,10,"position history 139 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,2),"location history 139 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 139 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*//\u{a}/";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"//\u{a}/","body history 140 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 140 step 0");
assert_eq!(p.state.position,10,"position history 140 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,2),"location history 140 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 140 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*//\u{a}a";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"//\u{a}a","body history 141 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 141 step 0");
assert_eq!(p.state.position,10,"position history 141 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,2),"location history 141 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 141 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*//\u{a}\u{a}";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"//\u{a}\u{a}","body history 142 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 142 step 0");
assert_eq!(p.state.position,10,"position history 142 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(5,1),"location history 142 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 142 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*/a**";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"/a**","body history 143 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 143 step 0");
assert_eq!(p.state.position,10,"position history 143 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,11),"location history 143 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 143 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*/a*a";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"/a*a","body history 144 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 144 step 0");
assert_eq!(p.state.position,10,"position history 144 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,11),"location history 144 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 144 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*/a*\u{a}";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"/a*\u{a}","body history 145 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 145 step 0");
assert_eq!(p.state.position,10,"position history 145 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,1),"location history 145 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 145 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*/a/*";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"/a/*","body history 146 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 146 step 0");
assert_eq!(p.state.position,10,"position history 146 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,11),"location history 146 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 146 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*/a//";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"/a//","body history 147 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 147 step 0");
assert_eq!(p.state.position,10,"position history 147 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,11),"location history 147 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 147 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*/a/a";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"/a/a","body history 148 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 148 step 0");
assert_eq!(p.state.position,10,"position history 148 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,11),"location history 148 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 148 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*/a/\u{a}";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"/a/\u{a}","body history 149 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 149 step 0");
assert_eq!(p.state.position,10,"position history 149 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,1),"location history 149 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 149 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*/aa*";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"/aa*","body history 150 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 150 step 0");
assert_eq!(p.state.position,10,"position history 150 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,11),"location history 150 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 150 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*/aa/";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"/aa/","body history 151 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 151 step 0");
assert_eq!(p.state.position,10,"position history 151 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,11),"location history 151 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 151 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*/aaa";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"/aaa","body history 152 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 152 step 0");
assert_eq!(p.state.position,10,"position history 152 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,11),"location history 152 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 152 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*/aa\u{a}";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"/aa\u{a}","body history 153 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 153 step 0");
assert_eq!(p.state.position,10,"position history 153 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,1),"location history 153 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 153 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*/a\u{a}*";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"/a\u{a}*","body history 154 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 154 step 0");
assert_eq!(p.state.position,10,"position history 154 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,2),"location history 154 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 154 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*/a\u{a}/";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"/a\u{a}/","body history 155 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 155 step 0");
assert_eq!(p.state.position,10,"position history 155 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,2),"location history 155 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 155 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*/a\u{a}a";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"/a\u{a}a","body history 156 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 156 step 0");
assert_eq!(p.state.position,10,"position history 156 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,2),"location history 156 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 156 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*/a\u{a}\u{a}";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"/a\u{a}\u{a}","body history 157 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 157 step 0");
assert_eq!(p.state.position,10,"position history 157 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(5,1),"location history 157 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 157 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*/\u{a}**";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"/\u{a}**","body history 158 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 158 step 0");
assert_eq!(p.state.position,10,"position history 158 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,3),"location history 158 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 158 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*/\u{a}*a";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"/\u{a}*a","body history 159 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 159 step 0");
assert_eq!(p.state.position,10,"position history 159 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,3),"location history 159 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 159 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*/\u{a}*\u{a}";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"/\u{a}*\u{a}","body history 160 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 160 step 0");
assert_eq!(p.state.position,10,"position history 160 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(5,1),"location history 160 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 160 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*/\u{a}/*";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"/\u{a}/*","body history 161 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 161 step 0");
assert_eq!(p.state.position,10,"position history 161 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,3),"location history 161 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 161 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*/\u{a}//";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"/\u{a}//","body history 162 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 162 step 0");
assert_eq!(p.state.position,10,"position history 162 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,3),"location history 162 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 162 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*/\u{a}/a";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"/\u{a}/a","body history 163 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 163 step 0");
assert_eq!(p.state.position,10,"position history 163 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,3),"location history 163 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 163 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*/\u{a}/\u{a}";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"/\u{a}/\u{a}","body history 164 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 164 step 0");
assert_eq!(p.state.position,10,"position history 164 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(5,1),"location history 164 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 164 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*/\u{a}a*";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"/\u{a}a*","body history 165 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 165 step 0");
assert_eq!(p.state.position,10,"position history 165 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,3),"location history 165 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 165 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*/\u{a}a/";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"/\u{a}a/","body history 166 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 166 step 0");
assert_eq!(p.state.position,10,"position history 166 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,3),"location history 166 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 166 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*/\u{a}aa";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"/\u{a}aa","body history 167 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 167 step 0");
assert_eq!(p.state.position,10,"position history 167 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,3),"location history 167 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 167 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*/\u{a}a\u{a}";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"/\u{a}a\u{a}","body history 168 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 168 step 0");
assert_eq!(p.state.position,10,"position history 168 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(5,1),"location history 168 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 168 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*/\u{a}\u{a}*";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"/\u{a}\u{a}*","body history 169 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 169 step 0");
assert_eq!(p.state.position,10,"position history 169 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(5,2),"location history 169 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 169 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*/\u{a}\u{a}/";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"/\u{a}\u{a}/","body history 170 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 170 step 0");
assert_eq!(p.state.position,10,"position history 170 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(5,2),"location history 170 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 170 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*/\u{a}\u{a}a";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"/\u{a}\u{a}a","body history 171 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 171 step 0");
assert_eq!(p.state.position,10,"position history 171 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(5,2),"location history 171 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 171 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*/\u{a}\u{a}\u{a}";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"/\u{a}\u{a}\u{a}","body history 172 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 172 step 0");
assert_eq!(p.state.position,10,"position history 172 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(6,1),"location history 172 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 172 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*a***";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"a***","body history 173 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 173 step 0");
assert_eq!(p.state.position,10,"position history 173 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,11),"location history 173 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 173 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*a**a";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"a**a","body history 174 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 174 step 0");
assert_eq!(p.state.position,10,"position history 174 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,11),"location history 174 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 174 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*a**\u{a}";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"a**\u{a}","body history 175 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 175 step 0");
assert_eq!(p.state.position,10,"position history 175 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,1),"location history 175 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 175 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*a*a*";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"a*a*","body history 176 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 176 step 0");
assert_eq!(p.state.position,10,"position history 176 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,11),"location history 176 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 176 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*a*a/";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"a*a/","body history 177 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 177 step 0");
assert_eq!(p.state.position,10,"position history 177 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,11),"location history 177 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 177 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*a*aa";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"a*aa","body history 178 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 178 step 0");
assert_eq!(p.state.position,10,"position history 178 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,11),"location history 178 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 178 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*a*a\u{a}";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"a*a\u{a}","body history 179 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 179 step 0");
assert_eq!(p.state.position,10,"position history 179 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,1),"location history 179 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 179 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*a*\u{a}*";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"a*\u{a}*","body history 180 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 180 step 0");
assert_eq!(p.state.position,10,"position history 180 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,2),"location history 180 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 180 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*a*\u{a}/";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"a*\u{a}/","body history 181 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 181 step 0");
assert_eq!(p.state.position,10,"position history 181 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,2),"location history 181 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 181 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*a*\u{a}a";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"a*\u{a}a","body history 182 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 182 step 0");
assert_eq!(p.state.position,10,"position history 182 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,2),"location history 182 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 182 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*a*\u{a}\u{a}";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"a*\u{a}\u{a}","body history 183 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 183 step 0");
assert_eq!(p.state.position,10,"position history 183 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(5,1),"location history 183 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 183 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*a/**";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"a/**","body history 184 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 184 step 0");
assert_eq!(p.state.position,10,"position history 184 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,11),"location history 184 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 184 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*a/*a";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"a/*a","body history 185 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 185 step 0");
assert_eq!(p.state.position,10,"position history 185 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,11),"location history 185 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 185 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*a/*\u{a}";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"a/*\u{a}","body history 186 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 186 step 0");
assert_eq!(p.state.position,10,"position history 186 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,1),"location history 186 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 186 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*a//*";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"a//*","body history 187 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 187 step 0");
assert_eq!(p.state.position,10,"position history 187 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,11),"location history 187 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 187 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*a///";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"a///","body history 188 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 188 step 0");
assert_eq!(p.state.position,10,"position history 188 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,11),"location history 188 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 188 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*a//a";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"a//a","body history 189 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 189 step 0");
assert_eq!(p.state.position,10,"position history 189 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,11),"location history 189 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 189 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*a//\u{a}";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"a//\u{a}","body history 190 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 190 step 0");
assert_eq!(p.state.position,10,"position history 190 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,1),"location history 190 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 190 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*a/a*";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"a/a*","body history 191 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 191 step 0");
assert_eq!(p.state.position,10,"position history 191 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,11),"location history 191 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 191 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*a/a/";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"a/a/","body history 192 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 192 step 0");
assert_eq!(p.state.position,10,"position history 192 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,11),"location history 192 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 192 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*a/aa";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"a/aa","body history 193 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 193 step 0");
assert_eq!(p.state.position,10,"position history 193 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,11),"location history 193 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 193 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*a/a\u{a}";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"a/a\u{a}","body history 194 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 194 step 0");
assert_eq!(p.state.position,10,"position history 194 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,1),"location history 194 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 194 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*a/\u{a}*";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"a/\u{a}*","body history 195 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 195 step 0");
assert_eq!(p.state.position,10,"position history 195 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,2),"location history 195 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 195 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*a/\u{a}/";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"a/\u{a}/","body history 196 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 196 step 0");
assert_eq!(p.state.position,10,"position history 196 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,2),"location history 196 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 196 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*a/\u{a}a";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"a/\u{a}a","body history 197 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 197 step 0");
assert_eq!(p.state.position,10,"position history 197 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,2),"location history 197 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 197 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*a/\u{a}\u{a}";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"a/\u{a}\u{a}","body history 198 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 198 step 0");
assert_eq!(p.state.position,10,"position history 198 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(5,1),"location history 198 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 198 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*aa**";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"aa**","body history 199 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 199 step 0");
assert_eq!(p.state.position,10,"position history 199 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,11),"location history 199 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 199 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*aa*a";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"aa*a","body history 200 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 200 step 0");
assert_eq!(p.state.position,10,"position history 200 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,11),"location history 200 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 200 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*aa*\u{a}";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"aa*\u{a}","body history 201 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 201 step 0");
assert_eq!(p.state.position,10,"position history 201 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,1),"location history 201 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 201 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*aa/*";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"aa/*","body history 202 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 202 step 0");
assert_eq!(p.state.position,10,"position history 202 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,11),"location history 202 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 202 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*aa//";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"aa//","body history 203 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 203 step 0");
assert_eq!(p.state.position,10,"position history 203 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,11),"location history 203 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 203 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*aa/a";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"aa/a","body history 204 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 204 step 0");
assert_eq!(p.state.position,10,"position history 204 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,11),"location history 204 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 204 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*aa/\u{a}";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"aa/\u{a}","body history 205 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 205 step 0");
assert_eq!(p.state.position,10,"position history 205 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,1),"location history 205 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 205 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*aaa*";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"aaa*","body history 206 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 206 step 0");
assert_eq!(p.state.position,10,"position history 206 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,11),"location history 206 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 206 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*aaa/";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"aaa/","body history 207 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 207 step 0");
assert_eq!(p.state.position,10,"position history 207 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,11),"location history 207 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 207 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*aaaa";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"aaaa","body history 208 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 208 step 0");
assert_eq!(p.state.position,10,"position history 208 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,11),"location history 208 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 208 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*aaa\u{a}";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"aaa\u{a}","body history 209 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 209 step 0");
assert_eq!(p.state.position,10,"position history 209 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,1),"location history 209 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 209 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*aa\u{a}*";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"aa\u{a}*","body history 210 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 210 step 0");
assert_eq!(p.state.position,10,"position history 210 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,2),"location history 210 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 210 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*aa\u{a}/";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"aa\u{a}/","body history 211 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 211 step 0");
assert_eq!(p.state.position,10,"position history 211 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,2),"location history 211 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 211 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*aa\u{a}a";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"aa\u{a}a","body history 212 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 212 step 0");
assert_eq!(p.state.position,10,"position history 212 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,2),"location history 212 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 212 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*aa\u{a}\u{a}";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"aa\u{a}\u{a}","body history 213 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 213 step 0");
assert_eq!(p.state.position,10,"position history 213 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(5,1),"location history 213 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 213 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*a\u{a}**";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"a\u{a}**","body history 214 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 214 step 0");
assert_eq!(p.state.position,10,"position history 214 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,3),"location history 214 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 214 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*a\u{a}*a";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"a\u{a}*a","body history 215 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 215 step 0");
assert_eq!(p.state.position,10,"position history 215 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,3),"location history 215 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 215 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*a\u{a}*\u{a}";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"a\u{a}*\u{a}","body history 216 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 216 step 0");
assert_eq!(p.state.position,10,"position history 216 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(5,1),"location history 216 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 216 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*a\u{a}/*";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"a\u{a}/*","body history 217 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 217 step 0");
assert_eq!(p.state.position,10,"position history 217 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,3),"location history 217 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 217 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*a\u{a}//";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"a\u{a}//","body history 218 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 218 step 0");
assert_eq!(p.state.position,10,"position history 218 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,3),"location history 218 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 218 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*a\u{a}/a";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"a\u{a}/a","body history 219 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 219 step 0");
assert_eq!(p.state.position,10,"position history 219 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,3),"location history 219 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 219 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*a\u{a}/\u{a}";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"a\u{a}/\u{a}","body history 220 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 220 step 0");
assert_eq!(p.state.position,10,"position history 220 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(5,1),"location history 220 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 220 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*a\u{a}a*";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"a\u{a}a*","body history 221 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 221 step 0");
assert_eq!(p.state.position,10,"position history 221 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,3),"location history 221 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 221 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*a\u{a}a/";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"a\u{a}a/","body history 222 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 222 step 0");
assert_eq!(p.state.position,10,"position history 222 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,3),"location history 222 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 222 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*a\u{a}aa";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"a\u{a}aa","body history 223 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 223 step 0");
assert_eq!(p.state.position,10,"position history 223 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,3),"location history 223 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 223 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*a\u{a}a\u{a}";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"a\u{a}a\u{a}","body history 224 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 224 step 0");
assert_eq!(p.state.position,10,"position history 224 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(5,1),"location history 224 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 224 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*a\u{a}\u{a}*";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"a\u{a}\u{a}*","body history 225 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 225 step 0");
assert_eq!(p.state.position,10,"position history 225 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(5,2),"location history 225 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 225 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*a\u{a}\u{a}/";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"a\u{a}\u{a}/","body history 226 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 226 step 0");
assert_eq!(p.state.position,10,"position history 226 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(5,2),"location history 226 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 226 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*a\u{a}\u{a}a";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"a\u{a}\u{a}a","body history 227 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 227 step 0");
assert_eq!(p.state.position,10,"position history 227 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(5,2),"location history 227 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 227 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*a\u{a}\u{a}\u{a}";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"a\u{a}\u{a}\u{a}","body history 228 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 228 step 0");
assert_eq!(p.state.position,10,"position history 228 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(6,1),"location history 228 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 228 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*\u{a}***";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"\u{a}***","body history 229 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 229 step 0");
assert_eq!(p.state.position,10,"position history 229 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,4),"location history 229 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 229 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*\u{a}**a";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"\u{a}**a","body history 230 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 230 step 0");
assert_eq!(p.state.position,10,"position history 230 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,4),"location history 230 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 230 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*\u{a}**\u{a}";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"\u{a}**\u{a}","body history 231 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 231 step 0");
assert_eq!(p.state.position,10,"position history 231 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(5,1),"location history 231 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 231 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*\u{a}*a*";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"\u{a}*a*","body history 232 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 232 step 0");
assert_eq!(p.state.position,10,"position history 232 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,4),"location history 232 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 232 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*\u{a}*a/";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"\u{a}*a/","body history 233 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 233 step 0");
assert_eq!(p.state.position,10,"position history 233 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,4),"location history 233 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 233 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*\u{a}*aa";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"\u{a}*aa","body history 234 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 234 step 0");
assert_eq!(p.state.position,10,"position history 234 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,4),"location history 234 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 234 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*\u{a}*a\u{a}";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"\u{a}*a\u{a}","body history 235 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 235 step 0");
assert_eq!(p.state.position,10,"position history 235 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(5,1),"location history 235 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 235 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*\u{a}*\u{a}*";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"\u{a}*\u{a}*","body history 236 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 236 step 0");
assert_eq!(p.state.position,10,"position history 236 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(5,2),"location history 236 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 236 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*\u{a}*\u{a}/";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"\u{a}*\u{a}/","body history 237 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 237 step 0");
assert_eq!(p.state.position,10,"position history 237 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(5,2),"location history 237 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 237 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*\u{a}*\u{a}a";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"\u{a}*\u{a}a","body history 238 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 238 step 0");
assert_eq!(p.state.position,10,"position history 238 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(5,2),"location history 238 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 238 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*\u{a}*\u{a}\u{a}";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"\u{a}*\u{a}\u{a}","body history 239 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 239 step 0");
assert_eq!(p.state.position,10,"position history 239 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(6,1),"location history 239 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 239 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*\u{a}/**";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"\u{a}/**","body history 240 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 240 step 0");
assert_eq!(p.state.position,10,"position history 240 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,4),"location history 240 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 240 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*\u{a}/*a";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"\u{a}/*a","body history 241 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 241 step 0");
assert_eq!(p.state.position,10,"position history 241 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,4),"location history 241 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 241 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*\u{a}/*\u{a}";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"\u{a}/*\u{a}","body history 242 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 242 step 0");
assert_eq!(p.state.position,10,"position history 242 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(5,1),"location history 242 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 242 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*\u{a}//*";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"\u{a}//*","body history 243 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 243 step 0");
assert_eq!(p.state.position,10,"position history 243 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,4),"location history 243 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 243 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*\u{a}///";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"\u{a}///","body history 244 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 244 step 0");
assert_eq!(p.state.position,10,"position history 244 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,4),"location history 244 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 244 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*\u{a}//a";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"\u{a}//a","body history 245 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 245 step 0");
assert_eq!(p.state.position,10,"position history 245 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,4),"location history 245 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 245 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*\u{a}//\u{a}";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"\u{a}//\u{a}","body history 246 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 246 step 0");
assert_eq!(p.state.position,10,"position history 246 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(5,1),"location history 246 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 246 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*\u{a}/a*";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"\u{a}/a*","body history 247 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 247 step 0");
assert_eq!(p.state.position,10,"position history 247 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,4),"location history 247 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 247 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*\u{a}/a/";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"\u{a}/a/","body history 248 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 248 step 0");
assert_eq!(p.state.position,10,"position history 248 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,4),"location history 248 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 248 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*\u{a}/aa";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"\u{a}/aa","body history 249 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 249 step 0");
assert_eq!(p.state.position,10,"position history 249 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,4),"location history 249 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 249 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*\u{a}/a\u{a}";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"\u{a}/a\u{a}","body history 250 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 250 step 0");
assert_eq!(p.state.position,10,"position history 250 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(5,1),"location history 250 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 250 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*\u{a}/\u{a}*";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"\u{a}/\u{a}*","body history 251 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 251 step 0");
assert_eq!(p.state.position,10,"position history 251 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(5,2),"location history 251 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 251 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*\u{a}/\u{a}/";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"\u{a}/\u{a}/","body history 252 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 252 step 0");
assert_eq!(p.state.position,10,"position history 252 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(5,2),"location history 252 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 252 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*\u{a}/\u{a}a";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"\u{a}/\u{a}a","body history 253 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 253 step 0");
assert_eq!(p.state.position,10,"position history 253 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(5,2),"location history 253 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 253 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*\u{a}/\u{a}\u{a}";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"\u{a}/\u{a}\u{a}","body history 254 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 254 step 0");
assert_eq!(p.state.position,10,"position history 254 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(6,1),"location history 254 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 254 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*\u{a}a**";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"\u{a}a**","body history 255 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 255 step 0");
assert_eq!(p.state.position,10,"position history 255 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,4),"location history 255 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 255 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*\u{a}a*a";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"\u{a}a*a","body history 256 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 256 step 0");
assert_eq!(p.state.position,10,"position history 256 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,4),"location history 256 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 256 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*\u{a}a*\u{a}";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"\u{a}a*\u{a}","body history 257 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 257 step 0");
assert_eq!(p.state.position,10,"position history 257 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(5,1),"location history 257 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 257 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*\u{a}a/*";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"\u{a}a/*","body history 258 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 258 step 0");
assert_eq!(p.state.position,10,"position history 258 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,4),"location history 258 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 258 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*\u{a}a//";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"\u{a}a//","body history 259 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 259 step 0");
assert_eq!(p.state.position,10,"position history 259 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,4),"location history 259 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 259 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*\u{a}a/a";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"\u{a}a/a","body history 260 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 260 step 0");
assert_eq!(p.state.position,10,"position history 260 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,4),"location history 260 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 260 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*\u{a}a/\u{a}";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"\u{a}a/\u{a}","body history 261 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 261 step 0");
assert_eq!(p.state.position,10,"position history 261 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(5,1),"location history 261 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 261 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*\u{a}aa*";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"\u{a}aa*","body history 262 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 262 step 0");
assert_eq!(p.state.position,10,"position history 262 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,4),"location history 262 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 262 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*\u{a}aa/";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"\u{a}aa/","body history 263 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 263 step 0");
assert_eq!(p.state.position,10,"position history 263 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,4),"location history 263 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 263 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*\u{a}aaa";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"\u{a}aaa","body history 264 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 264 step 0");
assert_eq!(p.state.position,10,"position history 264 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,4),"location history 264 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 264 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*\u{a}aa\u{a}";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"\u{a}aa\u{a}","body history 265 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 265 step 0");
assert_eq!(p.state.position,10,"position history 265 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(5,1),"location history 265 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 265 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*\u{a}a\u{a}*";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"\u{a}a\u{a}*","body history 266 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 266 step 0");
assert_eq!(p.state.position,10,"position history 266 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(5,2),"location history 266 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 266 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*\u{a}a\u{a}/";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"\u{a}a\u{a}/","body history 267 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 267 step 0");
assert_eq!(p.state.position,10,"position history 267 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(5,2),"location history 267 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 267 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*\u{a}a\u{a}a";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"\u{a}a\u{a}a","body history 268 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 268 step 0");
assert_eq!(p.state.position,10,"position history 268 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(5,2),"location history 268 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 268 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*\u{a}a\u{a}\u{a}";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"\u{a}a\u{a}\u{a}","body history 269 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 269 step 0");
assert_eq!(p.state.position,10,"position history 269 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(6,1),"location history 269 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 269 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*\u{a}\u{a}**";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"\u{a}\u{a}**","body history 270 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 270 step 0");
assert_eq!(p.state.position,10,"position history 270 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(5,3),"location history 270 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 270 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*\u{a}\u{a}*a";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"\u{a}\u{a}*a","body history 271 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 271 step 0");
assert_eq!(p.state.position,10,"position history 271 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(5,3),"location history 271 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 271 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*\u{a}\u{a}*\u{a}";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"\u{a}\u{a}*\u{a}","body history 272 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 272 step 0");
assert_eq!(p.state.position,10,"position history 272 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(6,1),"location history 272 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 272 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*\u{a}\u{a}/*";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"\u{a}\u{a}/*","body history 273 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 273 step 0");
assert_eq!(p.state.position,10,"position history 273 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(5,3),"location history 273 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 273 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*\u{a}\u{a}//";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"\u{a}\u{a}//","body history 274 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 274 step 0");
assert_eq!(p.state.position,10,"position history 274 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(5,3),"location history 274 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 274 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*\u{a}\u{a}/a";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"\u{a}\u{a}/a","body history 275 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 275 step 0");
assert_eq!(p.state.position,10,"position history 275 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(5,3),"location history 275 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 275 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*\u{a}\u{a}/\u{a}";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"\u{a}\u{a}/\u{a}","body history 276 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 276 step 0");
assert_eq!(p.state.position,10,"position history 276 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(6,1),"location history 276 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 276 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*\u{a}\u{a}a*";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"\u{a}\u{a}a*","body history 277 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 277 step 0");
assert_eq!(p.state.position,10,"position history 277 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(5,3),"location history 277 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 277 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*\u{a}\u{a}a/";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"\u{a}\u{a}a/","body history 278 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 278 step 0");
assert_eq!(p.state.position,10,"position history 278 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(5,3),"location history 278 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 278 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*\u{a}\u{a}aa";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"\u{a}\u{a}aa","body history 279 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 279 step 0");
assert_eq!(p.state.position,10,"position history 279 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(5,3),"location history 279 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 279 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*\u{a}\u{a}a\u{a}";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"\u{a}\u{a}a\u{a}","body history 280 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 280 step 0");
assert_eq!(p.state.position,10,"position history 280 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(6,1),"location history 280 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 280 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*\u{a}\u{a}\u{a}*";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"\u{a}\u{a}\u{a}*","body history 281 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 281 step 0");
assert_eq!(p.state.position,10,"position history 281 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(6,2),"location history 281 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 281 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*\u{a}\u{a}\u{a}/";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"\u{a}\u{a}\u{a}/","body history 282 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 282 step 0");
assert_eq!(p.state.position,10,"position history 282 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(6,2),"location history 282 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 282 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*\u{a}\u{a}\u{a}a";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"\u{a}\u{a}\u{a}a","body history 283 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 283 step 0");
assert_eq!(p.state.position,10,"position history 283 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(6,2),"location history 283 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 283 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*\u{a}\u{a}\u{a}\u{a}";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"\u{a}\u{a}\u{a}\u{a}","body history 284 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 284 step 0");
assert_eq!(p.state.position,10,"position history 284 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(7,1),"location history 284 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 284 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*# sourceURL=*/";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"# sourceURL=","body history 285 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 285 step 0");
assert_eq!(p.state.position,20,"position history 285 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,21),"location history 285 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("")),"URLs history 285 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*# sourceURL= */";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"# sourceURL= ","body history 286 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 286 step 0");
assert_eq!(p.state.position,21,"position history 286 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,22),"location history 286 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("")),"URLs history 286 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*# sourceURL=\u{9}*/";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"# sourceURL=\u{9}","body history 287 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 287 step 0");
assert_eq!(p.state.position,21,"position history 287 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,22),"location history 287 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("")),"URLs history 287 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*# sourceURL=\u{a}*/";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"# sourceURL=\u{a}","body history 288 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 288 step 0");
assert_eq!(p.state.position,21,"position history 288 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,3),"location history 288 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("")),"URLs history 288 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*# sourceURL=\u{d}\u{a}*/";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"# sourceURL=\u{d}\u{a}","body history 289 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 289 step 0");
assert_eq!(p.state.position,22,"position history 289 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,3),"location history 289 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("")),"URLs history 289 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*# sourceURL=\u{c}*/";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"# sourceURL=\u{c}","body history 290 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 290 step 0");
assert_eq!(p.state.position,21,"position history 290 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,3),"location history 290 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("")),"URLs history 290 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*# sourceURL=x.css*/";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"# sourceURL=x.css","body history 291 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 291 step 0");
assert_eq!(p.state.position,25,"position history 291 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,26),"location history 291 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("x.css")),"URLs history 291 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*# sourceURL=x.css */";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"# sourceURL=x.css ","body history 292 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 292 step 0");
assert_eq!(p.state.position,26,"position history 292 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,27),"location history 292 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("x.css")),"URLs history 292 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*# sourceURL=x.css\u{9}*/";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"# sourceURL=x.css\u{9}","body history 293 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 293 step 0");
assert_eq!(p.state.position,26,"position history 293 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,27),"location history 293 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("x.css")),"URLs history 293 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*# sourceURL=x.css\u{a}*/";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"# sourceURL=x.css\u{a}","body history 294 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 294 step 0");
assert_eq!(p.state.position,26,"position history 294 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,3),"location history 294 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("x.css")),"URLs history 294 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*# sourceURL=x.css\u{d}\u{a}*/";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"# sourceURL=x.css\u{d}\u{a}","body history 295 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 295 step 0");
assert_eq!(p.state.position,27,"position history 295 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,3),"location history 295 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("x.css")),"URLs history 295 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*# sourceURL=x.css\u{c}*/";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"# sourceURL=x.css\u{c}","body history 296 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 296 step 0");
assert_eq!(p.state.position,26,"position history 296 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,3),"location history 296 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("x.css")),"URLs history 296 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*# sourceURL=é𐀀.map*/";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"# sourceURL=é𐀀.map","body history 297 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 297 step 0");
assert_eq!(p.state.position,30,"position history 297 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,28),"location history 297 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("é𐀀.map")),"URLs history 297 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*# sourceURL=é𐀀.map */";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"# sourceURL=é𐀀.map ","body history 298 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 298 step 0");
assert_eq!(p.state.position,31,"position history 298 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,29),"location history 298 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("é𐀀.map")),"URLs history 298 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*# sourceURL=é𐀀.map\u{9}*/";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"# sourceURL=é𐀀.map\u{9}","body history 299 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 299 step 0");
assert_eq!(p.state.position,31,"position history 299 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,29),"location history 299 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("é𐀀.map")),"URLs history 299 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*# sourceURL=é𐀀.map\u{a}*/";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"# sourceURL=é𐀀.map\u{a}","body history 300 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 300 step 0");
assert_eq!(p.state.position,31,"position history 300 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,3),"location history 300 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("é𐀀.map")),"URLs history 300 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*# sourceURL=é𐀀.map\u{d}\u{a}*/";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"# sourceURL=é𐀀.map\u{d}\u{a}","body history 301 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 301 step 0");
assert_eq!(p.state.position,32,"position history 301 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,3),"location history 301 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("é𐀀.map")),"URLs history 301 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*# sourceURL=é𐀀.map\u{c}*/";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"# sourceURL=é𐀀.map\u{c}","body history 302 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 302 step 0");
assert_eq!(p.state.position,31,"position history 302 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,3),"location history 302 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("é𐀀.map")),"URLs history 302 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*# sourceURL=a\u{0}b*/";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"# sourceURL=a\u{0}b","body history 303 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 303 step 0");
assert_eq!(p.state.position,23,"position history 303 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,24),"location history 303 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("a\u{0}b")),"URLs history 303 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*# sourceURL=a\u{0}b */";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"# sourceURL=a\u{0}b ","body history 304 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 304 step 0");
assert_eq!(p.state.position,24,"position history 304 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,25),"location history 304 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("a\u{0}b")),"URLs history 304 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*# sourceURL=a\u{0}b\u{9}*/";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"# sourceURL=a\u{0}b\u{9}","body history 305 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 305 step 0");
assert_eq!(p.state.position,24,"position history 305 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,25),"location history 305 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("a\u{0}b")),"URLs history 305 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*# sourceURL=a\u{0}b\u{a}*/";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"# sourceURL=a\u{0}b\u{a}","body history 306 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 306 step 0");
assert_eq!(p.state.position,24,"position history 306 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,3),"location history 306 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("a\u{0}b")),"URLs history 306 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*# sourceURL=a\u{0}b\u{d}\u{a}*/";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"# sourceURL=a\u{0}b\u{d}\u{a}","body history 307 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 307 step 0");
assert_eq!(p.state.position,25,"position history 307 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,3),"location history 307 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("a\u{0}b")),"URLs history 307 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*# sourceURL=a\u{0}b\u{c}*/";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"# sourceURL=a\u{0}b\u{c}","body history 308 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 308 step 0");
assert_eq!(p.state.position,24,"position history 308 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,3),"location history 308 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("a\u{0}b")),"URLs history 308 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*# sourceMappingURL=*/";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"# sourceMappingURL=","body history 309 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 309 step 0");
assert_eq!(p.state.position,27,"position history 309 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,28),"location history 309 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some(""),Some("initial.css")),"URLs history 309 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*# sourceMappingURL= */";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"# sourceMappingURL= ","body history 310 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 310 step 0");
assert_eq!(p.state.position,28,"position history 310 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,29),"location history 310 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some(""),Some("initial.css")),"URLs history 310 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*# sourceMappingURL=\u{9}*/";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"# sourceMappingURL=\u{9}","body history 311 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 311 step 0");
assert_eq!(p.state.position,28,"position history 311 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,29),"location history 311 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some(""),Some("initial.css")),"URLs history 311 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*# sourceMappingURL=\u{a}*/";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"# sourceMappingURL=\u{a}","body history 312 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 312 step 0");
assert_eq!(p.state.position,28,"position history 312 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,3),"location history 312 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some(""),Some("initial.css")),"URLs history 312 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*# sourceMappingURL=\u{d}\u{a}*/";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"# sourceMappingURL=\u{d}\u{a}","body history 313 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 313 step 0");
assert_eq!(p.state.position,29,"position history 313 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,3),"location history 313 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some(""),Some("initial.css")),"URLs history 313 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*# sourceMappingURL=\u{c}*/";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"# sourceMappingURL=\u{c}","body history 314 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 314 step 0");
assert_eq!(p.state.position,28,"position history 314 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,3),"location history 314 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some(""),Some("initial.css")),"URLs history 314 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*# sourceMappingURL=x.css*/";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"# sourceMappingURL=x.css","body history 315 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 315 step 0");
assert_eq!(p.state.position,32,"position history 315 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,33),"location history 315 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("x.css"),Some("initial.css")),"URLs history 315 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*# sourceMappingURL=x.css */";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"# sourceMappingURL=x.css ","body history 316 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 316 step 0");
assert_eq!(p.state.position,33,"position history 316 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,34),"location history 316 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("x.css"),Some("initial.css")),"URLs history 316 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*# sourceMappingURL=x.css\u{9}*/";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"# sourceMappingURL=x.css\u{9}","body history 317 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 317 step 0");
assert_eq!(p.state.position,33,"position history 317 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,34),"location history 317 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("x.css"),Some("initial.css")),"URLs history 317 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*# sourceMappingURL=x.css\u{a}*/";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"# sourceMappingURL=x.css\u{a}","body history 318 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 318 step 0");
assert_eq!(p.state.position,33,"position history 318 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,3),"location history 318 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("x.css"),Some("initial.css")),"URLs history 318 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*# sourceMappingURL=x.css\u{d}\u{a}*/";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"# sourceMappingURL=x.css\u{d}\u{a}","body history 319 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 319 step 0");
assert_eq!(p.state.position,34,"position history 319 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,3),"location history 319 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("x.css"),Some("initial.css")),"URLs history 319 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*# sourceMappingURL=x.css\u{c}*/";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"# sourceMappingURL=x.css\u{c}","body history 320 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 320 step 0");
assert_eq!(p.state.position,33,"position history 320 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,3),"location history 320 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("x.css"),Some("initial.css")),"URLs history 320 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*# sourceMappingURL=é𐀀.map*/";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"# sourceMappingURL=é𐀀.map","body history 321 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 321 step 0");
assert_eq!(p.state.position,37,"position history 321 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,35),"location history 321 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("é𐀀.map"),Some("initial.css")),"URLs history 321 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*# sourceMappingURL=é𐀀.map */";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"# sourceMappingURL=é𐀀.map ","body history 322 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 322 step 0");
assert_eq!(p.state.position,38,"position history 322 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,36),"location history 322 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("é𐀀.map"),Some("initial.css")),"URLs history 322 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*# sourceMappingURL=é𐀀.map\u{9}*/";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"# sourceMappingURL=é𐀀.map\u{9}","body history 323 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 323 step 0");
assert_eq!(p.state.position,38,"position history 323 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,36),"location history 323 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("é𐀀.map"),Some("initial.css")),"URLs history 323 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*# sourceMappingURL=é𐀀.map\u{a}*/";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"# sourceMappingURL=é𐀀.map\u{a}","body history 324 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 324 step 0");
assert_eq!(p.state.position,38,"position history 324 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,3),"location history 324 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("é𐀀.map"),Some("initial.css")),"URLs history 324 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*# sourceMappingURL=é𐀀.map\u{d}\u{a}*/";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"# sourceMappingURL=é𐀀.map\u{d}\u{a}","body history 325 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 325 step 0");
assert_eq!(p.state.position,39,"position history 325 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,3),"location history 325 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("é𐀀.map"),Some("initial.css")),"URLs history 325 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*# sourceMappingURL=é𐀀.map\u{c}*/";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"# sourceMappingURL=é𐀀.map\u{c}","body history 326 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 326 step 0");
assert_eq!(p.state.position,38,"position history 326 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,3),"location history 326 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("é𐀀.map"),Some("initial.css")),"URLs history 326 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*# sourceMappingURL=a\u{0}b*/";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"# sourceMappingURL=a\u{0}b","body history 327 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 327 step 0");
assert_eq!(p.state.position,30,"position history 327 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,31),"location history 327 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("a\u{0}b"),Some("initial.css")),"URLs history 327 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*# sourceMappingURL=a\u{0}b */";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"# sourceMappingURL=a\u{0}b ","body history 328 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 328 step 0");
assert_eq!(p.state.position,31,"position history 328 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,32),"location history 328 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("a\u{0}b"),Some("initial.css")),"URLs history 328 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*# sourceMappingURL=a\u{0}b\u{9}*/";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"# sourceMappingURL=a\u{0}b\u{9}","body history 329 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 329 step 0");
assert_eq!(p.state.position,31,"position history 329 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,32),"location history 329 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("a\u{0}b"),Some("initial.css")),"URLs history 329 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*# sourceMappingURL=a\u{0}b\u{a}*/";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"# sourceMappingURL=a\u{0}b\u{a}","body history 330 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 330 step 0");
assert_eq!(p.state.position,31,"position history 330 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,3),"location history 330 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("a\u{0}b"),Some("initial.css")),"URLs history 330 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*# sourceMappingURL=a\u{0}b\u{d}\u{a}*/";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"# sourceMappingURL=a\u{0}b\u{d}\u{a}","body history 331 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 331 step 0");
assert_eq!(p.state.position,32,"position history 331 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,3),"location history 331 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("a\u{0}b"),Some("initial.css")),"URLs history 331 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*# sourceMappingURL=a\u{0}b\u{c}*/";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"# sourceMappingURL=a\u{0}b\u{c}","body history 332 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 332 step 0");
assert_eq!(p.state.position,31,"position history 332 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,3),"location history 332 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("a\u{0}b"),Some("initial.css")),"URLs history 332 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*@ sourceURL=*/";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"@ sourceURL=","body history 333 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 333 step 0");
assert_eq!(p.state.position,20,"position history 333 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,21),"location history 333 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("")),"URLs history 333 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*@ sourceURL= */";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"@ sourceURL= ","body history 334 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 334 step 0");
assert_eq!(p.state.position,21,"position history 334 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,22),"location history 334 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("")),"URLs history 334 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*@ sourceURL=\u{9}*/";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"@ sourceURL=\u{9}","body history 335 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 335 step 0");
assert_eq!(p.state.position,21,"position history 335 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,22),"location history 335 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("")),"URLs history 335 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*@ sourceURL=\u{a}*/";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"@ sourceURL=\u{a}","body history 336 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 336 step 0");
assert_eq!(p.state.position,21,"position history 336 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,3),"location history 336 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("")),"URLs history 336 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*@ sourceURL=\u{d}\u{a}*/";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"@ sourceURL=\u{d}\u{a}","body history 337 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 337 step 0");
assert_eq!(p.state.position,22,"position history 337 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,3),"location history 337 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("")),"URLs history 337 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*@ sourceURL=\u{c}*/";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"@ sourceURL=\u{c}","body history 338 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 338 step 0");
assert_eq!(p.state.position,21,"position history 338 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,3),"location history 338 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("")),"URLs history 338 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*@ sourceURL=x.css*/";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"@ sourceURL=x.css","body history 339 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 339 step 0");
assert_eq!(p.state.position,25,"position history 339 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,26),"location history 339 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("x.css")),"URLs history 339 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*@ sourceURL=x.css */";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"@ sourceURL=x.css ","body history 340 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 340 step 0");
assert_eq!(p.state.position,26,"position history 340 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,27),"location history 340 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("x.css")),"URLs history 340 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*@ sourceURL=x.css\u{9}*/";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"@ sourceURL=x.css\u{9}","body history 341 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 341 step 0");
assert_eq!(p.state.position,26,"position history 341 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,27),"location history 341 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("x.css")),"URLs history 341 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*@ sourceURL=x.css\u{a}*/";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"@ sourceURL=x.css\u{a}","body history 342 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 342 step 0");
assert_eq!(p.state.position,26,"position history 342 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,3),"location history 342 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("x.css")),"URLs history 342 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*@ sourceURL=x.css\u{d}\u{a}*/";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"@ sourceURL=x.css\u{d}\u{a}","body history 343 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 343 step 0");
assert_eq!(p.state.position,27,"position history 343 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,3),"location history 343 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("x.css")),"URLs history 343 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*@ sourceURL=x.css\u{c}*/";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"@ sourceURL=x.css\u{c}","body history 344 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 344 step 0");
assert_eq!(p.state.position,26,"position history 344 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,3),"location history 344 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("x.css")),"URLs history 344 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*@ sourceURL=é𐀀.map*/";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"@ sourceURL=é𐀀.map","body history 345 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 345 step 0");
assert_eq!(p.state.position,30,"position history 345 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,28),"location history 345 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("é𐀀.map")),"URLs history 345 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*@ sourceURL=é𐀀.map */";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"@ sourceURL=é𐀀.map ","body history 346 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 346 step 0");
assert_eq!(p.state.position,31,"position history 346 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,29),"location history 346 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("é𐀀.map")),"URLs history 346 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*@ sourceURL=é𐀀.map\u{9}*/";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"@ sourceURL=é𐀀.map\u{9}","body history 347 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 347 step 0");
assert_eq!(p.state.position,31,"position history 347 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,29),"location history 347 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("é𐀀.map")),"URLs history 347 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*@ sourceURL=é𐀀.map\u{a}*/";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"@ sourceURL=é𐀀.map\u{a}","body history 348 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 348 step 0");
assert_eq!(p.state.position,31,"position history 348 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,3),"location history 348 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("é𐀀.map")),"URLs history 348 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*@ sourceURL=é𐀀.map\u{d}\u{a}*/";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"@ sourceURL=é𐀀.map\u{d}\u{a}","body history 349 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 349 step 0");
assert_eq!(p.state.position,32,"position history 349 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,3),"location history 349 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("é𐀀.map")),"URLs history 349 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*@ sourceURL=é𐀀.map\u{c}*/";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"@ sourceURL=é𐀀.map\u{c}","body history 350 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 350 step 0");
assert_eq!(p.state.position,31,"position history 350 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,3),"location history 350 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("é𐀀.map")),"URLs history 350 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*@ sourceURL=a\u{0}b*/";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"@ sourceURL=a\u{0}b","body history 351 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 351 step 0");
assert_eq!(p.state.position,23,"position history 351 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,24),"location history 351 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("a\u{0}b")),"URLs history 351 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*@ sourceURL=a\u{0}b */";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"@ sourceURL=a\u{0}b ","body history 352 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 352 step 0");
assert_eq!(p.state.position,24,"position history 352 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,25),"location history 352 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("a\u{0}b")),"URLs history 352 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*@ sourceURL=a\u{0}b\u{9}*/";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"@ sourceURL=a\u{0}b\u{9}","body history 353 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 353 step 0");
assert_eq!(p.state.position,24,"position history 353 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,25),"location history 353 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("a\u{0}b")),"URLs history 353 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*@ sourceURL=a\u{0}b\u{a}*/";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"@ sourceURL=a\u{0}b\u{a}","body history 354 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 354 step 0");
assert_eq!(p.state.position,24,"position history 354 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,3),"location history 354 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("a\u{0}b")),"URLs history 354 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*@ sourceURL=a\u{0}b\u{d}\u{a}*/";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"@ sourceURL=a\u{0}b\u{d}\u{a}","body history 355 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 355 step 0");
assert_eq!(p.state.position,25,"position history 355 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,3),"location history 355 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("a\u{0}b")),"URLs history 355 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*@ sourceURL=a\u{0}b\u{c}*/";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"@ sourceURL=a\u{0}b\u{c}","body history 356 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 356 step 0");
assert_eq!(p.state.position,24,"position history 356 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,3),"location history 356 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("a\u{0}b")),"URLs history 356 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*@ sourceMappingURL=*/";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"@ sourceMappingURL=","body history 357 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 357 step 0");
assert_eq!(p.state.position,27,"position history 357 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,28),"location history 357 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some(""),Some("initial.css")),"URLs history 357 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*@ sourceMappingURL= */";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"@ sourceMappingURL= ","body history 358 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 358 step 0");
assert_eq!(p.state.position,28,"position history 358 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,29),"location history 358 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some(""),Some("initial.css")),"URLs history 358 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*@ sourceMappingURL=\u{9}*/";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"@ sourceMappingURL=\u{9}","body history 359 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 359 step 0");
assert_eq!(p.state.position,28,"position history 359 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,29),"location history 359 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some(""),Some("initial.css")),"URLs history 359 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*@ sourceMappingURL=\u{a}*/";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"@ sourceMappingURL=\u{a}","body history 360 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 360 step 0");
assert_eq!(p.state.position,28,"position history 360 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,3),"location history 360 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some(""),Some("initial.css")),"URLs history 360 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*@ sourceMappingURL=\u{d}\u{a}*/";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"@ sourceMappingURL=\u{d}\u{a}","body history 361 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 361 step 0");
assert_eq!(p.state.position,29,"position history 361 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,3),"location history 361 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some(""),Some("initial.css")),"URLs history 361 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*@ sourceMappingURL=\u{c}*/";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"@ sourceMappingURL=\u{c}","body history 362 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 362 step 0");
assert_eq!(p.state.position,28,"position history 362 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,3),"location history 362 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some(""),Some("initial.css")),"URLs history 362 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*@ sourceMappingURL=x.css*/";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"@ sourceMappingURL=x.css","body history 363 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 363 step 0");
assert_eq!(p.state.position,32,"position history 363 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,33),"location history 363 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("x.css"),Some("initial.css")),"URLs history 363 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*@ sourceMappingURL=x.css */";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"@ sourceMappingURL=x.css ","body history 364 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 364 step 0");
assert_eq!(p.state.position,33,"position history 364 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,34),"location history 364 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("x.css"),Some("initial.css")),"URLs history 364 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*@ sourceMappingURL=x.css\u{9}*/";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"@ sourceMappingURL=x.css\u{9}","body history 365 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 365 step 0");
assert_eq!(p.state.position,33,"position history 365 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,34),"location history 365 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("x.css"),Some("initial.css")),"URLs history 365 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*@ sourceMappingURL=x.css\u{a}*/";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"@ sourceMappingURL=x.css\u{a}","body history 366 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 366 step 0");
assert_eq!(p.state.position,33,"position history 366 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,3),"location history 366 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("x.css"),Some("initial.css")),"URLs history 366 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*@ sourceMappingURL=x.css\u{d}\u{a}*/";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"@ sourceMappingURL=x.css\u{d}\u{a}","body history 367 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 367 step 0");
assert_eq!(p.state.position,34,"position history 367 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,3),"location history 367 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("x.css"),Some("initial.css")),"URLs history 367 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*@ sourceMappingURL=x.css\u{c}*/";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"@ sourceMappingURL=x.css\u{c}","body history 368 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 368 step 0");
assert_eq!(p.state.position,33,"position history 368 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,3),"location history 368 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("x.css"),Some("initial.css")),"URLs history 368 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*@ sourceMappingURL=é𐀀.map*/";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"@ sourceMappingURL=é𐀀.map","body history 369 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 369 step 0");
assert_eq!(p.state.position,37,"position history 369 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,35),"location history 369 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("é𐀀.map"),Some("initial.css")),"URLs history 369 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*@ sourceMappingURL=é𐀀.map */";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"@ sourceMappingURL=é𐀀.map ","body history 370 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 370 step 0");
assert_eq!(p.state.position,38,"position history 370 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,36),"location history 370 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("é𐀀.map"),Some("initial.css")),"URLs history 370 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*@ sourceMappingURL=é𐀀.map\u{9}*/";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"@ sourceMappingURL=é𐀀.map\u{9}","body history 371 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 371 step 0");
assert_eq!(p.state.position,38,"position history 371 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,36),"location history 371 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("é𐀀.map"),Some("initial.css")),"URLs history 371 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*@ sourceMappingURL=é𐀀.map\u{a}*/";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"@ sourceMappingURL=é𐀀.map\u{a}","body history 372 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 372 step 0");
assert_eq!(p.state.position,38,"position history 372 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,3),"location history 372 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("é𐀀.map"),Some("initial.css")),"URLs history 372 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*@ sourceMappingURL=é𐀀.map\u{d}\u{a}*/";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"@ sourceMappingURL=é𐀀.map\u{d}\u{a}","body history 373 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 373 step 0");
assert_eq!(p.state.position,39,"position history 373 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,3),"location history 373 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("é𐀀.map"),Some("initial.css")),"URLs history 373 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*@ sourceMappingURL=é𐀀.map\u{c}*/";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"@ sourceMappingURL=é𐀀.map\u{c}","body history 374 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 374 step 0");
assert_eq!(p.state.position,38,"position history 374 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,3),"location history 374 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("é𐀀.map"),Some("initial.css")),"URLs history 374 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*@ sourceMappingURL=a\u{0}b*/";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"@ sourceMappingURL=a\u{0}b","body history 375 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 375 step 0");
assert_eq!(p.state.position,30,"position history 375 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,31),"location history 375 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("a\u{0}b"),Some("initial.css")),"URLs history 375 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*@ sourceMappingURL=a\u{0}b */";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"@ sourceMappingURL=a\u{0}b ","body history 376 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 376 step 0");
assert_eq!(p.state.position,31,"position history 376 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,32),"location history 376 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("a\u{0}b"),Some("initial.css")),"URLs history 376 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*@ sourceMappingURL=a\u{0}b\u{9}*/";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"@ sourceMappingURL=a\u{0}b\u{9}","body history 377 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 377 step 0");
assert_eq!(p.state.position,31,"position history 377 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,32),"location history 377 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("a\u{0}b"),Some("initial.css")),"URLs history 377 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*@ sourceMappingURL=a\u{0}b\u{a}*/";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"@ sourceMappingURL=a\u{0}b\u{a}","body history 378 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 378 step 0");
assert_eq!(p.state.position,31,"position history 378 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,3),"location history 378 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("a\u{0}b"),Some("initial.css")),"URLs history 378 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*@ sourceMappingURL=a\u{0}b\u{d}\u{a}*/";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"@ sourceMappingURL=a\u{0}b\u{d}\u{a}","body history 379 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 379 step 0");
assert_eq!(p.state.position,32,"position history 379 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,3),"location history 379 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("a\u{0}b"),Some("initial.css")),"URLs history 379 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*@ sourceMappingURL=a\u{0}b\u{c}*/";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"@ sourceMappingURL=a\u{0}b\u{c}","body history 380 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 380 step 0");
assert_eq!(p.state.position,31,"position history 380 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,3),"location history 380 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("a\u{0}b"),Some("initial.css")),"URLs history 380 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*#sourceURL=no*/";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"#sourceURL=no","body history 381 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 381 step 0");
assert_eq!(p.state.position,21,"position history 381 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,22),"location history 381 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 381 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*#  sourceURL=no*/";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"#  sourceURL=no","body history 382 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 382 step 0");
assert_eq!(p.state.position,23,"position history 382 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,24),"location history 382 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 382 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/* # sourceURL=no*/";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body," # sourceURL=no","body history 383 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 383 step 0");
assert_eq!(p.state.position,23,"position history 383 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,24),"location history 383 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 383 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*# SourceURL=no*/";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"# SourceURL=no","body history 384 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 384 step 0");
assert_eq!(p.state.position,22,"position history 384 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,23),"location history 384 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 384 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*# sourceURLX=no*/";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"# sourceURLX=no","body history 385 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 385 step 0");
assert_eq!(p.state.position,23,"position history 385 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,24),"location history 385 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 385 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*@ sourceMappingURL*/";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"@ sourceMappingURL","body history 386 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 386 step 0");
assert_eq!(p.state.position,26,"position history 386 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,27),"location history 386 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 386 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*x# sourceURL=no*/";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"x# sourceURL=no","body history 387 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 387 step 0");
assert_eq!(p.state.position,23,"position history 387 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,24),"location history 387 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 387 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*é𐀀\u{0}*/";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"é𐀀\u{0}","body history 388 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 388 step 0");
assert_eq!(p.state.position,15,"position history 388 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,13),"location history 388 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 388 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*outer /* inner*/";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"outer /* inner","body history 389 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 389 step 0");
assert_eq!(p.state.position,22,"position history 389 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,23),"location history 389 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 389 step 0");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*# sourceURL=a*//*# sourceMappingURL=m*//**//*@ sourceURL=*//*@ sourceMappingURL=é𐀀\u{c}ignored*/";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"# sourceURL=a","body history 390 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 390 step 0");
assert_eq!(p.state.position,21,"position history 390 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,22),"location history 390 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("a")),"URLs history 390 step 0");
assert!(input.is_char_boundary(p.state.position));
let body=consume_comment(&mut p);
assert_eq!(body,"# sourceMappingURL=m","body history 390 step 1");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,23,"slice history 390 step 1");
assert_eq!(p.state.position,45,"position history 390 step 1");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,46),"location history 390 step 1");
assert_eq!((p.source_map_url,p.source_url),(Some("m"),Some("a")),"URLs history 390 step 1");
assert!(input.is_char_boundary(p.state.position));
let body=consume_comment(&mut p);
assert_eq!(body,"","body history 390 step 2");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,47,"slice history 390 step 2");
assert_eq!(p.state.position,49,"position history 390 step 2");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,50),"location history 390 step 2");
assert_eq!((p.source_map_url,p.source_url),(Some("m"),Some("a")),"URLs history 390 step 2");
assert!(input.is_char_boundary(p.state.position));
let body=consume_comment(&mut p);
assert_eq!(body,"@ sourceURL=","body history 390 step 3");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,51,"slice history 390 step 3");
assert_eq!(p.state.position,65,"position history 390 step 3");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,66),"location history 390 step 3");
assert_eq!((p.source_map_url,p.source_url),(Some("m"),Some("")),"URLs history 390 step 3");
assert!(input.is_char_boundary(p.state.position));
let body=consume_comment(&mut p);
assert_eq!(body,"@ sourceMappingURL=é𐀀\u{c}ignored","body history 390 step 4");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,67,"slice history 390 step 4");
assert_eq!(p.state.position,102,"position history 390 step 4");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,10),"location history 390 step 4");
assert_eq!((p.source_map_url,p.source_url),(Some("é𐀀"),Some("")),"URLs history 390 step 4");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*# sourceMappingURL=old*//*# sourceMappingURL=new";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"# sourceMappingURL=old","body history 391 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 391 step 0");
assert_eq!(p.state.position,30,"position history 391 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,31),"location history 391 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("old"),Some("initial.css")),"URLs history 391 step 0");
assert!(input.is_char_boundary(p.state.position));
let body=consume_comment(&mut p);
assert_eq!(body,"# sourceMappingURL=new","body history 391 step 1");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,32,"slice history 391 step 1");
assert_eq!(p.state.position,54,"position history 391 step 1");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,55),"location history 391 step 1");
assert_eq!((p.source_map_url,p.source_url),(Some("new"),Some("initial.css")),"URLs history 391 step 1");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*# sourceURL=old*//*@ sourceURL=";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"# sourceURL=old","body history 392 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 392 step 0");
assert_eq!(p.state.position,23,"position history 392 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,24),"location history 392 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("old")),"URLs history 392 step 0");
assert!(input.is_char_boundary(p.state.position));
let body=consume_comment(&mut p);
assert_eq!(body,"@ sourceURL=","body history 392 step 1");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,25,"slice history 392 step 1");
assert_eq!(p.state.position,37,"position history 392 step 1");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,38),"location history 392 step 1");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("")),"URLs history 392 step 1");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/*é𐀀\u{d}\u{a}*//*\u{0}\u{d}*//*\u{a}\u{c}*//*# sourceURL=final*/";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body,"é𐀀\u{d}\u{a}","body history 393 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 393 step 0");
assert_eq!(p.state.position,16,"position history 393 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(4,3),"location history 393 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 393 step 0");
assert!(input.is_char_boundary(p.state.position));
let body=consume_comment(&mut p);
assert_eq!(body,"\u{0}\u{d}","body history 393 step 1");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,18,"slice history 393 step 1");
assert_eq!(p.state.position,22,"position history 393 step 1");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(5,3),"location history 393 step 1");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 393 step 1");
assert!(input.is_char_boundary(p.state.position));
let body=consume_comment(&mut p);
assert_eq!(body,"\u{a}\u{c}","body history 393 step 2");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,24,"slice history 393 step 2");
assert_eq!(p.state.position,28,"position history 393 step 2");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(7,3),"location history 393 step 2");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 393 step 2");
assert!(input.is_char_boundary(p.state.position));
let body=consume_comment(&mut p);
assert_eq!(body,"# sourceURL=final","body history 393 step 3");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,30,"slice history 393 step 3");
assert_eq!(p.state.position,49,"position history 393 step 3");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(7,24),"location history 393 step 3");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("final")),"URLs history 393 step 3");
assert!(input.is_char_boundary(p.state.position));
 }
 { let input="seed/* outer /* inner *//*# sourceURL=nested-boundary*/";
let mut p=Parser{input,state:ParserState{position:4,current_line_start_position:0,line_number_and_block_type:12},source_map_url:Some("initial.map"),source_url:Some("initial.css")};
let body=consume_comment(&mut p);
assert_eq!(body," outer /* inner ","body history 394 step 0");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,6,"slice history 394 step 0");
assert_eq!(p.state.position,24,"position history 394 step 0");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,25),"location history 394 step 0");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("initial.css")),"URLs history 394 step 0");
assert!(input.is_char_boundary(p.state.position));
let body=consume_comment(&mut p);
assert_eq!(body,"# sourceURL=nested-boundary","body history 394 step 1");
assert_eq!(body.as_ptr() as usize-input.as_ptr() as usize,26,"slice history 394 step 1");
assert_eq!(p.state.position,55,"position history 394 step 1");
let loc=p.state.source_location();assert_eq!((loc.line,loc.column),(3,56),"location history 394 step 1");
assert_eq!((p.source_map_url,p.source_url),(Some("initial.map"),Some("nested-boundary")),"URLs history 394 step 1");
assert!(input.is_char_boundary(p.state.position));
 }

for block in 0..4 {
 let mut state=ParserState{position:0,current_line_start_position:0,line_number_and_block_type:0xfffffff8+block};
 state.advance_line_number(1);
 assert_eq!(state.line_number(),(1u32<<30)-1);
 assert_eq!(state.line_number_and_block_type&3,block);
 std::panic::set_hook(Box::new(|_|{}));
 let overflow=std::panic::catch_unwind(std::panic::AssertUnwindSafe(||state.advance_line_number(1)));
 if cfg!(debug_assertions){assert!(overflow.is_err());}
 else{assert!(overflow.is_ok());assert_eq!(state.line_number(),0);assert_eq!(state.line_number_and_block_type&3,block);}
}
let mut p=Parser{input:"𐀀",state:ParserState{position:0,current_line_start_position:0,line_number_and_block_type:0},source_map_url:None,source_url:None};
p.consume_4byte_intro();assert_eq!(p.state.current_line_start_position,u32::MAX);
assert_eq!(p.state.source_location().column,3);
for _ in 0..3{p.consume_continuation_byte();assert_eq!(p.state.source_location().column,3);}
assert_eq!(p.state.position,4);
let state=ParserState{position:(1usize<<32)+5,current_line_start_position:0,line_number_and_block_type:0};
assert_eq!(state.source_location().column,6);
println!("PASS histories=395 comment_calls=405 raw_slices_positions_locations_and_both_URLs");
}
