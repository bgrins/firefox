import Readiness
open ComputedSizeReadiness
example : step witnessToken (.publishSize 30) witnessPartial = some (partial witnessToken 30) := by decide
