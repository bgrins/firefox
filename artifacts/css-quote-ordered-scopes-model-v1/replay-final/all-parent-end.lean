import Examples
open QuoteAppend QuoteScopes QuoteScopes.Examples
example : scanChildStarts 0 interleaved = [2, 2, 2] := by
  decide +kernel
