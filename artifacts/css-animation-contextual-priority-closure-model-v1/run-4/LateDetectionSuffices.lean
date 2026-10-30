import PriorityClosure
open PriorityClosure
example : sameComponent (run .afterPop .rejected) 0 1 = true := by decide
