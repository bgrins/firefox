use cssparser::{Parser,Token};
use std::io::{self,BufRead};
fn hex(s:&str)->String{s.as_bytes().iter().map(|b|format!("{b:02x}")).collect()}
fn option_hex(s:Option<&str>)->String{match s{None=>"none".into(),Some(value)=>format!("some:{}",hex(value))}}
fn main(){
 for (row,line) in io::stdin().lock().lines().enumerate(){
  let line=line.unwrap();let bytes:Vec<u8>=(0..line.len()).step_by(2).map(|i|u8::from_str_radix(&line[i..i+2],16).unwrap()).collect();let source=String::from_utf8(bytes).unwrap();
  let mut p=Parser::new(&source);p.look_for_arbitrary_substitution_functions(&["url"]);
  let mut index=0;
  while let Some(token)=p.codex_raw_token(){
   let (kind,value)=match token{Token::Ident(s)=>("ident",s.to_string()),Token::Function(s)=>("function",s.to_string()),Token::UnquotedUrl(s)=>("url",s.to_string()),Token::BadUrl(s)=>("bad-url",s.to_string()),Token::QuotedString(s)=>("string",s.to_string()),Token::BadString(s)=>("bad-string",s.to_string()),Token::WhiteSpace(s)=>("space",s.to_string()),Token::Comment(s)=>("comment",s.to_string()),Token::CloseParenthesis=>("close",String::new()),Token::Delim(c)=>("delim",c.to_string()),other=>("other",format!("{other:?}"))};
   let location=p.current_source_location();
   println!("{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}",row,index,kind,hex(&value),p.position().byte_index(),location.line,location.column,p.codex_pending(),p.codex_seen(),option_hex(p.current_source_url()),option_hex(p.current_source_map_url()));
   index+=1;
  }
 }
}
