import Mutant
open SubstitutedInherit
example : (resolve true false false (some 1) (some 10) witness).resetDependency = true ∧ (resolve true false true (some 1) (some 10) witness).resetDependency = false := by decide
