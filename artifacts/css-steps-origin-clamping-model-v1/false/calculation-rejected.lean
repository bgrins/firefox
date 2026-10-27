import Steps
open StepsOrigin
example : repaired .jumpNone (calculation 4 .nan) = none := by
  rw [repaired_nan]
  decide +kernel
