import Mutant
open RegisteredInherit
example : selected (witness true) (run true true (witness true) start) = some 7 := by decide
