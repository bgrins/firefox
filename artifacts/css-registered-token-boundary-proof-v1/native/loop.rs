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
