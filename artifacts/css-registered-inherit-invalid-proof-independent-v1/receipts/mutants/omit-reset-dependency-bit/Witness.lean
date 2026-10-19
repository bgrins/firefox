import Mutant
open RegisteredInherit
example : (run true true (witness false) start).inheritsResetStyle = true := by decide
