use cssparser::{Parser, Token};

fn candidate(attr: &str, unit: &str) -> Option<String> {
    let mut parser = Parser::new(attr);
    CANDIDATE_BODY
}

fn number_bits(text: &str) -> (u32, Option<i32>, bool) {
    let mut parser = Parser::new(text);
    let result = match *parser.next().unwrap() {
        Token::Number { value, int_value, has_sign } => (value.to_bits(), int_value, has_sign),
        _ => panic!("Not a number: {text:?}"),
    };
    parser.expect_exhausted().unwrap();
    result
}

fn check_constructed(text: &str, unit: &str, lexeme: &str) {
    let expected = number_bits(lexeme);
    let mut parser = Parser::new(text);
    let token = parser.next().unwrap();
    match token {
        Token::Number { value, int_value, has_sign } if unit.is_empty() => {
            assert_eq!((value.to_bits(), *int_value, *has_sign), expected);
        }
        Token::Percentage { unit_value, int_value, has_sign } if unit == "%" => {
            assert_eq!(unit_value.to_bits(), ((lexeme.parse::<f64>().unwrap() / 100.) as f32).to_bits());
            assert_eq!((*int_value, *has_sign), (expected.1, expected.2));
        }
        Token::Dimension { value, int_value, has_sign, unit: actual_unit } if !unit.is_empty() && unit != "%" => {
            assert_eq!((value.to_bits(), *int_value, *has_sign), expected);
            assert_eq!(&**actual_unit, unit);
        }
        _ => panic!("Wrong constructed token: {text:?}: {token:?}"),
    }
    parser.expect_exhausted().unwrap();
}

fn main() {
    let accepted = [
        ("10", "10"), (" 10 ", "10"), ("\t10\t", "10"),
        ("\n10\n", "10"), ("\r10\r", "10"), ("\x0c10\x0c", "10"),
        ("\r\n +1.25e2\t", "+1.25e2"), (".2", ".2"), ("+0", "+0"),
        ("-0", "-0"), ("-0.0", "-0.0"), ("-0e10", "-0e10"),
        ("1e2", "1e2"), ("1E+2", "1E+2"), ("1e-2", "1e-2"),
        ("1e1000", "1e1000"), ("-1e1000", "-1e1000"),
        ("1e-1000", "1e-1000"), ("-1e-1000", "-1e-1000"),
        ("16777217", "16777217"), ("2147483648", "2147483648"),
        ("10/**/", "10"), ("/**/10", "10"), (" /*x*/ 10 /*y*/ ", "10"),
        ("10/*unterminated", "10"),
    ];
    let rejected = ["", " ", "10 20", "10 junk", ".2 junk", "10px", "10%",
        "calc(10)", "var(--x)", "1e", "1e+", "10/**/20", "10/**/px",
        "10;", "10)", "10()", "10,", "NaN", "infinity", "10\u{a0}",
        "\u{a0}10", "10\u{b}", "10\0", "--1", "1."];
    let units = UNITS;
    let mut checked = 0;
    for (attr, lexeme) in accepted {
        for unit in units {
            let result = candidate(attr, unit).expect("Rejected valid numeric input");
            assert_eq!(result, format!("{lexeme}{unit}"), "attr {attr:?}, unit {unit:?}");
            check_constructed(&result, unit, lexeme);
            checked += 1;
        }
    }
    for attr in rejected {
        for unit in units {
            assert!(candidate(attr, unit).is_none(), "Accepted invalid input {attr:?}");
            checked += 1;
        }
    }
    println!("bridge cases passed: {checked}");
}
