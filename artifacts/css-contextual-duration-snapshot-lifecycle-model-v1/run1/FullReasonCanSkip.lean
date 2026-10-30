import SnapshotLifecycle
open SnapshotLifecycle
example : dispatch (some (⟨some 1000, 1000, .css⟩ : Collection Nat)) .full 1000 = false := by decide
