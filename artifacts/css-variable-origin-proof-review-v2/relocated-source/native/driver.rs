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
        let (mode, line)=line.split_once('|').unwrap();
        let (offset, line)=line.split_once('|').unwrap();
        let offset:usize=offset.parse().unwrap();
        let bytes=(0..line.len()).step_by(2).map(|i|u8::from_str_radix(&line[i..i+2],16).unwrap()).collect();
        let source=String::from_utf8(bytes).unwrap();
        let mut parser=Parser::new(&source);
        while parser.position().byte_index() < offset {
            parser.next_including_whitespace_and_comments().unwrap();
        }
        assert_eq!(parser.position().byte_index(),offset);
        parser.look_for_arbitrary_substitution_functions(&["var", "env", "attr"]);
        if mode == "cached" {
            let state = parser.state();
            let _ = parser.next_including_whitespace_and_comments();
            parser.reset(&state);
        }
        let value=match VariableValue::parse(&mut parser,None,&UrlExtraData) {
            Ok(v)=>v,
            Err(_)=>{println!("{{\"index\":{index},\"parse\":\"ERR\"}}");continue;}
        };
        let observed = parser.seen_arbitrary_substitution_functions();
        let mut refs=Vec::new();refs_json(&value.references.refs,&mut refs);
        let result=std::panic::catch_unwind(std::panic::AssertUnwindSafe(||{
            let functions=ComputedSubstitutionFunctions{present:true};
            let mut taint=AttrTaint::default();
            substitute_internal(&value,None,&functions,&Stylist,&computed::Context,&mut AttributeTracker,&mut SmallVec::new(),Some(&mut taint)).map(|v|(v.css.into_owned(),taint.0.iter().map(|r|(r.start,r.end)).collect::<Vec<_>>(),v.attr_tainted))
        }));
        let (status,output,ranges,aggregate)=match result {
            Ok(Ok((v,rs,a)))=>("OK",hex(&v),rs,a),
            Ok(Err(()))=>("ERR",String::new(),Vec::new(),false),
            Err(_)=>("PANIC",String::new(),Vec::new(),false)};
        let ranges=ranges.iter().map(|(a,b)|format!("[{a},{b}]")).collect::<Vec<_>>().join(",");
        println!("{{\"index\":{index},\"css_hex\":\"{}\",\"length\":{},\"refs\":[{}],\"status\":\"{status}\",\"output_hex\":\"{output}\",\"taint\":[{ranges}],\"aggregate\":{aggregate},\"observed\":{observed}}}",hex(&value.css),value.css.len(),refs.join(","));
    }
}
