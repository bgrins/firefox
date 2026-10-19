fn decoded(raw: &str) -> (String, usize) {
 let mut p=Parser::new(raw);
 let value=match p.next().unwrap(){Token::QuotedString(s)=>s.to_string(),t=>panic!("unexpected {:?}",t)};
 (value,p.position().byte_index())
}
fn main(){
 for (name,q) in [("double",'"'),("single",'\'')] {
  for n in 0..5 { for terminal in 0..2 {
   let raw=format!("{q}example{}{}","\\".repeat(n),if terminal==1{q.to_string()}else{String::new()});
   let expected=format!("example{}{}","\\".repeat(n/2),if terminal==1&&n%2==1{q.to_string()}else{String::new()});
   assert_eq!(decoded(&raw).0,expected,"independent pair grammar must match actual source tokenizer");
   let repaired=recover(&raw);let appended=format!("{repaired}, serif");let(value,end)=decoded(&appended);
   let ok=value==expected&&&appended[end..]==", serif";
   println!("{{\"id\":\"{name}-{n}-{terminal}\",\"ok\":{ok},\"decoded_preserved\":{},\"suffix_outside\":{}}}",value==expected,&appended[end..]==", serif");
  }}
  let raw=q.to_string();let repaired=recover(&raw);let appended=format!("{repaired}, serif");let(value,end)=decoded(&appended);
  let ok=value.is_empty()&&&appended[end..]==", serif";
  println!("{{\"id\":\"{name}-opening-only\",\"ok\":{ok}}}");
 }
}
