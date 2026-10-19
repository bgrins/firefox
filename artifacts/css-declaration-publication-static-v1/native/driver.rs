
fn main() {
    let values=["param(--a, var(--x, red))","param(--a, env(not-real, red))","param(--a, attr(data-x))","param(--a, )","none","param(--a, var(invalid))","param(--a, var())","param(--a, env())","param(--a, red !important)","param(--a, var(--x)) junk","initial","var(--whole)","param(--a, var(--x)), param(--b, blue)"];
    for value in values {
        let context=ParserContext{namespaces:Namespaces{prefixes:Default::default()},url_data:&UrlExtraData};
        let mut ordinary=Parser::new(value);
        ordinary.look_for_arbitrary_substitution_functions(ARBITRARY_SUBSTITUTION_FUNCTIONS);
        let ordinary_ok=ordinary.parse_entirely(|i|LinkParameters::parse(&context,i)).is_ok();
        let seen=ordinary.seen_arbitrary_substitution_functions();
        let mut input=Parser::new(value);let start=input.state();let mut scratch=vec![];
        let result=parse_non_custom_property_declaration_value_into(&mut scratch,&context,&mut input,&start,
            |d,i|{i.parse_entirely(|i|LinkParameters::parse(&context,i))?;d.push("ordinary");Ok(())},
            |d,_|d.push("wide"),|d,_|d.push("with-variables"));
        println!("{{\"value\":{:?},\"ordinary_ok\":{},\"seen\":{},\"helper_ok\":{},\"scratch\":{:?}}}",value,ordinary_ok,seen,result.is_ok(),scratch);
    }
}
