#[cfg(test)]
mod unit_token_classification_tests {
    use super::{Parser, ReferenceFlags, References, parse_declaration_value};

    fn parse(css: &str) -> (ReferenceFlags, String) {
        let mut input = Parser::new(css);
        let start = input.position();
        let mut references = References::default();
        let mut missing = String::new();
        parse_declaration_value(&mut input, start, None, &mut references, &mut missing).unwrap();
        input.expect_exhausted().unwrap();
        (references.flags, missing)
    }

    #[test]
    fn only_dimensions_contribute_unit_flags() {
        let empty = ReferenceFlags::empty();
        for (css, expected) in [
            ("em", empty),
            ("EM", empty),
            ("e\\6d", empty),
            ("lh", empty),
            ("@em", empty),
            ("#em", empty),
            ("#123", empty),
            ("url(em)", empty),
            ("url(\"em\")", empty),
            ("\"1em\"", empty),
            ("1/**/em", empty),
            ("13px", empty),
            ("1em", ReferenceFlags::FONT_UNITS),
            ("1e\\6d", ReferenceFlags::FONT_UNITS),
            ("calc(1em + 2px)", ReferenceFlags::FONT_UNITS),
            ("1lh", ReferenceFlags::FONT_UNITS | ReferenceFlags::LH_UNITS),
            ("1rem", ReferenceFlags::ROOT_FONT_UNITS),
            ("1rlh", ReferenceFlags::ROOT_FONT_UNITS | ReferenceFlags::ROOT_LH_UNITS),
        ] {
            assert_eq!(parse(css), (expected, String::new()), "{css}");
        }
    }

    #[test]
    fn shared_escape_and_url_repair_is_preserved() {
        assert_eq!(parse("url(em"), (ReferenceFlags::empty(), ")".into()));
        assert_eq!(parse("em\\"), (ReferenceFlags::empty(), "�".into()));
        assert_eq!(parse("1em\\"), (ReferenceFlags::empty(), "�".into()));
    }
}
