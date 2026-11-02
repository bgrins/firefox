import Readiness
open ComputedSizeReadiness
example : query ⟨1, [facetNode ⟨1, 1, 2, 3⟩ 30]⟩ witnessToken (.unit .computedSize) = .computedSize witnessToken 30 := by decide
