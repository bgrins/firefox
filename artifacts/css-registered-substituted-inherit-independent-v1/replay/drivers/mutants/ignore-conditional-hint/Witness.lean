import Mutant
open SubstitutedInherit
example : (refresh true ⟨some 20, true⟩ (resolve true false false (some 1) (some 10) witness)).value = some 20 := by decide
