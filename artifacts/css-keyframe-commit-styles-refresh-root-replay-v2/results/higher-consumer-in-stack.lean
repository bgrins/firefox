import Examples
open CommitRefresh
example : compose stack (refresh resolve 200 [.lower, .top, .higher] old) 0 = 999 := by
  have left : compose stack (refresh resolve 200 [.lower, .top, .higher] old) 0 = 210 := by decide +kernel
  have right : (999 : Rat) = 999 := by decide +kernel
  rw [left, right]
  decide +kernel
