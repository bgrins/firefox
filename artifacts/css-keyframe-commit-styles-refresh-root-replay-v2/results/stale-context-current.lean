import Examples
open CommitRefresh
example : compose stack (refresh resolve 100 stack old) 0 = compose stack (resolve 200) 0 := by
  have left : compose stack (refresh resolve 100 stack old) 0 = 110 := by decide +kernel
  have right : (compose stack (resolve 200) 0 : Rat) = 210 := by decide +kernel
  rw [left, right]
  decide +kernel
