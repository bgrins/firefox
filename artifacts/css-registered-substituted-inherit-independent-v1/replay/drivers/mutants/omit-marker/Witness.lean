import Mutant
open SubstitutedInherit
example : (resolve true false false (some 1) (some 10) witness).resetDependency = true := by decide
