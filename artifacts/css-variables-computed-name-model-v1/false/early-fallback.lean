import Examples
open ComputedNames.Examples
example : run valid = (some [.text "20px"], []) := by
  rw [valid_result]
  decide +kernel
