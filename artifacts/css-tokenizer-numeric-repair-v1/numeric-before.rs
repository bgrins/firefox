fn consume_numeric<'a>(parser: &mut Parser<'a>) -> Token<'a> {
    // Parse [+-]?\d*(\.\d+)?([eE][+-]?\d+)?
    // But this is always called so that there is at least one digit in \d*(\.\d+)?

    // Do all the math in f64 so that large numbers overflow to +/-inf
    // and i32::{MIN, MAX} are within range.

    let (has_sign, sign) = match parser.next_byte_unchecked() {
        b'-' => (true, -1.),
        b'+' => (true, 1.),
        _ => (false, 1.),
    };
    if has_sign {
        parser.advance(1);
    }

    let mut integral_part: f64 = 0.;
    while let Some(digit) = byte_to_decimal_digit(parser.next_byte_unchecked()) {
        integral_part = integral_part * 10. + digit as f64;
        parser.advance(1);
        if parser.is_eof() {
            break;
        }
    }

    let mut is_integer = true;

    let mut fractional_part: f64 = 0.;
    if parser.has_at_least(1)
        && parser.next_byte_unchecked() == b'.'
        && parser.byte_at(1).is_ascii_digit()
    {
        is_integer = false;
        parser.advance(1); // Consume '.'
        let mut factor = 0.1;
        while let Some(digit) = byte_to_decimal_digit(parser.next_byte_unchecked()) {
            fractional_part += digit as f64 * factor;
            factor *= 0.1;
            parser.advance(1);
            if parser.is_eof() {
                break;
            }
        }
    }

    let mut value = sign * (integral_part + fractional_part);

    if parser.has_at_least(1)
        && matches!(parser.next_byte_unchecked(), b'e' | b'E')
        && (parser.byte_at(1).is_ascii_digit()
            || (parser.has_at_least(2)
                && matches!(parser.byte_at(1), b'+' | b'-')
                && parser.byte_at(2).is_ascii_digit()))
    {
        is_integer = false;
        parser.advance(1);
        let (has_sign, sign) = match parser.next_byte_unchecked() {
            b'-' => (true, -1.),
            b'+' => (true, 1.),
            _ => (false, 1.),
        };
        if has_sign {
            parser.advance(1);
        }
        let mut exponent: f64 = 0.;
        while let Some(digit) = byte_to_decimal_digit(parser.next_byte_unchecked()) {
            exponent = exponent * 10. + digit as f64;
            parser.advance(1);
            if parser.is_eof() {
                break;
            }
        }
        value *= f64::powf(10., sign * exponent);
    }

    let int_value = if is_integer {
        Some(if value >= i32::MAX as f64 {
            i32::MAX
        } else if value <= i32::MIN as f64 {
            i32::MIN
        } else {
            value as i32
        })
    } else {
        None
    };

    if !parser.is_eof() && parser.next_byte_unchecked() == b'%' {
        parser.advance(1);
        return Percentage {
            unit_value: (value / 100.) as f32,
            int_value,
            has_sign,
        };
    }
    let value = value as f32;
    if is_ident_start(parser) {
        let unit = consume_name(parser);
        Dimension {
            value,
            int_value,
            has_sign,
            unit,
        }
    } else {
        Number {
            value,
            int_value,
            has_sign,
        }
    }
}
