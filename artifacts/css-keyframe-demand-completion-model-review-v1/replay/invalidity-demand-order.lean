import Examples
open DemandCompletion DemandCompletion.Examples
example : evaluate initial invalidFirst = evaluate initial pendingFirst := by
  decide +kernel
