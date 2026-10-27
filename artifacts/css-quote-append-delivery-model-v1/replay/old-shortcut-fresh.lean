import QuoteAppend
open QuoteAppend
example : (deliver explicitPairs (legacyAppend explicitPairs initial .noOpen)).childCache = childReference explicitPairs (legacyAppend explicitPairs initial .noOpen) := by decide +kernel
