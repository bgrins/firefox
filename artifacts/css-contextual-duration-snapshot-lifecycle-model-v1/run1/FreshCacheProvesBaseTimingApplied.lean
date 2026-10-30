import SnapshotLifecycle
open SnapshotLifecycle
example : commit (some (⟨none, 750, .css⟩ : Collection Nat)) 1000 2000 ⟨true, true⟩ = some ⟨some 1000, 1000, .css⟩ := by decide
