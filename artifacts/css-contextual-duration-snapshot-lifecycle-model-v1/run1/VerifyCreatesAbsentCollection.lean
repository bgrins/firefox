import SnapshotLifecycle
open SnapshotLifecycle
example : (step (none : Option (Collection Nat)) .verify 1000 1000 ⟨true, true⟩).isSome = true := by decide
