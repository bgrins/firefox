import QuoteAppend
open QuoteAppend
example : (deliver explicitPairs { append explicitPairs initial .noOpen with dirty := false }).childCache = [⟨1, "AAA"⟩, ⟨2, "AAA"⟩] := by decide +kernel
