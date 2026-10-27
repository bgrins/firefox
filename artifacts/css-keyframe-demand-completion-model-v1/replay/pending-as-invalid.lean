import Examples
open DemandCompletion DemandCompletion.Examples
example : evaluate (pendingAsInvalid initial) (.reference (.provider 1) (.literal [7])) = evaluate completed (.reference (.provider 1) (.literal [7])) := by
  decide +kernel
