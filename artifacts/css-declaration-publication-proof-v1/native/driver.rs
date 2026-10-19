
fn main() {
    let values=["param(--a, var(--x, red))","param(--a, env(not-real, red))","param(--a, attr(data-x))","param(--a, )","none","param(--a, var(invalid))","param(--a, var())","param(--a, env())","param(--a, red !important)","param(--a, var(--x)) junk","initial","var(--whole)","param(--a, var(--x)), param(--b, blue)"];
    for value in values {
        let context=ParserContext{namespaces:Namespaces{prefixes:Default::default()},url_data:&UrlExtraData};
        let mut ordinary=Parser::new(value);
        ordinary.look_for_arbitrary_substitution_functions(ARBITRARY_SUBSTITUTION_FUNCTIONS);
        let ordinary_ok=ordinary.parse_entirely(|i|LinkParameters::parse(&context,i)).is_ok();
        let seen=ordinary.seen_arbitrary_substitution_functions();
        let mut input=Parser::new(value);let start=input.state();let mut scratch=SourcePropertyDeclaration::default();
        let result=parse_non_custom_property_declaration_value_into(&mut scratch,&context,&mut input,&start,
            |d,i|{i.parse_entirely(|i|LinkParameters::parse(&context,i))?;d.push("ordinary");Ok(())},
            |d,_|d.push("wide"),|d,_|d.push("with-variables"));
        println!("{{\"value\":{:?},\"ordinary_ok\":{},\"seen\":{},\"helper_ok\":{},\"scratch\":{:?}}}",value,ordinary_ok,seen,result.is_ok(),scratch.declarations);
    }
    for mode in ["failure-declarations","failure-all"] {
        let context=ParserContext{namespaces:Namespaces{prefixes:Default::default()},url_data:&UrlExtraData};
        let mut input=Parser::new("var(invalid)");let start=input.state();let mut scratch=SourcePropertyDeclaration::default();
        let result=parse_non_custom_property_declaration_value_into(&mut scratch,&context,&mut input,&start,
            |d,i|{while i.next().is_ok() {} if mode=="failure-all" {d.all_shorthand=AllShorthand::Marker(9)}else{d.push("ordinary")};Ok(())},
            |d,_|d.push("wide"),|d,_|d.push("with-variables"));
        println!("{{\"mode\":{:?},\"helper_ok\":{},\"declarations\":{:?},\"all_present\":{}}}",mode,result.is_ok(),scratch.declarations,!matches!(scratch.all_shorthand,AllShorthand::NotSet));
    }
    let mut scratch=SourcePropertyDeclaration::with_one("ordinary");
    scratch.all_shorthand=AllShorthand::Marker(9);
    let (drained,all)= {let d=scratch.drain();(d.declarations.collect::<Vec<_>>(),matches!(d.all_shorthand,AllShorthand::Marker(9)))};
    println!("{{\"mode\":\"drain\",\"drained\":{:?},\"all_drained\":{},\"empty_after\":{}}}",drained,all,scratch.is_empty());
}
