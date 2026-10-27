import Examples
open QuoteAppend QuoteScopes QuoteScopes.Examples
example : assemble explicitPairs 0 [] inserted = reference explicitPairs 0 inserted := by
  simp only [inserted, assemble]
  decide +kernel
