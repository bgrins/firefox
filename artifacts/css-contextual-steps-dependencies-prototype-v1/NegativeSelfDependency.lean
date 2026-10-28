import SelfDependency
open ContextualEasing
example : nextFont (nextFont 10) = nextFont 10 := by decide +kernel
