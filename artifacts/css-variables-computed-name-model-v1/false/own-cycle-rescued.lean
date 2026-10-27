import Examples
open ComputedNames.Examples
example : run nameCycle = (some [.text "20px"], []) := by
  rw [name_cycle_result]
  decide +kernel
