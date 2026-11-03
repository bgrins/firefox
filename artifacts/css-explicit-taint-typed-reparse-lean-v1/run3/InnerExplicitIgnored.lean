import Reparse
open ExplicitTaintReparse RetainedAggregateTaint
example : transportedReparse echo ⟨quoted, true, false⟩ = some ⟨quoted, false⟩ := by decide
