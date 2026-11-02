import Readiness
open ComputedSizeReadiness
example : step witnessToken (.publishSize 30) witnessPartial = some (facetNode witnessToken 30) := by decide
