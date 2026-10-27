import Examples
open DemandCompletion DemandCompletion.Examples
example : evaluate initial (.reference (.provider 2) (.literal [7])) = evaluate changedInvalid (.reference (.provider 2) (.literal [7])) := by
  decide +kernel
