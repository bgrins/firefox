import Examples
open QuoteAppend QuoteScopes QuoteScopes.Examples
example : stale = staged explicitPairs 0 inserted := by
  simp only [stale, staged_eq_reference]
  decide +kernel
