import Examples
open ComputedNames.Examples
example : inner = (some [.text "20px"], []) := by
  rw [inner_mark_survives]
  decide +kernel
