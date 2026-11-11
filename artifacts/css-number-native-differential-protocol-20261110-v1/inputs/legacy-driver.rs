fn hex(bytes:&[u8])->String { bytes.iter().map(|b|format!("{b:02x}")).collect() }
fn main() {
 for line in io::stdin().lock().lines() {
  let line=line.unwrap();
  let bytes:Vec<u8>=(0..line.len()).step_by(2).map(|i|u8::from_str_radix(&line[i..i+2],16).unwrap()).collect();
  let css=String::from_utf8(bytes).unwrap();
  let mut parser=Parser::new(&css);
  let token=parser.next_including_whitespace_and_comments().unwrap().clone();
  let (kind,unit,sign,integer,value)=match token {
   Token::Number{has_sign,int_value,value} => ("number",String::new(),has_sign,int_value.is_some(),value),
   Token::Percentage{has_sign,int_value,unit_value} => ("percentage",String::new(),has_sign,int_value.is_some(),unit_value),
   Token::Dimension{has_sign,int_value,value,unit} => ("dimension",unit.to_string(),has_sign,int_value.is_some(),value),
   _ => ("other",String::new(),false,false,0.0),
  };
  let flags=if kind=="dimension" {ReferenceFlags::from_unit(&unit.as_str().into()).0} else {0};
  let consumed=parser.position().byte_index();
  assert!(css.is_char_boundary(consumed));
  println!("{}\t{}\t{}\t{}\t{}\t{}\t{:08x}\t{}\t{}",kind,consumed,hex(unit.as_bytes()),flags,sign,integer,value.to_bits(),resolved_token_dependencies(&css).map_or(-1,|f|f.0 as i32),hex(&css.as_bytes()[consumed..]));
 }
}
