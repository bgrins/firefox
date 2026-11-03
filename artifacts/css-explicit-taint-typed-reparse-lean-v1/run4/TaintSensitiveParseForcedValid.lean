import Reparse
open ExplicitTaintReparse RetainedAggregateTaint
example : nativeTransported (fun _ bit => if bit then none else some ⟨quoted, false⟩) dirty = some ⟨quoted, true⟩ := by decide
