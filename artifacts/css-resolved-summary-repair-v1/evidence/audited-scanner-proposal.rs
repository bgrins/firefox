// Artifact-only proposal; not compiled or installed.
fn resolved_unit_flags(mut css: &str) -> Option<ReferenceFlags> {
    let mut flags = ReferenceFlags::empty();
    while !css.is_empty() {
        let mut input = Parser::new(css);
        match input.next_including_whitespace_and_comments().ok()? {
            Token::Dimension { unit, .. } => flags.insert(ReferenceFlags::from_unit(unit)),
            Token::Function(name) if SubstitutionFunctionKind::from_ident(name).is_ok() => {
                return None;
            },
            Token::BadUrl(_) | Token::BadString(_) => return None,
            _ => {},
        }
        let consumed = input.position().byte_index();
        debug_assert!(consumed > 0);
        css = &css[consumed..];
    }
    Some(flags)
}
