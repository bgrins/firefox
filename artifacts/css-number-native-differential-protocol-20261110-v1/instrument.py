import argparse
from pathlib import Path

HOOK = '''    let lexical_hex = |s: &str| s.as_bytes().iter().map(|b| format!("{b:02x}")).collect::<String>();
    eprintln!("TRACE\\t{}\\t{}\\t{}\\t{}\\t{}\\t{}\\t{}\\t{}\\t{}\\t{}\\t{}\\t{}\\t{}\\t{}\\t{}",
        start_position.byte_index(), parser.position().byte_index(),
        lexical_integral_start.byte_index(), lexical_integral_end.byte_index(),
        lexical_fraction_start.byte_index(), lexical_fraction_end.byte_index(),
        lexical_exponent_start.byte_index(), lexical_exponent_end.byte_index(),
        lexical_hex(parser.slice_from(start_position)),
        lexical_hex(&parser.input[parser.position().byte_index()..]),
        lexical_hex(parser.slice(lexical_integral_start..lexical_integral_end)),
        lexical_hex(parser.slice(lexical_fraction_start..lexical_fraction_end)),
        lexical_hex(parser.slice(lexical_exponent_start..lexical_exponent_end)), has_sign, is_integer);
'''
INSERTIONS = [
    ('    let mut integral_part: f64 = 0.;',
     '    let lexical_integral_start = parser.position();\n'),
    ('    let mut is_integer = true;',
     '    let lexical_integral_end = parser.position();\n    let mut lexical_fraction_start = lexical_integral_end;\n'),
    ('        let mut factor = 0.1;',
     '        lexical_fraction_start = parser.position();\n'),
    ('    let mut value = sign * (integral_part + fractional_part);',
     '    let lexical_fraction_end = parser.position();\n    let mut lexical_exponent_start = lexical_fraction_end;\n    let mut lexical_exponent_end = lexical_fraction_end;\n'),
    ('        let mut exponent: f64 = 0.;',
     '        lexical_exponent_start = parser.position();\n'),
    ('        value *= f64::powf(10., sign * exponent);',
     '        lexical_exponent_end = parser.position();\n'),
    ('    // Reparse long numbers as a whole:', HOOK),
]


def instrument(source):
    start = source.index('fn consume_numeric<')
    end = source.index('\n#[inline]\nunsafe fn from_utf8_release_unchecked', start)
    body = source[start:end]
    changed = body
    for anchor, insertion in INSERTIONS:
        if changed.count(anchor) != 1:
            raise ValueError('Ambiguous instrumentation anchor: ' + anchor)
        changed = changed.replace(anchor, insertion + anchor, 1)
    reversed_body = changed
    for anchor, insertion in reversed(INSERTIONS):
        if reversed_body.count(insertion + anchor) != 1:
            raise ValueError('Instrumentation reversal ambiguity')
        reversed_body = reversed_body.replace(insertion + anchor, anchor, 1)
    if reversed_body != body:
        raise ValueError('Instrumentation changed the original body')
    return source[:start] + changed + source[end:]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    raw = args.source.read_text()
    changed = instrument(raw)
    args.output.write_text(changed)


if __name__ == '__main__':
    main()
