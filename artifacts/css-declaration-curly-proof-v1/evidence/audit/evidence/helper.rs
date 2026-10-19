fn parse_non_custom_property_declaration_value_into(
    declarations: &mut SourcePropertyDeclaration,
    context: &ParserContext,
    input: &mut Parser,
    start: &cssparser::ParserState,
    parse_entirely_into: impl FnOnce(
        &mut SourcePropertyDeclaration,
        &mut Parser,
    ) -> Result<(), ParseError>,
    parsed_wide_keyword: impl FnOnce(&mut SourcePropertyDeclaration, CSSWideKeyword),
    parsed_custom: impl FnOnce(&mut SourcePropertyDeclaration, custom_properties::VariableValue),
) -> Result<(), ParseError> {
    let mut starts_with_curly_block = false;
    input.look_for_arbitrary_substitution_functions(ARBITRARY_SUBSTITUTION_FUNCTIONS);
    if let Ok(token) = input.next() {
        match token {
            cssparser::Token::Ident(ident) => {
                if let Ok(wk) = CSSWideKeyword::from_ident(ident)
                    && input.expect_exhausted().is_ok()
                {
                    parsed_wide_keyword(declarations, wk);
                    let _ = input.seen_arbitrary_substitution_functions();
                    return Ok(());
                }
            },
            cssparser::Token::CurlyBracketBlock => {
                starts_with_curly_block = true;
            },
            _ => {},
        }
    };

    input.reset(start);

    let mut saw_arbitrary_substitution_functions = false;
    let err = match parse_entirely_into(declarations, input) {
        Ok(()) => {
            saw_arbitrary_substitution_functions = input.seen_arbitrary_substitution_functions();
            if !saw_arbitrary_substitution_functions {
                return Ok(());
            }
            ParseError::custom(style_traits::StyleParseErrorKind::UnspecifiedError)
        },
        Err(e) => e,
    };

    // Look for var(), env() and top-level curly blocks after the error.
    let start_pos = start.position();
    let mut at_start = start_pos == input.position();
    let mut invalid = false;
    while let Ok(token) = input.next() {
        if matches!(token, cssparser::Token::CurlyBracketBlock) {
            if !starts_with_curly_block || !at_start {
                invalid = true;
                break;
            }
        } else if starts_with_curly_block {
            invalid = true;
            break;
        }
        at_start = false;
    }
    saw_arbitrary_substitution_functions =
        saw_arbitrary_substitution_functions || input.seen_arbitrary_substitution_functions();
    if !saw_arbitrary_substitution_functions || invalid {
        return Err(err);
    }
    input.reset(start);
    let value = custom_properties::VariableValue::parse(
        input,
        Some(&context.namespaces.prefixes),
        context.url_data,
    )?;
    parsed_custom(declarations, value);
    Ok(())
}
