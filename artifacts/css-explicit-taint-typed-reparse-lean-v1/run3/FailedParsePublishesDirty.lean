import Reparse
open ExplicitTaintReparse RetainedAggregateTaint
example : withInitial ⟨quoted, false⟩ (transportedReparse (fun _ => none) dirty) = ⟨quoted, true⟩ := by decide
