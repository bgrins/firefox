import QuoteAppend
open QuoteAppend
example : (append explicitPairs initial .noOpen).childCache = childReference explicitPairs (append explicitPairs initial .noOpen) := by decide +kernel
