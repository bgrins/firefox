use cssparser::{Parser, Token};
type ParseError = cssparser::ParseError<()>;
type SourcePropertyDeclaration = Vec<&'static str>;
struct Namespaces { prefixes: () }
struct ParserContext { namespaces: Namespaces, url_data: () }
enum CSSWideKeyword { Initial }
impl CSSWideKeyword {
    fn from_ident(s: &str) -> Result<Self, ()> {
        if s.eq_ignore_ascii_case("initial") { Ok(Self::Initial) } else { Err(()) }
    }
}
mod style_traits {
    pub struct StyleParseErrorKind;
    impl StyleParseErrorKind { #[allow(non_upper_case_globals)] pub const UnspecifiedError: () = (); }
}
mod custom_properties {
    pub struct VariableValue;
    impl VariableValue {
        pub fn parse(_: &mut cssparser::Parser, _: Option<&()>, _: ()) -> Result<Self, super::ParseError> {
            Ok(Self)
        }
    }
}
const ARBITRARY_SUBSTITUTION_FUNCTIONS: &[&str] = &["var", "env", "attr"];
include!("evidence/helper.rs");

fn main() {
    let cases = [
        "serif {var(--x)}", "serif, {var(--x)}", "{var(--x)} serif",
        "{var(--x)}", "var(--x)", "serif {env(x)}", "serif {attr(x)}",
        "serif {}", "serif [var(--x)]", "serif f({var(--x)})",
        "serif {} var(--x)", "serif, var(--x) {}", "serif",
    ];
    for mode in ["single", "comma"] {
        for value in cases {
            let mut parser = Parser::new(value);
            let start = parser.state();
            let context = ParserContext { namespaces: Namespaces { prefixes: () }, url_data: () };
            let mut decls = vec![];
            let result = parse_non_custom_property_declaration_value_into(
                &mut decls, &context, &mut parser, &start,
                |decls, input| {
                    let mut one = |i: &mut Parser| -> Result<(), ParseError> {
                        i.expect_ident_matching("serif")?;
                        Ok(())
                    };
                    if mode == "comma" { input.parse_comma_separated(&mut one)?; }
                    else { input.parse_entirely(one)?; }
                    decls.push("ordinary");
                    Ok(())
                },
                |d, _| d.push("wide"), |d, _| d.push("fallback-gateway"),
            );
            let mut oracle = Parser::new(value);
            let mut top_count = 0;
            let mut curly = false;
            while let Ok(t) = oracle.next() { top_count += 1; curly |= matches!(t, Token::CurlyBracketBlock); }
            let syntax_ok = !curly || top_count == 1;
            println!("{{\"mode\":{:?},\"value\":{:?},\"result\":{:?},\"gateway\":{},\"curly_rule\":{}}}", mode, value, result.is_ok(), decls.contains(&"fallback-gateway"), syntax_ok);
        }
    }
}
