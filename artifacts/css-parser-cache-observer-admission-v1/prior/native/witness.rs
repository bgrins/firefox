use cssparser::{Parser,Token,ParseError,Delimiter};
fn calc(p:&mut Parser)->Result<(),ParseError<()>> {
 match p.next()? {
  Token::Function(n) if n.eq_ignore_ascii_case("calc") => p.parse_nested_block(calc),
  Token::Dimension{..}|Token::Number{..} => Ok(()),
  _ => Err(ParseError::unexpected_token()),
 }
}
struct Declarations { qualified:bool }
impl<'i> cssparser::AtRuleParser<'i> for Declarations { type Prelude=();type AtRule=String;type Error=(); }
impl<'i> cssparser::QualifiedRuleParser<'i> for Declarations {type Prelude=();type QualifiedRule=String;type Error=();}
impl<'i> cssparser::DeclarationParser<'i> for Declarations {
 type Declaration=String;type Error=();
 fn parse_value(&mut self,name:cssparser::CowRcStr<'i>,p:&mut Parser<'i>,_:&cssparser::ParserState)->Result<String,ParseError<()>> {
  if name.eq_ignore_ascii_case("padding-left") {p.parse_until_before(Delimiter::Bang,calc)?;return Ok("padding".into());}
  if name.eq_ignore_ascii_case("color") {let value=p.expect_ident()?.to_string();p.expect_exhausted()?;return Ok(value);}
  Err(ParseError::unexpected_token())
 }
}
impl<'i> cssparser::RuleBodyItemParser<'i,String,()> for Declarations {
 fn parse_declarations(&self)->bool {true}
 fn parse_qualified(&self)->bool {self.qualified}
}
fn main(){
 for qualified in [false,true] {
  for depth in [1usize,75,76] {
   let raw=format!("color:red;padding-left:{}1px{};color:blue;)","calc(".repeat(depth),")".repeat(depth-1));
   let mut p=Parser::new(&raw);let mut handler=Declarations{qualified};
   let colors:Vec<_>=cssparser::RuleBodyParser::new(&mut p,&mut handler).filter_map(Result::ok).collect();
   let leaks=colors.iter().any(|v|v=="blue");assert_eq!(leaks,!qualified && depth==76);
   println!("{{\"case\":\"rule-body\",\"qualified_retry\":{qualified},\"depth\":{depth},\"accepted\":{colors:?}}}");
  }
 }

 for primed in [false,true] {
  let mut p=Parser::new("var(--x)");let start=p.state();
  if primed {assert!(matches!(p.next(),Ok(Token::Function(_))));p.reset(&start);}
  p.look_for_arbitrary_substitution_functions(&["var"]);
  assert!(matches!(p.next(),Ok(Token::Function(_))));
  let seen=p.seen_arbitrary_substitution_functions();assert_eq!(seen,!primed);
  println!("{{\"case\":\"function-cache\",\"primed\":{primed},\"seen\":{seen}}}");
 }
 for directive in ["sourceURL","sourceMappingURL"] {
  let raw=format!("(/*# {directive}=A */)/*# {directive}=B */");let mut p=Parser::new(&raw);
  assert!(matches!(p.next(),Ok(Token::ParenthesisBlock)));let inside=p.state();
  assert!(matches!(p.next_including_whitespace_and_comments(),Ok(Token::Comment(_))));
  let before=if directive=="sourceURL" {p.current_source_url()}else{p.current_source_map_url()};assert_eq!(before,Some("B"));
  p.reset(&inside);
  assert!(matches!(p.next_including_whitespace_and_comments(),Ok(Token::Comment(_))));
  assert!(p.next_including_whitespace_and_comments().is_err());
  let after=if directive=="sourceURL" {p.current_source_url()}else{p.current_source_map_url()};assert_eq!(after,Some("A"));
  let mut fresh=Parser::new(&raw);while fresh.next_including_whitespace_and_comments().is_ok(){};
  let plain=if directive=="sourceURL" {fresh.current_source_url()}else{fresh.current_source_map_url()};assert_eq!(plain,Some("B"));
  println!("{{\"case\":\"comment-cache\",\"field\":\"{directive}\",\"after_replay\":\"A\",\"fresh\":\"B\",\"same_eof\":true}}");
 }
 for depth in [1usize,74,75,76,77] {
  let raw=format!("{}1px{}; color:blue; ); color:green;", "calc(".repeat(depth),")".repeat(depth-1));
  let mut p=Parser::new(&raw);
  let result:Result<(),ParseError<()>>=p.parse_until_after(Delimiter::Semicolon,calc);
  assert!(result.is_err());
  let pos=p.position().byte_index();let remaining=&raw[pos..];
  let leaked=remaining.starts_with(" color:blue;");assert_eq!(leaked,depth>=76);
  println!("{{\"case\":\"depth-recovery\",\"depth\":{depth},\"inner_declaration_exposed\":{leaked},\"remaining\":{remaining:?}}}");
 }
 let raw="var(--x)";let mut p=Parser::new(raw);p.look_for_arbitrary_substitution_functions(&["var"]);let start=p.state();p.next().unwrap();p.reset(&start);
 assert!(p.seen_arbitrary_substitution_functions());println!("{{\"case\":\"speculative-preservation-control\",\"seen_after_reset\":true}}");
}
