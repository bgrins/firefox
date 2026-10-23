import ProviderPath
open ProviderPath
example : ColumnReadiness.newGate (markedWorld true) 3 = true := by
  rw [dirty_ancestor_countermodel.2.2.2]
  decide
