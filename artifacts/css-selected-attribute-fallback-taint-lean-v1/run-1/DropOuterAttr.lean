import Fallback
open SelectedAttributeFallback RetainedAggregateTaint
example : (publish (append initial (chunk fallbackValue 7))).tainted = false := by decide
