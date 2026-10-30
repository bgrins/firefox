import MaskedBaseInput
open MaskedBaseInput
example : (fun (_ : Nat) => 0) 16 ≠ (fun (_ : Nat) => 0) 32 := by decide
