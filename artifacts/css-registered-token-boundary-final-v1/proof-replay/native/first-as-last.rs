use cssparser::{Parser as CSSParser, Token, TokenSerializationType};
fn scan(css:&str)->(TokenSerializationType,TokenSerializationType) {
        let mut input = CSSParser::new(&css);
        let mut first = TokenSerializationType::Nothing;
        let mut last = TokenSerializationType::Nothing;
        while let Ok(token) = input.next_including_whitespace() {
            first.set_if_nothing(token.serialization_type());
            if last == TokenSerializationType::Nothing { last = match token {
                // The parser skips nested blocks, including their closing token.
                Token::Function(_)
                | Token::ParenthesisBlock
                | Token::SquareBracketBlock
                | Token::CurlyBracketBlock => TokenSerializationType::Other,
                _ => token.serialization_type(),
            }; }
        }
        drop(input);
(first,last)
}
fn main(){ let cases = [("","Nothing","Nothing"),
("/**/","Nothing","Nothing"),
(" ","WhiteSpace","WhiteSpace"),
("/**/20px/**/","Dimension","Dimension"),
("20px","Dimension","Dimension"),
("25%","Percentage","Percentage"),
("calc(20px + 5%)","Function","Other"),
("25% 20px","Percentage","Dimension"),
("20px 25%","Dimension","Percentage"),
("[20px]","Other","Other"),
("(20px)","OpenParen","Other"),
("{20px}","Other","Other"),
("f(g([20px]))","Function","Other"),
("f(20px) 25%","Function","Percentage"),
("25% f(20px)","Percentage","Other"),
(" f(20px) ","WhiteSpace","WhiteSpace"),
("\"/*20px*/\"","Other","Other"),
("url(foo)","UrlOrBadUrl","UrlOrBadUrl"),
("url(\"foo\")","Function","Other"),
("r\\65 d","Ident","Ident"),
("@/**/calc(20px + 5%)","DelimAt","Other"),
("f(/**/20px/**/)/**/","Function","Other"),
("1, 20px","Number","Dimension"),
("f(20px)/**/red","Function","Ident")]; for (i,(css,first,last)) in cases.iter().enumerate(){
let raw=cssparser::codex_flat_classes(css); let flat=(raw.first().copied().unwrap_or_default(),raw.last().copied().unwrap_or_default()); let actual=scan(css); println!("{}|{:?}|{:?}|{:?}|{:?}",i,actual.0,actual.1,flat.0,flat.1); assert_eq!((format!("{:?}",flat.0),format!("{:?}",flat.1)),(first.to_string(),last.to_string()),"independent fixture"); assert_eq!(actual,flat,"boundary mismatch"); }}