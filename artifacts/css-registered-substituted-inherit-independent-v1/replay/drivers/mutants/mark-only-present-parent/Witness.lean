import Mutant
open SubstitutedInherit
example : (resolve true false false (some 1) none absent).resetDependency = true := by decide
