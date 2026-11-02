import Readiness
open ComputedSizeReadiness
example : step witnessToken (.publishSize 20) (initial witnessToken) = some witnessPartial := by decide
