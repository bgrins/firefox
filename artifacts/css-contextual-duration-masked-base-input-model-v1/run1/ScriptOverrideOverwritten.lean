import MaskedBaseInput
open MaskedBaseInput
example : (inputStep maskedView duration { before with owner := .script, applied := 1250 } 32).applied = 2000 := by decide
