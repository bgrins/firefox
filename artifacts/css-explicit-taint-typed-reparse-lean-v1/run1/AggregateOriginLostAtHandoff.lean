import Reparse
open ExplicitTaintReparse RetainedAggregateTaint
example : transportedReparse echo (wrap (publish dirtyWitness)) = some ⟨dirtyWitness.bytes, false⟩ := by decide
