MUTATIONS = {
    'reported-sign-lost': {
        'old': '    // Reparse long numbers as a whole:',
        'new': '    let has_sign = false;\n    // Reparse long numbers as a whole:',
        'witness': 'legacy-2-single',
        'changed_columns': ['hasSign'],
    },
    'exponent-type-lost': {
        'old': '    {\n        is_integer = false;\n        parser.advance(1);\n        let (has_sign, sign)',
        'new': '    {\n        parser.advance(1);\n        let (has_sign, sign)',
        'witness': 'legacy-8-single',
        'changed_columns': ['isInteger'],
    },
    'exponent-eof-lookahead': {
        'old': "    if parser.has_at_least(1)\n        && matches!(parser.next_byte_unchecked(), b'e' | b'E')",
        'new': "    if parser.has_at_least(2)\n        && matches!(parser.next_byte_unchecked(), b'e' | b'E')",
        'witness': 'legacy-8-single',
        'changed_columns': ['consumed', 'rest', 'exponentDigits', 'isInteger'],
    },
}


def mutate(source, name):
    if name == 'baseline':
        return source
    mutation = MUTATIONS[name]
    start = source.index('fn consume_numeric<')
    end = source.index('\n#[inline]\nunsafe fn from_utf8_release_unchecked', start)
    body = source[start:end]
    if body.count(mutation['old']) != 1:
        raise ValueError('Mutation anchor changed: ' + name)
    changed = body.replace(mutation['old'], mutation['new'], 1)
    if changed.replace(mutation['new'], mutation['old'], 1) != body:
        raise ValueError('Mutation is not reversible')
    return source[:start] + changed + source[end:]
