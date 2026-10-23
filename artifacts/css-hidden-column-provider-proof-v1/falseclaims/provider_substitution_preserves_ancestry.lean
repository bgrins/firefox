import ProviderReadiness
open ColumnReadiness
example : newSelection hiddenDirtyProvider 3 0 = ancestors hiddenDirtyProvider 3 2 := by decide
