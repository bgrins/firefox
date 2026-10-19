use cssparser::Parser;
use std::io::{self, BufRead};
fn main() {
 for (case,line) in io::stdin().lock().lines().enumerate() {
  let line=line.unwrap(); let fields:Vec<_>=line.split('|').collect(); assert_eq!(fields.len(),2);
  let raw:Vec<u8>=(0..fields[0].len()).step_by(2).map(|i| u8::from_str_radix(&fields[0][i..i+2],16).unwrap()).collect();
  let source=String::from_utf8(raw).unwrap(); let mut parser=Parser::new(&source); let mut saved=Vec::new();
  println!("{case}|0|init|none|{}|none",parser.history_state());
  for (index,op) in fields[1].split(';').enumerate() {
   let mut result="none".to_string();
   match op {
    "fetch"|"stop" => { result=parser.history_fetch(op=="stop"); }
    "save" => saved.insert(0,parser.state()),
    "query" => result=parser.seen_arbitrary_substitution_functions().to_string(),
    _ if op.starts_with("reset:") => parser.reset(&saved[op[6..].parse::<usize>().unwrap()]),
    _ if op.starts_with("enable:") => {
      let names:Vec<&'static str>=op[7..].split(',').map(|s| &*Box::leak(s.to_owned().into_boxed_str())).collect();
      parser.look_for_arbitrary_substitution_functions(Box::leak(names.into_boxed_slice()));
    }
    _ => panic!("unknown operation"),
   }
   println!("{case}|{}|{op}|{result}|{}|{}",index+1,parser.history_state(),if saved.is_empty() { "none".into() } else { saved.iter().map(|s|s.history_cursor()).collect::<Vec<_>>().join(",") });
  }
 }
}
