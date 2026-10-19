fn hex(s:&str)->String {s.as_bytes().iter().map(|b|format!("{b:02x}")).collect()}
fn refs_json(refs:&[SubstitutionFunctionReference],out:&mut Vec<String>) {
    for r in refs {
        out.push(format!("[{}, {}, {}]",r.start,r.end,r.fallback.as_ref().map_or(0,|f|f.start.get())));
        if let Some(f)=&r.fallback {refs_json(&f.references.refs,out);}
    }
}
fn main() {
    std::panic::set_hook(Box::new(|_|{}));
    for (index,line) in io::stdin().lock().lines().enumerate() {
        let line=line.unwrap();
        let bytes=(0..line.len()).step_by(2).map(|i|u8::from_str_radix(&line[i..i+2],16).unwrap()).collect();
        let source=String::from_utf8(bytes).unwrap();
        let mut parser=Parser::new(&source);
        parser.skip_whitespace();
        let value=VariableValue::parse(&mut parser,None,&UrlExtraData).unwrap();
        let mut refs=Vec::new();refs_json(&value.references.refs,&mut refs);
        let result=std::panic::catch_unwind(std::panic::AssertUnwindSafe(||{
            let functions=ComputedSubstitutionFunctions{present:true};
            substitute_internal(&value,None,&functions,&Stylist,&computed::Context,&mut AttributeTracker,&mut SmallVec::new(),None).map(|v|v.css.into_owned())
        }));
        let (status,output)=match result {Ok(Ok(v))=>("OK",hex(&v)),Ok(Err(()))=>("ERR",String::new()),Err(_)=>("PANIC",String::new())};
        println!("{{\"index\":{index},\"css_hex\":\"{}\",\"length\":{},\"refs\":[{}],\"status\":\"{status}\",\"output_hex\":\"{output}\"}}",hex(&value.css),value.css.len(),refs.join(","));
    }
}
