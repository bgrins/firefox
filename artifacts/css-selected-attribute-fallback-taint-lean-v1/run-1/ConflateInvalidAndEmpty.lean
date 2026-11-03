import Fallback
open SelectedAttributeFallback RetainedAggregateTaint
example : evaluate absent (.fallback .attr 8 "missing" (.literal [])) = none := by decide
