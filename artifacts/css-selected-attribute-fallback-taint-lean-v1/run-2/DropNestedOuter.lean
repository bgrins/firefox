import Fallback
open SelectedAttributeFallback RetainedAggregateTaint
example : (mark .attr 7 (mark .attr 8 clean)).origins = [8] := by decide
