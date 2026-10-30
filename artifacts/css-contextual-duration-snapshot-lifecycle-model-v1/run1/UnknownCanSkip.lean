import SnapshotLifecycle
open SnapshotLifecycle
example : dispatch (some (⟨none, 1000, .css⟩ : Collection Nat)) .verify 1000 = false := by decide
