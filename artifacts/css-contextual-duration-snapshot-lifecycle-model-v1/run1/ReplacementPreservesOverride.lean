import SnapshotLifecycle
open SnapshotLifecycle
example : commit (some (⟨some 1000, 1250, .script⟩ : Collection Nat)) 2000 2000 ⟨true, false⟩ = some ⟨some 2000, 1250, .script⟩ := by decide
