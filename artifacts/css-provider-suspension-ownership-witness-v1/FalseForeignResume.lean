import Ownership
open SuspensionOwnership
example : resume 2 ⟨some 1⟩ = (.running, ⟨none⟩) := by decide +kernel
