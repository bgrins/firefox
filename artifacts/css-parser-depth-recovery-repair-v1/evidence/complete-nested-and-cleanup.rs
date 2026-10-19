pub fn parse_nested_block<'i, F, T, E>(
    parser: &mut Parser<'i>,
    parse: F,
) -> Result<T, ParseError<E>>
where
    F: FnOnce(&mut Parser<'i>) -> Result<T, ParseError<E>>,
{
    let block_type = parser.state.take_at_start_of().expect(
        "\
         A nested parser can only be created when a Function, \
         ParenthesisBlock, SquareBracketBlock, or CurlyBracketBlock \
         token was just consumed.\
         ",
    );
    if parser.current_block_depth >= parser.nested_block_limit && parser.nested_block_limit != 0 {
        parser.consume_until_end_of_block(block_type);
        return Err(ParseError::from_basic_kind(
            BasicParseErrorKind::TooManyNestedBlocks,
        ));
    }
    // Fine to use wrapping addition, overflow can only occur without a limit.
    parser.current_block_depth = parser.current_block_depth.wrapping_add(1);

    let old_stop_before = parser.stop_before;
    parser.stop_before = match block_type {
        BlockType::CurlyBracket => ClosingDelimiter::CloseCurlyBracket,
        BlockType::SquareBracket => ClosingDelimiter::CloseSquareBracket,
        BlockType::Parenthesis => ClosingDelimiter::CloseParenthesis,
    };
    let result = parser.parse_entirely(parse);
    parser.skip_block_at_start();
    parser.consume_until_end_of_block(block_type);
    parser.stop_before = old_stop_before;
    parser.current_block_depth = parser.current_block_depth.wrapping_sub(1);
    result
}

impl Parser<'_> {
    /// Consume tokens until the end of a block of the given type that we're at the start of,
    /// ignoring any `stop_before` delimiters.
    #[inline(never)]
    #[cold]
    pub(crate) fn consume_until_end_of_block(&mut self, block_type: BlockType) {
        let mut stack = SmallVec::<[BlockType; 16]>::new();
        stack.push(block_type);

        // FIXME: have a special-purpose tokenizer method for this that does less work.
        while !self.is_eof() {
            let token = self.next_unchecked();
            if let Some(nested_block_type) = self.state.take_at_start_of() {
                stack.push(nested_block_type);
                continue;
            }
            if let Some(b) = BlockType::closing(&token) {
                if *stack.last().unwrap() == b {
                    stack.pop();
                    if stack.is_empty() {
                        return;
                    }
                }
            }
        }
    }
}
