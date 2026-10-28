import Ownership
open SuspensionOwnership
example : release 2 ⟨some 1⟩ = ⟨none⟩ := by decide +kernel
