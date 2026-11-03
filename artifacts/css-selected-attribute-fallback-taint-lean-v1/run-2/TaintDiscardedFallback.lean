import Fallback
open SelectedAttributeFallback RetainedAggregateTaint
example : evaluate primaryEnv (.fallback .other 2 "valid" dirtyUnused) ≠ some clean := by decide
