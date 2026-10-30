import InputSelection
open InputSelection
example : (verify { initial with owner := .script, applied := 1250 } 1500 1500).applied = 1500 := by decide
