import Examples
open CounterDelivery CounterDelivery.Examples
example : (full true initial children).map counter = [3, 3, 7] := by
  decide +kernel
