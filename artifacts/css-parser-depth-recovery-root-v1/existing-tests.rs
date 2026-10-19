use cssparser::{Parser, ParseError, ParseErrorKind, BasicParseErrorKind};

#[test]
fn outer_block_end_consumed() {
    let mut input = Parser::new("(calc(true))");
    assert!(input.expect_parenthesis_block().is_ok());
    assert!(
        input
            .parse_nested_block(|input| input
                .expect_function_matching("calc")
                .map_err(Into::<ParseError<()>>::into))
            .is_ok()
    );
    println!("{:?}", input.position());
    assert!(input.next().is_err());
}

#[test]
fn nested_block_limit() {
    // Recursively descends into `calc(calc(calc(…1…)))`, which is the shape of expression that
    // would blow the stack without a nesting limit.
    fn parse_calc(input: &mut Parser) -> Result<(), ParseError<()>> {
        if input.try_parse(|input| input.expect_number()).is_ok() {
            return Ok(());
        }
        input.expect_function_matching("calc")?;
        input.parse_nested_block(parse_calc)
    }

    // Returns `Err(())` if (and only if) parsing bailed out due to the nesting limit.
    fn parse(depth: usize, limit: Option<u8>) -> Result<(), ()> {
        let css = format!("{}1{}", "calc(".repeat(depth), ")".repeat(depth));
        let mut parser = Parser::new(&css);
        if let Some(limit) = limit {
            parser.set_nested_block_limit(limit);
        }
        parser.parse_entirely(parse_calc).map_err(|e| match e.kind {
            ParseErrorKind::Basic(BasicParseErrorKind::TooManyNestedBlocks) => (),
            other => panic!(
                "Unexpected error parsing {} nested blocks: {:?}",
                depth, other
            ),
        })
    }

    // The default limit is 75 nested blocks.
    assert_eq!(parse(75, None), Ok(()));
    assert_eq!(parse(76, None), Err(()));
    assert_eq!(parse(10_000, None), Err(()));

    // The limit is configurable...
    assert_eq!(parse(3, Some(3)), Ok(()));
    assert_eq!(parse(4, Some(3)), Err(()));
    assert_eq!(parse(100, Some(255)), Ok(()));

    // ...and a limit of zero means no limit at all.
    assert_eq!(parse(1000, Some(0)), Ok(()));
}
