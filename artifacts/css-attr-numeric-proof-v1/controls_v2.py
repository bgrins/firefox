LEAN_MUTATIONS = {
    'PrefixOnly': (
        '| .number p :: rest => if (significant rest).isEmpty then some p else none',
        '| .number p :: _ => some p'),
    'EraseSign': (
        '| .number => .number p',
        '| .number => .number { p with negative := false }'),
    'WrongPercentage': (
        '| .percentage => .percentage p',
        '| .percentage => .number p'),
    'ClearTaint': (
        '(parseWhole tokens).map fun p => ⟨construct p unit, true⟩',
        '(parseWhole tokens).map fun p => ⟨construct p unit, false⟩'),
    'DiscardFallback': (
        '| none => fallback\n',
        '| none => none\n'),
}

RUST_MUTATIONS = {
    'PrefixOnly': ('parser.expect_exhausted().ok()?;', ''),
    'KeepRawInput': ('String::from(parser.slice_from(start))', 'String::from(attr)'),
    'KeepLeadingTrivia': ('parser.skip_whitespace();', ''),
    'OmitUnit': ('s.push_str(unit);', ''),
}
