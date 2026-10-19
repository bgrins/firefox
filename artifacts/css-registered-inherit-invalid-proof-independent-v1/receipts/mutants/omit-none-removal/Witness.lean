import Mutant
open RegisteredInherit
example : selected (witness false) (run true true (witness false) start) = none := by decide
