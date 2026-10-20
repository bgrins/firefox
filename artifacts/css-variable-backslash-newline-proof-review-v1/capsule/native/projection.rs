use cssparser::{Parser,Token,ParseError,Delimiter};
use std::io::{self,BufRead};
fn hex(raw: &str) -> String { raw.as_bytes().iter().map(|b|format!("{b:02x}")).collect() }
fn block(token: &Token<'_>) -> bool {
    matches!(token,Token::Function(_)|Token::ParenthesisBlock|Token::SquareBracketBlock|Token::CurlyBracketBlock)
}
fn drain(p: &mut Parser<'_>) -> Result<(),ParseError<()>> {
    while let Ok(token)=p.next_including_whitespace_and_comments() {
        if block(token) { p.parse_nested_block(drain)?; }
    }
    Ok(())
}
fn main() {
    for (index,line) in io::stdin().lock().lines().enumerate() {
        let line=line.unwrap();
        let raw:Vec<u8>=(0..line.len()).step_by(2).map(|i|u8::from_str_radix(&line[i..i+2],16).unwrap()).collect();
        let source=String::from_utf8(raw).unwrap();
        let mut p=Parser::new(&source);
        let state=p.state();
        if !matches!(p.next_including_whitespace_and_comments(),Ok(Token::WhiteSpace(_))) { p.reset(&state); }
        let mut rows=Vec::new();
        let result:Result<(),ParseError<()>>=p.parse_until_before(Delimiter::Bang|Delimiter::Semicolon,|p| {
            loop {
                let start=p.position();
                let token=match p.next_including_whitespace_and_comments(){Ok(t)=>t,Err(_)=>break};
                let kind=format!("{:?}",token.serialization_type());
                let backslash=matches!(token,Token::Delim('\\'));
                if block(token) { p.parse_nested_block(drain)?; }
                rows.push(format!("{{\"kind\":\"{kind}\",\"backslash\":{backslash},\"raw_hex\":\"{}\"}}",hex(p.slice_from(start))));
            }
            Ok(())
        });
        assert!(result.is_ok());
        println!("{{\"index\":{index},\"tokens\":[{}]}}",rows.join(","));
    }
}
