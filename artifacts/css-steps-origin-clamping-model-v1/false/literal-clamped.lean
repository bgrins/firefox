import Steps
open StepsOrigin
example : repaired .jumpNone (.literal 1) = some 2 := by
  change (none : Option Int) = some 2
  decide +kernel
