use cssparser::Parser;
use std::io::{self, BufRead};
fn main() {
    for (case,line) in io::stdin().lock().lines().enumerate() {
        let line=line.unwrap(); let fields:Vec<_>=line.split('|').collect();
        let raw:Vec<u8>=(0..fields[0].len()).step_by(2).map(|i| u8::from_str_radix(&fields[0][i..i+2],16).unwrap()).collect();
        let source=String::from_utf8(raw).unwrap(); let mut p=Parser::new(&source);
        println!("{case}|0|init|none|{}",p.nested_snapshot());
        for (i,op) in fields[1].split(';').enumerate() {
            let result=match op {
                "enable"=>{p.look_for_arbitrary_substitution_functions(&["var"]);"none".into()},
                "query"=>p.seen_arbitrary_substitution_functions().to_string(),
                "next"=>p.wrapper_next(false),
                "nested0fail"=>p.nested_probe(0,false).to_string(),
                "nested0ok"=>p.nested_probe(0,true).to_string(),
                "nested1ok"=>p.nested_probe(1,true).to_string(),
                "until0fail"=>p.until_probe(0,false).to_string(),
                "until0stop"=>p.until_probe(0,true).to_string(),
                "until1fail"=>p.until_probe(1,false).to_string(),
                "until1stop"=>p.until_probe(1,true).to_string(),
                "link"=>p.link_empty_projection().to_string(),
                _ if op.starts_with("limit")=>{p.nested_limit(op[5..].parse().unwrap());"none".into()},
                _ if op.starts_with("depth")=>{p.nested_depth(op[5..].parse().unwrap());"none".into()},
                _=>panic!("unknown operation"),
            };
            println!("{case}|{}|{op}|{result}|{}",i+1,p.nested_snapshot());
        }
    }
}
