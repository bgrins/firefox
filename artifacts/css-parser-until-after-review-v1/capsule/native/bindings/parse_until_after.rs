pub fn parse_until_after<'i, F, T, E>(
    parser: &mut Parser<'i>,
    delimiters: Delimiters,
    error_behavior: ParseUntilErrorBehavior,
    parse: F,
) -> Result<T, ParseError<E>>
where
    F: FnOnce(&mut Parser<'i>) -> Result<T, ParseError<E>>,
{
    let result = parse_until_before(parser, delimiters, error_behavior, parse);
    if error_behavior == ParseUntilErrorBehavior::Stop && result.is_err() {
        return result;
    }
    if let Some(next_byte) = parser.next_byte() {
        let delimiter = Delimiters::from_byte(next_byte);
        if !parser.stop_before.contains(delimiter) {
            debug_assert!(delimiters.contains(delimiter));
            // We know this byte is ASCII.
            parser.advance(1);
            if next_byte == b'{' {
                parser.consume_until_end_of_block(BlockType::CurlyBracket);
            }
        }
    }
    result
}
