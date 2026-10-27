import Steps
open StepsOrigin
example : repaired .jumpNone (.calculation none) = some 2 := by
  change (none : Option Int) = some 2
  decide +kernel
