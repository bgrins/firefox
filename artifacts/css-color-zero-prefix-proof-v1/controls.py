MUTATIONS = {
    'SkipNormalizedZero': [('if !normalize && combined == 0 then a', 'if combined == 0 then a')],
    'ZeroInterpolationWeights': [('if combined == 0 then ((1/2 : Rat), (1/2 : Rat))', 'if combined == 0 then ((0 : Rat), (0 : Rat))')],
    'GivePrefixUnitWeight': [('⟨mix a.color weights.1 b.color weights.2, combined⟩', '⟨mix a.color weights.1 b.color weights.2, if combined == 0 then 1 else combined⟩')],
    'NormalizeRawCancellation': [
        ('if !normalize && combined == 0 then a', 'if false then a'),
        ('let weights := if normalize then\n      if combined', 'let weights := if normalize || combined == 0 then\n      if combined'),
    ],
}
