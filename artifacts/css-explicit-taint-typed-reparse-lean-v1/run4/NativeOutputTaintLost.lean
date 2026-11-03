import Reparse
open ExplicitTaintReparse RetainedAggregateTaint
example : nativeLegacy (fun _ _ => some ⟨quoted, true⟩) dirty = some ⟨quoted, false⟩ := by decide
