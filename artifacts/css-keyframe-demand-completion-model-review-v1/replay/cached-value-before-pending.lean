import Examples
open DemandCompletion DemandCompletion.Examples
example : evaluate (cachedFirst stale) (.reference (.provider 1) .invalid) = evaluate (fillPending (lookup stale) (fun _ => [40])) (.reference (.provider 1) .invalid) := by
  decide +kernel
