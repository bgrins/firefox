import ProviderPath
open ProviderPath
example : ColumnReadiness.newGate (markedWorld false) 3 = false := by
  rw [clean_column_old_closed_new_open.2]
  decide
