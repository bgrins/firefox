import Examples
open QuoteAppend QuoteScopes QuoteScopes.Examples
example : staged explicitPairs 3 (.scope (.scope pair .empty) .empty) = staged explicitPairs 0 (.scope (.scope pair .empty) .empty) := by
  simp only [staged_eq_reference]
  decide +kernel
