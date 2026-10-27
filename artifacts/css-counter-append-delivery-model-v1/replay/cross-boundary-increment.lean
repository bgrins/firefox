import Examples
open CounterDelivery CounterDelivery.Examples
example : apply (.increment 30 2) [] = apply (.increment 30 2) [⟨10, 1⟩] := by
  decide +kernel
