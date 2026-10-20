use cssparser::Parser;
use std::io::{self, BufRead};
fn main() {
    for (case, line) in io::stdin().lock().lines().enumerate() {
        let line = line.unwrap(); let fields: Vec<_> = line.split('|').collect();
        assert_eq!(fields.len(), 2);
        let raw: Vec<u8> = (0..fields[0].len()).step_by(2).map(|i| u8::from_str_radix(&fields[0][i..i+2], 16).unwrap()).collect();
        let source = String::from_utf8(raw).unwrap(); let mut p = Parser::new(&source); let mut saved = None;
        println!("{case}|0|init|none|{}", p.after_snapshot());
        for (i, op) in fields[1].split(';').enumerate() {
            let args: Vec<_> = op.split(':').collect();
            let result = match args[0] {
                "enable" => { p.look_for_arbitrary_substitution_functions(&["var", "env", "attr"]); "none".into() },
                "query" => p.seen_arbitrary_substitution_functions().to_string(),
                "next" => p.after_next(),
                "save" => { saved = Some(p.state()); "none".into() },
                "reset" => { p.reset(saved.as_ref().unwrap()); "none".into() },
                "outer" => { p.after_outer(args[1].parse().unwrap()); "none".into() },
                "limit" => { p.after_limit(args[1].parse().unwrap()); "none".into() },
                "depth" => { p.after_depth(args[1].parse().unwrap()); "none".into() },
                "after" => p.after_probe(args[1].parse().unwrap(), args[2].parse().unwrap(), args[3] == "1", args[4] == "1").to_string(),
                _ => panic!("unknown operation"),
            };
            println!("{case}|{}|{op}|{result}|{}", i+1, p.after_snapshot());
        }
    }
}
