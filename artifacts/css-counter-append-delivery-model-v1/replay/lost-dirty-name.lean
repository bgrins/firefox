import Examples
open CounterDelivery CounterDelivery.Examples
example : (stale (.set 99 3)).map counter = [3, 3, 7] := by
  decide +kernel
