import Examples
open DemandCompletion DemandCompletion.Examples
example : eagerReference initial (.provider 0) (.reference (.provider 1) .invalid) = evaluate initial unused := by
  decide +kernel
