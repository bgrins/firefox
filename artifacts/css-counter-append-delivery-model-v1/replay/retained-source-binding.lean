import Examples
open CounterDelivery CounterDelivery.Examples
example : (deliver mark (updated (.set 99 3)) staleSources (full false initial children)).map counter = [3, 3, 7] := by
  decide +kernel
