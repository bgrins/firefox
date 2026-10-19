use cssparser::{Parser,Token,ParseError,Delimiter,ParseErrorKind,BasicParseErrorKind};
fn calc(p:&mut Parser)->Result<(),ParseError<()>> {
 match p.next()? {
  Token::Function(n) if n.eq_ignore_ascii_case("calc")=>p.parse_nested_block(calc),
  Token::Dimension{..}=>Ok(()),
  _=>Err(ParseError::unexpected_token()),
 }
}
fn main(){
 let fixed=std::env::args().nth(1).unwrap()=="candidate";
 for limit in [0u8,1,2,3,75] {
  for depth in [1usize,2,3,4,74,75,76,77,100] {
   for retry in [false,true] {
    let raw=format!("{}1px{};color:blue;);color:green;", "calc(".repeat(depth),")".repeat(depth-1));
    let mut p=Parser::new(&raw);p.set_nested_block_limit(limit);
    let result:Result<(),ParseError<()>>=p.parse_until_after(Delimiter::Semicolon,|p|if retry {p.try_parse(calc)}else{calc(p)});
    assert!(result.is_err());let suffix=&raw[p.position().byte_index()..];
    let leaked=suffix.starts_with("color:blue");
    assert_eq!(leaked,!fixed && !retry && limit>0 && depth>limit as usize);
    if !leaked {assert_eq!(suffix,"color:green;");}
    println!("{{\"family\":\"unwind\",\"limit\":{limit},\"depth\":{depth},\"retry\":{retry},\"leaked\":{leaked},\"suffix\":{suffix:?}}}");
   }
  }
 }
 for (kind,open,close,wrong) in [("paren","(",")","]}"),("square","[","]", ")}"),("curly","{","}",")]")] {
  for (case,body) in ["", ";hidden", "\"; ) ] }\" /* ) ] } */", wrong,"child([nested]);hidden"].iter().enumerate() {
   for primed in [false,true] {
    let raw=format!("outer({open}{body}{close} marker);after()");
    let mut p=Parser::new(&raw);p.set_nested_block_limit(1);let mut invoked=false;let mut marker=false;
    let outer:Result<(),ParseError<()>>=p.parse_until_after(Delimiter::Semicolon,|p|{
     p.next()?;
     p.parse_nested_block(|p|{
      let before=p.state();p.next()?;if primed {p.reset(&before);p.next()?;}
      let child:Result<(),ParseError<()>>=p.parse_nested_block(|_|{invoked=true;Ok(())});assert!(matches!(child.unwrap_err().kind,ParseErrorKind::Basic(BasicParseErrorKind::TooManyNestedBlocks)));
      marker=matches!(p.next(),Ok(Token::Ident(n)) if *n=="marker");
      Ok(())
     })
    });
    assert!(!invoked);
    if fixed {assert!(outer.is_ok());assert!(marker);}
    assert!(matches!(p.next(),Ok(Token::Function(n)) if *n=="after"));
    let mut after=false;let result:Result<(),ParseError<()>>=p.parse_nested_block(|_|{after=true;Ok(())});assert!(after && result.is_ok());
    println!("{{\"family\":\"catch\",\"kind\":{kind:?},\"case\":{case},\"primed\":{primed},\"callback_invoked\":{invoked},\"marker\":{marker},\"after_callback\":{after}}}");
   }
  }
  for primed in [false,true] {
   let raw=format!("outer({open}; hidden");let mut p=Parser::new(&raw);p.set_nested_block_limit(1);p.next().unwrap();let mut invoked=false;let mut eof=false;
   let _:Result<(),ParseError<()>>=p.parse_nested_block(|p|{
    let s=p.state();p.next()?;if primed{p.reset(&s);p.next()?;}
    let result:Result<(),ParseError<()>>=p.parse_nested_block(|_|{invoked=true;Ok(())});assert!(matches!(result.unwrap_err().kind,ParseErrorKind::Basic(BasicParseErrorKind::TooManyNestedBlocks)));eof=p.position().byte_index()==raw.len();Ok(())
   });
   assert!(!invoked);if fixed{assert!(eof);}
   println!("{{\"family\":\"eof\",\"kind\":{kind:?},\"primed\":{primed},\"at_eof_after_rejection\":{eof}}}");
  }
 }
}
