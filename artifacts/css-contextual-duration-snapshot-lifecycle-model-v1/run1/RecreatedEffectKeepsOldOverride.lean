import SnapshotLifecycle
open SnapshotLifecycle
example : step (commit (some (⟨some 1000, 1250, .script⟩ : Collection Nat)) 1000 1000 ⟨false, true⟩) .full 2000 2000 ⟨true, true⟩ = some ⟨some 2000, 1250, .script⟩ := by decide
