use cssparser::{Parser, Token};
fn track(raw: &str, colon: bool, reset: bool) {
    let mut p = Parser::new(raw);
    if colon { p.expect_ident().unwrap(); p.expect_colon().unwrap(); }
    p.skip_whitespace();
    let start = p.state();
    p.look_for_arbitrary_substitution_functions(&["var", "env", "attr"]);
    assert!(matches!(p.next(), Ok(Token::Function(_))));
    if reset { p.reset(&start); }
    while p.next().is_ok() {}
    assert!(p.seen_arbitrary_substitution_functions());
    println!("{{\"case\":\"entry-prefix\",\"raw\":{raw:?},\"colon\":{colon},\"reset\":{reset},\"seen\":true}}");
}
fn main() {
    for reset in [false, true] {
        track("var(--x)", false, reset);
        track("width: /* comment */ var(--x)", true, reset);
        track("width: calc(var(--x) + 1px)", true, reset);
    }
    for primed in [false, true] {
        let mut p = Parser::new("var(--x)"); let start = p.state();
        if primed { p.next().unwrap(); p.reset(&start); }
        p.look_for_arbitrary_substitution_functions(&["var"]);
        p.next().unwrap();
        let seen = p.seen_arbitrary_substitution_functions();
        assert_eq!(seen, !primed);
        println!("{{\"case\":\"late-enable\",\"primed\":{primed},\"seen\":{seen}}}");
    }
    for directive in ["sourceURL", "sourceMappingURL"] {
        for replay in [0, 1, 2] {
            let raw = format!("(/*# {directive}=A */)/*# {directive}=B */");
            let mut p = Parser::new(&raw); p.next().unwrap(); let inside = p.state();
            p.next_including_whitespace_and_comments().unwrap();
            assert_eq!(if directive == "sourceURL" { p.current_source_url() } else { p.current_source_map_url() }, Some("B"));
            p.reset(&inside);
            match replay {
                0 => { while p.next_including_whitespace_and_comments().is_ok() {} }
                1 => { while p.next().is_ok() {} }
                _ => {
                    p.parse_nested_block::<_, _, ()>(|i| i.expect_no_error_token().map_err(Into::into)).unwrap();
                    while p.next_including_whitespace_and_comments().is_ok() {}
                }
            }
            let actual = if directive == "sourceURL" { p.current_source_url() } else { p.current_source_map_url() };
            assert_eq!(actual, Some(if replay == 0 { "A" } else { "B" }));
            assert_eq!(p.position().byte_index(), raw.len());
            println!("{{\"case\":\"comment-replay\",\"field\":\"{directive}\",\"replay\":{replay},\"url\":\"{}\",\"eof\":true}}", actual.unwrap());
        }
    }
}
