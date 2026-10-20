pub fn parse_until_before<'i, F, T, E>(
    parser: &mut Parser<'i>,
    delimiters: Delimiters,
    error_behavior: ParseUntilErrorBehavior,
    parse: F,
) -> Result<T, ParseError<E>>
where
    F: FnOnce(&mut Parser<'i>) -> Result<T, ParseError<E>>,
{
    let old_stop_before = parser.stop_before;
    let delimiters = parser.stop_before | delimiters;
    parser.stop_before = delimiters;
    let result = parser.parse_entirely(parse);
    parser.stop_before = old_stop_before;
    if error_behavior == ParseUntilErrorBehavior::Stop && result.is_err() {
        return result;
    }
    parser.skip_block_at_start();
    // FIXME: have a special-purpose tokenizer method for this that does less work.
    while let Some(next_byte) = parser.next_byte() {
        if delimiters.contains(Delimiters::from_byte(next_byte)) {
            break;
        }
        parser.next_unchecked();
        parser.skip_block_at_start();
    }
    result
}
