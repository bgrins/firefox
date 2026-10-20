use cssparser::{Parser as CSSParser, Token, TokenSerializationType as T};
type TokenSerializationType = T;
fn scan(css: &str) -> (T,T) {
        let mut input = CSSParser::new(&css);
        let mut first = TokenSerializationType::Nothing;
        let mut last = TokenSerializationType::Nothing;
        while let Ok(token) = input.next_including_whitespace() {
            first.set_if_nothing(token.serialization_type());
            last = match token {
                // The parser skips nested blocks, including their closing token.
                Token::Function(_)
                | Token::ParenthesisBlock
                | Token::SquareBracketBlock
                | Token::CurlyBracketBlock => TokenSerializationType::Other,
                _ => token.serialization_type(),
            };
        }
        drop(input);
(first,last)
}
fn main() {
    for (css, expected) in [
        ("[20px]25%", (T::Other, T::Percentage)),
        ("/**/calc(20px)/**/ 1", (T::Function, T::Number)),
        ("\"\"ident", (T::Other, T::Ident)),
    ] {
        let flat = cssparser::codex_flat_classes(css);
        assert_eq!((flat[0], *flat.last().unwrap()), expected);
        assert_eq!(scan(css), expected);
        println!("valid {css:?}: {expected:?}");
    }
    let incomplete = "f(20px";
    let flat = cssparser::codex_flat_classes(incomplete);
    assert_eq!(scan(incomplete), (T::Function, T::Other));
    assert_eq!((flat[0], *flat.last().unwrap()), (T::Function, T::Dimension));
    println!("unclosed input excluded: scanner closing boundary differs from raw last token");
}
