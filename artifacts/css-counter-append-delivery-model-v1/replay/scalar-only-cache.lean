import Examples
open CounterDelivery CounterDelivery.Examples
example : counters [⟨20, 5⟩, ⟨10, 1⟩] = counters [⟨20, 5⟩, ⟨10, 3⟩] := by
  decide +kernel
